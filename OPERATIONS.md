# Meridian Care HMS Operations

## Current scope

Django serves the pages and SQLite is the transactional database. Patient, staff, ward, bed, and appointment records are stored in SQL. An empty database is shown as empty; no sample hospital data is automatically loaded. Create the first user with Django's superuser command, then create wards, beds, and staff in the protected Django admin. Patient registration and appointment scheduling are available in the application.

When `DJANGO_DEBUG=true` (the local default), the app opens directly to the dashboard and management pages do not require sign-in. With `DJANGO_DEBUG=false`, all management pages require an authenticated Django user. This project has no role-based authorization yet, so treat every authenticated account as having access to patient and report data. Do not expose the debug server to the public internet.

## Windows development

From the project directory in PowerShell:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8765
```

Open `http://127.0.0.1:8765/`. In local debug mode the dashboard opens directly. The admin console is at `http://127.0.0.1:8765/admin/`.

For local development, `DJANGO_DEBUG` defaults to `true` and Django generates an ephemeral development secret. Set `DJANGO_SECRET_KEY` before setting `DJANGO_DEBUG=false`; configure comma-separated `DJANGO_ALLOWED_HOSTS` for the deployment host. The generated local secret changes when Django restarts, so set a stable secret for persistent browser sessions.

## Verification

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test hms
python check_css.py
python verify_static.py
python smoke_test.py
```

`smoke_test.py` expects the development server at port 8765. The Django test suite creates and destroys its own temporary database; it does not seed or alter the local records.

## Data setup

1. Sign in to `/admin/`.
2. Create wards and their bed records. Capacity shown in the app is counted from bed records; `out_of_service` beds are excluded from available capacity.
3. Add staff and mark their availability.
4. Register patients from the Patients page. A bed is optional, and the form only offers unoccupied beds.
5. Schedule appointments from the Appointments page. An active doctor/time slot can only be booked once.

CSV reports use the selected date range. Staff and current bed inventory exports are snapshots. Historical occupancy is not available because bed assignment events are not yet stored.

## Hadoop / HDFS / Hive

The application uses short-timeout, cached WebHDFS and Beeline connection checks. Neither service is required for normal Django/SQLite workflows. The status panel reports `Not configured` or `Unavailable` when no live connection can be verified; it does not label local SQL data as Hive output.

Optional environment variables:

```powershell
$env:HDFS_WEBHDFS_URL = 'http://namenode-host:9870'
$env:HDFS_DATASET_PATHS = 'covid_cases=/datasets/covid_cases,admissions=/datasets/admissions'
$env:HIVE_JDBC_URL = 'jdbc:hive2://hive-host:10000/default'
$env:BEELINE_PATH = 'C:\path\to\beeline.cmd'
```

HDFS inventory reports metadata returned by WebHDFS for explicitly configured paths. File count, total bytes, format when inferable from the path, and modification time are actual NameNode metadata. Record counts require a format-aware reader and remain `Not determined`. Hive currently performs only a bounded `SELECT 1` connectivity check; analytic query execution is not enabled because no Hive service, table schema, or credentials are configured.

## Dependency report

| Dependency | Current state | Purpose | Install command if absent |
| --- | --- | --- | --- |
| Python 3.14 | Available | Runtime | Install a supported Python release from python.org; no install was attempted |
| Django 6.1.2 | Available | Web framework and ORM | `python -m pip install Django==6.1.2` |
| SQLite | Available via Python standard library | Local SQL database | None |
| Node.js | Available in the current environment | JavaScript syntax checks only | Not required to run Django |
| Chart.js 4.4.0 | Loaded from the existing jsDelivr CDN reference | Browser charts | No package install; requires browser network access |
| Hadoop / WebHDFS | Not detected or configured | Optional distributed storage integration | Requires an existing Hadoop cluster and its operator-provided WebHDFS endpoint; no software was installed |
| Hive / Beeline | Not detected or configured | Optional Hive query integration | Requires an existing Hive service and compatible Beeline client; no software was installed |
| PDF library | Not installed | Optional PDF exports | Not required; CSV export is implemented |

The project currently has no `requirements.txt`; Django 6.1.2 is the only Python package required by the application itself. Do not install Hadoop/Hive from an unverified distribution or download an installer without approving the exact deployment approach first.

## File audit and cleanup candidates

No project files were deleted. These findings are classifications only; remove nothing without explicit approval.

| Classification | Paths | Finding |
| --- | --- | --- |
| Required | `manage.py`, `config/`, `hms/`, `templates/`, `static/`, `db.sqlite3`, `hms/migrations/` | App source, configured SQL data, static UI, and schema history. Preserve the database and migrations. |
| Potentially useful | `check_css.py`, `smoke_test.py`, `verify_static.py`, `hms/tests.py` | Verification tooling; the two HTTP smoke scripts were updated for authenticated, empty-database behavior. |
| Appears unused; approval required | `fix1.py`, `tmp_inspect.py` | One-off source-edit/fixture-inspection helpers; neither is imported by the application. Review before removal. |
| Generated artifacts; approval required | `server2.log`, `server_err.log`, `server_out.log`, `hms/__pycache__/` | Old server output and Python bytecode. Logs may contain local paths and tracebacks; review before archiving/removing. |
| Obsolete fixture module; approval required | `hms/mock_data.py` | Contains fictional hardcoded metrics and records; no live application imports it. Kept in place pending approval. |
| Sensitive/protected | `db.sqlite3`, any future `.env` or user-uploaded files | Keep local and never commit or delete as part of cleanup. No `.env` file was found in the inspected project root. |
