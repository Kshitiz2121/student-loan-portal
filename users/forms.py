from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import StudentUser, FinancierUser


class StudentUserCreationForm(UserCreationForm):
    """Form for student registration"""
    
    # University choices (same as in loans/forms.py)
    TOP_INDIAN_UNIVERSITIES = [
        'Indian Institute of Technology Bombay',
        'Indian Institute of Technology Delhi',
        'Indian Institute of Technology Madras',
        'Indian Institute of Technology Kanpur',
        'Indian Institute of Technology Kharagpur',
        'Indian Institute of Technology Roorkee',
        'Indian Institute of Science Bangalore',
        'Indian Institute of Technology Guwahati',
        'University of Delhi',
        'Jawaharlal Nehru University',
        'University of Mumbai',
        'Savitribai Phule Pune University',
        'University of Calcutta',
        'University of Madras',
        'Banaras Hindu University',
        'Birla Institute of Technology and Science Pilani',
        'National Institute of Technology Trichy',
        'National Institute of Technology Warangal',
        'Vellore Institute of Technology',
        'Anna University',
    ]
    
    university = forms.ChoiceField(
        choices=[(u, u) for u in TOP_INDIAN_UNIVERSITIES],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = StudentUser
        fields = [
            'email', 'first_name', 'last_name', 'password1', 'password2',
            'student_id', 'university', 'gpa', 'phone_number', 'address', 'date_of_birth'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00',
                'max': '10.00'
            }),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user type to student
        self.fields['user_type'] = forms.CharField(
            initial='student',
            widget=forms.HiddenInput()
        )
    
    def clean_gpa(self):
        gpa = self.cleaned_data.get('gpa')
        if gpa < 0.00 or gpa > 10.00:
            raise forms.ValidationError('GPA must be between 0.00 and 10.00.')
        return gpa
    
    def clean_university(self):
        university = self.cleaned_data.get('university')
        if university not in [u[0] for u in self.fields['university'].choices]:
            raise forms.ValidationError('Please select a valid university from the list.')
        return university


class FinancierUserCreationForm(UserCreationForm):
    """Form for financier registration"""
    
    class Meta:
        model = StudentUser
        fields = [
            'email', 'first_name', 'last_name', 'password1', 'password2',
            'phone_number', 'address', 'date_of_birth'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set user type to financier
        self.fields['user_type'] = forms.CharField(
            initial='financier',
            widget=forms.HiddenInput()
        )
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'financier'
        if commit:
            user.save()
        return user


class FinancierProfileForm(forms.ModelForm):
    """Form for updating financier profile"""
    
    class Meta:
        model = FinancierUser
        fields = ['financier_id', 'company_name', 'investment_amount', 'bank_account']
        widgets = {
            'financier_id': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'investment_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.00'
            }),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_investment_amount(self):
        amount = self.cleaned_data.get('investment_amount')
        if amount < 0:
            raise forms.ValidationError('Investment amount cannot be negative.')
        return amount


class StudentProfileForm(forms.ModelForm):
    """Form for updating student profile"""
    
    class Meta:
        model = StudentUser
        fields = ['phone_number', 'address', 'date_of_birth', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
