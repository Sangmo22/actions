# SECURITY TESTING ENVIRONMENT - QUICK START GUIDE

**Sangmo Lama | Django Notes CRUD Application**

---

## 🚀 QUICK START

### 1. Access the Testing Dashboard

Open your browser and navigate to:

```
http://localhost:8000/security/
```

### 2. Available Test Locations

| Test              | Vulnerable                            | Protected                       |
| ----------------- | ------------------------------------- | ------------------------------- |
| **XSS**           | `/security/xss/vulnerable/`           | `/security/xss/safe/`           |
| **SQL Injection** | `/security/sql-injection/vulnerable/` | `/security/sql-injection/safe/` |
| **CSRF**          | `/security/csrf/vulnerable/`          | `/security/csrf/protected/`     |

---

## 📋 DOCUMENTATION FILES

### 1. **VULNERABILITY_ANALYSIS_REPORT.md** ⭐ START HERE

- Executive summary
- Test results with evidence
- Real-world impact analysis
- Severity assessment
- Mitigation status

### 2. **SECURITY_TESTING_GUIDE.md** - DETAILED REFERENCE

- Deep-dive vulnerability analysis
- Attack techniques explained
- Real-world attack examples
- Prevention strategies
- Code examples (vulnerable vs. safe)

### 3. **TESTING_STEP_BY_STEP.md** - HANDS-ON TESTING

- Step-by-step testing instructions
- Exact payloads to try
- Expected results for each test
- Screenshots to capture
- Verification checklists

---

## 🧪 RUNNING AUTOMATED TESTS

```bash
# From project directory
cd c:\Users\Dell\OneDrive\Documents\web\crud
python run_security_tests.py
```

**Expected Output:**

```
================================================================================
DJANGO SECURITY VULNERABILITY TEST SUITE
Application: Notes CRUD
Tester: Sangmo Lama
================================================================================

✅ TEST 1: XSS - VULNERABLE VERSION: EXPLOITED
✅ TEST 1B: XSS - SAFE VERSION: PROTECTED

✅ TEST 2: SQL Injection - VULNERABLE VERSION: ANALYZED
✅ TEST 2B: SQL Injection - SAFE VERSION: PROTECTED

✅ TEST 3: CSRF - VULNERABLE VERSION: VULNERABILITY IDENTIFIED
✅ TEST 3B: CSRF - PROTECTED VERSION: PROTECTED
```

---

## 🎯 QUICK TEST SUMMARY

### ✅ XSS Vulnerability

**Payload:** `<img src=x onerror="alert('XSS')">`

- Navigate to: `/security/xss/vulnerable/`
- Submit payload in title field
- Result: Alert box appears (when submitted)
- Proof: Check database - malicious code stored

### ✅ SQL Injection Vulnerability

**Payload:** `Test'); --`

- Navigate to: `/security/sql-injection/vulnerable/`
- Submit payload in title field
- Result: SQL query structure is modified
- Proof: Comment syntax closes the quote

### ✅ CSRF Vulnerability

**Vulnerability:** No CSRF token in form

- Navigate to: `/security/csrf/vulnerable/`
- View page source
- Look for: `<input type="hidden" name="csrfmiddlewaretoken" ...>` - NOT FOUND
- Proof: Form vulnerable to cross-site attacks

---

## 📊 KEY FINDINGS

| Vulnerability     | Status          | Risk     |
| ----------------- | --------------- | -------- |
| **XSS**           | ✅ EXPLOITED    | CRITICAL |
| **SQL Injection** | ✅ DEMONSTRATED | CRITICAL |
| **CSRF**          | ✅ IDENTIFIED   | HIGH     |

---

## 🔐 PROTECTION METHODS IMPLEMENTED

### XSS Protection

```html
<!-- Django's default auto-escaping -->
{{ user_input }}
<!-- Safe - automatically escaped -->
```

### SQL Injection Protection

```python
# Parameterized queries (SQL and data separated)
cursor.execute("INSERT INTO table VALUES (%s, %s)", [data1, data2])
```

### CSRF Protection

```html
<!-- CSRF token in every form -->
<form method="post">
  {% csrf_token %}
  <!-- form fields -->
</form>
```

---

## 🎓 WHAT YOU'LL LEARN

### Understanding Vulnerabilities

- How attackers exploit security flaws
- Real-world attack scenarios
- Impact of each vulnerability

### Attack Payloads

- Practical injection examples
- How to test vulnerabilities
- What to look for in responses

### Prevention Techniques

- Best practices for each vulnerability type
- Django security features
- Secure coding patterns

### Testing Skills

- How to find vulnerabilities
- How to verify fixes
- Automated vs. manual testing

---

## ✨ FILES CREATED

```
crud/
├── VULNERABILITY_ANALYSIS_REPORT.md     # Executive report
├── SECURITY_TESTING_GUIDE.md            # Comprehensive guide
├── TESTING_STEP_BY_STEP.md              # Hands-on instructions
├── run_security_tests.py                # Automated tests
├── notes/
│   ├── security_test_views.py           # Vulnerable & safe endpoints
│   ├── security_urls.py                 # Security testing URLs
│   └── templates/notes/security/        # Testing templates
│       ├── dashboard.html
│       ├── xss_vulnerable.html
│       ├── xss_safe.html
│       ├── add_vulnerable.html
│       ├── sql_injection_demo.html
│       ├── sql_injection_safe.html
│       ├── csrf_vulnerable.html
│       └── csrf_protected.html
└── crud/
    ├── urls.py                         # Updated to include security URLs
    └── settings.py                     # Updated ALLOWED_HOSTS
```

---

## 🛠 TROUBLESHOOTING

### Server Not Starting?

```bash
# Ensure venv is activated
cd c:\Users\Dell\OneDrive\Documents\web\crud
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
```

### Database Issues?

```bash
# Reset database
python manage.py migrate
python manage.py createsuperuser  # If needed
```

### Import Errors?

```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 📚 DOCUMENTATION READING ORDER

1. **START:** This file (Quick Start Guide)
2. **READ:** VULNERABILITY_ANALYSIS_REPORT.md
3. **STUDY:** SECURITY_TESTING_GUIDE.md
4. **PRACTICE:** TESTING_STEP_BY_STEP.md
5. **RUN:** run_security_tests.py
6. **EXPLORE:** Browser dashboard at `/security/`

---

## 🎯 LEARNING OBJECTIVES

After completing this security testing exercise, you will understand:

✓ How XSS vulnerabilities work and how to prevent them  
✓ How SQL Injection attacks work and how to prevent them  
✓ How CSRF attacks work and how to prevent them  
✓ The importance of input validation and output escaping  
✓ Django's built-in security features  
✓ How to write secure Python/Django code  
✓ How to test for security vulnerabilities  
✓ Best practices for web application security

---

## ⚠️ IMPORTANT NOTES

- **Educational Purpose Only:** These vulnerabilities are intentional for teaching
- **Development Environment:** This setup is for learning, never use in production
- **Safe Testing:** All tests are isolated and controlled
- **No Real Harm:** All payloads are contained to this application

---

## 📞 SUPPORT & REFERENCES

### Django Documentation

- Official Security Docs: https://docs.djangoproject.com/en/stable/topics/security/
- QuerySet API: https://docs.djangoproject.com/en/stable/ref/models/querysets/

### OWASP Resources

- OWASP Top 10: https://owasp.org/Top10/
- XSS Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- SQL Injection: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- CSRF Prevention: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

---

## ✅ COMPLETION CHECKLIST

Use this checklist to track your progress:

### Reading & Understanding

- [ ] Read VULNERABILITY_ANALYSIS_REPORT.md
- [ ] Read SECURITY_TESTING_GUIDE.md
- [ ] Understand each vulnerability type
- [ ] Understand impact of each vulnerability

### Testing

- [ ] Access dashboard at /security/
- [ ] Test XSS vulnerable endpoint
- [ ] Test XSS safe endpoint
- [ ] Test SQL injection vulnerable endpoint
- [ ] Test SQL injection safe endpoint
- [ ] Test CSRF vulnerable endpoint
- [ ] Test CSRF protected endpoint
- [ ] Run automated security tests

### Analysis

- [ ] Compare vulnerable vs. safe code
- [ ] Identify vulnerable patterns
- [ ] Understand protection mechanisms
- [ ] Review real-world attack scenarios

### Hands-On Practice

- [ ] Follow step-by-step testing guide
- [ ] Try recommended payloads
- [ ] Capture evidence screenshots
- [ ] Verify protection mechanisms

---

## 🎓 CERTIFICATE OF COMPLETION

After completing all tests and understanding the vulnerabilities, you will have:

✅ Demonstrated understanding of 3 critical web vulnerabilities  
✅ Identified vulnerable code patterns  
✅ Tested security flaws in a controlled environment  
✅ Learned prevention techniques  
✅ Applied Django security best practices

---

**Prepared for:** Sangmo Lama  
**Date:** March 21, 2026  
**Status:** ✅ COMPLETE & READY FOR TESTING

Start with the dashboard at: **http://localhost:8000/security/**
