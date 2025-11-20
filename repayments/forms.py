from django import forms
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from .models import Repayment, Withdrawal, Investment


class RepaymentForm(forms.ModelForm):
    """Form for students to record repayments"""
    
    amount_paid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Amount must be greater than 0")],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter amount paid',
            'step': '0.01',
            'min': '0.01'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=Repayment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Transaction ID or reference number (optional)'
        })
    )
    
    # UPI specific fields
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter UPI ID (e.g., yourname@paytm)',
            'pattern': r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Please enter a valid UPI ID (e.g., yourname@paytm)'
            )
        ]
    )
    
    # Bank transfer specific fields
    bank_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank name'
        })
    )
    
    account_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account number'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{9,18}$',
                message='Account number must be 9-18 digits'
            )
        ]
    )
    
    ifsc_code = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'IFSC code (e.g., SBIN0001234)',
            'pattern': r'^[A-Z]{4}0[A-Z0-9]{6}$'
        }),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
                message='Please enter a valid IFSC code (e.g., SBIN0001234)'
            )
        ]
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Additional notes about the payment (optional)',
            'rows': 3
        })
    )
    
    class Meta:
        model = Repayment
        fields = ['amount_paid', 'payment_method', 'transaction_id', 'upi_id', 
                 'bank_name', 'account_number', 'ifsc_code', 'notes']
    
    def __init__(self, *args, **kwargs):
        """Accept optional 'loan' kwarg and store it for validation."""
        self.loan = kwargs.pop('loan', None)
        super().__init__(*args, **kwargs)
    
    def clean_amount_paid(self):
        """Validate payment amount"""
        amount_paid = self.cleaned_data.get('amount_paid')
        if amount_paid <= 0:
            raise forms.ValidationError('Payment amount must be greater than 0.')
        return amount_paid
    
    def clean(self):
        """Additional validation"""
        cleaned_data = super().clean()
        
        # Check if loan exists and is approved
        if self.loan:
            if self.loan.status != 'Approved':
                raise forms.ValidationError(
                    'You can only make repayments for approved loans.'
                )
            
            # Check if payment amount exceeds remaining loan amount
            total_paid = sum(
                repayment.amount_paid 
                for repayment in self.loan.repayments.filter(status='Paid')
            )
            remaining_amount = self.loan.total_amount_due - total_paid
            
            if cleaned_data.get('amount_paid', 0) > remaining_amount:
                raise forms.ValidationError(
                    f'Payment amount cannot exceed remaining loan amount (₹{remaining_amount:.2f}).'
                )
        
        return cleaned_data


class RepaymentUpdateForm(forms.ModelForm):
    """Form for updating repayments (admin use)"""
    
    amount_paid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01, message="Amount must be greater than 0")],
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=Repayment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('Manual Entry', 'Manual Entry'),
            ('UPI', 'UPI'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Cash', 'Cash'),
            ('Cheque', 'Cheque'),
            ('Credit Card', 'Credit Card'),
            ('Debit Card', 'Debit Card'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    class Meta:
        model = Repayment
        fields = [
            'amount_paid', 'status', 'payment_method', 'payment_date',
            'transaction_id', 'notes'
        ]
    
    def clean_amount_paid(self):
        """Validate payment amount"""
        amount_paid = self.cleaned_data.get('amount_paid')
        if amount_paid <= 0:
            raise forms.ValidationError('Payment amount must be greater than 0.')
        return amount_paid
    
    def clean_payment_date(self):
        """Validate payment date"""
        payment_date = self.cleaned_data.get('payment_date')
        if payment_date and payment_date > timezone.now():
            raise forms.ValidationError('Payment date cannot be in the future.')
        return payment_date
    
    def clean(self):
        """Additional validation for payment method specific fields"""
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        upi_id = cleaned_data.get('upi_id')
        bank_name = cleaned_data.get('bank_name')
        account_number = cleaned_data.get('account_number')
        ifsc_code = cleaned_data.get('ifsc_code')
        
        # Validate UPI specific fields
        if payment_method == 'UPI' and not upi_id:
            raise forms.ValidationError('UPI ID is required for UPI payments.')
        
        # Validate Bank Transfer specific fields
        if payment_method == 'Bank Transfer' and (not bank_name or not account_number or not ifsc_code):
            raise forms.ValidationError('Bank name, account number, and IFSC code are required for bank transfers.')
        
        return cleaned_data


class WithdrawalForm(forms.ModelForm):
    """Form for financiers to request withdrawals"""
    
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(100.00, message="Minimum withdrawal amount is 100 INR")],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter withdrawal amount',
            'step': '0.01',
            'min': '100.00'
        })
    )
    
    withdrawal_method = forms.ChoiceField(
        choices=Withdrawal.WITHDRAWAL_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    bank_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank name'
        })
    )
    
    account_holder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account holder name'
        })
    )
    
    account_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account number'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{9,18}$',
                message='Account number must be 9-18 digits'
            )
        ]
    )
    
    ifsc_code = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'IFSC code (e.g., SBIN0001234)',
            'pattern': r'^[A-Z]{4}0[A-Z0-9]{6}$'
        }),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
                message='Please enter a valid IFSC code (e.g., SBIN0001234)'
            )
        ]
    )
    
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter UPI ID (e.g., yourname@paytm)',
            'pattern': r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Please enter a valid UPI ID (e.g., yourname@paytm)'
            )
        ]
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Additional notes about the withdrawal (optional)',
            'rows': 3
        })
    )
    
    class Meta:
        model = Withdrawal
        fields = ['amount', 'withdrawal_method', 'bank_name', 'account_holder_name', 
                 'account_number', 'ifsc_code', 'upi_id', 'notes']
    
    def clean_amount(self):
        """Validate withdrawal amount"""
        amount = self.cleaned_data.get('amount')
        if amount < 100:
            raise forms.ValidationError('Minimum withdrawal amount is 100 INR.')
        return amount
    
    def clean(self):
        """Additional validation for withdrawal method specific fields"""
        cleaned_data = super().clean()
        withdrawal_method = cleaned_data.get('withdrawal_method')
        upi_id = cleaned_data.get('upi_id')
        
        # Validate UPI specific fields
        if withdrawal_method == 'UPI' and not upi_id:
            raise forms.ValidationError('UPI ID is required for UPI withdrawals.')
        
        return cleaned_data


class WithdrawalUpdateForm(forms.ModelForm):
    """Form for updating withdrawals (admin use)"""
    
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(100.00, message="Amount must be greater than 0")],
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=Withdrawal.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    withdrawal_method = forms.ChoiceField(
        choices=Withdrawal.WITHDRAWAL_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    bank_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    account_holder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    account_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    ifsc_code = forms.CharField(
        max_length=11,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    class Meta:
        model = Withdrawal
        fields = [
            'amount', 'status', 'withdrawal_method', 'bank_name', 
            'account_holder_name', 'account_number', 'ifsc_code', 
            'upi_id', 'transaction_id', 'notes'
        ]
    
    def clean_amount(self):
        """Validate withdrawal amount"""
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Withdrawal amount must be greater than 0.')
        return amount


class InvestmentForm(forms.ModelForm):
    """Form for financiers to make investments in loans"""
    
    investment_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1000.00, message="Minimum investment amount is 1,000 INR")],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter investment amount',
            'step': '0.01',
            'min': '1000.00'
        })
    )
    
    expected_return_rate = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        initial=12.00,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Expected annual return rate (%)',
            'step': '0.01',
            'min': '1.00',
            'max': '50.00'
        })
    )
    
    investment_method = forms.ChoiceField(
        choices=Investment.INVESTMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Bank details for investment
    bank_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bank name'
        })
    )
    
    account_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account number'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{9,18}$',
                message='Account number must be 9-18 digits'
            )
        ]
    )
    
    ifsc_code = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'IFSC code (e.g., SBIN0001234)',
            'pattern': r'^[A-Z]{4}0[A-Z0-9]{6}$'
        }),
        validators=[
            RegexValidator(
                regex=r'^[A-Z]{4}0[A-Z0-9]{6}$',
                message='Please enter a valid IFSC code (e.g., SBIN0001234)'
            )
        ]
    )
    
    # UPI details (if UPI investment)
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter UPI ID (e.g., yourname@paytm)',
            'pattern': r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        }),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message='Please enter a valid UPI ID (e.g., yourname@paytm)'
            )
        ]
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Additional notes about the investment (optional)',
            'rows': 3
        })
    )
    
    class Meta:
        model = Investment
        fields = ['investment_amount', 'expected_return_rate', 'investment_method',
                 'bank_name', 'account_number', 'ifsc_code', 'upi_id', 'notes']
    
    def clean_investment_amount(self):
        """Validate investment amount"""
        amount = self.cleaned_data.get('investment_amount')
        if amount < 1000:
            raise forms.ValidationError('Minimum investment amount is 1,000 INR.')
        return amount
    
    def clean_expected_return_rate(self):
        """Validate expected return rate"""
        rate = self.cleaned_data.get('expected_return_rate')
        if rate < 1.00 or rate > 50.00:
            raise forms.ValidationError('Expected return rate must be between 1% and 50%.')
        return rate
    
    def clean(self):
        """Additional validation for investment method specific fields"""
        cleaned_data = super().clean()
        investment_method = cleaned_data.get('investment_method')
        upi_id = cleaned_data.get('upi_id')
        bank_name = cleaned_data.get('bank_name')
        account_number = cleaned_data.get('account_number')
        ifsc_code = cleaned_data.get('ifsc_code')
        
        # Validate UPI specific fields
        if investment_method == 'UPI' and not upi_id:
            raise forms.ValidationError('UPI ID is required for UPI investments.')
        
        # Validate Bank Transfer specific fields
        if investment_method == 'Bank Transfer':
            if not bank_name:
                raise forms.ValidationError('Bank name is required for bank transfers.')
            if not account_number:
                raise forms.ValidationError('Account number is required for bank transfers.')
            if not ifsc_code:
                raise forms.ValidationError('IFSC code is required for bank transfers.')
        
        return cleaned_data


class InvestmentUpdateForm(forms.ModelForm):
    """Form for updating investments (admin use)"""
    
    investment_amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(1000.00, message="Amount must be greater than 0")],
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    expected_return_rate = forms.DecimalField(
        max_digits=4,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=Investment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    investment_method = forms.ChoiceField(
        choices=Investment.INVESTMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    bank_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    account_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    ifsc_code = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    transaction_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    
    class Meta:
        model = Investment
        fields = [
            'investment_amount', 'expected_return_rate', 'status', 'investment_method',
            'bank_name', 'account_number', 'ifsc_code', 'upi_id', 'transaction_id', 'notes'
        ]
    
    def clean_investment_amount(self):
        """Validate investment amount"""
        amount = self.cleaned_data.get('investment_amount')
        if amount <= 0:
            raise forms.ValidationError('Investment amount must be greater than 0.')
        return amount
    
    def clean_expected_return_rate(self):
        """Validate expected return rate"""
        rate = self.cleaned_data.get('expected_return_rate')
        if rate < 1.00 or rate > 50.00:
            raise forms.ValidationError('Expected return rate must be between 1% and 50%.')
        return rate
