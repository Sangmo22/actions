# notes/forms.py
from django import forms
from .models import Note


class NoteForm(forms.Form):
    title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'id': 'title'}),
        error_messages={'required': 'Title is required'}
    )
    description = forms.CharField(
        # required=False,
        widget=forms.Textarea(attrs={'id': 'description'}),
        error_messages={'required': 'Description is required'}
    )

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) < 10:
            raise forms.ValidationError('Description must be at least 10 characters long.')
        return description

    def create(self, validated_data):
        return Note.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance