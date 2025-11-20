from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from .models import LoanApplication

# Comprehensive list of Indian universities and colleges
TOP_INDIAN_UNIVERSITIES = [
    # Indian Institutes of Technology (IITs)
    'Indian Institute of Technology Bombay',
    'Indian Institute of Technology Delhi',
    'Indian Institute of Technology Madras',
    'Indian Institute of Technology Kanpur',
    'Indian Institute of Technology Kharagpur',
    'Indian Institute of Technology Roorkee',
    'Indian Institute of Technology Guwahati',
    'Indian Institute of Technology Hyderabad',
    'Indian Institute of Technology Indore',
    'Indian Institute of Technology Jodhpur',
    'Indian Institute of Technology Mandi',
    'Indian Institute of Technology Patna',
    'Indian Institute of Technology Ropar',
    'Indian Institute of Technology Bhubaneswar',
    'Indian Institute of Technology Gandhinagar',
    'Indian Institute of Technology Goa',
    'Indian Institute of Technology Jammu',
    'Indian Institute of Technology Dharwad',
    'Indian Institute of Technology Tirupati',
    'Indian Institute of Technology Palakkad',
    'Indian Institute of Technology Bhilai',
    'Indian Institute of Technology Dhanbad',
    
    # Indian Institute of Science
    'Indian Institute of Science Bangalore',
    
    # National Institutes of Technology (NITs)
    'National Institute of Technology Trichy',
    'National Institute of Technology Warangal',
    'National Institute of Technology Surathkal',
    'National Institute of Technology Calicut',
    'National Institute of Technology Durgapur',
    'National Institute of Technology Allahabad',
    'National Institute of Technology Bhopal',
    'National Institute of Technology Jalandhar',
    'National Institute of Technology Jaipur',
    'National Institute of Technology Kurukshetra',
    'National Institute of Technology Rourkela',
    'National Institute of Technology Silchar',
    'National Institute of Technology Srinagar',
    'National Institute of Technology Hamirpur',
    'National Institute of Technology Jamshedpur',
    'National Institute of Technology Patna',
    'National Institute of Technology Raipur',
    'National Institute of Technology Agartala',
    'National Institute of Technology Arunachal Pradesh',
    'National Institute of Technology Delhi',
    'National Institute of Technology Goa',
    'National Institute of Technology Manipur',
    'National Institute of Technology Meghalaya',
    'National Institute of Technology Mizoram',
    'National Institute of Technology Nagaland',
    'National Institute of Technology Puducherry',
    'National Institute of Technology Sikkim',
    'National Institute of Technology Uttarakhand',
    
    # Central Universities
    'University of Delhi',
    'Jawaharlal Nehru University',
    'Jamia Millia Islamia',
    'Aligarh Muslim University',
    'Banaras Hindu University',
    'University of Allahabad',
    'Central University of Punjab',
    'Central University of Rajasthan',
    'Central University of Gujarat',
    'Central University of Haryana',
    'Central University of Himachal Pradesh',
    'Central University of Jammu',
    'Central University of Jharkhand',
    'Central University of Karnataka',
    'Central University of Kerala',
    'Central University of Odisha',
    'Central University of South Bihar',
    'Central University of Tamil Nadu',
    'Central University of Telangana',
    'Central University of Uttarakhand',
    'Central University of West Bengal',
    'Central University of Andhra Pradesh',
    'Central University of Kashmir',
    'Central University of Ladakh',
    'Central University of Manipur',
    'Central University of Mizoram',
    'Central University of Nagaland',
    'Central University of Sikkim',
    'Central University of Tripura',
    
    # State Universities - Major States
    'University of Mumbai',
    'Savitribai Phule Pune University',
    'University of Calcutta',
    'University of Madras',
    'Anna University',
    'Osmania University',
    'Andhra University',
    'Karnataka University',
    'Mysore University',
    'Bangalore University',
    'Gujarat University',
    'Maharaja Sayajirao University of Baroda',
    'University of Rajasthan',
    'University of Lucknow',
    'Chaudhary Charan Singh University',
    'Dr. A.P.J. Abdul Kalam Technical University',
    'Guru Gobind Singh Indraprastha University',
    'Jamia Hamdard',
    'University of Kerala',
    'Calicut University',
    'Kannur University',
    'Mahatma Gandhi University',
    'University of Burdwan',
    'Jadavpur University',
    'Rabindra Bharati University',
    'Vidyasagar University',
    'North Bengal University',
    'University of Kalyani',
    'Bidhan Chandra Krishi Viswavidyalaya',
    'University of Gour Banga',
    
    # Private Universities
    'Birla Institute of Technology and Science Pilani',
    'Vellore Institute of Technology',
    'Manipal Academy of Higher Education',
    'Amity University',
    'SRM Institute of Science and Technology',
    'Lovely Professional University',
    'Symbiosis International University',
    'Christ University',
    'Jain University',
    'NMIMS University',
    'Ashoka University',
    'Azim Premji University',
    'FLAME University',
    'Krea University',
    'OP Jindal Global University',
    'Shiv Nadar University',
    'Bennett University',
    'UPES University',
    'Chandigarh University',
    'Galgotias University',
    'KIIT University',
    'Siksha O Anusandhan University',
    'Amrita Vishwa Vidyapeetham',
    'Karunya Institute of Technology and Sciences',
    'SASTRA University',
    'Thapar Institute of Engineering and Technology',
    'Bharath Institute of Higher Education and Research',
    'Vel Tech Rangarajan Dr. Sagunthala R&D Institute',
    'Hindustan Institute of Technology and Science',
    'Kalasalingam Academy of Research and Education',
    
    # Deemed Universities
    'Indian Institute of Science Education and Research',
    'Tata Institute of Fundamental Research',
    'Indian Statistical Institute',
    'All India Institute of Medical Sciences',
    'Post Graduate Institute of Medical Education and Research',
    'Sanjay Gandhi Postgraduate Institute of Medical Sciences',
    'Jawaharlal Institute of Postgraduate Medical Education and Research',
    'Sree Chitra Tirunal Institute for Medical Sciences and Technology',
    'National Institute of Mental Health and Neuro Sciences',
    'Institute of Chemical Technology',
    'Indian Institute of Space Science and Technology',
    'National Institute of Design',
    'Film and Television Institute of India',
    'National School of Drama',
    'Indian Agricultural Research Institute',
    'Central Institute of Fisheries Education',
    'National Dairy Research Institute',
    'Indian Veterinary Research Institute',
    'Central Institute of Medicinal and Aromatic Plants',
    'Central Institute of Plastics Engineering and Technology',
    
    # Specialized Institutes
    'Indian Institute of Management Ahmedabad',
    'Indian Institute of Management Bangalore',
    'Indian Institute of Management Calcutta',
    'Indian Institute of Management Lucknow',
    'Indian Institute of Management Kozhikode',
    'Indian Institute of Management Indore',
    'Indian Institute of Management Shillong',
    'Indian Institute of Management Rohtak',
    'Indian Institute of Management Ranchi',
    'Indian Institute of Management Raipur',
    'Indian Institute of Management Tiruchirappalli',
    'Indian Institute of Management Udaipur',
    'Indian Institute of Management Kashipur',
    'Indian Institute of Management Amritsar',
    'Indian Institute of Management Bodh Gaya',
    'Indian Institute of Management Nagpur',
    'Indian Institute of Management Sambalpur',
    'Indian Institute of Management Sirmaur',
    'Indian Institute of Management Visakhapatnam',
    'Indian Institute of Management Jammu',
    
    # Medical Colleges and Universities
    'All India Institute of Medical Sciences Delhi',
    'All India Institute of Medical Sciences Bhopal',
    'All India Institute of Medical Sciences Bhubaneswar',
    'All India Institute of Medical Sciences Jodhpur',
    'All India Institute of Medical Sciences Patna',
    'All India Institute of Medical Sciences Raipur',
    'All India Institute of Medical Sciences Rishikesh',
    'All India Institute of Medical Sciences Nagpur',
    'All India Institute of Medical Sciences Mangalagiri',
    'All India Institute of Medical Sciences Gorakhpur',
    'All India Institute of Medical Sciences Rajkot',
    'All India Institute of Medical Sciences Kalyani',
    'All India Institute of Medical Sciences Deoghar',
    'All India Institute of Medical Sciences Bibinagar',
    'All India Institute of Medical Sciences Guwahati',
    'All India Institute of Medical Sciences Bathinda',
    'All India Institute of Medical Sciences Bilaspur',
    'All India Institute of Medical Sciences Madurai',
    'All India Institute of Medical Sciences Vijayawada',
    'All India Institute of Medical Sciences Raebareli',
    'All India Institute of Medical Sciences Darbhanga',
    
    # Agricultural Universities
    'Indian Agricultural Research Institute',
    'National Dairy Research Institute',
    'Central Institute of Fisheries Education',
    'Indian Veterinary Research Institute',
    'Central Institute of Medicinal and Aromatic Plants',
    'Central Institute of Plastics Engineering and Technology',
    'Central Institute of Post-Harvest Engineering and Technology',
    'Central Institute of Agricultural Engineering',
    'Central Institute of Freshwater Aquaculture',
    'Central Institute of Brackishwater Aquaculture',
    'Central Institute of Fisheries Nautical and Engineering Training',
    'Central Institute of Fisheries Technology',
    'Central Institute of Sub-tropical Horticulture',
    'Central Institute of Temperate Horticulture',
    'Central Institute of Arid Horticulture',
    
    # Regional Universities
    'University of Kashmir',
    'University of Jammu',
    'Himachal Pradesh University',
    'Punjab University',
    'Guru Nanak Dev University',
    'Punjabi University',
    'Panjab University',
    'Guru Gobind Singh Indraprastha University',
    'Chaudhary Charan Singh University',
    'Dr. A.P.J. Abdul Kalam Technical University',
    'Bundelkhand University',
    'Dr. Ram Manohar Lohia Avadh University',
    'Dr. Shakuntala Misra National Rehabilitation University',
    'Dr. Bhimrao Ambedkar University',
    'Dr. Ram Manohar Lohia National Law University',
    
    # Other Notable Universities
    'Tata Institute of Social Sciences',
    'Indian Institute of Foreign Trade',
    'Indian Institute of Mass Communication',
    'Indian Institute of Tourism and Travel Management',
    'Indian Institute of Forest Management',
    'Indian Institute of Rural Management',
    'Indian Institute of Public Administration',
    'Indian Institute of Corporate Affairs',
    'Indian Institute of Banking and Finance',
    'Indian Institute of Insurance',
    'Indian Institute of Actuaries',
    'Indian Institute of Chartered Accountants',
    'Indian Institute of Company Secretaries',
    'Indian Institute of Cost and Works Accountants',
]


class LoanApplicationForm(forms.ModelForm):
    """Form for students to apply for loans"""
    
    amount = forms.IntegerField(
        validators=[
            MinValueValidator(500, message="Minimum loan amount is 500 INR"),
            MaxValueValidator(100000, message="Maximum loan amount is 100,000 INR")
        ],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter loan amount (500-100000 INR)',
            'min': '500',
            'max': '100000'
        })
    )

    university = forms.ChoiceField(
        choices=[(u, u) for u in TOP_INDIAN_UNIVERSITIES],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Please provide a detailed reason for your loan application...',
            'rows': 4
        })
    )
    
    repayment_due_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat()
        })
    )
    
    class Meta:
        model = LoanApplication
        fields = ['amount', 'reason', 'repayment_due_date']
    
    def __init__(self, *args, **kwargs):
        """Accept optional 'user' kwarg and store it for validation."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Preselect user's current university if present
        if self.user and getattr(self.user, 'university', None):
            if self.user.university in TOP_INDIAN_UNIVERSITIES:
                self.fields['university'].initial = self.user.university
    
    def clean_amount(self):
        """Validate loan amount"""
        amount = self.cleaned_data.get('amount')
        if amount < 500 or amount > 100000:
            raise forms.ValidationError('Loan amount must be between 500 and 100,000 INR.')
        return amount
    
    def clean_repayment_due_date(self):
        """Validate repayment due date"""
        repayment_due_date = self.cleaned_data.get('repayment_due_date')
        if repayment_due_date:
            if repayment_due_date <= timezone.now().date():
                raise forms.ValidationError('Repayment due date must be in the future.')
            
            # Ensure due date is not more than 1 year from now
            max_date = timezone.now().date() + timedelta(days=365)
            if repayment_due_date > max_date:
                raise forms.ValidationError('Repayment due date cannot be more than 1 year from now.')
        
        return repayment_due_date
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Ensure selected university is from the approved list
        selected_university = cleaned_data.get('university')
        if selected_university not in TOP_INDIAN_UNIVERSITIES:
            raise forms.ValidationError('Selected university is not eligible for this loan program.')

        # Check if student is eligible for loan
        if hasattr(self, 'user') and self.user:
            if not self.user.is_eligible_for_loan:
                raise forms.ValidationError(
                    'You are not eligible for a loan. Your GPA must be 6.0 or higher.'
                )
            
            if self.user.has_active_loan:
                raise forms.ValidationError(
                    'You already have an active loan. Please complete repayment before applying for a new one.'
                )
        
        return cleaned_data


class LoanApplicationUpdateForm(forms.ModelForm):
    """Form for updating loan applications (admin use)"""
    
    amount = forms.IntegerField(
        validators=[
            MinValueValidator(500, message="Minimum loan amount is 500 INR"),
            MaxValueValidator(100000, message="Maximum loan amount is 100,000 INR")
        ],
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )
    
    status = forms.ChoiceField(
        choices=LoanApplication.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add admin notes here...'
        })
    )
    
    repayment_due_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    interest_rate = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0.00',
            'max': '20.00'
        })
    )
    
    class Meta:
        model = LoanApplication
        fields = [
            'amount', 'reason', 'status', 'admin_notes', 
            'repayment_due_date', 'interest_rate'
        ]
    
    def clean_amount(self):
        """Validate loan amount"""
        amount = self.cleaned_data.get('amount')
        if amount < 500 or amount > 5000:
            raise forms.ValidationError('Loan amount must be between 500 and 5000 INR.')
        return amount
    
    def clean_interest_rate(self):
        """Validate interest rate"""
        interest_rate = self.cleaned_data.get('interest_rate')
        if interest_rate < 0.00 or interest_rate > 20.00:
            raise forms.ValidationError('Interest rate must be between 0.00 and 20.00%.')
        return interest_rate
