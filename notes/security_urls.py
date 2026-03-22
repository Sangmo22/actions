# Security testing URLs
from django.urls import path
from . import security_test_views

app_name = 'security'

urlpatterns = [
    # Dashboard
    path('', security_test_views.security_test_dashboard, name='dashboard'),
    
    # XSS Vulnerabilities
    path('xss/vulnerable/', security_test_views.xss_vulnerable_display, name='xss-vulnerable'),
    path('xss/safe/', security_test_views.xss_safe_display, name='xss-safe'),
    path('xss/add-vulnerable/', security_test_views.add_note_xss_vulnerable, name='xss-add-vulnerable'),
    
    # SQL Injection Vulnerabilities
    path('sql-injection/vulnerable/', security_test_views.sql_injection_demo, name='sql-demo'),
    path('sql-injection/safe/', security_test_views.sql_injection_safe, name='sql-safe'),
    
    # CSRF Vulnerabilities
    path('csrf/vulnerable/', security_test_views.csrf_vulnerable_add, name='csrf-vulnerable'),
    path('csrf/protected/', security_test_views.csrf_protected_add, name='csrf-protected'),
]
