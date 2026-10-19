import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


def new_patient_id():
	return f'MC-{uuid.uuid4().hex[:8].upper()}'


class Staff(models.Model):
	name = models.CharField(max_length=120)
	role = models.CharField(max_length=100)
	department = models.CharField(max_length=80)
	phone = models.CharField(max_length=30, blank=True)
	email = models.EmailField(blank=True)
	shift = models.CharField(max_length=80, blank=True)
	experience = models.CharField(max_length=40, blank=True)
	available = models.BooleanField(default=True)
	is_active = models.BooleanField(default=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Ward(models.Model):
	name = models.CharField(max_length=80, unique=True)
	capacity = models.PositiveSmallIntegerField(default=0)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name


class Bed(models.Model):
	ward = models.ForeignKey(Ward, on_delete=models.PROTECT, related_name='beds')
	number = models.CharField(max_length=20)
	out_of_service = models.BooleanField(default=False)

	class Meta:
		ordering = ['ward__name', 'number']
		constraints = [
			models.UniqueConstraint(fields=['ward', 'number'], name='unique_bed_per_ward'),
		]

	def __str__(self):
		return f'{self.ward.name} · {self.number}'


class Patient(models.Model):
	GENDER = [('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')]
	BLOOD_GROUP = [(value, value) for value in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-')]
	COVID_STATUS = [
		('Positive', 'Positive'),
		('Negative', 'Negative'),
		('Recovered', 'Recovered'),
	]
	SEVERITY = [
		('Stable', 'Stable'),
		('Mild', 'Mild'),
		('Moderate', 'Moderate'),
		('Severe', 'Severe'),
		('Critical', 'Critical'),
	]

	uhid = models.CharField(max_length=16, unique=True, default=new_patient_id, editable=False)
	name = models.CharField(max_length=120)
	age = models.PositiveSmallIntegerField()
	gender = models.CharField(max_length=20, choices=GENDER)
	district = models.CharField(max_length=80, blank=True)
	blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP, blank=True)
	phone = models.CharField(max_length=30, blank=True)
	covid_status = models.CharField(max_length=12, choices=COVID_STATUS)
	severity = models.CharField(max_length=12, choices=SEVERITY)
	admission_covid_status = models.CharField(max_length=12, choices=COVID_STATUS, null=True, blank=True)
	symptoms = models.TextField(blank=True)
	oxygen = models.BooleanField(default=False)
	ward = models.ForeignKey(Ward, on_delete=models.PROTECT, related_name='patients', null=True, blank=True)
	bed = models.ForeignKey(Bed, on_delete=models.PROTECT, related_name='patients', null=True, blank=True)
	doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, related_name='patients', null=True, blank=True)
	admitted_on = models.DateField(default=timezone.localdate, db_index=True)
	discharged_at = models.DateTimeField(null=True, blank=True, db_index=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-admitted_on', 'name']
		constraints = [
			models.UniqueConstraint(
				fields=['bed'],
				condition=Q(bed__isnull=False, discharged_at__isnull=True),
				name='unique_active_bed_assignment',
			),
		]

	def clean(self):
		if self.age > 120:
			raise ValidationError({'age': 'Age must be 120 or younger.'})
		if self.admitted_on and self.admitted_on > timezone.localdate():
			raise ValidationError({'admitted_on': 'Admission date cannot be in the future.'})
		if self.bed_id and self.ward_id and self.bed.ward_id != self.ward_id:
			raise ValidationError({'bed': 'The selected bed must belong to the selected ward.'})
		if self.discharged_at and self.discharged_at.date() < self.admitted_on:
			raise ValidationError({'discharged_at': 'Discharge cannot be before admission.'})

	def save(self, *args, **kwargs):
		if self._state.adding and not self.admission_covid_status:
			self.admission_covid_status = self.covid_status
		super().save(*args, **kwargs)

	@property
	def discharged(self):
		return self.discharged_at is not None

	@property
	def admitted(self):
		return self.admitted_on.isoformat()

	@property
	def bed_label(self):
		return self.bed.number if self.bed_id else '—'

	def __str__(self):
		return f'{self.name} ({self.uhid})'


class Appointment(models.Model):
	TYPES = [
		('Consultation', 'Consultation'),
		('Follow-up', 'Follow-up'),
		('Review', 'Review'),
		('Post-discharge', 'Post-discharge'),
	]
	STATUSES = [
		('Scheduled', 'Scheduled'),
		('Confirmed', 'Confirmed'),
		('Completed', 'Completed'),
		('Cancelled', 'Cancelled'),
	]

	patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='appointments')
	doctor = models.ForeignKey(Staff, on_delete=models.PROTECT, related_name='appointments')
	starts_at = models.DateTimeField(db_index=True)
	appointment_type = models.CharField(max_length=24, choices=TYPES, default='Consultation')
	status = models.CharField(max_length=12, choices=STATUSES, default='Scheduled')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['starts_at']
		constraints = [
			models.UniqueConstraint(
				fields=['doctor', 'starts_at'],
				condition=~Q(status='Cancelled'),
				name='unique_active_doctor_slot',
			),
		]

	def clean(self):
		if self.starts_at and timezone.is_naive(self.starts_at):
			self.starts_at = timezone.make_aware(self.starts_at)
		if self.starts_at and self.starts_at < timezone.now() and self.status == 'Scheduled':
			raise ValidationError({'starts_at': 'A new appointment must be in the future.'})
		if self.doctor_id and self.starts_at:
			conflicts = Appointment.objects.filter(doctor=self.doctor, starts_at=self.starts_at).exclude(pk=self.pk).exclude(status='Cancelled')
			if conflicts.exists():
				raise ValidationError({'starts_at': 'This doctor already has an appointment at that time.'})

	@property
	def date(self):
		return timezone.localtime(self.starts_at).date().isoformat()

	@property
	def time(self):
		return timezone.localtime(self.starts_at).strftime('%H:%M')

	@property
	def department(self):
		return self.doctor.department

	@property
	def id_label(self):
		return f'APT-{self.pk:04d}'

	def __str__(self):
		return f'{self.patient.name} · {self.date} {self.time}'
