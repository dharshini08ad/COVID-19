import re

with open('hms/bigdata.py', 'r') as f:
    content = f.read()

# Extract the current function
idx = content.find('def export_to_hdfs_format')
if idx < 0:
    print('Function not found')
    exit(1)

# Find the end of the function (next top-level def)
next_def = content.find('\ndef ', idx + 10)
if next_def < 0:
    next_def = len(content)

# Get the current function
old_func = content[idx:next_def]
print('Old function length:', len(old_func))
print('Old function starts:', repr(old_func[:100]))

# Create new function
new_func = '''def export_to_hdfs_format(data_type='patients'):
    """Export local database into standard HDFS-compatible CSV or JSON format.

    Runs against local SQLite database and writes CSV files to the local temp
    directory. Simulates HDF5-compatible storage format. Verifies files exist
    before returning.
    """
    from hms.models import Patient, Bed, Ward, Staff
    init_hdfs_lake_storage()

    temp_dir = tempfile.gettempdir()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if data_type == 'patients':
        filename = os.path.join(temp_dir, f'covid_patients_lake_{timestamp}.csv')
        patients = Patient.objects.select_related('ward', 'bed', 'doctor').all()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['uhid', 'name', 'age', 'gender', 'district', 'blood_group',
                           'phone', 'covid_status', 'severity', 'admission_covid_status',
                           'symptoms', 'oxygen', 'ward', 'bed', 'doctor', 'admitted_on', 'discharged_at'])
            for p in patients:
                writer.writerow([
                    p.uhid, p.name, p.age, p.gender, p.district, p.blood_group,
                    p.phone, p.covid_status, p.severity, p.admission_covid_status or p.covid_status,
                    p.symptoms, 'true' if p.oxygen else 'false',
                    p.ward.name if p.ward else '',
                    p.bed.number if p.bed else '',
                    p.doctor.name if p.doctor else '',
                    p.admitted_on.isoformat() if p.admitted_on else '',
                    p.discharged_at.isoformat() if p.discharged_at else '',
                ])
        # Verify file was created
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return filename, patients.count()
        else:
            return None, 0

    elif data_type == 'admissions':
        filename = os.path.join(temp_dir, f'hospital_admissions_stream_{timestamp}.csv')
        admissions = Patient.objects.filter(models_q_positive()).select_related('ward', 'bed', 'doctor')
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['uhid', 'name', 'age', 'gender', 'district', 'covid_status', 'severity', 'ward', 'bed', 'doctor', 'admitted_on', 'discharged_at'])
            for p in admissions:
                writer.writerow([
                    p.uhid, p.name, p.age, p.gender, p.district, p.covid_status, p.severity,
                    p.ward.name if p.ward else '',
                    p.bed.number if p.bed else '',
                    p.doctor.name if p.doctor else '',
                    p.admitted_on.isoformat() if p.admitted_on else '',
                    p.discharged_at.isoformat() if p.discharged_at else '',
                ])
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return filename, admissions.count()
        else:
            return None, 0

    elif data_type == 'bed_occupancy':
        filename = os.path.join(temp_dir, f'bed_occupancy_timeseries_{timestamp}.csv')
        beds = Bed.objects.select_related('ward').all()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ward', 'bed_number', 'occupied', 'patient_uhid', 'patient_name', 'admitted_on', 'out_of_service'])
            for bed in beds:
                patient = bed.patients.filter(discharged_at__isnull=True).first()
                writer.writerow([
                    bed.ward.name, bed.number,
                    'Yes' if patient else 'No',
                    patient.uhid if patient else '',
                    patient.name if patient else '',
                    patient.admitted_on.isoformat() if patient else '',
                    'Yes' if bed.out_of_service else 'No',
                ])
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return filename, beds.count()
        else:
            return None, 0

    elif data_type == 'icu_telemetry':
        filename = os.path.join(temp_dir, f'icu_vitals_telemetry_{timestamp}.csv')
        lake_root = get_lake_root()
        src_file = lake_root / 'user' / 'hadoop' / 'covid19' / 'icu_telemetry' / 'icu_bedside_telemetry_stream.csv'
        if src_file.exists():
            shutil.copyfile(src_file, filename)
            with open(filename, 'r', encoding='utf-8') as f:
                lines = sum(1 for _ in f) - 1
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                return filename, lines
            else:
                return None, 0
        else:
            sync_db_to_hdfs()
            return export_to_hdfs_format('icu_telemetry')

    return None, 0'''

# Replace
new_content = content[:idx] + new_func + content[next_def:]

with open('hms/bigdata.py', 'w') as f:
    f.write(new_content)

print('Replacement complete')

# Verify
with open('hms/bigdata.py', 'r') as f:
    verify = f.read()
idx2 = verify.find('def export_to_hdfs_format')
if idx2 >= 0:
    print('Verification - new function starts:', repr(verify[idx2:idx2+100]))
