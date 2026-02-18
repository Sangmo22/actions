from django import forms
from .models import Note

class NoteForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        error_messages={'required': "Title is required."}
       )
    description =forms.CharField(
       widget=forms.Textarea(),
       error_messages={'required': "Description is required."})
    
    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) < 10:
            raise forms.ValidationError("Description must be at least 10 characters long.")
        return description

    def create(self,validated_data):
        return Note.objects.create(**validated_data)