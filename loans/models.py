from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class LoanApplication(models.Model):
    """Model for student loan applications"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(
        'users.StudentUser', 
        on_delete=models.CASCADE, 
        related_name='loan_applications'
    )
    
    amount = models.IntegerField(
        validators=[
            MinValueValidator(500, message="Minimum loan amount is 500 INR"),
            MaxValueValidator(100000, message="Maximum loan amount is 100,000 INR")
        ],
        help_text="Loan amount in INR (500-100,000)"
    )
    
    reason = models.TextField(help_text="Reason for loan application")
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    
    admin_notes = models.TextField(blank=True, null=True, help_text="Admin notes for approval/rejection")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Repayment details
    repayment_due_date = models.DateField(help_text="Due date for loan repayment")
    interest_rate = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=10.00,
        help_text="Monthly simple interest rate (%) (used for display; calculation fixed at 10%)"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Loan Application'
        verbose_name_plural = 'Loan Applications'
    
    def __str__(self):
        return f"Loan #{self.id} - {self.student.get_full_name()} - {self.amount} INR"
    
    def save(self, *args, **kwargs):
        # Auto-approve if GPA >= 6.0 and no active loans
        if not self.pk and self.student.is_eligible_for_loan and not self.student.has_active_loan:
            self.status = 'Approved'
            self.admin_notes = "Auto-approved: GPA >= 6.0 and no active loans"
        
        # Set repayment due date to 12 months from approval if not set
        if self.status == 'Approved' and not self.repayment_due_date:
            self.repayment_due_date = timezone.now().date() + timedelta(days=365)
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        if self.status == 'Approved' and self.repayment_due_date:
            return timezone.now().date() > self.repayment_due_date
        return False
    
    @property
    def total_amount_due(self):
        """Calculate total amount due using 10% per month simple interest."""
        if self.status == 'Approved' and self.repayment_due_date:
            months = self.repayment_months
            monthly_rate = Decimal('0.10')
            principal = Decimal(self.amount)
            interest = principal * monthly_rate * Decimal(months)
            return principal + interest
        return Decimal(self.amount)

    @property
    def total_interest(self):
        """Interest portion only for the full term at 10% per month simple interest."""
        if self.status == 'Approved' and self.repayment_due_date:
            months = self.repayment_months
            monthly_rate = Decimal('0.10')
            principal = Decimal(self.amount)
            return principal * monthly_rate * Decimal(months)
        return Decimal('0.00')
    
    @property
    def days_until_due(self):
        """Calculate days until repayment is due"""
        if self.status == 'Approved' and self.repayment_due_date:
            days = (self.repayment_due_date - timezone.now().date()).days
            return max(0, days)
        return None

    @property
    def days_overdue(self):
        """Number of days past the due date (0 if not overdue)."""
        if self.status == 'Approved' and self.repayment_due_date:
            days = (timezone.now().date() - self.repayment_due_date).days
            return max(0, days)
        return 0

    @property
    def repayment_months(self):
        """Number of months between loan start and due date (minimum 1, partial months count as full)."""
        if not self.repayment_due_date:
            return 0
        start = (self.created_at or timezone.now()).date()
        end = self.repayment_due_date
        months = (end.year - start.year) * 12 + (end.month - start.month)
        if end.day > start.day:
            months += 1
        return max(1, months)

    @property
    def monthly_payment(self):
        """Equal monthly payment based on simple interest total divided by months."""
        months = self.repayment_months
        if months == 0:
            return Decimal('0.00')
        total = self.total_amount_due
        return total / Decimal(months)
