"""Fictional sample data for the frontend MVP.

Everything here is mock data for UI rendering only.
No real patient information is used anywhere in this project.
"""

STATS = {
    'total_patients': 1284,
    'active_cases': 146,
    'beds_available': 87,
    'icu_occupancy': 78,      # percent
    'discharged': 1042,
    'oxygen_occupancy': 64,   # percent
    'today_admissions': 18,
    'today_discharges': 23,
    'vaccinated_staff': 412,
}

# Daily COVID case trend (last 30 days)
CASE_TREND_LABELS = [
    'Sep 18', 'Sep 19', 'Sep 20', 'Sep 21', 'Sep 22', 'Sep 23', 'Sep 24',
    'Sep 25', 'Sep 26', 'Sep 27', 'Sep 28', 'Sep 29', 'Sep 30', 'Oct 01',
    'Oct 02', 'Oct 03', 'Oct 04', 'Oct 05', 'Oct 06', 'Oct 07', 'Oct 08',
    'Oct 09', 'Oct 10', 'Oct 11', 'Oct 12', 'Oct 13', 'Oct 14', 'Oct 15',
    'Oct 16', 'Oct 17',
]
CASE_TREND_NEW = [
    32, 28, 41, 37, 45, 52, 48, 39, 35, 44, 51, 58, 62, 55, 47,
    42, 38, 49, 56, 61, 54, 46, 40, 37, 43, 50, 47, 39, 34, 31,
]
CASE_TREND_RECOVERED = [
    25, 30, 27, 33, 36, 40, 42, 38, 35, 31, 37, 44, 49, 51, 46,
    43, 40, 36, 42, 48, 52, 50, 45, 41, 38, 44, 49, 46, 42, 40,
]

# Monthly trend (12 months)
MONTHLY_LABELS = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May',
                  'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
MONTHLY_CASES = [820, 960, 1340, 1180, 890, 640, 430, 310, 380, 520, 760, 610]
MONTHLY_RECOVERED = [740, 880, 1150, 1090, 840, 610, 415, 300, 360, 490, 710, 580]
MONTHLY_DEATHS = [18, 24, 31, 22, 15, 9, 6, 4, 5, 8, 12, 9]

# Ward resource utilization (%)
RESOURCE_LABELS = ['General Ward', 'HDU', 'ICU', 'Oxygen Beds', 'Pediatric', 'Isolation']
RESOURCE_UTILIZATION = [72, 66, 78, 64, 38, 58]

# District-wise sample statistics
DISTRICTS = [
    {'name': 'Chennai North', 'cases': 312, 'active': 41, 'recovered': 262, 'deaths': 9, 'rate': 84.0},
    {'name': 'Chennai South', 'cases': 268, 'active': 33, 'recovered': 226, 'deaths': 9, 'rate': 84.3},
    {'name': 'Coimbatore', 'cases': 194, 'active': 21, 'recovered': 166, 'deaths': 7, 'rate': 85.6},
    {'name': 'Madurai', 'cases': 152, 'active': 17, 'recovered': 130, 'deaths': 5, 'rate': 85.5},
    {'name': 'Tiruchirappalli', 'cases': 118, 'active': 12, 'recovered': 102, 'deaths': 4, 'rate': 86.4},
    {'name': 'Salem', 'cases': 96, 'active': 9, 'recovered': 84, 'deaths': 3, 'rate': 87.5},
    {'name': 'Tirunelveli', 'cases': 74, 'active': 7, 'recovered': 64, 'deaths': 3, 'rate': 86.5},
    {'name': 'Vellore', 'cases': 70, 'active': 6, 'recovered': 61, 'deaths': 3, 'rate': 87.1},
]


# Patients — fictional records only
PATIENTS = [
    {'id': 1, 'name': 'Aarav Sharma', 'uhid': 'UH-24091', 'age': 34, 'gender': 'Male',
     'covid_status': 'Positive', 'ward': 'General Ward', 'bed': 'G-14',
     'admitted': '2026-10-12', 'discharged': False, 'doctor': 'Dr. Meera Krishnan',
     'phone': '+91 98400 11001', 'blood_group': 'B+', 'oxygen': False,
     'symptoms': 'Fever, cough, fatigue', 'severity': 'Moderate'},
    {'id': 2, 'name': 'Lakshmi Narayanan', 'uhid': 'UH-24092', 'age': 58, 'gender': 'Female',
     'covid_status': 'Positive', 'ward': 'ICU', 'bed': 'ICU-03',
     'admitted': '2026-10-09', 'discharged': False, 'doctor': 'Dr. Arjun Patel',
     'phone': '+91 98400 11002', 'blood_group': 'O+', 'oxygen': True,
     'symptoms': 'Breathlessness, fever', 'severity': 'Critical'},
    {'id': 3, 'name': 'Karthik Rajan', 'uhid': 'UH-24093', 'age': 41, 'gender': 'Male',
     'covid_status': 'Recovered', 'ward': 'Isolation', 'bed': 'ISO-07',
     'admitted': '2026-09-28', 'discharged': True, 'doctor': 'Dr. Meera Krishnan',
     'phone': '+91 98400 11003', 'blood_group': 'A+', 'oxygen': False,
     'symptoms': 'Mild fever', 'severity': 'Mild'},
    {'id': 4, 'name': 'Priya Venkatesan', 'uhid': 'UH-24094', 'age': 29, 'gender': 'Female',
     'covid_status': 'Negative', 'ward': 'General Ward', 'bed': 'G-22',
     'admitted': '2026-10-15', 'discharged': False, 'doctor': 'Dr. Sana Fathima',
     'phone': '+91 98400 11004', 'blood_group': 'AB+', 'oxygen': False,
     'symptoms': 'Post-surgery observation', 'severity': 'Stable'},
    {'id': 5, 'name': 'Ravi Chandran', 'uhid': 'UH-24095', 'age': 62, 'gender': 'Male',
     'covid_status': 'Positive', 'ward': 'HDU', 'bed': 'HDU-05',
     'admitted': '2026-10-11', 'discharged': False, 'doctor': 'Dr. Arjun Patel',
     'phone': '+91 98400 11005', 'blood_group': 'B-', 'oxygen': True,
     'symptoms': 'Cough, oxygen saturation low', 'severity': 'Severe'},
    {'id': 6, 'name': 'Divya Balakrishnan', 'uhid': 'UH-24096', 'age': 45, 'gender': 'Female',
     'covid_status': 'Recovered', 'ward': 'General Ward', 'bed': '—',
     'admitted': '2026-09-20', 'discharged': True, 'doctor': 'Dr. Sana Fathima',
     'phone': '+91 98400 11006', 'blood_group': 'O-', 'oxygen': False,
     'symptoms': 'Fever, body pain', 'severity': 'Mild'},
    {'id': 7, 'name': 'Mohammed Irfan', 'uhid': 'UH-24097', 'age': 37, 'gender': 'Male',
     'covid_status': 'Positive', 'ward': 'Isolation', 'bed': 'ISO-02',
     'admitted': '2026-10-16', 'discharged': False, 'doctor': 'Dr. Nithya Raman',
     'phone': '+91 98400 11007', 'blood_group': 'A-', 'oxygen': False,
     'symptoms': 'Dry cough, loss of taste', 'severity': 'Moderate'},
    {'id': 8, 'name': 'Ananya Deshpande', 'uhid': 'UH-24098', 'age': 51, 'gender': 'Female',
     'covid_status': 'Positive', 'ward': 'ICU', 'bed': 'ICU-08',
     'admitted': '2026-10-07', 'discharged': False, 'doctor': 'Dr. Arjun Patel',
     'phone': '+91 98400 11008', 'blood_group': 'B+', 'oxygen': True,
     'symptoms': 'Pneumonia, breathlessness', 'severity': 'Critical'},
    {'id': 9, 'name': 'Suresh Kumar', 'uhid': 'UH-24099', 'age': 66, 'gender': 'Male',
     'covid_status': 'Recovered', 'ward': 'HDU', 'bed': '—',
     'admitted': '2026-09-14', 'discharged': True, 'doctor': 'Dr. Nithya Raman',
     'phone': '+91 98400 11009', 'blood_group': 'O+', 'oxygen': False,
     'symptoms': 'Fever, diabetes comorbidity', 'severity': 'Severe'},
    {'id': 10, 'name': 'Kavitha Subramanian', 'uhid': 'UH-24100', 'age': 33, 'gender': 'Female',
     'covid_status': 'Negative', 'ward': 'Pediatric', 'bed': 'P-03',
     'admitted': '2026-10-17', 'discharged': False, 'doctor': 'Dr. Sana Fathima',
     'phone': '+91 98400 11010', 'blood_group': 'AB-', 'oxygen': False,
     'symptoms': 'Routine observation', 'severity': 'Stable'},
    {'id': 11, 'name': 'Vignesh Murugan', 'uhid': 'UH-24101', 'age': 27, 'gender': 'Male',
     'covid_status': 'Positive', 'ward': 'General Ward', 'bed': 'G-09',
     'admitted': '2026-10-14', 'discharged': False, 'doctor': 'Dr. Meera Krishnan',
     'phone': '+91 98400 11011', 'blood_group': 'A+', 'oxygen': False,
     'symptoms': 'Fever, sore throat', 'severity': 'Mild'},
    {'id': 12, 'name': 'Ramya Sundaram', 'uhid': 'UH-24102', 'age': 48, 'gender': 'Female',
     'covid_status': 'Recovered', 'ward': 'Isolation', 'bed': '—',
     'admitted': '2026-09-25', 'discharged': True, 'doctor': 'Dr. Nithya Raman',
     'phone': '+91 98400 11012', 'blood_group': 'B+', 'oxygen': False,
     'symptoms': 'Fever, cough', 'severity': 'Moderate'},
]

# Recent admissions for the dashboard table

# Doctors and staff — fictional
STAFF = [
    {'id': 1, 'name': 'Dr. Arjun Patel', 'role': 'Senior Consultant', 'department': 'Critical Care',
     'available': True, 'phone': '+91 98840 20001', 'email': 'arjun.patel@example.com',
     'shift': 'Morning (08:00 – 14:00)', 'patients': 14, 'experience': '14 yrs'},
    {'id': 2, 'name': 'Dr. Meera Krishnan', 'role': 'Consultant', 'department': 'Pulmonology',
     'available': True, 'phone': '+91 98840 20002', 'email': 'meera.k@example.com',
     'shift': 'Evening (14:00 – 20:00)', 'patients': 11, 'experience': '10 yrs'},
    {'id': 3, 'name': 'Dr. Sana Fathima', 'role': 'Consultant', 'department': 'General Medicine',
     'available': False, 'phone': '+91 98840 20003', 'email': 'sana.f@example.com',
     'shift': 'Night (20:00 – 08:00)', 'patients': 9, 'experience': '8 yrs'},
    {'id': 4, 'name': 'Dr. Nithya Raman', 'role': 'Senior Consultant', 'department': 'Infectious Diseases',
     'available': True, 'phone': '+91 98840 20004', 'email': 'nithya.r@example.com',
     'shift': 'Morning (08:00 – 14:00)', 'patients': 12, 'experience': '16 yrs'},
    {'id': 5, 'name': 'Nurse Felicia Dsouza', 'role': 'Head Nurse', 'department': 'ICU',
     'available': True, 'phone': '+91 98840 20005', 'email': 'felicia.d@example.com',
     'shift': 'Morning (08:00 – 14:00)', 'patients': 0, 'experience': '12 yrs'},
    {'id': 6, 'name': 'Dr. Vikram Sethi', 'role': 'Consultant', 'department': 'Radiology',
     'available': False, 'phone': '+91 98840 20006', 'email': 'vikram.s@example.com',
     'shift': 'Evening (14:00 – 20:00)', 'patients': 0, 'experience': '9 yrs'},
    {'id': 7, 'name': 'Technician Rahul Menon', 'role': 'Lab Technician', 'department': 'Pathology',
     'available': True, 'phone': '+91 98840 20007', 'email': 'rahul.m@example.com',
     'shift': 'Morning (08:00 – 14:00)', 'patients': 0, 'experience': '5 yrs'},
    {'id': 8, 'name': 'Nurse Anjali Verma', 'role': 'ICU Nurse', 'department': 'ICU',
     'available': True, 'phone': '+91 98840 20008', 'email': 'anjali.v@example.com',
     'shift': 'Night (20:00 – 08:00)', 'patients': 0, 'experience': '7 yrs'},
]

# Appointments — fictional
APPOINTMENTS = [
    {'id': 'APT-3011', 'patient': 'Aarav Sharma', 'doctor': 'Dr. Meera Krishnan',
     'date': '2026-10-18', 'time': '09:30', 'type': 'Follow-up', 'status': 'Confirmed',
     'department': 'Pulmonology'},
    {'id': 'APT-3012', 'patient': 'Lakshmi Narayanan', 'doctor': 'Dr. Arjun Patel',
     'date': '2026-10-18', 'time': '10:15', 'type': 'Consultation', 'status': 'Completed',
     'department': 'Critical Care'},
    {'id': 'APT-3013', 'patient': 'Priya Venkatesan', 'doctor': 'Dr. Sana Fathima',
     'date': '2026-10-18', 'time': '11:00', 'type': 'Post-discharge', 'status': 'Scheduled',
     'department': 'General Medicine'},
    {'id': 'APT-3014', 'patient': 'Ravi Chandran', 'doctor': 'Dr. Arjun Patel',
     'date': '2026-10-18', 'time': '11:45', 'type': 'Review', 'status': 'Confirmed',
     'department': 'Critical Care'},
    {'id': 'APT-3015', 'patient': 'Mohammed Irfan', 'doctor': 'Dr. Nithya Raman',
     'date': '2026-10-18', 'time': '12:30', 'type': 'Consultation', 'status': 'Cancelled',
     'department': 'Infectious Diseases'},
    {'id': 'APT-3016', 'patient': 'Vignesh Murugan', 'doctor': 'Dr. Meera Krishnan',
     'date': '2026-10-19', 'time': '09:00', 'type': 'Follow-up', 'status': 'Scheduled',
     'department': 'Pulmonology'},
    {'id': 'APT-3017', 'patient': 'Ananya Deshpande', 'doctor': 'Dr. Arjun Patel',
     'date': '2026-10-19', 'time': '10:30', 'type': 'Review', 'status': 'Confirmed',
     'department': 'Critical Care'},
    {'id': 'APT-3018', 'patient': 'Kavitha Subramanian', 'doctor': 'Dr. Sana Fathima',
     'date': '2026-10-19', 'time': '14:00', 'type': 'Consultation', 'status': 'Scheduled',
     'department': 'General Medicine'},
]

# Bed and ICU inventory
BEDS = [
    {'ward': 'General Ward', 'total': 120, 'occupied': 86, 'available': 34},
    {'ward': 'HDU', 'total': 40, 'occupied': 26, 'available': 14},
    {'ward': 'ICU', 'total': 32, 'occupied': 25, 'available': 7},
    {'ward': 'Oxygen Beds', 'total': 48, 'occupied': 31, 'available': 17},
    {'ward': 'Isolation', 'total': 60, 'occupied': 35, 'available': 25},
    {'ward': 'Pediatric', 'total': 24, 'occupied': 9, 'available': 15},
]

OXYGEN = {'cylinders_total': 180, 'cylinders_in_use': 115, 'plants_online': 3,
          'psa_capacity_lpm': 1200, 'current_demand_lpm': 768}


# Big-data panel — HDFS cluster status (mock)
HDFS = {
    'cluster_name': 'covid-hospital-cluster',
    'live_nodes': 12,
    'dead_nodes': 0,
    'configured_capacity_tb': 240.0,
    'used_capacity_tb': 168.4,
    'hdfs_usage_pct': 70.2,
    'total_blocks': 4821934,
    'missing_blocks': 0,
    'under_replicated': 214,
    'last_checkpoint': '2026-10-18 03:45 IST',
    'datasets': [
        {'name': 'covid_cases_daily', 'size': '42.6 GB', 'rows': '18.4 M', 'format': 'ORC', 'updated': '17 Oct 2026, 23:58'},
        {'name': 'hospital_admissions', 'size': '88.1 GB', 'rows': '41.2 M', 'format': 'Parquet', 'updated': '18 Oct 2026, 02:10'},
        {'name': 'bed_occupancy_stream', 'size': '11.9 GB', 'rows': '96.7 M', 'format': 'Avro', 'updated': '18 Oct 2026, 06:32'},
        {'name': 'vaccination_registry', 'size': '26.8 GB', 'rows': '12.9 M', 'format': 'ORC', 'updated': '17 Oct 2026, 21:05'},
    ],
}

# Hive analysis results (mock)
HIVE_ANALYSIS = [
    {'query': 'District-wise active cases (last 7 days)', 'rows_scanned': '12.9 M',
     'runtime': '18.4 s', 'result': 'Chennai North leads with 41 active cases'},
    {'query': 'Average ICU length of stay by severity', 'rows_scanned': '41.2 M',
     'runtime': '26.1 s', 'result': 'Critical: 9.2 days · Severe: 6.4 days'},
    {'query': 'Recovery rate trend by month', 'rows_scanned': '18.4 M',
     'runtime': '11.7 s', 'result': 'Oct recovery rate at 82.6%'},
    {'query': 'Bed occupancy hotspots (P95 utilization)', 'rows_scanned': '96.7 M',
     'runtime': '31.8 s', 'result': 'ICU crossed 90% occupancy on 6 days'},
]

# Reports page
REPORT_SUMMARY = [
    {'label': 'Reports Generated', 'value': '1,842', 'delta': '+126 this month'},
    {'label': 'Patients Covered', 'value': '1,284', 'delta': '+48 this week'},
    {'label': 'Avg. Length of Stay', 'value': '6.8 days', 'delta': '−0.4 vs last month'},
    {'label': 'Recovery Rate', 'value': '82.6%', 'delta': '+2.1% vs last month'},
]

REPORT_MONTHLY_ROWS = [
    {'month': 'October 2026', 'admissions': 312, 'discharges': 288, 'deaths': 9,
     'occupancy': 71.4, 'recovery': 82.6},
    {'month': 'September 2026', 'admissions': 402, 'discharges': 388, 'deaths': 12,
     'occupancy': 74.8, 'recovery': 81.9},
    {'month': 'August 2026', 'admissions': 288, 'discharges': 271, 'deaths': 8,
     'occupancy': 62.3, 'recovery': 84.1},
    {'month': 'July 2026', 'admissions': 214, 'discharges': 205, 'deaths': 5,
     'occupancy': 48.9, 'recovery': 85.7},
    {'month': 'June 2026', 'admissions': 176, 'discharges': 168, 'deaths': 4,
     'occupancy': 41.2, 'recovery': 86.4},
]

RECENT_ADMISSIONS = PATIENTS[:6]
