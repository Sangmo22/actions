import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crud.settings')
django.setup()

from notes.models import Note

# Create sample notes
Note.objects.create(title="First Note", description="This is my first note with enough characters")
Note.objects.create(title="Django Tutorial", description="Learning Django CRUD operations with forms and validation")
Note.objects.create(title="Shopping List", description="Buy groceries: milk, eggs, bread, and vegetables")

# Display all notes
print("\n=== All Notes ===")
for note in Note.objects.all():
    print(f"ID: {note.id}, Title: {note.title}, Description: {note.description}")

print("\nNotes created successfully!")
