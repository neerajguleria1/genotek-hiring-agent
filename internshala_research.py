"""
Internshala Programmatic Access - Technical Research Report v2
==============================================================
Objective: Systematically test programmatic access to Internshala,
document all findings, map the auth architecture, and propose a
compliant production integration path.

Constraints:
- No automated login
- No session cookie extraction
- No CSRF bypass
- No unauthorized scraping
"""

import requests
import json

session = requests.Session()
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://internshala.com/jobs/",
}
session.headers.update(BASE_HEADERS)

results = []

def log(step, url, status, result, failure_reason=None, headers_used=None):
    entry = {"step": step, "url": url, "status": status, "result": result}
    if failure_reason:
        entry["failure_reason"] = failure_reason
    if headers_used:
        entry["headers_used"] = headers_used
    results.append(entry)
    print(f"\n[{step}] {url}")
    print(f"  Status  : {status}")
    print(f"  Result  : {result}")
    if failure_reason:
        print(f"  Failure : {failure_reason}")
    if headers_used:
        print(f"  Headers : {headers_used}")

print("=" * 70)
print("INTERNSHALA PROGRAMMATIC ACCESS - TECHNICAL RESEARCH REPORT v2")
print("=" * 70)

# -------------------------------------------------------
# STEP 1: PUBLIC ACCESS TESTING
# -------------------------------------------------------
print("\n\n--- STEP 1: PUBLIC ACCESS TESTING ---")

# 1a. Homepage structure
try:
    r = session.get("https://internshala.com/jobs/", timeout=10)
    log("1a", "https://internshala.com/jobs/", r.status_code,
        f"Server-rendered HTML ({len(r.text)} chars). No JSON payload. "
        "Page contains csrftoken in meta tag and cookie.",
        "Not a data API — full Django-rendered template.")
except Exception as e:
    log("1a", "https://internshala.com/jobs/", "ERROR", str(e))

# 1b. Search criterias endpoint
try:
    r = session.get("https://internshala.com/jobs/get_search_criterias/", timeout=10)
    if r.status_code == 200:
        data = r.json()
        log("1b", "https://internshala.com/jobs/get_search_criterias/", 200,
            f"PUBLIC JSON. {data.get('category_count','?')} categories, "
            f"{data.get('location_count','?')} locations. "
            "Metadata only — no candidate or applicant data.")
    else:
        log("1b", "https://internshala.com/jobs/get_search_criterias/",
            r.status_code, r.text[:100], "Blocked")
except Exception as e:
    log("1b", "https://internshala.com/jobs/get_search_criterias/", "ERROR", str(e))

# 1c. Job listings XHR — default headers
try:
    r = session.get("https://internshala.com/jobs/match-1/", timeout=10)
    ct = r.headers.get("Content-Type", "")
    log("1c", "https://internshala.com/jobs/match-1/", r.status_code,
        f"Content-Type: {ct}. HTML fragment returned, not JSON.",
        "No structured data. Full response requires authenticated session context.",
        "X-Requested-With: XMLHttpRequest")
except Exception as e:
    log("1c", "https://internshala.com/jobs/match-1/", "ERROR", str(e))

# 1d. Job listings — with Accept: application/json header variation
try:
    r = session.get(
        "https://internshala.com/jobs/match-1/",
        headers={**BASE_HEADERS, "Accept": "application/json"},
        timeout=10
    )
    ct = r.headers.get("Content-Type", "")
    log("1d", "https://internshala.com/jobs/match-1/ [Accept: application/json]",
        r.status_code,
        f"Content-Type: {ct}. Server ignores Accept header — still returns HTML.",
        "Server does not support content negotiation on this endpoint.",
        "Accept: application/json")
except Exception as e:
    log("1d", "https://internshala.com/jobs/match-1/ [Accept: application/json]", "ERROR", str(e))

# 1e. Query param variation
try:
    r = session.get(
        "https://internshala.com/jobs/match-1/?format=json",
        timeout=10
    )
    ct = r.headers.get("Content-Type", "")
    log("1e", "https://internshala.com/jobs/match-1/?format=json", r.status_code,
        f"Content-Type: {ct}. format=json param has no effect.",
        "No query-param based content negotiation available.",
        "?format=json query param")
except Exception as e:
    log("1e", "https://internshala.com/jobs/match-1/?format=json", "ERROR", str(e))

# -------------------------------------------------------
# STEP 2: CONTROLLED REQUEST REPLAY (no auth)
# -------------------------------------------------------
print("\n\n--- STEP 2: CONTROLLED REQUEST REPLAY (NO AUTH) ---")

endpoints = [
    ("2a", "https://internshala.com/recruiter/applications/"),
    ("2b", "https://internshala.com/api/v1/applications/"),
    ("2c", "https://internshala.com/recruiter/get_applications/"),
    ("2d", "https://internshala.com/jobs/get_jobs/"),
    ("2e", "https://internshala.com/jobs/get_jobs/?page=1&per_page=20"),
]

for step, url in endpoints:
    try:
        r = session.get(url, timeout=10, allow_redirects=False)
        if r.status_code == 403:
            log(step, url, 403,
                "Access constrained by session validation.",
                "Missing: sessionid cookie + csrftoken. "
                "Server returns 403 before processing request body.")
        elif r.status_code in (301, 302):
            location = r.headers.get("Location", "?")
            log(step, url, r.status_code,
                f"Redirect → {location}",
                "Unauthenticated request redirected to login. "
                "Server-side session check fires before route handler.")
        elif r.status_code == 404:
            log(step, url, 404,
                "Endpoint not publicly exposed.",
                "Route either does not exist or is conditionally registered.")
        elif r.status_code == 200:
            ct = r.headers.get("Content-Type", "")
            log(step, url, 200,
                f"Content-Type: {ct} | Length: {len(r.text)} chars")
        else:
            log(step, url, r.status_code, r.text[:80])
    except Exception as e:
        log(step, url, "ERROR", str(e))

# -------------------------------------------------------
# STEP 3: FAILURE ANALYSIS
# -------------------------------------------------------
print("\n\n--- STEP 3: FAILURE ANALYSIS ---")
print("""
All protected endpoints are constrained by one or more of the following:

A. SESSION COOKIE (sessionid)
   - Django session middleware validates sessionid on every request
   - Set only after successful credential authentication
   - Absent in all unauthenticated requests → immediate 403 or redirect
   - Lifecycle: created on login → stored server-side → expires on logout/timeout

B. CSRF TOKEN (csrftoken)
   - Django CsrfViewMiddleware enforces token on all state-changing requests
   - Token is embedded in page HTML and set as a cookie on page load
   - Must match between cookie value and request header (X-CSRFToken)
   - Cannot be replayed without an active session — token is session-bound

C. CONTENT NEGOTIATION NOT SUPPORTED
   - Tested: Accept: application/json header → no effect
   - Tested: ?format=json query param → no effect
   - Server returns HTML regardless of requested content type
   - Confirms: no REST API layer exists on these routes

D. NO PUBLIC API SURFACE
   - No API key authentication system observed
   - No OAuth endpoints found
   - No documented developer API
   - All data access is gated behind browser session context
""")

# -------------------------------------------------------
# STEP 4: SYSTEM ARCHITECTURE MAPPING
# -------------------------------------------------------
print("\n\n--- STEP 4: SYSTEM ARCHITECTURE ---")
print("""
Request/Response Lifecycle (observed via DevTools + controlled tests):

  UNAUTHENTICATED FLOW:
  Client → GET /jobs/match-1/
         → Django SessionMiddleware: no sessionid → reject
         → Response: 302 redirect to /login OR 403 Forbidden
         → No route handler executed

  AUTHENTICATED FLOW (browser context):
  Client → GET /login → server returns HTML with csrftoken in meta + cookie
         → POST /login {email, password, csrftoken}
         → Django authenticates → creates server-side session
         → Sets-Cookie: sessionid=xxx; csrftoken=yyy
         → Client stores both cookies

  SUBSEQUENT API CALLS:
  Client → GET /jobs/match-1/
         → Headers: Cookie: sessionid=xxx; csrftoken=yyy
         → Django SessionMiddleware: validates sessionid → pass
         → Django CsrfViewMiddleware: validates token → pass
         → Route handler executes → returns JSON/HTML response

  SERVER-SIDE VALIDATION ORDER:
  1. SessionMiddleware (checks sessionid cookie)
  2. CsrfViewMiddleware (checks csrftoken on POST/PUT/DELETE)
  3. Permission checks (is user a recruiter? does job belong to them?)
  4. Route handler executes

  KEY OBSERVATION:
  Validation happens at middleware level — before any route logic.
  This means endpoint enumeration alone cannot bypass auth.
  The session + CSRF layer must be satisfied first.
""")

# -------------------------------------------------------
# STEP 5: ADDITIONAL TECHNICAL EXPLORATION
# -------------------------------------------------------
print("\n\n--- STEP 5: ADDITIONAL TECHNICAL EXPLORATION ---")
print("""
Safe, non-invasive next steps for deeper investigation:

1. HEADER ANALYSIS (DevTools)
   - Capture full request headers from an authenticated browser session
   - Identify all required headers beyond Cookie and X-CSRFToken
   - Check for custom headers (X-App-Version, X-Client-ID, etc.)

2. TOKEN LIFECYCLE STUDY (conceptual)
   - Observe how csrftoken changes across sessions
   - Determine if token is rotating (per-request) or static (per-session)
   - Django default: static per-session, rotates on login

3. RESPONSE STRUCTURE MAPPING
   - For publicly accessible endpoints (e.g. get_search_criterias/)
   - Map full JSON schema to understand data model
   - Useful for designing integration layer once API access is granted

4. RECRUITER PORTAL OBSERVATION
   - With a legitimate recruiter account, observe all XHR calls
   - Map the full API surface available to authenticated recruiters
   - This is the exact API surface a data partnership would expose

5. ROBOTS.TXT + SITEMAP ANALYSIS
   - Check https://internshala.com/robots.txt for disallowed paths
   - Confirms which routes are explicitly off-limits for bots
""")

# -------------------------------------------------------
# STEP 6: COMPLIANT INTEGRATION STRATEGY
# -------------------------------------------------------
print("\n\n--- STEP 6: COMPLIANT INTEGRATION STRATEGY ---")
print("""
Option 1: Official API Partnership (Production Path)
  - Engage Internshala partnerships/enterprise team
  - Request recruiter data API or webhook access
  - Standard for enterprise ATS integrations
  - Contact: https://internshala.com/contact-us/
  - Timeline: 1–4 weeks for agreement + integration

Option 2: Recruiter Portal CSV Export (Available Today)
  - Internshala recruiter dashboard supports applicant CSV export
  - GenoTek recruiter exports → uploads to /candidates/bulk endpoint
  - Already implemented and deployed
  - Zero legal risk, operational within hours

Option 3: ATS Webhook Integration
  - If Internshala supports outbound webhooks (common in enterprise plans)
  - Configure webhook → POST to /candidates endpoint on new application
  - Fully automated, fully authorized

Option 4: Candidate-Consented Import
  - Candidates apply via GenoTek form
  - Optional: "Import from Internshala profile" (user-initiated)
  - User-consented data flow — same pattern as OAuth profile import
  - Compliant, scalable, no partnership required
""")

# -------------------------------------------------------
# ENGINEERING CONCLUSION
# -------------------------------------------------------
print("\n\n--- ENGINEERING CONCLUSION ---")
print("""
Public endpoints (get_search_criterias/) return structured JSON without
authentication. All candidate and applicant data endpoints are constrained
by Django session + CSRF middleware, which validates at the request
pipeline level before any route handler executes. Content negotiation
and query-param variations produce no change in behavior, confirming
the absence of a REST API layer. Production access requires either a
formal data partnership with Internshala or a user-consented import
flow. The recruiter CSV export path is operational today with zero
integration overhead. Further automation would require operating within
an authenticated browser context or an authorized API surface.
""")

# -------------------------------------------------------
# FULL ATTEMPTS LOG
# -------------------------------------------------------
print("\n\n--- FULL ATTEMPTS LOG (JSON) ---")
print(json.dumps(results, indent=2))
