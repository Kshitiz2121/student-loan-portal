from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Repayment, Withdrawal


@admin.register(Repayment)
class RepaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Repayment model"""
    
    list_display = [
        'id', 'loan_info', 'amount_paid', 'status', 'payment_method',
        'payment_date', 'transaction_id', 'is_successful_display'
    ]
    
    list_filter = [
        'status', 'payment_method', 'payment_date', 'created_at'
    ]
    
    search_fields = [
        'loan__student__email', 'loan__student__first_name', 
        'loan__student__last_name', 'transaction_id', 'notes'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'is_successful', 'formatted_amount',
        'payment_date_formatted'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('loan', 'amount_paid', 'status', 'payment_method')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'gateway_transaction_id', 'gateway_response', 'payment_date', 'notes')
        }),
        ('UPI Details', {
            'fields': ('upi_id',),
            'classes': ('collapse',)
        }),
        ('Bank Transfer Details', {
            'fields': ('bank_name', 'account_number', 'ifsc_code'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed_by', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('is_successful', 'formatted_amount', 'payment_date_formatted'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_failed']
    
    ordering = ['-payment_date']
    
    def loan_info(self, obj):
        """Display loan information with link to admin"""
        if obj.loan:
            url = reverse('admin:loans_loanapplication_change', args=[obj.loan.id])
            return format_html(
                '<a href="{}">Loan #{}</a> - {}',
                url,
                obj.loan.id,
                obj.loan.student.get_full_name()
            )
        return "N/A"
    loan_info.short_description = 'Loan'
    loan_info.admin_order_field = 'loan__id'
    
    def is_successful_display(self, obj):
        """Display success status with color coding"""
        if obj.is_successful:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Success</span>'
            )
        elif obj.status == 'Failed':
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Failed</span>'
            )
        else:
            return format_html(
                '<span style="color: orange;">⏳ Pending</span>'
            )
    is_successful_display.short_description = 'Payment Status'
    
    def mark_as_paid(self, request, queryset):
        """Action to mark selected repayments as paid"""
        updated = queryset.filter(status='Pending').update(status='Paid')
        self.message_user(
            request, 
            f"Successfully marked {updated} repayment(s) as paid."
        )
    mark_as_paid.short_description = "Mark selected repayments as paid"
    
    def mark_as_failed(self, request, queryset):
        """Action to mark selected repayments as failed"""
        updated = queryset.filter(status='Pending').update(status='Failed')
        self.message_user(
            request, 
            f"Successfully marked {updated} repayment(s) as failed."
        )
    mark_as_failed.short_description = "Mark selected repayments as failed"
    
    def get_queryset(self, request):
        """Custom queryset with related loan and student data"""
        return super().get_queryset(request).select_related('loan__student')


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    """Admin configuration for Withdrawal model"""
    
    list_display = [
        'id', 'financier_info', 'amount', 'withdrawal_method', 'status', 
        'created_at', 'processed_by_info'
    ]
    
    list_filter = [
        'status', 'withdrawal_method', 'created_at'
    ]
    
    search_fields = [
        'financier__user__first_name', 'financier__user__last_name', 
        'financier__financier_id', 'transaction_id', 'notes'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'formatted_amount', 'masked_account_number', 'masked_upi_id'
    ]
    
    fieldsets = (
        ('Withdrawal Information', {
            'fields': ('financier', 'amount', 'withdrawal_method', 'status')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_holder_name', 'account_number', 'ifsc_code')
        }),
        ('UPI Details', {
            'fields': ('upi_id',),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed_by', 'processed_at', 'transaction_id')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Security Fields', {
            'fields': ('masked_account_number', 'masked_upi_id'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_withdrawals', 'complete_withdrawals', 'reject_withdrawals']
    
    ordering = ['-created_at']
    
    def financier_info(self, obj):
        """Display financier information with link to admin"""
        if obj.financier:
            url = reverse('admin:users_financieruser_change', args=[obj.financier.id])
            return format_html(
                '<a href="{}">{}</a> ({})',
                url,
                obj.financier.user.get_full_name(),
                obj.financier.financier_id
            )
        return "N/A"
    financier_info.short_description = 'Financier'
    financier_info.admin_order_field = 'financier__user__first_name'
    
    def processed_by_info(self, obj):
        """Display processed by information"""
        if obj.processed_by:
            return obj.processed_by.get_full_name()
        return "Not Processed"
    processed_by_info.short_description = 'Processed By'
    
    def approve_withdrawals(self, request, queryset):
        """Action to approve selected withdrawals"""
        updated = queryset.filter(status='Pending').update(status='Processing')
        self.message_user(
            request, 
            f"Successfully approved {updated} withdrawal(s) for processing."
        )
    approve_withdrawals.short_description = "Approve selected withdrawals"
    
    def complete_withdrawals(self, request, queryset):
        """Action to mark selected withdrawals as completed"""
        updated = queryset.filter(status='Processing').update(status='Completed')
        self.message_user(
            request, 
            f"Successfully marked {updated} withdrawal(s) as completed."
        )
    complete_withdrawals.short_description = "Mark selected withdrawals as completed"
    
    def reject_withdrawals(self, request, queryset):
        """Action to reject selected withdrawals"""
        updated = queryset.filter(status='Pending').update(status='Failed')
        self.message_user(
            request, 
            f"Successfully rejected {updated} withdrawal(s)."
        )
    reject_withdrawals.short_description = "Reject selected withdrawals"
    
    def get_queryset(self, request):
        """Custom queryset with related financier data"""
        return super().get_queryset(request).select_related('financier__user', 'processed_by')
