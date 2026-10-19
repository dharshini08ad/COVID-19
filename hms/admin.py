from django.contrib import admin

from .models import Appointment, Bed, Patient, Staff, Ward


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
	list_display = ('uhid', 'name', 'covid_status', 'severity', 'ward', 'admitted_on', 'discharged_at')
	list_filter = ('covid_status', 'severity', 'ward', 'discharged_at')
	search_fields = ('uhid', 'name', 'phone')


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
	list_display = ('name', 'role', 'department', 'available', 'is_active')
	list_filter = ('department', 'available', 'is_active')
	search_fields = ('name', 'email', 'phone')


@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
	list_display = ('name', 'capacity')


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
	list_display = ('ward', 'number', 'out_of_service')
	list_filter = ('ward', 'out_of_service')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
	list_display = ('patient', 'doctor', 'starts_at', 'appointment_type', 'status')
	list_filter = ('status', 'appointment_type', 'starts_at')
	search_fields = ('patient__name', 'patient__uhid', 'doctor__name')
