# Security Testing Views - Controlled Vulnerability Demonstrations
# ======================================================================
# WARNING: These views are intentionally vulnerable for educational purposes only.
# DO NOT use these patterns in production code.

from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from .models import Note
from .forms import NoteForm


# ============================================================================
# 1. XSS (Cross-Site Scripting) Vulnerability Demonstrations
# ============================================================================

def xss_vulnerable_display(request):
    """
    Demonstrates XSS vulnerability by rendering user input without escaping.
    This view intentionally bypasses Django's auto-escaping to show the danger.
    """
    notes = Note.objects.all().order_by('-id')
    context = {
        'notes': notes,
        'explanation': 'This page renders note content WITHOUT proper escaping. Try injecting scripts!'
    }
    return render(request, 'notes/security/xss_vulnerable.html', context)


def xss_safe_display(request):
    """
    Demonstrates safe XSS prevention using Django's auto-escaping.
    """
    notes = Note.objects.all().order_by('-id')
    context = {
        'notes': notes,
        'explanation': 'This page uses Django auto-escaping (default behavior). Malicious scripts are escaped.'
    }
    return render(request, 'notes/security/xss_safe.html', context)


@require_http_methods(["GET", "POST"])
def add_note_xss_vulnerable(request):
    """
    Vulnerable endpoint that stores and displays unsanitized user input.
    """
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            # Store unsanitized input
            title = form.cleaned_data['title']
            desc = form.cleaned_data['description']
            Note.objects.create(title=title, description=desc)
            messages.success(request, 'Note added successfully! (Vulnerable - no HTML escaping)')
            return redirect('security:xss-vulnerable')
    else:
        form = NoteForm()
    
    return render(request, 'notes/security/add_vulnerable.html', {'form': form})


# ============================================================================
# 2. SQL Injection Vulnerability Demonstrations
# ============================================================================

def sql_injection_demo(request):
    """
    Demonstrates SQL Injection vulnerability using raw SQL.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        
        # VULNERABLE: Using string concatenation in SQL
        sql = f"""
        INSERT INTO notes_note (title, description)
        VALUES ('{title}', '{description}');
        """
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
            messages.success(request, 'Note added (using vulnerable SQL)')
            return redirect('security:sql-demo')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    notes = Note.objects.all().order_by('-id')
    context = {
        'notes': notes,
        'explanation': 'This view is vulnerable to SQL injection. Try injecting SQL code in the fields.',
        'example_payload': "'); DROP TABLE notes_note; --"
    }
    return render(request, 'notes/security/sql_injection_demo.html', context)


def sql_injection_safe(request):
    """
    Demonstrates safe SQL using parameterized queries.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        
        # SAFE: Using parameterized queries
        sql = "INSERT INTO notes_note (title, description) VALUES (%s, %s);"
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, [title, description])
            messages.success(request, 'Note added safely (using parameterized query)')
            return redirect('security:sql-safe')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    notes = Note.objects.all().order_by('-id')
    context = {
        'notes': notes,
        'explanation': 'This view uses parameterized queries. SQL injection attempts are safely handled.',
    }
    return render(request, 'notes/security/sql_injection_safe.html', context)


# ============================================================================
# 3. CSRF (Cross-Site Request Forgery) Vulnerability Demonstrations
# ============================================================================

@require_http_methods(["GET", "POST"])
def csrf_vulnerable_add(request):
    """
    Vulnerable endpoint without CSRF protection (CS token not required).
    """
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        
        if title and len(description) >= 10:
            Note.objects.create(title=title, description=description)
            messages.success(request, 'Note added successfully (CSRF Vulnerable)')
            return redirect('security:csrf-vulnerable')
        else:
            messages.error(request, 'Invalid input')
    
    notes = Note.objects.all().order_by('-id')
    csrf_token = get_token(request)
    context = {
        'notes': notes,
        'csrf_token': csrf_token,
        'explanation': 'This endpoint does NOT require CSRF token validation. It is vulnerable to CSRF attacks.',
        'attack_example': 'A malicious site can craft a form that auto-submits to this endpoint.'
    }
    return render(request, 'notes/security/csrf_vulnerable.html', context)


@require_http_methods(["GET", "POST"])
def csrf_protected_add(request):
    """
    Protected endpoint with proper CSRF token validation.
    """
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.create(form.cleaned_data)
            messages.success(request, 'Note added safely (CSRF Protected)')
            return redirect('security:csrf-protected')
        else:
            messages.error(request, 'Form validation failed')
    else:
        form = NoteForm()
    
    context = {
        'form': form,
        'explanation': 'This endpoint uses {% csrf_token %} in the form. CSRF protection is enabled.',
    }
    return render(request, 'notes/security/csrf_protected.html', context)


# ============================================================================
# Security Testing Dashboard
# ============================================================================

def security_test_dashboard(request):
    """
    Main dashboard showing all security vulnerability demonstrations.
    """
    tests = [
        {
            'name': 'XSS (Cross-Site Scripting)',
            'vulnerable_url': 'security:xss-vulnerable',
            'safe_url': 'security:xss-safe',
            'description': 'Test how the application handles JavaScript code in user input.',
            'attack_vector': '<img src=x onerror="alert(\'XSS\')">'
        },
        {
            'name': 'SQL Injection',
            'vulnerable_url': 'security:sql-demo',
            'safe_url': 'security:sql-safe',
            'description': 'Test how the application handles SQL code in user input.',
            'attack_vector': "'); DELETE FROM notes_note; --"
        },
        {
            'name': 'CSRF (Cross-Site Request Forgery)',
            'vulnerable_url': 'security:csrf-vulnerable',
            'safe_url': 'security:csrf-protected',
            'description': 'Test if the application validates request origins.',
            'attack_vector': 'Auto-submitted form from malicious site'
        },
    ]
    
    context = {
        'tests': tests,
        'note_count': Note.objects.count(),
        'explanation': 'Security Vulnerability Testing Dashboard - Educational Purpose Only'
    }
    return render(request, 'notes/security/dashboard.html', context)
