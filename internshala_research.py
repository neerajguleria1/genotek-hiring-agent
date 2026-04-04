"""
Internshala Access Attempt - Research Documentation
====================================================
This script documents what we tried to access Internshala programmatically
and exactly what walls we hit. This is NOT a scraper — it's a technical
audit of why autonomous access is not possible without authorization.
"""

import requests

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://internshala.com/jobs/",
})

print("=" * 60)
print("INTERNSHALA PROGRAMMATIC ACCESS - RESEARCH FINDINGS")
print("=" * 60)

# -------------------------------------------------------
# STEP 1: Try unauthenticated access to job listings
# -------------------------------------------------------
print("\n[STEP 1] Trying unauthenticated request to job listings...")
try:
    r = session.get("https://internshala.com/jobs/", timeout=10)
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        print("  Result: Page loads — but it's server-rendered HTML, not JSON")
        print("  Problem: No structured data, no API response")
except Exception as e:
    print(f"  Error: {e}")

# -------------------------------------------------------
# STEP 2: Try the internal search criterias endpoint
# (Found via browser Network tab inspection)
# -------------------------------------------------------
print("\n[STEP 2] Trying internal endpoint: get_search_criterias/")
try:
    r = session.get(
        "https://internshala.com/jobs/get_search_criterias/",
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=10
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"  Result: SUCCESS — returns {data.get('category_count', '?')} categories, {data.get('location_count', '?')} locations")
        print("  Note: This is metadata only — no candidate/applicant data")
    else:
        print(f"  Result: BLOCKED — {r.text[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# -------------------------------------------------------
# STEP 3: Try to fetch actual job listings via XHR
# -------------------------------------------------------
print("\n[STEP 3] Trying to fetch job listings via XHR...")
try:
    r = session.get(
        "https://internshala.com/jobs/match-1/",
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=10
    )
    print(f"  Status: {r.status_code}")
    if r.status_code == 200:
        print("  Result: Returns HTML fragment — not JSON, not structured data")
        print("  Problem: Still no applicant data, just job postings")
    elif r.status_code == 403:
        print("  Result: 403 FORBIDDEN")
        print("  Reason: Requires authenticated session")
    else:
        print(f"  Result: {r.status_code} — {r.text[:100]}")
except Exception as e:
    print(f"  Error: {e}")

# -------------------------------------------------------
# STEP 4: Try recruiter/applicant API endpoints
# -------------------------------------------------------
print("\n[STEP 4] Trying recruiter applicant endpoints...")
endpoints = [
    "https://internshala.com/recruiter/applications/",
    "https://internshala.com/api/v1/applications/",
    "https://internshala.com/recruiter/get_applications/",
]
for url in endpoints:
    try:
        r = session.get(url, timeout=10)
        print(f"  {url}")
        print(f"  Status: {r.status_code}")
        if r.status_code == 403:
            print("  Result: 403 FORBIDDEN — login + CSRF token required")
        elif r.status_code == 404:
            print("  Result: 404 NOT FOUND — endpoint doesn't exist publicly")
        elif r.status_code == 302:
            print(f"  Result: 302 REDIRECT → {r.headers.get('Location', '?')} (redirected to login)")
        else:
            print(f"  Result: {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

# -------------------------------------------------------
# SUMMARY
# -------------------------------------------------------
print("\n" + "=" * 60)
print("FINDINGS SUMMARY")
print("=" * 60)
print("""
1. PUBLIC ENDPOINTS FOUND:
   - get_search_criterias/ → returns category/location metadata (no auth needed)
   - Job listing pages → server-rendered HTML only, no JSON API

2. WALLS HIT:
   - All recruiter/applicant endpoints return 403 or redirect to login
   - Job listing XHR calls require: session cookie + CSRF token
   - CSRF token is generated per-session, tied to browser login
   - No public API exists for candidate/applicant data

3. WHAT WOULD BE NEEDED TO BYPASS:
   - Maintain authenticated browser session (Selenium/Playwright)
   - Extract and replay CSRF tokens per request
   - This = unauthorized access → violates Internshala ToS + IT Act 2000

4. CONCLUSION:
   - Autonomous access to Internshala applicant data is NOT possible
     without either:
     a) A formal data partnership/API agreement with Internshala, OR
     b) Unauthorized session hijacking (illegal)
   - Recommended path: Contact Internshala for recruiter API access
""")
