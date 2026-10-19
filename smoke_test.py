"""Verify rendered pages contain expected markers and no template errors."""
import re
import os
from uuid import uuid4

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

BASE = "http://127.0.0.1:8765"

CHECKS = {
    "/": [("login-card", "login form"), ("visual-title", "visual panel"), ("csrfmiddlewaretoken", "CSRF token")],
    "/dashboard/": [("dashboard-data", "database chart data"), ("Active COVID-19 cases", "case summary"),
                    ("Hospital capacity", "capacity board")],
    "/patients/": [("patientTable", "patient table"), ("Patient directory", "patient heading"),
                   ("Register patient", "register link")],
    "/staff/": [("roster", "staff roster"), ("All departments", "department filter"), ("Add staff", "add staff action")],
    "/appointments/": [("apptTable", "appointments table"), ("apptModal", "appointment form"),
                       ("Schedule appointment", "schedule action")],
    "/beds/": [("board", "bed capacity board"), ("No beds are configured", "empty state")],
    "/analytics/": [("analytics-data", "database chart data"), ("HDFS", "HDFS status"),
                    ("Hive", "Hive status"), ("Not configured", "unavailable services")],
    "/reports/": [("Download CSV", "CSV export"), ("No admissions or discharges", "empty state")],
}
if settings.DEBUG:
    CHECKS['/'] = CHECKS['/dashboard/']

user = get_user_model().objects.create_user(username=f'smoke-{uuid4().hex[:12]}')
client = Client()
client.force_login(user)
anonymous_client = Client()
failed = False
try:
    for page, markers in CHECKS.items():
        active_client = anonymous_client if page == '/' else client
        resp = active_client.get(page, follow=True)
        html = resp.content.decode("utf-8", errors="replace")
        problems = []
        if resp.status_code != 200:
            problems.append(f"HTTP {resp.status_code}")
        for needle, label in markers:
            if needle not in html:
                problems.append(f"missing {label}")
        if re.search(r"\{%|\{\{", html):
            problems.append("unrendered template tags!")
        if "Traceback" in html or "Exception" in html:
            problems.append("exception in page")
        status = "OK " if not problems else "FAIL"
        if problems:
            failed = True
        print(f"{status} {page:<18} {'; '.join(problems) if problems else ''}")
finally:
    user.delete()

print("\nALL PAGES PASSED" if not failed else "\nSOME CHECKS FAILED")
raise SystemExit(failed)
