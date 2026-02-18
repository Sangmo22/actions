# notes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Note
from .forms import NoteForm


# READ - Display all notes
def index(request):
    notes = Note.objects.all().order_by('-id')  # Latest first
    return render(request, 'notes/index.html', {'notes': notes})


# CREATE - Add new note
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.create(form.cleaned_data)
            messages.success(request, 'Data added successfully!')
            return redirect('notes:index')
    else:
        form = NoteForm()

    return render(request, 'notes/add.html', {'form': form})


# UPDATE - Edit note
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            form.update(note, form.cleaned_data)
            messages.success(request, 'Data updated successfully!')
            return redirect('notes:index')
    else:
        form = NoteForm(initial={
            'title': note.title,
            'description': note.description
        })

    return render(request, 'notes/edit.html', {'form': form})


# DELETE - Delete
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.delete()
    messages.success(request, 'Note deleted successfully!')
    return redirect('notes:index')