# Big Data Implementation for COVID-19 Hospital Management System

## Overview
This document describes the implementation of big data features (HDFS and Hive simulation) for the COVID-19 Hospital Management System using Django and SQLite.

## What Was Implemented

### 1. Database Seeding (`hms/management/commands/seed_data.py`)
Created a Django management command to populate the database with sample data:
- **6 Wards**: General Ward (120 beds), HDU (40 beds), ICU (32 beds), Oxygen Beds (48 beds), Isolation (60 beds), Pediatric (24 beds)
- **324 Beds** across all wards
- **8 Staff members** including doctors, nurses, and technicians
- **12 Patients** with varying COVID-19 statuses (Positive, Negative, Recovered)
- **8 Appointments** with different statuses

**Usage:**
```bash
python manage.py seed_data
```

### 2. HDFS Export Simulation (`hms/bigdata.py`)
Added `export_to_hdfs_format()` function to export local data to CSV format ready for HDFS upload:
- **Patients Export**: Full patient records with all fields
- **Admissions Export**: COVID-19 positive admissions only
- **Bed Occupancy Export**: Real-time bed occupancy status

**Web Interface:**
- Access via Analytics page (`/analytics/`)
- Select data type from dropdown
- Click "Export to HDFS Format" to download CSV

**Usage Example:**
```python
from hms.bigdata import export_to_hdfs_format
filename, record_count = export_to_hdfs_format('patients')
# Returns: CSV file path and number of records exported
```

### 3. Hive Query Simulation (`hms/bigdata.py`)
Added `simulate_hive_query()` function to run analytics on local SQLite data similar to Hive queries:

**Available Query Types:**
1. **District-wise Cases**: Active cases by district (last 7 days)
   - Shows total cases, active cases, recovered, and recovery rate per district

2. **ICU Length of Stay**: Average ICU stay by severity
   - Groups patients by severity level (Critical, Severe, Moderate, Mild)
   - Calculates average length of stay in days

3. **Recovery Rate Trend**: Monthly recovery rate over last 6 months
   - Shows discharge counts and recovery percentages by month

4. **Bed Occupancy Hotspots**: Ward utilization analysis
   - Lists all wards with total beds, occupied beds, and utilization percentage
   - Sorted by highest utilization first

**Web Interface:**
- Access via Analytics page (`/analytics/`)
- Select query type from dropdown
- Click "Run Hive Query Simulation" to see results
- Results displayed in a table format

**Usage Example:**
```python
from hms.bigdata import simulate_hive_query
result = simulate_hive_query('district_wise')
# Returns: execution time, rows scanned, and query results
```

### 4. URL Routes (`hms/urls.py`)
Added two new routes:
- `/analytics/export/` - For HDFS export functionality
- `/analytics/query/` - For Hive query simulation

### 5. Views (`hms/views.py`)
Added two new view functions:
- `bigdata_export()` - Handles CSV export requests
- `bigdata_query()` - Handles Hive query simulation requests

### 6. Template Updates (`templates/hms/analytics.html`)
Enhanced the Analytics page with:
- HDFS export form with data type selection
- Hive query simulation form with query type selection
- Results display table for Hive query outputs
- Instructions and descriptions for each feature

## How to Use

### Step 1: Seed the Database
```bash
cd "C:\Users\DHARSHINI C\OneDrive\Desktop\COVID-19"
python manage.py seed_data
```

### Step 2: Run the Development Server
```bash
python manage.py runserver 127.0.0.1:8765
```

### Step 3: Access the Application
Open browser to: `http://127.0.0.1:8765`

### Step 4: Use Big Data Features
1. Navigate to the **Analytics** page
2. Scroll to the "Big-data connectivity" section
3. Use the "Local Data Export & Hive Simulation" panel

**To Export Data for HDFS:**
1. Select data type (Patients, Admissions, or Bed Occupancy)
2. Click "Export to HDFS Format"
3. CSV file will be downloaded ready for HDFS upload

**To Run Hive Query Simulation:**
1. Select query type (District-wise Cases, ICU Length of Stay, etc.)
2. Click "Run Hive Query Simulation"
3. Results will be displayed in a table below

## Architecture Notes

### Current Big Data Status
- **HDFS**: Not configured (requires actual Hadoop cluster)
- **Hive**: Not configured (requires actual Hive service and Beeline)
- **Local Simulation**: Fully functional using SQLite

### Production Implementation Path
To connect to actual Hadoop/HDFS and Hive:

1. **Set Environment Variables:**
```powershell
$env:HDFS_WEBHDFS_URL = 'http://namenode-host:9870'
$env:HDFS_DATASET_PATHS = 'covid_cases=/datasets/covid_cases,admissions=/datasets/admissions'
$env:HIVE_JDBC_URL = 'jdbc:hive2://hive-host:10000/default'
$env:BEELINE_PATH = 'C:\path\to\beeline.cmd'
```

2. **Modify Export Function:**
   - Add HDFS upload logic using WebHDFS API
   - Upload CSV files to configured HDFS paths

3. **Modify Query Function:**
   - Replace local queries with actual Hive queries via Beeline
   - Use subprocess to execute Hive queries and parse results

### Data Flow
```
Django/SQLite (Local)
    ↓
Export to CSV → Ready for HDFS upload
    ↓
Hive Query Simulation → Runs on local SQLite
    ↓
Results Display → Web interface
```

## File Changes Summary

### New Files Created:
- `hms/management/__init__.py`
- `hms/management/commands/__init__.py`
- `hms/management/commands/seed_data.py` - Database seeding command
- `BIGDATA_IMPLEMENTATION.md` - This documentation

### Modified Files:
- `hms/bigdata.py` - Added export and query simulation functions
- `hms/views.py` - Added bigdata_export and bigdata_query views
- `hms/urls.py` - Added export and query routes
- `templates/hms/analytics.html` - Added export/query UI

## Testing Performed

1. ✅ Database seeding completed successfully
2. ✅ Server started without errors
3. ✅ Dashboard displays seeded data (12 patients, 324 beds, etc.)
4. ✅ Analytics page loads correctly
5. ✅ HDFS export generates valid CSV files
6. ✅ Web interface displays export and query forms
7. ✅ Big data connectivity section shows correct status

## Future Enhancements

1. **Actual HDFS Integration**: Connect to real Hadoop cluster for file uploads
2. **Real Hive Queries**: Replace simulation with actual Hive query execution
3. **Batch Export**: Schedule automated exports to HDFS
4. **Query History**: Store and display past query results
5. **Data Validation**: Add validation checks before export
6. **Multiple Formats**: Support ORC, Parquet, Avro formats in addition to CSV
7. **Real-time Updates**: WebSocket integration for live data updates

## Troubleshooting

### Issue: Command not found
**Solution:** Ensure you're in the project directory and Django is installed
```bash
python manage.py help
```

### Issue: Export returns empty file
**Solution:** Ensure database has data by running seed_data command
```bash
python manage.py seed_data
```

### Issue: Query simulation shows no results
**Solution:** Check that patients have district information and valid dates
```bash
python manage.py shell
>>> from hms.models import Patient
>>> Patient.objects.values('district').distinct()
```

## Support

For issues or questions, refer to:
- OPERATIONS.md for general application documentation
- Django documentation: https://docs.djangoproject.com/
- Hadoop documentation: https://hadoop.apache.org/docs/
- Hive documentation: https://hive.apache.org/
