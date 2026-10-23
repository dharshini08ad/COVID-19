import csv
import os
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required as django_login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Exists, OuterRef, Q
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import AppointmentForm, PatientForm, StaffForm
from .bigdata import (
    platform_status, export_to_hdfs_format, simulate_hive_query,
    sync_db_to_hdfs, init_hdfs_lake_storage, get_lake_root,
    PRESET_HIVE_QUERIES, HIVE_TABLE_CATALOG, models_q_positive
)
from .models import Appointment, Bed, Patient, Staff, Ward


def login_required(view):
    if settings.DEBUG:
        return view
    return django_login_required(view)


def login_page(request):
    if request.user.is_authenticated or settings.DEBUG:
        return redirect('hms:dashboard')
    error = ''
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', ''),
        )
        if user is not None:
            login(request, user)
            request.session.set_expiry(1209600 if request.POST.get('remember') else 0)
            destination = request.POST.get('next', '')
            if url_has_allowed_host_and_scheme(destination, {request.get_host()}):
                return redirect(destination)
            return redirect('hms:dashboard')
        error = 'The username or password is incorrect.'
    return render(request, 'hms/login.html', {'error': error, 'next': request.GET.get('next', '')})


def logout_page(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    logout(request)
    return redirect('hms:login')


def _ward_summary():
    rows = []
    active_patient = Patient.objects.filter(bed_id=OuterRef('pk'), discharged_at__isnull=True)
    for ward in Ward.objects.annotate(registered_beds=Count('beds')).filter(registered_beds__gt=0).order_by('name'):
        ward_beds = Bed.objects.filter(ward=ward).annotate(occupied_now=Exists(active_patient))
        total = ward_beds.filter(out_of_service=False).count()
        occupied = ward_beds.filter(out_of_service=False, occupied_now=True).count()
        out_of_service = ward_beds.filter(out_of_service=True).count()
        rows.append({
            'ward': ward.name,
            'total': total,
            'occupied': occupied,
            'available': total - occupied,
            'out_of_service': out_of_service,
        })
    return rows


def _month_starts(end_day, count=12):
    year, month = end_day.year, end_day.month
    result = []
    for _ in range(count):
        result.append(date(year, month, 1))
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(result))


def _date_key(value):
    return value.date() if isinstance(value, datetime) else value


@login_required
def dashboard(request):
    today = timezone.localdate()
    start = _parse_date(request.GET.get('start'), today - timedelta(days=29))
    end = _parse_date(request.GET.get('end'), today)
    if start > end:
        start, end = end, start
    if (end - start).days > 364:
        start = end - timedelta(days=364)
    patients = Patient.objects.all()
    admissions = patients.filter(admitted_on__range=(start, end), admission_covid_status='Positive').values('admitted_on').annotate(count=Count('pk'))
    recoveries = patients.filter(
        admission_covid_status='Positive', covid_status='Recovered', discharged_at__date__range=(start, end),
    ).values('discharged_at__date').annotate(count=Count('pk'))
    covid_discharges = patients.filter(
        admission_covid_status='Positive', discharged_at__date__range=(start, end),
    ).values('discharged_at__date').annotate(count=Count('pk'))
    admissions_by_day = {row['admitted_on']: row['count'] for row in admissions}
    recoveries_by_day = {row['discharged_at__date']: row['count'] for row in recoveries}
    discharges_by_day = {row['discharged_at__date']: row['count'] for row in covid_discharges}
    day_list = [start + timedelta(days=offset) for offset in range((end - start).days + 1)]
    ward_rows = _ward_summary()
    total_beds = sum(row['total'] for row in ward_rows)
    occupied_beds = sum(row['occupied'] for row in ward_rows)
    dashboard_chart_data = {
        'trendLabels': [day.strftime('%b %d') for day in day_list],
        'newCases': [admissions_by_day.get(day, 0) for day in day_list],
        'recovered': [recoveries_by_day.get(day, 0) for day in day_list],
        'resourceLabels': [row['ward'] for row in ward_rows],
        'resourceUtil': [round(100 * row['occupied'] / row['total'], 1) if row['total'] else 0 for row in ward_rows],
    }
    active = patients.filter(covid_status='Positive', discharged_at__isnull=True)
    return render(request, 'hms/dashboard.html', {
        'page_title': 'Hospital dashboard', 'active': 'dashboard',
        'today': today,
        'stats': {
            'total_patients': patients.count(),
            'active_cases': active.count(),
            'critical_patients': active.filter(severity='Critical').count(),
            'beds_available': total_beds - occupied_beds,
            'beds_occupied': occupied_beds,
            'beds_total': total_beds,
            'today_admissions': patients.filter(admitted_on=today).count(),
            'today_discharges': patients.filter(discharged_at__date=today).count(),
            'available_staff': Staff.objects.filter(is_active=True, available=True).count(),
            'today_appointments': Appointment.objects.filter(starts_at__date=today).exclude(status='Cancelled').count(),
            'new_admissions_period': patients.filter(admitted_on__range=(start, end), admission_covid_status='Positive').count(),
            'recoveries_period': patients.filter(admission_covid_status='Positive', covid_status='Recovered', discharged_at__date__range=(start, end)).count(),
        },
        'recent_admissions': patients.select_related('ward', 'bed').order_by('-admitted_on', '-created_at')[:6],
        'beds': ward_rows,
        'has_patient_data': patients.filter(admitted_on__range=(start, end)).exists(),
        'dashboard_chart_data': dashboard_chart_data,
        'start_date': start.isoformat(), 'end_date': end.isoformat(),
    })


@login_required
def patients(request):
    rows = Patient.objects.select_related('ward', 'bed', 'doctor').all()
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    discharge = request.GET.get('discharge', '')
    department = request.GET.get('department', '')
    if query:
        rows = rows.filter(
            Q(name__icontains=query) | Q(uhid__icontains=query)
            | Q(doctor__name__icontains=query) | Q(doctor__department__icontains=query)
        )
    if status in dict(Patient.COVID_STATUS):
        rows = rows.filter(covid_status=status)
    if discharge == 'admitted':
        rows = rows.filter(discharged_at__isnull=True)
    elif discharge == 'discharged':
        rows = rows.filter(discharged_at__isnull=False)
    if department:
        rows = rows.filter(doctor__department=department)
    paginator = Paginator(rows, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'hms/patients.html', {
        'page_title': 'Patient management', 'active': 'patients',
        'patients': page_obj.object_list, 'page_obj': page_obj, 'total': paginator.count,
        'search_query': query, 'selected_status': status, 'selected_discharge': discharge,
        'departments': Staff.objects.filter(is_active=True).order_by().values_list('department', flat=True).distinct(),
        'selected_department': department,
    })


@login_required
def patient_register(request):
    form = PatientForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            patient = form.save()
        except IntegrityError:
            form.add_error('bed', 'That bed was assigned by another request. Select a different bed and try again.')
        else:
            messages.success(request, f'Patient {patient.uhid} was registered.')
            return redirect('hms:patient_detail', patient_id=patient.pk)
    return render(request, 'hms/patient_register.html', {
        'page_title': 'Register patient', 'active': 'patients', 'form': form, 'editing': False,
    })


@login_required
def patient_detail(request, patient_id):
    patient = get_object_or_404(Patient.objects.select_related('ward', 'bed', 'doctor'), pk=patient_id)
    return render(request, 'hms/patient_detail.html', {
        'page_title': patient.name, 'active': 'patients', 'patient': patient,
    })


@login_required
def patient_edit(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    form = PatientForm(request.POST if request.method == 'POST' else None, instance=patient)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            form.add_error('bed', 'That bed was assigned by another request. Select a different bed and try again.')
        else:
            messages.success(request, f'Patient {patient.uhid} was updated.')
            return redirect('hms:patient_detail', patient_id=patient.pk)
    return render(request, 'hms/patient_register.html', {
        'page_title': 'Edit patient', 'active': 'patients', 'form': form, 'editing': True, 'patient': patient,
    })


@login_required
def patient_discharge(request, patient_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    patient = get_object_or_404(Patient, pk=patient_id)
    if patient.discharged_at is None:
        patient.discharged_at = timezone.now()
        patient.save(update_fields=['discharged_at'])
        messages.success(request, f'{patient.name} was discharged.')
    else:
        messages.info(request, 'This patient is already discharged.')
    return redirect('hms:patient_detail', patient_id=patient.pk)


@login_required
def staff(request):
    form = StaffForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        member = form.save()
        messages.success(request, f'{member.name} was added to the staff directory.')
        return redirect('hms:staff')
    staff_rows = Staff.objects.filter(is_active=True).annotate(
        active_patients=Count('patients', filter=Q(patients__discharged_at__isnull=True), distinct=True),
    )
    query = request.GET.get('q', '').strip()
    department = request.GET.get('department', '')
    availability = request.GET.get('availability', '')
    role = request.GET.get('role', '')
    if query:
        staff_rows = staff_rows.filter(Q(name__icontains=query) | Q(role__icontains=query) | Q(department__icontains=query))
    if department:
        staff_rows = staff_rows.filter(department=department)
    if availability in ('available', 'unavailable'):
        staff_rows = staff_rows.filter(available=(availability == 'available'))
    if role:
        staff_rows = staff_rows.filter(role=role)
    return render(request, 'hms/staff.html', {
        'page_title': 'Doctors & staff', 'active': 'staff', 'staff': staff_rows,
        'staff_form': form, 'show_staff_form': bool(request.POST and not form.is_valid()),
        'departments': Staff.objects.filter(is_active=True).order_by().values_list('department', flat=True).distinct(),
        'selected_department': department, 'selected_availability': availability, 'search_query': query,
        'roles': Staff.objects.filter(is_active=True).order_by().values_list('role', flat=True).distinct(),
        'selected_role': role,
    })


@login_required
def staff_edit(request, staff_id):
    member = get_object_or_404(Staff, pk=staff_id, is_active=True)
    form = StaffForm(request.POST if request.method == 'POST' else None, instance=member)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'{member.name} was updated.')
        return redirect('hms:staff')
    return render(request, 'hms/staff_form.html', {
        'page_title': 'Edit staff member', 'active': 'staff', 'form': form, 'member': member,
    })


@login_required
def staff_detail(request, staff_id):
    member = get_object_or_404(Staff, pk=staff_id, is_active=True)
    return render(request, 'hms/staff_detail.html', {
        'page_title': member.name, 'active': 'staff', 'member': member,
        'active_patient_count': member.patients.filter(discharged_at__isnull=True).count(),
    })


@login_required
def appointments(request):
    form = AppointmentForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            form.add_error('appointment_time', 'That doctor and time slot was just booked. Choose another time.')
        else:
            messages.success(request, 'Appointment saved.')
            return redirect('hms:appointments')
    rows = Appointment.objects.select_related('patient', 'doctor').all()
    status = request.GET.get('status', '')
    if status in dict(Appointment.STATUSES):
        rows = rows.filter(status=status)
    return render(request, 'hms/appointments.html', {
        'page_title': 'Appointments', 'active': 'appointments', 'appointments': rows,
        'patients': Patient.objects.order_by('name'), 'staff': Staff.objects.filter(is_active=True),
        'admissions': Patient.objects.filter(discharged_at__isnull=True).select_related('ward', 'bed').order_by('-admitted_on'),
        'appointment_form': form, 'show_appointment_form': bool(request.POST and not form.is_valid()),
        'selected_status': status, 'appointment_statuses': Appointment.STATUSES,
        'appointment_action': reverse('hms:appointments'),
    })


@login_required
def appointment_edit(request, appointment_id):
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    form = AppointmentForm(request.POST if request.method == 'POST' else None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            form.add_error('appointment_time', 'That doctor and time slot was just booked. Choose another time.')
        else:
            messages.success(request, 'Appointment updated.')
            return redirect('hms:appointments')
    rows = Appointment.objects.select_related('patient', 'doctor').all()
    return render(request, 'hms/appointments.html', {
        'page_title': 'Reschedule appointment', 'active': 'appointments', 'appointments': rows,
        'patients': Patient.objects.order_by('name'), 'staff': Staff.objects.filter(is_active=True),
        'admissions': Patient.objects.filter(discharged_at__isnull=True).select_related('ward', 'bed'),
        'appointment_form': form, 'show_appointment_form': True,
        'selected_status': '', 'appointment_statuses': Appointment.STATUSES,
        'appointment_action': reverse('hms:appointment_edit', args=[appointment.pk]),
    })


@login_required
def appointment_cancel(request, appointment_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    appointment = get_object_or_404(Appointment, pk=appointment_id)
    if appointment.status not in ('Completed', 'Cancelled'):
        appointment.status = 'Cancelled'
        appointment.save(update_fields=['status'])
        messages.success(request, 'Appointment cancelled.')
    return redirect('hms:appointments')


@login_required
def beds(request):
    ward_rows = _ward_summary()
    total_beds = sum(row['total'] for row in ward_rows)
    occupied = sum(row['occupied'] for row in ward_rows)
    out_of_service = sum(row['out_of_service'] for row in ward_rows)
    return render(request, 'hms/beds.html', {
        'page_title': 'Bed management', 'active': 'beds', 'beds': ward_rows,
        'total_beds': total_beds, 'total_occupied': occupied,
        'total_available': total_beds - occupied, 'total_out_of_service': out_of_service,
        'bed_chart_data': {
            'wards': [row['ward'] for row in ward_rows],
            'occupied': [row['occupied'] for row in ward_rows],
            'free': [row['available'] for row in ward_rows],
        },
    })


@login_required
def analytics(request):
    today = timezone.localdate()
    start = _parse_date(request.GET.get('start'), today - timedelta(days=364))
    end = _parse_date(request.GET.get('end'), today)
    if start > end:
        start, end = end, start
    months = []
    month = start.replace(day=1)
    while month <= end:
        months.append(month)
        month = date(month.year + (month.month == 12), 1 if month.month == 12 else month.month + 1, 1)

    admissions = Patient.objects.filter(admitted_on__range=(start, end)).filter(models_q_positive()).annotate(
        month=TruncMonth('admitted_on'),
    ).values('month').annotate(total=Count('pk'))
    recovered = Patient.objects.filter(
        discharged_at__date__gte=start, discharged_at__date__lte=end,
        covid_status='Recovered',
    ).annotate(month=TruncMonth('discharged_at')).values('month').annotate(total=Count('pk'))
    admission_by_month = {_date_key(row['month']): row['total'] for row in admissions}
    recovered_by_month = {_date_key(row['month']): row['total'] for row in recovered}

    daily_start = max(start, end - timedelta(days=29))
    daily_admissions = Patient.objects.filter(admitted_on__range=(daily_start, end)).filter(models_q_positive()).values(
        'admitted_on',
    ).annotate(total=Count('pk'))
    daily_recoveries = Patient.objects.filter(
        discharged_at__date__range=(daily_start, end), covid_status='Recovered',
    ).values('discharged_at__date').annotate(total=Count('pk'))
    daily_discharges = Patient.objects.filter(
        discharged_at__date__range=(daily_start, end),
    ).values('discharged_at__date').annotate(total=Count('pk'))
    daily_cases = {row['admitted_on']: row['total'] for row in daily_admissions}
    daily_recovered = {row['discharged_at__date']: row['total'] for row in daily_recoveries}
    daily_discharged = {row['discharged_at__date']: row['total'] for row in daily_discharges}
    days = [daily_start + timedelta(days=index) for index in range((end - daily_start).days + 1)]

    active_count = Patient.objects.filter(
        covid_status='Positive', discharged_at__isnull=True, admitted_on__lt=daily_start,
    ).count()
    daily_active = []
    for day in days:
        active_count += daily_cases.get(day, 0) - daily_discharged.get(day, 0)
        daily_active.append(max(active_count, 0))

    period_patients = Patient.objects.filter(admitted_on__range=(start, end))
    positive_total = period_patients.filter(models_q_positive()).count()
    recovered_total = Patient.objects.filter(
        covid_status='Recovered', discharged_at__date__range=(start, end),
    ).count()
    discharged_total = Patient.objects.filter(
        discharged_at__date__range=(start, end),
    ).count()

    district_rows = Patient.objects.filter(
        admitted_on__range=(start, end)
    ).filter(models_q_positive()).exclude(district='').values('district').annotate(
        cases=Count('pk'),
        active=Count('pk', filter=Q(covid_status='Positive', discharged_at__isnull=True)),
        recovered=Count('pk', filter=Q(covid_status='Recovered')),
    ).order_by('-cases')
    districts = []
    for row in district_rows:
        districts.append({
            'name': row['district'], 'cases': row['cases'], 'active': row['active'],
            'recovered': row['recovered'],
            'rate': round(100 * row['recovered'] / row['cases'], 1) if row['cases'] else 0,
        })

    chart_data = {
        'monthlyLabels': [month.strftime('%b %Y') for month in months],
        'monthlyCases': [admission_by_month.get(month, 0) for month in months],
        'monthlyRecovered': [recovered_by_month.get(month, 0) for month in months],
        'dailyLabels': [day.strftime('%b %d') for day in days],
        'dailyNew': [daily_cases.get(day, 0) for day in days],
        'dailyRecovered': [daily_recovered.get(day, 0) for day in days],
        'dailyActive': daily_active,
        'districtNames': [row['name'] for row in districts],
        'districtActive': [row['active'] for row in districts],
    }
    platform = platform_status()
    has_period_data = period_patients.exists() or Patient.objects.filter(
        discharged_at__date__range=(start, end),
    ).exists()
    hive_query_result = request.session.pop('hive_query_result', None)
    hive_query_last = request.session.pop('hive_query_result_last_query', None)

    if hive_query_result:
        # Ensure the stored result has all expected fields
        if 'engine_status' not in hive_query_result:
            hive_query_result['engine_status'] = 'LOCAL_SIMULATION'
        if 'status' not in hive_query_result:
            hive_query_result['status'] = 'SUCCESS'
        if 'hive_engine_configured' not in hive_query_result:
            hive_query_result['hive_engine_configured'] = False
        if 'hdfs_engine_configured' not in hive_query_result:
            hive_query_result['hdfs_engine_configured'] = False
    else:
        hive_query_result = simulate_hive_query('district_wise')
        hive_query_last = 'district_wise'

    return render(request, 'hms/analytics.html', {
        'page_title': 'Hospital analytics', 'active': 'analytics',
        'chart_data': chart_data,
        'positive_total': positive_total, 'recovered_total': recovered_total,
        'active_total': Patient.objects.filter(covid_status='Positive', discharged_at__isnull=True).count(),
        'recovery_rate': round(100 * recovered_total / discharged_total, 1) if discharged_total else (round(100 * recovered_total / max(1, positive_total), 1) if positive_total else None),
        'hdfs_status': platform['hdfs']['status'], 'hive_status': platform['hive']['status'],
        'hdfs_detail': platform['hdfs']['detail'], 'hive_detail': platform['hive']['detail'],
        'platform': platform,
        'hdfs_datasets': platform['hdfs_datasets'],
        'districts': districts, 'has_patient_data': has_period_data,
        'start_date': start.isoformat(), 'end_date': end.isoformat(),
        'hive_query_result': hive_query_result,
        'hive_query_last': hive_query_last,
        'hive_presets': PRESET_HIVE_QUERIES,
    })


def _parse_date(value, fallback):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return fallback


def _report_csv(start, end, report_type):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f'meridian-{report_type}-snapshot-{timezone.localdate().isoformat()}.csv' if report_type in {'beds', 'staff'} else f'meridian-{report_type}-{start.isoformat()}-to-{end.isoformat()}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)

    def write_row(values):
        safe_values = [
            "'" + value if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')) else value
            for value in values
        ]
        writer.writerow(safe_values)

    if report_type == 'staff':
        write_row(['Name', 'Role', 'Department', 'Availability'])
        for member in Staff.objects.filter(is_active=True).order_by('department', 'name'):
            write_row([member.name, member.role, member.department, 'Available' if member.available else 'Unavailable'])
    elif report_type == 'appointments':
        write_row(['Appointment', 'Patient ID', 'Patient', 'Doctor', 'Date', 'Time', 'Type', 'Status'])
        for item in Appointment.objects.filter(starts_at__date__range=(start, end)).select_related('patient', 'doctor'):
            write_row([item.id_label, item.patient.uhid, item.patient.name, item.doctor.name, item.date, item.time, item.appointment_type, item.status])
    elif report_type == 'beds':
        write_row(['Ward', 'Beds in service', 'Occupied', 'Available', 'Out of service'])
        for row in _ward_summary():
            write_row([row['ward'], row['total'], row['occupied'], row['available'], row['out_of_service']])
    elif report_type == 'discharges':
        write_row(['Patient ID', 'Patient', 'COVID status', 'Severity', 'Ward', 'Admission date', 'Discharge date'])
        records = Patient.objects.filter(discharged_at__date__range=(start, end)).select_related('ward')
        for patient in records:
            write_row([patient.uhid, patient.name, patient.covid_status, patient.severity, patient.ward.name if patient.ward_id else '', patient.admitted_on, patient.discharged_at.date()])
    elif report_type == 'covid':
        write_row(['Patient ID', 'Patient', 'COVID status', 'Severity', 'District', 'Admission date', 'Discharge date'])
        records = Patient.objects.filter(admitted_on__range=(start, end), admission_covid_status='Positive')
        for patient in records:
            write_row([patient.uhid, patient.name, patient.covid_status, patient.severity, patient.district, patient.admitted_on, patient.discharged_at.date() if patient.discharged_at else ''])
    else:
        write_row(['Patient ID', 'Patient', 'Age', 'COVID status', 'Severity', 'Ward', 'Bed', 'Admission date', 'Discharge date'])
        records = Patient.objects.filter(admitted_on__range=(start, end)).select_related('ward', 'bed')
        for patient in records:
            write_row([patient.uhid, patient.name, patient.age, patient.covid_status, patient.severity, patient.ward.name if patient.ward_id else '', patient.bed.number if patient.bed_id else '', patient.admitted_on, patient.discharged_at.date() if patient.discharged_at else ''])
    return response


@login_required
def reports(request):
    today = timezone.localdate()
    start = _parse_date(request.GET.get('start'), today - timedelta(days=365))
    end = _parse_date(request.GET.get('end'), today)
    if start > end:
        start, end = end, start
    report_type = request.GET.get('report_type', 'patients')
    report_types = {'patients', 'admissions', 'discharges', 'covid', 'beds', 'staff', 'appointments'}
    if report_type not in report_types:
        report_type = 'patients'
    if request.GET.get('download') == 'csv':
        return _report_csv(start, end, report_type)
    months = [month for month in _month_starts(end) if start.replace(day=1) <= month <= end.replace(day=1)]
    monthly_rows = []
    for month in months:
        next_month = date(month.year + (month.month == 12), 1 if month.month == 12 else month.month + 1, 1)
        period_start = max(start, month)
        period_end = min(end, next_month - timedelta(days=1))
        admissions = Patient.objects.filter(admitted_on__range=(period_start, period_end)).count()
        discharges = Patient.objects.filter(discharged_at__date__range=(period_start, period_end))
        discharge_count = discharges.count()
        recovered_count = discharges.filter(covid_status='Recovered').count()
        if admissions or discharge_count:
            monthly_rows.append({
                'month': month.strftime('%B %Y'), 'admissions': admissions,
                'discharges': discharge_count,
                'recovery': round(100 * recovered_count / discharge_count, 1) if discharge_count else 0,
            })
    registered = Patient.objects.count()
    admission_count = Patient.objects.filter(admitted_on__range=(start, end)).count()
    discharges = Patient.objects.filter(discharged_at__date__range=(start, end))
    discharge_count = discharges.count()
    recovery_rate = round(100 * discharges.filter(covid_status='Recovered').count() / discharge_count, 1) if discharge_count else 0
    report_chart_data = {
        'labels': [row['month'] for row in monthly_rows],
        'admissions': [row['admissions'] for row in monthly_rows],
        'discharges': [row['discharges'] for row in monthly_rows],
    }
    ward_rows = _ward_summary()
    return render(request, 'hms/reports.html', {
        'page_title': 'Operational reports', 'active': 'reports',
        'summary': [
            {'label': 'Registered patients', 'value': registered, 'delta': ''},
            {'label': 'Admissions in period', 'value': admission_count, 'delta': f'({start.strftime("%b %d")} - {end.strftime("%b %d")})'},
            {'label': 'Discharges in period', 'value': discharge_count, 'delta': f'({start.strftime("%b %d")} - {end.strftime("%b %d")})'},
            {'label': 'Recovered among discharges', 'value': f'{recovery_rate}%', 'delta': ''},
        ],
        'monthly_rows': monthly_rows,
        'monthly_labels': [row['month'] for row in monthly_rows],
        'monthly_cases': [row['admissions'] for row in monthly_rows],
        'monthly_recovered': [row['discharges'] for row in monthly_rows],
        'report_chart_data': report_chart_data,
        'wards': ward_rows,
        'start_date': start.isoformat(), 'end_date': end.isoformat(),
        'selected_report_type': report_type, 'has_data': bool(monthly_rows),
        'download_url': f"{reverse('hms:reports')}?start={start.isoformat()}&end={end.isoformat()}&report_type={report_type}&download=csv",
    })


@login_required
def bigdata_export(request):
    data_type = request.GET.get('type', 'patients')
    filename, record_count = export_to_hdfs_format(data_type)

    if filename:
        # Verify file exists and has content
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                response = HttpResponse(content, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
                messages.success(request, f'Exported {record_count} records to CSV format for HDFS upload.')
                # Clean up temp file
                try:
                    os.unlink(filename)
                except OSError:
                    pass
                return response
            except Exception as read_err:
                messages.error(request, f'Exported {record_count} records, but failed to read file: {str(read_err)}')
                # Still clean up
                try:
                    os.unlink(filename)
                except OSError:
                    pass
        else:
            messages.error(request, 'Export failed: file was created but is empty or does not exist.')
            try:
                os.unlink(filename)
            except OSError:
                pass
    else:
        messages.error(request, 'Invalid data type for export.')

    return redirect('hms:analytics')


@login_required
def bigdata_query(request):
    query_type = request.GET.get('query', 'district_wise')
    custom_sql = request.GET.get('sql', '').strip()
    next_url = request.GET.get('next')

    try:
        result = simulate_hive_query(query_type, custom_sql=custom_sql if custom_sql else None)

        if result['results']:
            messages.success(request, f"HiveQL query '{result['title']}' executed successfully in {result['execution_time_seconds']}s (scanned {result['rows_scanned']:,} records). Status: {result['engine_status']}")
        else:
            messages.info(request, 'Hive query execution returned 0 rows.')

        # Store in session with a copy to avoid reference issues
        request.session['hive_query_result'] = dict(result)
        request.session['hive_query_result_last_query'] = query_type

    except Exception as e:
        messages.error(request, f'Hive query execution failed: {str(e)}')
        # Store error state in session
        request.session['hive_query_result'] = {
            'query_type': query_type,
            'title': 'Error Query',
            'status': 'ERROR',
            'error_message': str(e),
            'rows': [],
            'headers': [],
            'results': [],
            'engine_status': 'LOCAL_SIMULATION (Hive engine unavailable)',
        }
        request.session['hive_query_result_last_query'] = query_type

    if next_url:
        return redirect(next_url)
    return redirect('hms:analytics')


@login_required
def bigdata_studio(request):
    init_hdfs_lake_storage()
    platform = platform_status()
    hive_presets = PRESET_HIVE_QUERIES
    table_catalog = HIVE_TABLE_CATALOG

    query_key = request.GET.get('query', 'district_wise')
    custom_sql = request.GET.get('sql', '').strip()

    if custom_sql:
        query_result = simulate_hive_query('custom', custom_sql=custom_sql)
    else:
        query_result = simulate_hive_query(query_key)

    return render(request, 'hms/bigdata_studio.html', {
        'page_title': 'HDFS & Hive Big Data Studio',
        'active': 'bigdata',
        'platform': platform,
        'datasets': platform['hdfs_datasets'],
        'presets': hive_presets,
        'selected_query': query_key,
        'query_result': query_result,
        'catalog': table_catalog,
        'lake_base_path': '/user/hadoop/covid19',
    })


@login_required
def bigdata_sync(request):
    result = sync_db_to_hdfs()
    messages.success(
        request,
        f"Sqoop ETL Ingest Completed: {result['patients_synced']} patients, {result['telemetry_readings']} telemetry vitals synced to HDFS Lake."
    )
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('hms:bigdata_studio')


@login_required
def bigdata_preview(request):
    dataset_name = request.GET.get('dataset', 'patients')
    lake_root = get_lake_root()
    base_hdfs = lake_root / 'user' / 'hadoop' / 'covid19'

    path_map = {
        'patients': base_hdfs / 'patients' / 'covid_patients_master.csv',
        'admissions': base_hdfs / 'admissions' / 'admissions_partitioned_stream.csv',
        'icu_telemetry': base_hdfs / 'icu_telemetry' / 'icu_bedside_telemetry_stream.csv',
        'bed_occupancy': base_hdfs / 'bed_occupancy' / 'bed_occupancy_hourly_snapshots.csv',
        'district_epidemiology': base_hdfs / 'district_epidemiology' / 'district_epidemiology_census.csv',
        'vaccination_registry': base_hdfs / 'vaccination_registry' / 'vaccination_breakthrough_logs.csv',
    }

    target = path_map.get(dataset_name)
    headers = []
    rows = []
    if target and target.exists():
        with open(target, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
                for _ in range(15):
                    rows.append(next(reader))
            except StopIteration:
                pass
    return JsonResponse({'dataset': dataset_name, 'headers': headers, 'rows': rows, 'path': f'/user/hadoop/covid19/{dataset_name}'})