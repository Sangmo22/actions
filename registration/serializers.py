from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from .models import Registration
import re


class RegistrationSerializer(serializers.Serializer):
    """Registration serializer with comprehensive validation"""

    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(
        max_length=100,
        error_messages={'required': 'Name is required', 'blank': 'Name is required'}
    )
    gender = serializers.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        error_messages={'required': 'Gender is required'}
    )
    hobbies = serializers.ListField(
        child=serializers.CharField(),
        error_messages={'required': 'Hobbies is required'}
    )
    appointment = serializers.DateTimeField(
        error_messages={'required': 'Appointment date & time is required'}
    )
    country = serializers.ChoiceField(
        choices=[('Nepal', 'Nepal'), ('India', 'India'), ('USA', 'USA')],
        error_messages={'required': 'Country is required'}
    )
    email = serializers.EmailField(
        error_messages={'required': 'Email is required', 'invalid': 'Enter a valid email address'}
    )
    phone = serializers.CharField(
        max_length=15,
        error_messages={'required': 'Phone number is required', 'blank': 'Phone number is required'}
    )
    resume = serializers.FileField(
        error_messages={'required': 'Resume file is required'}
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={'required': 'Password is required', 'blank': 'Password is required'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        error_messages={'required': 'Confirm Password is required'}
    )
    created_at = serializers.DateTimeField(read_only=True)

    def validate_appointment(self, value):
        """Validate appointment is not in the past"""
        now = timezone.now()
        if value < now:
            raise serializers.ValidationError(
                'Appointment date & time cannot be in the past'
            )
        return value

    def validate_phone(self, value):
        """Validate phone number format (Nepal format)"""
        phone_regex = r'^(?:9\d{9}|01\d{7})$'
        if not re.match(phone_regex, value):
            raise serializers.ValidationError(
                'Please enter a valid phone number (9xxxxxxxxx or 01xxxxxxx)'
            )
        return value

    def validate_resume(self, value):
        """Validate resume file type and size"""
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx']
        extension = value.name.split('.')[-1].lower()
        if extension not in allowed_extensions:
            raise serializers.ValidationError(
                f'Unsupported file format. Allowed: {", ".join(allowed_extensions)}'
            )

        max_size = 2 * 1024 * 1024  # 2MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                'File size should be less than 2MB'
            )
        return value

    def validate_password(self, value):
        """Validate password strength"""
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d\s]).{8,}$'
        if not re.match(password_regex, value):
            raise serializers.ValidationError(
                'Password must be at least 8 characters long and include '
                'one uppercase letter, one lowercase letter, one number, '
                'and one symbol'
            )
        return value

    def validate_hobbies(self, value):
        """Validate at least one hobby is selected"""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                'Please select at least one hobby'
            )
        return value

    def validate(self, data):
        """Validate confirm password matches password"""
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Confirm Password did not match Password'
            })

        return data

    def create(self, validated_data):
        """Create registration with hashed password"""
        validated_data.pop('confirm_password')
        validated_data['password'] = make_password(validated_data['password'])
        return Registration.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update registration instance"""
        validated_data.pop('confirm_password', None)
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance