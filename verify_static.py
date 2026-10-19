"""Verify the stylesheet serves with HTTP 200 and is linked on every page."""
import urllib.request
import os
from uuid import uuid4

import django
from django.contrib.auth import get_user_model
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

BASE = "http://127.0.0.1:8765"

# 1) Stylesheet itself
req = urllib.request.Request(BASE + "/static/css/style.css", headers={"User-Agent": "verify"})
with urllib.request.urlopen(req, timeout=10) as resp:
    body = resp.read()
    ctype = resp.headers.get("Content-Type", "")
    print(f"stylesheet: HTTP {resp.status}  {len(body)} bytes  content-type={ctype}")
    css = body.decode("utf-8")
    for marker in [":root", ".rail", ".ed-grid", ".masthead", "@media"]:
        assert marker in css, f"missing {marker} in served CSS"
    print("served CSS contains core sections: OK")

# 2) Every page links the stylesheet
PAGES = ["/", "/dashboard/", "/patients/", "/patients/register/",
         "/staff/", "/appointments/", "/beds/", "/analytics/", "/reports/"]
user = get_user_model().objects.create_user(username=f'static-{uuid4().hex[:12]}')
client = Client()
client.force_login(user)
anonymous_client = Client()
all_ok = True
try:
    for page in PAGES:
        active_client = anonymous_client if page == '/' else client
        response = active_client.get(page, follow=True)
        html = response.content.decode("utf-8", errors="replace")
        linked = response.status_code == 200 and 'href="/static/css/style.css" rel="stylesheet"' in html
        print(f"{'OK ' if linked else 'FAIL'} {page:<22} HTTP {response.status_code} stylesheet linked={linked}")
        all_ok = all_ok and linked
finally:
    user.delete()

print("\nALL PAGES LINK STYLESHEET" if all_ok else "\nSOME PAGES MISSING STYLESHEET")
raise SystemExit(not all_ok)
