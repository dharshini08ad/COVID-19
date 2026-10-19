from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Appointment, Bed, Patient, Staff, Ward
from .bigdata import hdfs_status, hive_status
from .forms import PatientForm


class HospitalWorkflowTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='auditor', password='a-strong-test-password')
		self.client.force_login(self.user)
		self.ward = Ward.objects.create(name='ICU', capacity=2)
		self.bed = Bed.objects.create(ward=self.ward, number='ICU-01')
		self.doctor = Staff.objects.create(name='Dr. Test', role='Consultant', department='ICU')

	def create_patient(self, **overrides):
		values = {
			'name': 'Test Patient', 'age': 40, 'gender': 'Other', 'covid_status': 'Positive',
			'severity': 'Moderate', 'ward': self.ward, 'admitted_on': timezone.localdate(),
		}
		values.update(overrides)
		return Patient.objects.create(**values)

	def test_private_pages_redirect_to_login(self):
		self.client.logout()
		response = self.client.get(reverse('hms:dashboard'))
		self.assertRedirects(response, f"{reverse('hms:login')}?next={reverse('hms:dashboard')}")

	def test_login_authenticates_and_rejects_external_redirect(self):
		self.client.logout()
		response = self.client.post(reverse('hms:login'), {
			'username': 'auditor', 'password': 'a-strong-test-password',
			'next': 'https://attacker.invalid/', 'remember': 'on',
		})
		self.assertRedirects(response, reverse('hms:dashboard'))
		self.assertEqual(self.client.get(reverse('hms:dashboard')).status_code, 200)

	def test_patient_registration_persists_and_lists_record(self):
		response = self.client.post(reverse('hms:patient_register'), {
			'name': 'Persisted Patient', 'age': '31', 'gender': 'Female', 'district': 'North',
			'blood_group': 'A+', 'phone': '555-0100', 'covid_status': 'Positive',
			'severity': 'Mild', 'ward': str(self.ward.pk), 'bed': str(self.bed.pk),
			'doctor': str(self.doctor.pk), 'admitted_on': timezone.localdate().isoformat(),
			'symptoms': 'Cough',
		})
		self.assertEqual(response.status_code, 302)
		patient = Patient.objects.get(name='Persisted Patient')
		self.assertTrue(patient.uhid.startswith('MC-'))
		self.assertContains(self.client.get(reverse('hms:patients')), patient.uhid)
		self.assertContains(self.client.get(reverse('hms:patient_detail', args=[patient.pk])), 'Cough')

	def test_patient_form_rejects_future_admission_date(self):
		form = PatientForm(data={
			'name': 'Future Admission', 'age': '20', 'gender': 'Female',
			'covid_status': 'Positive', 'severity': 'Mild',
			'admitted_on': (timezone.localdate() + timedelta(days=1)).isoformat(),
			'ward': '', 'bed': '', 'doctor': '', 'blood_group': '', 'phone': '',
			'district': '', 'symptoms': '', 'oxygen': '',
		})
		self.assertFalse(form.is_valid())
		self.assertIn('admitted_on', form.errors)

	def test_patient_edit_persists_updated_fields(self):
		patient = self.create_patient()
		response = self.client.post(reverse('hms:patient_edit', args=[patient.pk]), {
			'name': 'Updated Patient', 'age': '41', 'gender': 'Other', 'district': 'South',
			'blood_group': '', 'phone': '', 'covid_status': 'Positive', 'severity': 'Severe',
			'ward': str(self.ward.pk), 'bed': '', 'doctor': str(self.doctor.pk),
			'admitted_on': patient.admitted_on.isoformat(), 'symptoms': 'Updated symptoms',
		})
		self.assertEqual(response.status_code, 302)
		patient.refresh_from_db()
		self.assertEqual(patient.name, 'Updated Patient')
		self.assertEqual(patient.severity, 'Severe')

	def test_patient_directory_filters_by_doctor_department(self):
		patient = self.create_patient(doctor=self.doctor)
		response = self.client.get(reverse('hms:patients'), {'department': 'ICU'})
		self.assertContains(response, patient.uhid)
		self.assertContains(response, 'ICU')

	def test_staff_department_filter_uses_database_values(self):
		Staff.objects.create(name='Ward Nurse', role='Nurse', department='General Ward')
		response = self.client.get(reverse('hms:staff'), {'department': 'ICU'})
		self.assertContains(response, 'Dr. Test')
		self.assertNotContains(response, 'Ward Nurse')

	def test_staff_role_filter_uses_database_values(self):
		Staff.objects.create(name='Ward Nurse', role='Nurse', department='General Ward')
		response = self.client.get(reverse('hms:staff'), {'role': 'Nurse'})
		self.assertContains(response, 'Ward Nurse')
		self.assertNotContains(response, 'Dr. Test')

	def test_staff_creation_persists(self):
		response = self.client.post(reverse('hms:staff'), {
			'name': 'New Clinician', 'role': 'Registrar', 'department': 'Radiology',
			'email': 'clinician@example.test', 'phone': '5550101', 'shift': 'Day',
			'experience': '2 years', 'available': 'on',
		})
		self.assertEqual(response.status_code, 302)
		self.assertTrue(Staff.objects.filter(name='New Clinician', department='Radiology').exists())

	def test_authenticated_primary_routes_render(self):
		patient = self.create_patient()
		appointment = Appointment.objects.create(
			patient=patient, doctor=self.doctor,
			starts_at=timezone.now() + timedelta(days=3),
		)
		routes = [
			reverse('hms:dashboard'), reverse('hms:patients'),
			reverse('hms:patient_register'), reverse('hms:patient_detail', args=[patient.pk]),
			reverse('hms:patient_edit', args=[patient.pk]), reverse('hms:staff'),
			reverse('hms:staff_detail', args=[self.doctor.pk]), reverse('hms:staff_edit', args=[self.doctor.pk]),
			reverse('hms:appointments'), reverse('hms:appointment_edit', args=[appointment.pk]),
			reverse('hms:beds'), reverse('hms:analytics'), reverse('hms:reports'),
		]
		for route in routes:
			with self.subTest(route=route):
				self.assertEqual(self.client.get(route).status_code, 200)

	def test_appointment_conflict_is_rejected(self):
		patient = self.create_patient()
		starts_at = timezone.localtime(timezone.now() + timedelta(days=2)).replace(second=0, microsecond=0)
		starts_at = starts_at.replace(minute=0)
		Appointment.objects.create(patient=patient, doctor=self.doctor, starts_at=starts_at)
		response = self.client.post(reverse('hms:appointments'), {
			'patient': str(patient.pk), 'doctor': str(self.doctor.pk),
			'appointment_date': starts_at.date().isoformat(),
			'appointment_time': starts_at.strftime('%H:%M'), 'appointment_type': 'Review',
		})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(Appointment.objects.count(), 1)
		self.assertContains(response, 'already has an appointment')

	def test_appointment_creation_persists(self):
		patient = self.create_patient()
		appointment_date = (timezone.localdate() + timedelta(days=4)).isoformat()
		response = self.client.post(reverse('hms:appointments'), {
			'patient': str(patient.pk), 'doctor': str(self.doctor.pk),
			'appointment_date': appointment_date, 'appointment_time': '11:30',
			'appointment_type': 'Follow-up',
		})
		self.assertEqual(response.status_code, 302)
		self.assertTrue(Appointment.objects.filter(patient=patient, appointment_type='Follow-up').exists())

	def test_analytics_uses_recorded_data_and_reports_hdfs_unavailable(self):
		self.create_patient(district='North')
		response = self.client.get(reverse('hms:analytics'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Not configured')
		self.assertContains(response, 'North')
		self.assertContains(response, 'analytics-data')

	def test_admission_covid_status_is_retained_after_outcome_changes(self):
		patient = self.create_patient()
		patient.covid_status = 'Recovered'
		patient.save()
		patient.refresh_from_db()
		self.assertEqual(patient.admission_covid_status, 'Positive')
		self.assertEqual(patient.covid_status, 'Recovered')

	def test_dashboard_date_filter_changes_case_chart(self):
		today = timezone.localdate()
		self.create_patient(name='In range', admitted_on=today - timedelta(days=1))
		self.create_patient(name='Out of range', admitted_on=today - timedelta(days=3))
		response = self.client.get(reverse('hms:dashboard'), {
			'start': (today - timedelta(days=1)).isoformat(), 'end': today.isoformat(),
		})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['dashboard_chart_data']['newCases'], [1, 0])

	def test_csv_export_has_header_and_database_row(self):
		patient = self.create_patient()
		today = timezone.localdate().isoformat()
		response = self.client.get(reverse('hms:reports'), {
			'start': today, 'end': today, 'report_type': 'patients', 'download': 'csv',
		})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
		self.assertIn('Patient ID,Patient,Age', response.content.decode())
		self.assertIn(patient.uhid, response.content.decode())

	def test_csv_export_escapes_spreadsheet_formulas(self):
		self.create_patient(name='=HYPERLINK("https://attacker.invalid")')
		today = timezone.localdate().isoformat()
		response = self.client.get(reverse('hms:reports'), {
			'start': today, 'end': today, 'report_type': 'patients', 'download': 'csv',
		})
		self.assertIn("'=HYPERLINK", response.content.decode())

	def test_discharge_releases_bed_capacity(self):
		patient = self.create_patient(bed=self.bed)
		response = self.client.post(reverse('hms:patient_discharge', args=[patient.pk]))
		self.assertEqual(response.status_code, 302)
		patient.refresh_from_db()
		self.assertIsNotNone(patient.discharged_at)
		beds_response = self.client.get(reverse('hms:beds'))
		self.assertContains(beds_response, '1 available')

	def test_big_data_status_is_truthful_when_unconfigured_or_unavailable(self):
		with patch.dict('os.environ', {}, clear=True):
			self.assertEqual(hdfs_status()['status'], 'Not configured')
			self.assertEqual(hive_status()['status'], 'Not configured')
		with patch.dict('os.environ', {'HDFS_WEBHDFS_URL': 'http://127.0.0.1:1'}, clear=True):
			self.assertEqual(hdfs_status()['status'], 'Unavailable')
