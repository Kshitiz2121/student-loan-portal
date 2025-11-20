from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class StudentUserManager(BaseUserManager):
    """Custom manager for StudentUser model"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class StudentUser(AbstractUser):
    """Custom User model for students"""
    
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('financier', 'Financier'),
    ]
    
    # Override username to use email
    username = None
    email = models.EmailField(unique=True)
    
    # User type field
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES,
        default='student'
    )
    
    # Student specific fields
    student_id = models.CharField(max_length=20, unique=True, help_text="University Student ID")
    university = models.CharField(max_length=100, help_text="University/College name")
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0.00), MaxValueValidator(10.00)],
        help_text="Grade Point Average (0.00 - 10.00)"
    )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Profile picture
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'student_id', 'university', 'gpa']
    
    # Use custom manager
    objects = StudentUserManager()
    
    class Meta:
        verbose_name = 'Student User'
        verbose_name_plural = 'Student Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.student_id})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_financier(self):
        return self.user_type == 'financier'
    
    @property
    def is_eligible_for_loan(self):
        """Check if student is eligible for loan based on GPA"""
        return self.gpa >= 6.0
    
    @property
    def has_active_loan(self):
        """Check if student has an active loan"""
        from loans.models import LoanApplication
        return LoanApplication.objects.filter(
            student=self,
            status__in=['Pending', 'Approved']
        ).exists()


class FinancierUser(models.Model):
    """Financier profile linked to StudentUser model"""
    
    user = models.OneToOneField(StudentUser, on_delete=models.CASCADE, related_name='financier_profile')
    
    # Financier specific fields
    financier_id = models.CharField(max_length=20, unique=True, help_text="Financier ID")
    company_name = models.CharField(max_length=100, blank=True, null=True, help_text="Company name (if applicable)")
    investment_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Total amount invested in the platform"
    )
    interest_rate = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=Decimal('2.00'),
        help_text="Interest rate earned (2% default)"
    )
    bank_account = models.CharField(max_length=50, blank=True, null=True, help_text="Bank account for interest payments")
    
    class Meta:
        verbose_name = 'Financier Profile'
        verbose_name_plural = 'Financier Profiles'
        ordering = ['-user__created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.financier_id})"
    
    @property
    def total_earned_interest(self):
        """Calculate total interest earned"""
        # This will be calculated based on actual loan disbursements
        return Decimal('0.00')  # Placeholder for now
    
    @property
    def active_investments(self):
        """Get active investment amount"""
        from loans.models import LoanApplication
        active_loans = LoanApplication.objects.filter(status='Approved')
        # For now, return investment amount - in real implementation, track actual disbursements
        return self.investment_amount
