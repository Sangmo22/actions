# Security Vulnerabilities - Step-by-Step Testing Guide

**For: Sangmo Lama | Django Notes CRUD Application**

---

## 🚀 Getting Started

**Server URL:** `http://localhost:8000/security/`

The dashboard provides an interactive interface to:

- Test 3 critical vulnerabilities
- Compare vulnerable vs. protected implementations
- Understand attack mechanics
- Learn prevention strategies

---

## 📋 Test Plan Overview

| Test # | Vulnerability | Vulnerable URL                        | Protected URL                   | Status |
| ------ | ------------- | ------------------------------------- | ------------------------------- | ------ |
| 1      | XSS           | `/security/xss/vulnerable/`           | `/security/xss/safe/`           | Ready  |
| 2      | SQL Injection | `/security/sql-injection/vulnerable/` | `/security/sql-injection/safe/` | Ready  |
| 3      | CSRF          | `/security/csrf/vulnerable/`          | `/security/csrf/protected/`     | Ready  |

---

## 🎯 TEST 1: Cross-Site Scripting (XSS) Vulnerability

### Test 1A: Stored XSS Attack

**Objective:** Demonstrate JavaScript execution in stored data

**Steps:**

1. **Navigate to:** `http://localhost:8000/security/xss/vulnerable/`

2. **Fill the form with:**
   - **Title:** `<img src=x onerror="alert('🔴 XSS VULNERABILITY CONFIRMED - JavaScript Executed!')">`
   - **Description:** `This is a test of XSS vulnerability in the Notes application. The image tag with onerror event handler should execute JavaScript code.` (≥10 chars ✓)

3. **Click:** "Submit & See XSS" button

4. **Expected Result:**
   - ✅ Alert popup appears with message: "🔴 XSS VULNERABILITY CONFIRMED - JavaScript Executed!"
   - ✅ You are redirected back to the vulnerable page
   - ✅ The malicious note is now stored in the database
   - ✅ The alert appears AGAIN when you refresh the page (Stored XSS)

**Evidence Captured:**

- Alert box showing code execution
- Note appears in table with HTML tags visible in browser inspector
- Page source shows `|safe` filter in template

---

### Test 1B: Analyze Vulnerable Code

**Location:** View page source at `/security/xss/vulnerable/`

**Find in template:**

```html
<!-- VULNERABLE: Rendering without escaping -->
<td>{{ note.title|safe }}</td>
<td>{{ note.description|safe }}</td>
```

**Vulnerability Details:**

- The `|safe` filter bypasses Django's auto-escaping
- Browser interprets the string as HTML/JavaScript
- `<img src=x onerror="...">` triggers JavaScript execution

**Attack Chain:**

```
User Input → Database → Template (unsafe rendering) → Browser Execution
```

---

### Test 1C: Protected Implementation

**Navigate to:** `http://localhost:8000/security/xss/safe/`

**Steps:**

1. **Fill the form with the SAME payload:**
   - **Title:** `<img src=x onerror="alert('XSS')">`
   - **Description:** `Test description for safe version` (≥10 chars)

2. **Click:** "Submit" button

3. **Expected Result:**
   - ✅ No alert popup appears
   - ✅ Redirect to safe page
   - ✅ Check the notes table - the payload is displayed as TEXT
   - ✅ The `<img...>` tags are visible as text, not HTML

**View Page Source:**

```html
<!-- SAFE: Using Django's auto-escaping (default) -->
<td>{{ note.title }}</td>
<td>{{ note.description }}</td>
```

**Browser HTML Output:**

```html
<td>&lt;img src=x onerror=&quot;alert('XSS')&quot;&gt;</td>
```

**Why Protection Works:**

- Django auto-escapes HTML special characters
- `<` → `&lt;`
- `>` → `&gt;`
- `"` → `&quot;`
- Browser displays it as plain text, not executable code

---

### Test 1D: Additional XSS Payloads to Try

| Payload                                           | Expected Behavior                         |
| ------------------------------------------------- | ----------------------------------------- |
| `<script>alert('XSS')</script>`                   | Script tag attempt - no execution on safe |
| `<svg/onload="alert('XSS')">`                     | SVG-based injection                       |
| `<div onmouseover="alert('XSS')">Hover</div>`     | Event handler injection                   |
| `javascript:alert('XSS')`                         | Protocol-based injection                  |
| `<iframe src="javascript:alert('XSS')"></iframe>` | iframe injection                          |

---

## 🎯 TEST 2: SQL Injection Vulnerability

### Test 2A: Comment-Based SQL Injection

**Objective:** Demonstrate SQL code injection through string concatenation

**Steps:**

1. **Navigate to:** `http://localhost:8000/security/sql-injection/vulnerable/`

2. **Fill the form with:**
   - **Title:** `Test'); --`
   - **Description:** `This is a comment-based SQL injection attempt. The -- symbol comments out the rest of the SQL statement.` (≥10 chars ✓)

3. **Click:** "Submit & Inject SQL" button

4. **Expected Result:**
   - ✅ Note appears to be created (check table or messages)
   - ✅ The comment (--) modifies the SQL query execution
   - ✅ Data is stored in database

**SQL Query Analysis:**

```sql
-- Original query structure:
INSERT INTO notes_note (title, description)
VALUES ('Test'); --', 'description');

-- What actually executes:
INSERT INTO notes_note (title, description)
VALUES ('Test');
-- The rest is commented out!
```

---

### Test 2B: Data Extraction Attempt

**Steps:**

1. **Stay on vulnerable page:** `http://localhost:8000/security/sql-injection/vulnerable/`

2. **Fill the form with:**
   - **Title:** `' OR '1'='1`
   - **Description:** `This attempts to create a condition that is always true in SQL. Used to extract all records bypassing WHERE conditions.` (≥10 chars ✓)

3. **Click:** "Submit & Inject SQL" button

4. **Expected Result:**
   - ✅ Injection attempt is processed
   - ✅ Data stored in database
   - ✅ Application doesn't crash (SQLite limitations prevent full exploitation)

**SQL Pattern:**

```sql
INSERT INTO notes_note (title, description)
VALUES (' OR '1'='1', 'description');
-- The '1'='1' is always true
```

---

### Test 2C: Analyze Vulnerable Code

**Location:** View page source at `/security/sql-injection/vulnerable/`

**Find in views.py:**

```python
# VULNERABLE CODE
sql = f"""
INSERT INTO notes_note (title, description)
VALUES ('{title}', '{desc}');
"""

with connection.cursor() as cursor:
    cursor.execute(sql)  # DANGER!
```

**Why It's Vulnerable:**

- User input directly concatenated into SQL string with f-strings
- No separation between SQL code and data
- Attacker can close quotes and inject arbitrary SQL
- No validation or parameterization

**Attack Vector:**

```
User Input: Test'); DROP TABLE notes_note; --
SQL becomes: INSERT ... VALUES ('Test'); DROP TABLE notes_note; --'...)
Results: Multiple SQL statements executed!
```

---

### Test 2D: Protected Implementation

**Navigate to:** `http://localhost:8000/security/sql-injection/safe/`

**Steps:**

1. **Fill the form with the SAME payload:**
   - **Title:** `Test'); --`
   - **Description:** `Test description for safe version` (≥10 chars)

2. **Click:** "Submit (Safe)" button

3. **Expected Result:**
   - ✅ Note is created successfully
   - ✅ Check the table - the payload is stored as LITERAL TEXT
   - ✅ No SQL injection occurs

**View Page Source:**

```python
# SAFE CODE - Parameterized Query
sql = "INSERT INTO notes_note (title, description) VALUES (%s, %s);"

with connection.cursor() as cursor:
    cursor.execute(sql, [title, description])  # Parameters passed separately
```

**Why Protection Works:**

- SQL template is fixed
- User input passed as separate parameters `[title, description]`
- Database driver escapes special characters
- Input treated as DATA, not SQL code

**Comparison:**

| Vulnerable                     | Safe                                   |
| ------------------------------ | -------------------------------------- |
| `VALUES ('{title}', '{desc}')` | `VALUES (%s, %s)` with `[title, desc]` |
| SQL and data mixed             | SQL and data separated                 |
| Quotes can break query         | Quotes treated as literal characters   |
| Injection possible             | Injection impossible                   |

---

### Test 2E: More SQL Injection Patterns to Try

| Payload                              | Attack Type      | Effect                             |
| ------------------------------------ | ---------------- | ---------------------------------- |
| `'; DELETE FROM notes_note; --`      | Destructive      | Attempts table deletion            |
| `' UNION SELECT * FROM auth_user --` | Data extraction  | Attempts user data extraction      |
| `); DROP PROCEDURE [procname]; --`   | Code execution   | Attempts stored procedure deletion |
| `' AND SLEEP(5) -- `                 | Time-based blind | Causes delay in response           |

---

## 🎯 TEST 3: Cross-Site Request Forgery (CSRF) Vulnerability

### Test 3A: Unauthenticated CSRF Test (Info Only)

**Objective:** Understand how CSRF exploits authenticated sessions

**Note:** This test requires creating a separate malicious HTML file, as Django's CSRF protection is difficult to fully bypass without CSRF token generation.

**Steps:**

1. **Navigate to:** `http://localhost:8000/security/csrf/vulnerable/`

2. **Observe the HTML form:**
   - Check page source (`Ctrl+Shift+I` → Elements)
   - Look for the form fields
   - **CRITICAL:** Notice NO `{% csrf_token %}` in the form
   - No hidden CSRF token field exists

3. **Form HTML Analysis:**
   ```html
   <form action="..." method="post">
     {# VULNERABLE: No {% csrf_token %} #}
     <input type="text" name="title" />
     <textarea name="description"></textarea>
     <input type="submit" />
   </form>
   ```

**Expected Result:**

- ✅ Form has method="POST"
- ✅ No CSRF token field present
- ✅ Vulnerable to unauthorized submissions

---

### Test 3B: Manual CSRF Demonstration (Admin/Testing Only)

**Important:** This test shows the vulnerability in a controlled environment.

**Steps:**

1. **Create malicious HTML file** (save as `csrf_attack.html`):

   ```html
   <!DOCTYPE html>
   <html>
     <head>
       <title>Claim Prize</title>
     </head>
     <body onload="document.getElementById('csrf-form').submit()">
       <h1>Processing your prize claim... Please wait.</h1>

       <form
         id="csrf-form"
         action="http://localhost:8000/security/csrf/vulnerable/"
         method="POST"
         style="display:none;"
       >
         <input
           type="hidden"
           name="title"
           value="HACKED - Account Compromised!"
         />
         <input
           type="hidden"
           name="description"
           value="This note was created by a CSRF attack. The attacker exploited your authenticated session without your knowledge or consent."
         />
       </form>
     </body>
   </html>
   ```

2. **Scenario Setup:**
   - Keep Notes app open and logged in (Tab 1)
   - Open `csrf_attack.html` in another tab (Tab 2)

3. **What Happens:**
   - ✅ Form auto-submits via JavaScript
   - ✅ Your browser includes session cookie with request
   - ✅ Note created without your explicit permission
   - ✅ Server performs unauthorized action

4. **Verify Attack:**
   - Switch back to Tab 1 and refresh
   - Observe the malicious note in the table
   - You never explicitly submitted that form!

---

### Test 3C: Protected Implementation

**Navigate to:** `http://localhost:8000/security/csrf/protected/`

**Steps:**

1. **View page source:**
   - Check Elements/Inspector
   - Look for the form

2. **Find the CSRF token:**

   ```html
   <form action="..." method="post">
     {% csrf_token %}
     <!-- Renders to: -->
     <input type="hidden" name="csrfmiddlewaretoken" value="9a3b4c..." />
     <input type="text" name="title" />
     <textarea name="description"></textarea>
   </form>
   ```

3. **Token Details:**
   - **Unique per session:** Each user has different token
   - **Unique per page:** Each form might have different token
   - **Cryptographically secure:** Cannot be guessed
   - **Server-validated:** Compared during POST verification

---

### Test 3D: Why CSRF Attack Fails on Protected Version

**Scenario:** Attacker tries same attack on protected endpoint

```html
<!-- Attacker's malicious form -->
<form action="http://localhost:8000/security/csrf/protected/" method="POST">
  <input type="hidden" name="title" value="Hacked" />
  <input type="hidden" name="description" value="Attack" />

  <!-- ❌ MISSING CSRF TOKEN! -->
  <!-- Attacker cannot obtain your token (same-origin policy) -->
</form>
```

**Server Verification Process:**

```
1. POST request received
2. Server extracts csrfmiddlewaretoken
3. Token check: Is token present? NO ❌
4. Result: 403 Forbidden
5. Request rejected, attack fails
```

**Error Response:**

```
403 Forbidden

The CSRF token is missing or incorrect.
```

---

### Test 3E: AJAX/JavaScript Requests with CSRF

**For modern applications using Fetch API:**

```javascript
// Get CSRF token from page
const token = document.querySelector("[name=csrfmiddlewaretoken]").value;

// Send authenticated request
fetch("/security/csrf/protected/", {
  method: "POST",
  headers: {
    "X-CSRFToken": token,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    title: "Safe Note",
    description: "Created via authenticated AJAX",
  }),
});
```

**Why This Works:**

- Token included in header: `X-CSRFToken`
- Server validates token from header
- Same-origin policy prevents cross-site access
- Attack fails because attacker cannot send valid token

---

## 🔍 Method to Verify Each Vulnerability

### XSS Verification Checklist

- [ ] Alert popup appears on vulnerable page
- [ ] Alert does NOT appear on safe page
- [ ] Page source shows `|safe` filter in vulnerable template
- [ ] Page source shows no `|safe` in safe template
- [ ] Browser DevTools shows HTML entities on safe version
- [ ] Database content shows HTML tags in vulnerable version

**Screenshots to Capture:**

1. Alert box with XSS message
2. Template source showing `|safe`
3. Table displaying HTML as text (safe version)
4. Browser inspector showing escaped entities

---

### SQL Injection Verification Checklist

- [ ] Note with '); -- is created on vulnerable page
- [ ] Note appears in table with injection payload visible
- [ ] Page source shows `f"INSERT ... VALUES ('..."` in vulnerable code
- [ ] Page source shows `VALUES (%s, %s)` with parameters in safe code
- [ ] Same payload stored as literal text on safe page
- [ ] No SQL errors expose table structure

**Screenshots to Capture:**

1. Vulnerable form with injection payload
2. Note table showing stored injection payload
3. View source showing string concatenation SQL
4. Safe version showing parameterized query code
5. Safe page with escaped injection stored as text

---

### CSRF Verification Checklist

- [ ] Vulnerable form has NO csrf_token field
- [ ] Protected form HAS csrf_token field
- [ ] View source shows missing token in vulnerable form
- [ ] View source shows `{% csrf_token %}` in protected form
- [ ] Manual malicious form submission creates unauthorized note
- [ ] Browser console shows 403 when attacking protected endpoint
- [ ] X-CSRFToken required in request headers for AJAX

**Screenshots to Capture:**

1. Vulnerable form HTML (no token field)
2. Protected form HTML (with token)
3. Network request showing missing token
4. Network request showing 403 Forbidden error
5. Malicious note appearing in database

---

## 📊 Summary Table: Before & After

| Aspect     | Vulnerable            | Protected                 |
| ---------- | --------------------- | ------------------------- |
| **XSS**    | `{{ var\|safe }}`     | `{{ var }}`               |
| **XSS**    | User scripts execute  | User scripts escaped      |
| **SQL**    | `f"VALUES ('{var}')"` | `VALUES (%s)` w/ params   |
| **SQL**    | Input mixed with code | Input separated from code |
| **CSRF**   | No CSRF token         | `{% csrf_token %}`        |
| **CSRF**   | No token validation   | Token validated           |
| **Result** | Data stolen/modified  | Protected & safe          |

---

## 🎓 Key Learning Outcomes

### For Each Vulnerability:

**XSS:**

- Understand how injectable content executes in browsers
- Learn why auto-escaping is critical
- Recognize `|safe` filter dangers

**SQL Injection:**

- Understand SQL query structure
- Learn parameterized query benefits
- Recognize string concatenation risks

**CSRF:**

- Understand session cookie exploitation
- Learn token-based protection
- Recognize form origin validation

---

## ⚠️ Important Reminders

1. **Educational Use Only:** These vulnerabilities are intentionally included for learning
2. **Never In Production:** Never use these patterns in real applications
3. **Always Escape Output:** Use Django's auto-escaping by default
4. **Always Parameterize:** Separate SQL code from data
5. **Always Validate:** Include CSRF tokens in all forms
6. **Test Regularly:** Include security testing in your pipeline

---

## 📚 Quick Reference: Prevention Shortcuts

```python
# ✅ Safe XSS Prevention
{{ user_input }}  # Auto-escaped (default)
{{ user_input|escape }}  # Explicit escaping

# ❌ Dangerous
{{ user_input|safe }}  # NEVER do this with user input

# ✅ Safe SQL Injection Prevention
User.objects.filter(id=user_id)  # Django ORM
cursor.execute(sql, [param1, param2])  # Parameterized

# ❌ Dangerous
cursor.execute(f"SELECT * WHERE id = '{user_id}'")  # String concat

# ✅ Safe CSRF Prevention
<form method="post">
    {% csrf_token %}  # Always include
    <input ...>
</form>

# ❌ Dangerous
<form method="post">
    <!-- No {% csrf_token %} -->
</form>
```

---

**Document Status:** ✅ Complete and Ready for Testing  
**Last Updated:** Sangmo Lama  
**Application:** Django Notes CRUD  
**Environment:** Development/Testing Only
