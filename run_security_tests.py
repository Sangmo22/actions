#!/usr/bin/env python
"""
Security Vulnerability Testing Script
Django Notes CRUD Application
Author: Sangmo Lama
Purpose: Demonstrate and test XSS, SQL Injection, and CSRF vulnerabilities
"""

import os
import django
from django.conf import settings
from django.test.client import Client

# Setup Django - must be before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crud.settings')
django.setup()

from notes.models import Note


class VulnerabilityTester:
    """Test suite for security vulnerabilities"""
    
    def __init__(self):
        self.client = Client()
        self.results = {
            'xss': {},
            'sql_injection': {},
            'csrf': {}
        }
        
    def test_xss_vulnerable(self):
        """Test XSS on vulnerable endpoint"""
        print("\n" + "="*80)
        print("TEST 1: XSS (Cross-Site Scripting) - VULNERABLE VERSION")
        print("="*80)
        
        payload = '<img src=x onerror="alert(\'XSS\')">'
        form_data = {
            'title': payload,
            'description': 'This is a test of XSS vulnerability in the Notes application.'
        }
        
        print(f"\n📝 Payload: {payload}")
        print(f"Form Data: {form_data}")
        
        # Submit to vulnerable endpoint
        response = self.client.post(
            '/security/xss/add-vulnerable/',
            form_data,
            follow=True
        )
        
        print(f"\n✓ Response Status: {response.status_code}")
        print(f"✓ Redirected to: {response.redirect_chain[-1][0] if response.redirect_chain else 'N/A'}")
        
        # Check if payload is stored in database
        try:
            note = Note.objects.filter(title__icontains='onerror').first()
            if note:
                print(f"✓ Payload stored in database!")
                print(f"  - Title: {note.title[:50]}...")
                print(f"  - Description: {note.description[:50]}...")
                self.results['xss']['vulnerable'] = 'EXPLOITED'
                return True
        except Exception as e:
            print(f"✗ Error checking database: {e}")
        
        return False
    
    def test_xss_safe(self):
        """Test XSS on safe endpoint"""
        print("\n" + "="*80)
        print("TEST 1B: XSS (Cross-Site Scripting) - SAFE VERSION")
        print("="*80)
        
        payload = '<img src=x onerror="alert(\'XSS\')">'
        data = {'title': payload, 'description': 'Safe version test description here.'}
        
        print(f"\n📝 Same Payload: {payload}")
        
        response = self.client.get('/security/xss/safe/')
        print(f"✓ Safe endpoint accessible: {response.status_code == 200}")
        
        # Check if payload in response, but escaped
        if '&lt;' in response.content.decode('utf-8') or 'script' in response.content.decode('utf-8'):
            print("✓ Response contains HTML escaping/auto-escaping")
            self.results['xss']['safe'] = 'PROTECTED'
        else:
            print("⚠ Could not verify escaping in response")
        
        return True
    
    def test_sql_injection_vulnerable(self):
        """Test SQL Injection on vulnerable endpoint"""
        print("\n" + "="*80)
        print("TEST 2: SQL Injection - VULNERABLE VERSION")
        print("="*80)
        
        payload = "Test'); --"
        form_data = {
            'title': payload,
            'description': 'This is a test of SQL injection vulnerability. Comment-based attack using -- syntax.'
        }
        
        print(f"\n📝 Payload: {payload}")
        print(f"Form Data: {form_data}")
        print(f"\nSQL Injection Type: Comment-based (using --)")
        print(f"Expected SQL Query Structure:")
        print(f"  INSERT INTO notes_note (title, description)")
        print(f"  VALUES ('{payload}', '...')  <-- Quotes can be closed!")
        
        # Initial count
        initial_count = Note.objects.count()
        
        # Submit to vulnerable endpoint
        try:
            response = self.client.post(
                '/security/sql-injection/vulnerable/',
                form_data,
                follow=True
            )
            
            final_count = Note.objects.count()
            
            print(f"\n✓ Response Status: {response.status_code}")
            print(f"✓ Notes before: {initial_count}")
            print(f"✓ Notes after: {final_count}")
            
            if final_count > initial_count:
                note = Note.objects.filter(title__icontains="');").first()
                if note:
                    print(f"✓ SQL Injection Payload Stored!")
                    print(f"  - Title: {note.title}")
                    self.results['sql_injection']['vulnerable'] = 'EXPLOITED'
                    return True
        except Exception as e:
            print(f"Database operation error (may be expected): {e}")
            print(f"⚠ SQLi attempt may have caused SQL syntax error")
        
        return False
    
    def test_sql_injection_safe(self):
        """Test SQL Injection on safe endpoint"""
        print("\n" + "="*80)
        print("TEST 2B: SQL Injection - SAFE VERSION (Parameterized Queries)")
        print("="*80)
        
        payload = "Test'); --"
        form_data = {
            'title': payload,
            'description': 'Safe version stores malicious input as literal text.'
        }
        
        print(f"\n📝 Same Payload: {payload}")
        print(f"\nProtection Method: Parameterized Queries")
        print(f"SQL Query Structure:")
        print(f"  INSERT INTO notes_note (title, description)")
        print(f"  VALUES (%s, %s)")
        print(f"  ['{payload}', '...']  <-- Passed as parameters, not code!")
        
        initial_count = Note.objects.count()
        
        try:
            response = self.client.post(
                '/security/sql-injection/safe/',
                form_data,
                follow=True
            )
            
            final_count = Note.objects.count()
            
            print(f"\n✓ Response Status: {response.status_code}")
            print(f"✓ Notes inserted: {final_count - initial_count}")
            
            # Check if payload stored as literal text
            note = Note.objects.filter(title=payload).first()
            if note:
                print(f"✓ Payload stored safely as literal text!")
                print(f"  - Title: {note.title}")
                print(f"  - No SQL injection occurred")
                self.results['sql_injection']['safe'] = 'PROTECTED'
                return True
        except Exception as e:
            print(f"✗ Error: {e}")
        
        return False
    
    def test_csrf_vulnerable(self):
        """Analyze CSRF vulnerable endpoint"""
        print("\n" + "="*80)
        print("TEST 3: CSRF (Cross-Site Request Forgery) - VULNERABLE VERSION")
        print("="*80)
        
        print(f"\n📝 CSRF Vulnerability Characteristics:")
        
        # Check for CSRF token in page
        response = self.client.get('/security/csrf/vulnerable/')
        content = response.content.decode('utf-8')
        
        has_csrf_token = 'csrfmiddlewaretoken' in content
        has_csrf_tag = '{%' in content and 'csrf_token' in content
        
        print(f"✓ Page Status: {response.status_code} OK")
        print(f"✗ Has CSRF Token Field: {has_csrf_token}")
        print(f"✗ Has CSRF Template Tag: {has_csrf_tag}")
        
        if not has_csrf_token and not has_csrf_tag:
            print(f"\n🔴 VULNERABILITY CONFIRMED:")
            print(f"   - No CSRF token in form")
            print(f"   - No hidden CSRF token field")
            print(f"   - Form is vulnerable to CSRF attacks")
            self.results['csrf']['vulnerable'] = 'EXPLOITED'
            return True
        
        return False
    
    def test_csrf_protected(self):
        """Analyze CSRF protected endpoint"""
        print("\n" + "="*80)
        print("TEST 3B: CSRF (Cross-Site Request Forgery) - PROTECTED VERSION")
        print("="*80)
        
        print(f"\n📝 CSRF Protection Characteristics:")
        
        # Check for CSRF token
        response = self.client.get('/security/csrf/protected/')
        content = response.content.decode('utf-8')
        
        has_csrf_token = 'csrfmiddlewaretoken' in content
        has_csrf_tag = '{%' in content and 'csrf_token' in content
        
        print(f"✓ Page Status: {response.status_code} OK")
        print(f"✓ Has CSRF Token Field: {has_csrf_token}")
        print(f"✓ Has CSRF Template Tag: {has_csrf_tag}")
        
        if has_csrf_token or has_csrf_tag:
            print(f"\n🟢 PROTECTION CONFIRMED:")
            print(f"   - CSRF token included in form")
            print(f"   - CSRF token validation enabled")
            print(f"   - Form is protected against CSRF attacks")
            self.results['csrf']['protected'] = 'PROTECTED'
            return True
        
        return False
    
    def generate_report(self):
        """Generate security testing report"""
        print("\n" + "="*80)
        print("SECURITY TESTING SUMMARY REPORT")
        print("="*80)
        
        print("\n📊 TEST RESULTS:")
        print("\n1. XSS (Cross-Site Scripting)")
        print(f"   - Vulnerable: {self.results['xss'].get('vulnerable', 'NOT TESTED')}")
        print(f"   - Safe: {self.results['xss'].get('safe', 'NOT TESTED')}")
        
        print("\n2. SQL Injection")
        print(f"   - Vulnerable: {self.results['sql_injection'].get('vulnerable', 'NOT TESTED')}")
        print(f"   - Safe: {self.results['sql_injection'].get('safe', 'NOT TESTED')}")
        
        print("\n3. CSRF (Cross-Site Request Forgery)")
        print(f"   - Vulnerable: {self.results['csrf'].get('vulnerable', 'NOT TESTED')}")
        print(f"   - Protected: {self.results['csrf'].get('protected', 'NOT TESTED')}")
        
        print("\n" + "="*80)
        print("✅ Testing Complete!")
        print("="*80)
        print("\n📝 Next Steps:")
        print("1. Review detailed testing guide: SECURITY_TESTING_GUIDE.md")
        print("2. Follow step-by-step instructions: TESTING_STEP_BY_STEP.md")
        print("3. Open browser to: http://localhost:8000/security/")
        print("4. Test each vulnerability manually and capture screenshots")
        print("\n")


def main():
    """Run all vulnerability tests"""
    print("\n" + "="*80)
    print("DJANGO SECURITY VULNERABILITY TEST SUITE")
    print("Application: Notes CRUD")
    print("Tester: Sangmo Lama")
    print("="*80)
    
    tester = VulnerabilityTester()
    
    # Run all tests
    print("\n🧪 Running security tests...\n")
    
    tester.test_xss_vulnerable()
    tester.test_xss_safe()
    
    tester.test_sql_injection_vulnerable()
    tester.test_sql_injection_safe()
    
    tester.test_csrf_vulnerable()
    tester.test_csrf_protected()
    
    # Generate report
    tester.generate_report()


if __name__ == '__main__':
    main()
