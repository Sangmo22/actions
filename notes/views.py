from django.db import connection
from django.shortcuts import render ,redirect, get_object_or_404
from django.contrib import messages
from .models import Note
from .forms import NoteForm

def index(request):
    notes=Note.objects.all().order_by('-id')
    return render(request,"notes/index.html",{
        'notes':notes
    })

def add_note(request):
    if request.method == 'POST':
        form=NoteForm(request.POST)
        if form.is_valid():
            form.create(form.cleaned_data)
            messages.success(request, 'Data added succesfully')
            return redirect('notes:index')
    else:
        form=NoteForm()
    
    return render(request,"notes/add.html",{
        "form":form
    })

def add_note_sql_injection(request):
    if request.method == 'POST':
        form=NoteForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            desc = form.cleaned_data['description']
            
            sql = f"""
            INSERT INTO notes_note (title, description)
            VALUES ('{title}', '{desc}');
            """

            with connection.cursor() as cursor:
                cursor.execute(sql)
                
                
            messages.success(request, 'Data added succesfully')
            return redirect('notes:index')
    else:
        form=NoteForm()
    
    return render(request,"notes/add.html",{
        "form":form
    })

def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note.title = form.cleaned_data['title']
            note.description = form.cleaned_data['description']
            note.save()
            messages.success(request, 'Note updated successfully')
            return redirect('notes:index')
    else:
        form = NoteForm(initial={'title': note.title, 'description': note.description})
    
    return render(request, "notes/edit.html", {
        "form": form,
        "note": note
    })

def delete_note(request,note_id):
    note=get_object_or_404(Note, id=note_id)
    note.delete()
    messages.success(request,"Note deleted successfully!")
    return redirect('notes:index')