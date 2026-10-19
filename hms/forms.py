from datetime import datetime, time, timedelta

from django import forms
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from .models import Appointment, Bed, Patient, Staff


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'name', 'age', 'gender', 'district', 'blood_group', 'phone', 'covid_status',
            'severity', 'ward', 'bed', 'doctor', 'admitted_on', 'symptoms', 'oxygen',
        ]
        widgets = {'admitted_on': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        occupied = Patient.objects.filter(bed_id=OuterRef('pk'), discharged_at__isnull=True)
        beds = Bed.objects.filter(out_of_service=False).annotate(is_occupied=Exists(occupied)).filter(is_occupied=False)
        if self.instance.pk and self.instance.bed_id:
            beds = Bed.objects.filter(Q(pk=self.instance.bed_id) | Q(pk__in=beds.values('pk')))
        self.fields['bed'].queryset = beds.select_related('ward')
        self.fields['doctor'].queryset = Staff.objects.filter(is_active=True)
        self.fields['bed'].required = False
        self.fields['ward'].required = False
        self.fields['doctor'].required = False

    def clean(self):
        cleaned = super().clean()
        bed = cleaned.get('bed')
        ward = cleaned.get('ward')
        if bed and ward and bed.ward_id != ward.pk:
            self.add_error('bed', 'Choose a bed from the selected ward.')
        elif bed and not ward:
            cleaned['ward'] = bed.ward
        return cleaned


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['name', 'role', 'department', 'phone', 'email', 'shift', 'experience', 'available']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+91 XXXXX XXXXX'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['email'].required = False
        self.fields['shift'].required = False
        self.fields['experience'].required = False


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    appointment_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.order_by('name')
        self.fields['doctor'].queryset = Staff.objects.filter(is_active=True).order_by('name')
        if self.instance.pk:
            self.initial.setdefault('appointment_date', timezone.localtime(self.instance.starts_at).date())
            self.initial.setdefault('appointment_time', timezone.localtime(self.instance.starts_at).time())
        else:
            self.initial.setdefault('appointment_date', timezone.localdate() + timedelta(days=1))
            self.initial.setdefault('appointment_time', time(10, 0))

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('appointment_date')
        time = cleaned.get('appointment_time')
        doctor = cleaned.get('doctor')
        if date and time:
            starts_at = timezone.make_aware(datetime.combine(date, time), timezone.get_current_timezone())
            cleaned['starts_at'] = starts_at
            if starts_at <= timezone.now():
                self.add_error('appointment_date', 'Choose a future date and time.')
            if doctor and Appointment.objects.filter(doctor=doctor, starts_at=starts_at).exclude(status='Cancelled').exclude(pk=self.instance.pk).exists():
                self.add_error('appointment_time', 'This doctor already has an appointment at that time.')
        return cleaned

    def save(self, commit=True):
        appointment = super().save(commit=False)
        appointment.starts_at = self.cleaned_data['starts_at']
        if commit:
            appointment.save()
        return appointment