import random
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from hms.models import Staff, Ward, Bed, Patient, Appointment
from hms.bigdata import sync_db_to_hdfs, init_hdfs_lake_storage


class Command(BaseCommand):
    help = 'Seed the database with rich, realistic COVID-19 hospital records, bed occupancy, appointments, and HDFS Big Data telemetry'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting full clinical database seeding...'))

        # Clear existing data
        Appointment.objects.all().delete()
        Patient.objects.all().delete()
        Bed.objects.all().delete()
        Ward.objects.all().delete()
        Staff.objects.all().delete()

        today = timezone.localdate()
        rng = random.Random(1337)

        # 1. Create Wards and Beds
        ward_specs = [
            ('ICU', 32, 24),           # 32 beds, 24 occupied (~75%)
            ('HDU', 40, 28),           # 40 beds, 28 occupied (~70%)
            ('Oxygen Beds', 48, 36),   # 48 beds, 36 occupied (~75%)
            ('Isolation', 60, 36),     # 60 beds, 36 occupied (~60%)
            ('General Ward', 120, 78), # 120 beds, 78 occupied (~65%)
            ('Pediatric', 24, 14),     # 24 beds, 14 occupied (~58%)
        ]

        ward_map = {}
        all_beds_by_ward = {}

        for w_name, capacity, target_occ in ward_specs:
            ward = Ward.objects.create(name=w_name, capacity=capacity)
            ward_map[w_name] = ward
            beds_list = []
            prefix = w_name[:2].upper() if w_name != 'General Ward' else 'G'
            for i in range(1, capacity + 1):
                bed_num = f"{prefix}-{i:02d}"
                bed = Bed.objects.create(ward=ward, number=bed_num, out_of_service=(i > capacity - 2 and w_name in ['General Ward', 'Isolation']))
                beds_list.append(bed)
            all_beds_by_ward[w_name] = beds_list

        total_beds = Bed.objects.count()
        self.stdout.write(f'Created {len(ward_map)} hospital wards with {total_beds} total beds.')

        # 2. Create Doctors and Medical Staff (18 members)
        staff_data = [
            {'name': 'Dr. Arjun Patel', 'role': 'Senior Consultant & HOD', 'department': 'Critical Care',
             'phone': '+91 98840 20001', 'email': 'arjun.patel@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '16 yrs', 'available': True},
            {'name': 'Dr. Meera Krishnan', 'role': 'Senior Pulmonologist', 'department': 'Pulmonology',
             'phone': '+91 98840 20002', 'email': 'meera.k@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '14 yrs', 'available': True},
            {'name': 'Dr. Nithya Raman', 'role': 'Senior Epidemiologist & Virologist', 'department': 'Infectious Diseases',
             'phone': '+91 98840 20004', 'email': 'nithya.r@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '18 yrs', 'available': True},
            {'name': 'Dr. Sana Fathima', 'role': 'Consultant Physician', 'department': 'General Medicine',
             'phone': '+91 98840 20003', 'email': 'sana.f@meridiancare.in', 'shift': 'Evening (14:00 – 20:00)', 'experience': '9 yrs', 'available': True},
            {'name': 'Dr. Vikram Sethi', 'role': 'Chief of Thoracic Radiology', 'department': 'Radiology',
             'phone': '+91 98840 20006', 'email': 'vikram.s@meridiancare.in', 'shift': 'Evening (14:00 – 20:00)', 'experience': '12 yrs', 'available': True},
            {'name': 'Dr. Rajesh Sundaram', 'role': 'Intensivist Specialist', 'department': 'Critical Care',
             'phone': '+91 98840 20009', 'email': 'rajesh.s@meridiancare.in', 'shift': 'Night (20:00 – 08:00)', 'experience': '11 yrs', 'available': True},
            {'name': 'Dr. Ananya Roy', 'role': 'Pediatric Pulmonologist', 'department': 'Pediatrics',
             'phone': '+91 98840 20010', 'email': 'ananya.roy@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '10 yrs', 'available': True},
            {'name': 'Dr. Karthik Narayanan', 'role': 'Consultant Pulmonologist', 'department': 'Pulmonology',
             'phone': '+91 98840 20011', 'email': 'karthik.n@meridiancare.in', 'shift': 'Night (20:00 – 08:00)', 'experience': '8 yrs', 'available': True},
            {'name': 'Nurse Felicia Dsouza', 'role': 'ICU Nursing Superintendent', 'department': 'Critical Care',
             'phone': '+91 98840 20005', 'email': 'felicia.d@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '15 yrs', 'available': True},
            {'name': 'Nurse Anjali Verma', 'role': 'Senior ICU Staff Nurse', 'department': 'Critical Care',
             'phone': '+91 98840 20008', 'email': 'anjali.v@meridiancare.in', 'shift': 'Night (20:00 – 08:00)', 'experience': '7 yrs', 'available': True},
            {'name': 'Nurse Saravanan K.', 'role': 'Oxygen Therapy Coordinator', 'department': 'Pulmonology',
             'phone': '+91 98840 20012', 'email': 'saravanan.k@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '9 yrs', 'available': True},
            {'name': 'Nurse Deepa Lakshmi', 'role': 'Infection Control Officer', 'department': 'Infectious Diseases',
             'phone': '+91 98840 20013', 'email': 'deepa.l@meridiancare.in', 'shift': 'Evening (14:00 – 20:00)', 'experience': '11 yrs', 'available': True},
            {'name': 'Nurse Jennifer Thomas', 'role': 'Pediatric Triage Nurse', 'department': 'Pediatrics',
             'phone': '+91 98840 20014', 'email': 'jennifer.t@meridiancare.in', 'shift': 'Evening (14:00 – 20:00)', 'experience': '6 yrs', 'available': True},
            {'name': 'Technician Rahul Menon', 'role': 'Senior Molecular Biologist', 'department': 'Pathology',
             'phone': '+91 98840 20007', 'email': 'rahul.m@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '6 yrs', 'available': True},
            {'name': 'Technician Sneha Nair', 'role': 'Blood Gas & RT-PCR Analyst', 'department': 'Pathology',
             'phone': '+91 98840 20015', 'email': 'sneha.n@meridiancare.in', 'shift': 'Evening (14:00 – 20:00)', 'experience': '5 yrs', 'available': True},
            {'name': 'Dr. Harish Chandra', 'role': 'Emergency Physician', 'department': 'General Medicine',
             'phone': '+91 98840 20016', 'email': 'harish.c@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '13 yrs', 'available': True},
            {'name': 'Dr. Lavanya Balaji', 'role': 'Consultant Microbiologist', 'department': 'Pathology',
             'phone': '+91 98840 20017', 'email': 'lavanya.b@meridiancare.in', 'shift': 'Morning (08:00 – 14:00)', 'experience': '10 yrs', 'available': False},
            {'name': 'Nurse Manoj Prabhakar', 'role': 'Triage Nurse', 'department': 'General Medicine',
             'phone': '+91 98840 20018', 'email': 'manoj.p@meridiancare.in', 'shift': 'Night (20:00 – 08:00)', 'experience': '8 yrs', 'available': True},
        ]

        staff_objs = []
        doctors_list = []
        for s in staff_data:
            member = Staff.objects.create(**s)
            staff_objs.append(member)
            if member.name.startswith('Dr.'):
                doctors_list.append(member)

        self.stdout.write(f'Created {len(staff_objs)} staff and clinicians.')

        # 3. Patient Demographics & Profile Definitions
        first_names_m = [
            'Aarav', 'Karthik', 'Ravi', 'Mohammed', 'Vignesh', 'Suresh', 'Deepak', 'Ganesh',
            'Manoj', 'Arun', 'Prakash', 'Ramesh', 'Harish', 'Vijay', 'Balaji', 'Sanjay',
            'Siddharth', 'Naveen', 'Ashwin', 'Madhavan', 'Subramaniam', 'Dinesh', 'Venkatesh',
            'Raghav', 'Pradeep', 'Saravanan', 'Gautam', 'Kishore', 'Bhuvanesh', 'Murugan'
        ]
        first_names_f = [
            'Lakshmi', 'Priya', 'Divya', 'Ananya', 'Kavitha', 'Ramya', 'Meenakshi', 'Shanthi',
            'Gayathri', 'Nandhini', 'Sowmya', 'Aishwarya', 'Pavithra', 'Deepika', 'Kirthika',
            'Radha', 'Kalyani', 'Bhavani', 'Revathi', 'Geetha', 'Subhashini', 'Vasanthi',
            'Sudha', 'Keerthana', 'Saranya', 'Malathi', 'Janani', 'Swetha', 'Pooja', 'Abirami'
        ]
        last_names = [
            'Sharma', 'Narayanan', 'Rajan', 'Venkatesan', 'Chandran', 'Balakrishnan', 'Irfan',
            'Deshpande', 'Kumar', 'Subramanian', 'Murugan', 'Sundaram', 'Krishnamoorthy',
            'Natarajan', 'Srinivasan', 'Raghavan', 'Pillai', 'Menon', 'Iyer', 'Chettiar',
            'Reddy', 'Gounder', 'Naidu', 'Choudhury', 'Patel', 'Sen', 'Mukherjee', 'Varma'
        ]
        districts = [
            'Chennai North', 'Chennai South', 'Coimbatore', 'Madurai',
            'Tiruchirappalli', 'Salem', 'Tirunelveli', 'Vellore',
            'Thanjavur', 'Erode', 'Tiruppur', 'Kanchipuram'
        ]
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

        symptom_pool = [
            'High fever (103°F), bilateral ground-glass opacities, severe dyspnea, SpO2 82%',
            'Persistent dry cough, loss of smell (anosmia), extreme fatigue, SpO2 94%',
            'Shortness of breath on exertion, chest heaviness, intermittent fever, SpO2 89%',
            'Severe respiratory distress, ARDS, bilateral pneumonia, SpO2 78%, requires BiPAP',
            'Mild fever, sore throat, mild nasal congestion, normal lung vitals, SpO2 98%',
            'Fever, loss of taste, headache, body ache, stable room air SpO2 96%',
            'Bronchospasm, continuous cough, diabetic comorbidity, oxygen saturation 87%',
            'Asymptomatic post-exposure screening with positive RT-PCR confirmation',
            'Post-operative fever with respiratory consolidation, SpO2 91%',
            'Pediatric acute wheezing, chest indrawing, fever, SpO2 92%',
        ]

        patients_created = []

        # ======================================================================
        # Group A: Active Inpatients Currently in Wards (60 patients)
        # ======================================================================
        # Distribute active inpatients across wards to match realistic occupancy
        active_patient_assignments = [
            ('ICU', 22, 'Critical', True),
            ('HDU', 20, 'Severe', True),
            ('Oxygen Beds', 24, 'Moderate', True),
            ('Isolation', 18, 'Moderate', False),
            ('General Ward', 22, 'Mild', False),
            ('Pediatric', 8, 'Mild', False),
        ]

        patient_idx = 0
        used_beds_per_ward = {w: 0 for w in ward_map}

        for ward_name, count, target_severity, req_oxygen in active_patient_assignments:
            ward = ward_map[ward_name]
            beds = all_beds_by_ward[ward_name]

            for _ in range(count):
                patient_idx += 1
                is_male = rng.random() > 0.48
                f_name = rng.choice(first_names_m if is_male else first_names_f)
                l_name = rng.choice(last_names)
                name = f"{f_name} {l_name}"

                if ward_name == 'Pediatric':
                    age = rng.randint(2, 16)
                elif target_severity in ['Critical', 'Severe']:
                    age = rng.randint(45, 82)
                else:
                    age = rng.randint(19, 74)

                district = rng.choice(districts)
                blood_group = rng.choice(blood_groups)
                doc = rng.choice(doctors_list)

                # Bed assignment
                bed_idx = used_beds_per_ward[ward_name]
                bed = beds[bed_idx] if bed_idx < len(beds) else None
                used_beds_per_ward[ward_name] += 1

                # Admission between 1 and 24 days ago
                adm_days_ago = rng.randint(1, 24)
                admitted_on = today - timedelta(days=adm_days_ago)

                # Symptoms
                symptoms = rng.choice(symptom_pool)
                phone = f"+91 {rng.randint(70000, 99999)} {rng.randint(10000, 99999)}"

                patient = Patient.objects.create(
                    name=name,
                    age=age,
                    gender='Male' if is_male else 'Female',
                    district=district,
                    blood_group=blood_group,
                    phone=phone,
                    covid_status='Positive',
                    severity=target_severity,
                    admission_covid_status='Positive',
                    symptoms=symptoms,
                    oxygen=req_oxygen,
                    ward=ward,
                    bed=bed,
                    doctor=doc,
                    admitted_on=admitted_on,
                    discharged_at=None,
                )
                patients_created.append(patient)

        # ======================================================================
        # Group B: Historical Recovered & Discharged Patients (70 patients)
        # ======================================================================
        # Spread across the past 360 days so 12-month charts have rich data
        for i in range(70):
            patient_idx += 1
            is_male = rng.random() > 0.5
            f_name = rng.choice(first_names_m if is_male else first_names_f)
            l_name = rng.choice(last_names)
            name = f"{f_name} {l_name}"
            age = rng.randint(18, 79)
            district = rng.choice(districts)
            blood_group = rng.choice(blood_groups)
            doc = rng.choice(doctors_list)
            ward = rng.choice(list(ward_map.values()))

            # Admission date spread across 15 to 350 days ago
            days_ago = rng.randint(14, 350)
            admitted_on = today - timedelta(days=days_ago)
            stay_days = rng.randint(5, 18)
            discharge_date = admitted_on + timedelta(days=stay_days)
            if discharge_date > today:
                discharge_date = today - timedelta(days=1)

            discharged_at = timezone.make_aware(
                datetime.combine(discharge_date, datetime.strptime(f"{rng.randint(9, 18):02d}:{rng.randint(0, 59):02d}", "%H:%M").time())
            )

            severity = rng.choice(['Mild', 'Moderate', 'Severe', 'Stable'])
            symptoms = 'Recovered after treatment course: ' + rng.choice(symptom_pool)
            phone = f"+91 {rng.randint(70000, 99999)} {rng.randint(10000, 99999)}"

            patient = Patient.objects.create(
                name=name,
                age=age,
                gender='Male' if is_male else 'Female',
                district=district,
                blood_group=blood_group,
                phone=phone,
                covid_status='Recovered',
                severity='Stable',
                admission_covid_status='Positive',  # CRITICAL: Was admitted Positive!
                symptoms=symptoms,
                oxygen=False,
                ward=ward,
                bed=None,  # Released bed
                doctor=doc,
                admitted_on=admitted_on,
                discharged_at=discharged_at,
            )
            patients_created.append(patient)

        # ======================================================================
        # Group C: Negative / Observation Patients (15 patients)
        # ======================================================================
        for i in range(15):
            patient_idx += 1
            is_male = rng.random() > 0.5
            f_name = rng.choice(first_names_m if is_male else first_names_f)
            l_name = rng.choice(last_names)
            name = f"{f_name} {l_name}"
            age = rng.randint(21, 68)
            district = rng.choice(districts)
            blood_group = rng.choice(blood_groups)
            doc = rng.choice(doctors_list)

            # Assign some to General Ward beds
            gw_beds = all_beds_by_ward['General Ward']
            gw_used = used_beds_per_ward['General Ward']
            gw_bed = gw_beds[gw_used] if gw_used < len(gw_beds) else None
            used_beds_per_ward['General Ward'] += 1

            admitted_on = today - timedelta(days=rng.randint(1, 10))
            patient = Patient.objects.create(
                name=name,
                age=age,
                gender='Male' if is_male else 'Female',
                district=district,
                blood_group=blood_group,
                phone=f"+91 {rng.randint(70000, 99999)} {rng.randint(10000, 99999)}",
                covid_status='Negative',
                severity='Stable',
                admission_covid_status='Negative',
                symptoms='Post-surgical observation, RT-PCR negative on admission.',
                oxygen=False,
                ward=ward_map['General Ward'],
                bed=gw_bed,
                doctor=doc,
                admitted_on=admitted_on,
                discharged_at=None,
            )
            patients_created.append(patient)

        self.stdout.write(f'Created {len(patients_created)} realistic patient clinical records.')

        # 4. Create Appointments (48 appointments)
        appointment_types = ['Consultation', 'Follow-up', 'Review', 'Post-discharge']
        appointment_statuses = ['Confirmed', 'Scheduled', 'Completed', 'Cancelled']
        time_slots = ['09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '14:00', '14:30', '15:00', '15:30', '16:00']

        booked_slots = set()
        appts_count = 0

        # Create past completed appointments (last 7 days) and upcoming appointments (next 7 days)
        for offset in range(-7, 8):
            appt_date = today + timedelta(days=offset)
            # 3 to 4 appointments per day
            for _ in range(rng.randint(3, 5)):
                doc = rng.choice(doctors_list)
                slot = rng.choice(time_slots)
                slot_key = (doc.pk, appt_date.isoformat(), slot)
                if slot_key in booked_slots:
                    continue
                booked_slots.add(slot_key)

                patient = rng.choice(patients_created)
                starts_at = timezone.make_aware(
                    datetime.combine(appt_date, datetime.strptime(slot, "%H:%M").time())
                )

                if offset < 0:
                    status = 'Completed' if rng.random() > 0.15 else 'Cancelled'
                elif offset == 0:
                    status = 'Confirmed' if rng.random() > 0.3 else 'Scheduled'
                else:
                    status = 'Scheduled' if rng.random() > 0.4 else 'Confirmed'

                Appointment.objects.create(
                    patient=patient,
                    doctor=doc,
                    starts_at=starts_at,
                    appointment_type=rng.choice(appointment_types),
                    status=status,
                )
                appts_count += 1

        self.stdout.write(f'Created {appts_count} doctor appointments.')

        # 5. Automatically Ingest Data into HDFS Data Lake (Sqoop-style Pipeline)
        self.stdout.write('Synchronizing clinical records into HDFS Data Lake & Hive Metastore...')
        init_hdfs_lake_storage()
        sync_result = sync_db_to_hdfs()

        self.stdout.write(self.style.SUCCESS('Database and HDFS Data Lake Seeding Completed!'))
        self.stdout.write(f"  • Total Wards: {Ward.objects.count()}")
        self.stdout.write(f"  • Total Beds: {Bed.objects.count()} (Occupied: {used_beds_per_ward['General Ward'] + used_beds_per_ward['ICU'] + used_beds_per_ward['HDU'] + used_beds_per_ward['Oxygen Beds'] + used_beds_per_ward['Isolation'] + used_beds_per_ward['Pediatric']})")
        self.stdout.write(f"  • Total Staff: {Staff.objects.count()}")
        self.stdout.write(f"  • Total Patients: {Patient.objects.count()} (Active: {Patient.objects.filter(discharged_at__isnull=True).count()}, Recovered: {Patient.objects.filter(covid_status='Recovered').count()})")
        self.stdout.write(f"  • Total Appointments: {Appointment.objects.count()}")
        self.stdout.write(f"  • HDFS Vitals Telemetry: {sync_result['telemetry_readings']} records")
        self.stdout.write(f"  • HDFS Bed Snapshots: {sync_result['bed_snapshots']} records")
        self.stdout.write(f"  • HDFS District Census: {sync_result['district_records']} records")
