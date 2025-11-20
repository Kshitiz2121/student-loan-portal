from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class Repayment(models.Model):
    """Model for tracking loan repayments"""
    
    STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Processing', 'Processing'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('Manual Entry', 'Manual Entry'),
        ('UPI', 'UPI (PhonePe, Google Pay, Paytm, BHIM)'),
        ('Bank Transfer', 'Bank Transfer (NEFT/RTGS/IMPS)'),
        ('Net Banking', 'Net Banking'),
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Wallet', 'Digital Wallet'),
        ('Cash', 'Cash Payment'),
        ('Cheque', 'Cheque'),
        ('DD', 'Demand Draft'),
        ('Razorpay', 'Razorpay Gateway'),
        ('PayPal', 'PayPal'),
        ('Stripe', 'Stripe'),
    ]
    
    loan = models.ForeignKey(
        'loans.LoanApplication',
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Amount must be greater than 0")]
    )
    
    payment_date = models.DateTimeField(default=timezone.now)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default='Manual Entry',
        help_text="Method of payment"
    )
    
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID or reference number"
    )
    
    gateway_transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Payment gateway transaction ID"
    )
    
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        help_text="Payment gateway response data"
    )
    
    # UPI specific fields
    upi_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="UPI ID used for payment"
    )
    
    # Bank transfer specific fields
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Bank name for transfer"
    )
    
    account_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Account number (masked)"
    )
    
    ifsc_code = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        help_text="IFSC code"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the payment"
    )
    
    # Processing fields
    processed_by = models.ForeignKey(
        'users.StudentUser',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='processed_repayments',
        help_text="Admin who processed this payment"
    )
    
    processed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the payment was processed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Repayment'
        verbose_name_plural = 'Repayments'
    
    def __str__(self):
        return f"Repayment #{self.id} - {self.loan} - {self.amount_paid} INR"
    
    def save(self, *args, **kwargs):
        # Auto-mark as paid if status is not explicitly set
        if self.status == 'Pending' and self.amount_paid > 0:
            self.status = 'Paid'
        
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        """Check if payment was successful"""
        return self.status == 'Paid'
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        return f"₹{self.amount_paid}"
    
    @property
    def payment_date_formatted(self):
        """Return formatted payment date"""
        return self.payment_date.strftime("%B %d, %Y at %I:%M %p")
    
    @property
    def masked_account_number(self):
        """Return masked account number for display"""
        if self.account_number and len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number or "N/A"
    
    @property
    def masked_upi_id(self):
        """Return masked UPI ID for display"""
        if self.upi_id:
            parts = self.upi_id.split('@')
            if len(parts) == 2:
                username = parts[0]
                if len(username) > 3:
                    return f"{username[:2]}***@{parts[1]}"
            return self.upi_id
        return "N/A"


class Withdrawal(models.Model):
    """Model for tracking financier withdrawals"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    WITHDRAWAL_METHOD_CHOICES = [
        ('Bank Transfer', 'Bank Transfer (NEFT/RTGS/IMPS)'),
        ('UPI', 'UPI Transfer'),
        ('Cheque', 'Cheque'),
        ('DD', 'Demand Draft'),
        ('Wire Transfer', 'International Wire Transfer'),
    ]
    
    financier = models.ForeignKey(
        'users.FinancierUser',
        on_delete=models.CASCADE,
        related_name='withdrawals'
    )
    
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(100.00, message="Minimum withdrawal amount is 100 INR")]
    )
    
    withdrawal_method = models.CharField(
        max_length=50,
        choices=WITHDRAWAL_METHOD_CHOICES,
        default='Bank Transfer'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    
    # Bank details for withdrawal
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    
    # UPI details (if UPI withdrawal)
    upi_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    # Processing details
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Bank transaction ID"
    )
    
    processed_by = models.ForeignKey(
        'users.StudentUser',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='processed_withdrawals',
        help_text="Admin who processed this withdrawal"
    )
    
    processed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the withdrawal"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Withdrawal'
        verbose_name_plural = 'Withdrawals'
    
    def __str__(self):
        return f"Withdrawal #{self.id} - {self.financier.user.get_full_name()} - ₹{self.amount}"
    
    @property
    def masked_account_number(self):
        """Return masked account number for display"""
        if self.account_number and len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number or "N/A"
    
    @property
    def masked_upi_id(self):
        """Return masked UPI ID for display"""
        if self.upi_id:
            parts = self.upi_id.split('@')
            if len(parts) == 2:
                username = parts[0]
                if len(username) > 3:
                    return f"{username[:2]}***@{parts[1]}"
            return self.upi_id
        return "N/A"
    
    @property
    def formatted_amount(self):
        """Return formatted amount with currency"""
        return f"₹{self.amount:,.2f}"


class Investment(models.Model):
    """Model for tracking financier investments in loans"""
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Defaulted', 'Defaulted'),
    ]
    
    INVESTMENT_METHOD_CHOICES = [
        ('Bank Transfer', 'Bank Transfer (NEFT/RTGS/IMPS)'),
        ('UPI', 'UPI Transfer'),
        ('Cheque', 'Cheque'),
        ('DD', 'Demand Draft'),
        ('Wire Transfer', 'International Wire Transfer'),
        ('Online Payment', 'Online Payment Gateway'),
    ]
    
    financier = models.ForeignKey(
        'users.FinancierUser',
        on_delete=models.CASCADE,
        related_name='investments'
    )
    
    loan = models.ForeignKey(
        'loans.LoanApplication',
        on_delete=models.CASCADE,
        related_name='investments',
        help_text="Loan application being invested in"
    )
    
    investment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1000.00, message="Minimum investment amount is 1,000 INR")]
    )
    
    expected_return_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=12.00,
        help_text="Expected annual return rate (%)"
    )
    
    investment_method = models.CharField(
        max_length=50,
        choices=INVESTMENT_METHOD_CHOICES,
        default='Bank Transfer'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    
    # Investment details
    investment_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date when investment was made"
    )
    
    maturity_date = models.DateTimeField(
        help_text="Expected maturity date for the investment"
    )
    
    # Payment details for investment
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction ID for the investment payment"
    )
    
    gateway_transaction_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Payment gateway transaction ID"
    )
    
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        help_text="Payment gateway response data"
    )
    
    # Bank details for investment
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    account_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    
    ifsc_code = models.CharField(
        max_length=11,
        blank=True,
        null=True
    )
    
    # UPI details (if UPI investment)
    upi_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    # Processing details
    processed_by = models.ForeignKey(
        'users.StudentUser',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='processed_investments',
        help_text="Admin who processed this investment"
    )
    
    processed_at = models.DateTimeField(
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the investment"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Investment'
        verbose_name_plural = 'Investments'
        unique_together = ['financier', 'loan']  # One investment per financier per loan
    
    def __str__(self):
        return f"Investment #{self.id} - {self.financier.user.get_full_name()} - ₹{self.investment_amount} - Loan #{self.loan.id}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate maturity date based on loan repayment due date
        if not self.maturity_date and self.loan:
            self.maturity_date = self.loan.repayment_due_date
        
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        """Check if investment is active"""
        return self.status in ['Approved', 'Active']
    
    @property
    def is_completed(self):
        """Check if investment is completed"""
        return self.status == 'Completed'
    
    @property
    def formatted_amount(self):
        """Return formatted investment amount with currency"""
        return f"₹{self.investment_amount:,.2f}"
    
    @property
    def expected_return_amount(self):
        """Calculate expected return amount"""
        if self.loan:
            # Calculate based on loan interest rate and investment period
            return self.investment_amount * (self.expected_return_rate / 100) * (self.loan.interest_rate / 100)
        return Decimal('0.00')
    
    @property
    def total_return_amount(self):
        """Calculate total return amount (principal + interest)"""
        return self.investment_amount + self.expected_return_amount
    
    @property
    def masked_account_number(self):
        """Return masked account number for display"""
        if self.account_number and len(self.account_number) > 4:
            return f"****{self.account_number[-4:]}"
        return self.account_number or "N/A"
    
    @property
    def masked_upi_id(self):
        """Return masked UPI ID for display"""
        if self.upi_id:
            parts = self.upi_id.split('@')
            if len(parts) == 2:
                username = parts[0]
                if len(username) > 3:
                    return f"{username[:2]}***@{parts[1]}"
            return self.upi_id
        return "N/A"
    
    @property
    def investment_period_days(self):
        """Calculate investment period in days"""
        if self.maturity_date:
            return (self.maturity_date - self.investment_date).days
        return 0
