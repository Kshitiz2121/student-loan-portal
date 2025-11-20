from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import LoanApplication


@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for LoanApplication model"""
    
    list_display = [
        'id', 'student_info', 'amount', 'status', 'created_at', 
        'repayment_due_date', 'is_overdue_display', 'total_amount_due'
    ]
    
    list_filter = [
        'status', 'created_at', 'repayment_due_date', 'interest_rate'
    ]
    
    search_fields = [
        'student__email', 'student__first_name', 'student__last_name', 
        'student__student_id', 'reason'
    ]
    
    readonly_fields = [
        'created_at', 'updated_at', 'is_overdue', 'total_amount_due', 
        'days_until_due'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'amount', 'reason', 'status')
        }),
        ('Repayment Details', {
            'fields': ('repayment_due_date', 'interest_rate', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Calculated Fields', {
            'fields': ('is_overdue', 'total_amount_due', 'days_until_due'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_loans', 'reject_loans', 'mark_overdue']
    
    ordering = ['-created_at']
    
    def student_info(self, obj):
        """Display student information with link to admin"""
        if obj.student:
            url = reverse('admin:users_studentuser_change', args=[obj.student.id])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.student.get_full_name(),
                obj.student.student_id
            )
        return "N/A"
    student_info.short_description = 'Student'
    student_info.admin_order_field = 'student__first_name'
    
    def is_overdue_display(self, obj):
        """Display overdue status with color coding"""
        if obj.is_overdue:
            return format_html(
                '<span style="color: red; font-weight: bold;">OVERDUE</span>'
            )
        elif obj.status == 'Approved':
            return format_html(
                '<span style="color: green;">On Time</span>'
            )
        return "N/A"
    is_overdue_display.short_description = 'Overdue Status'
    
    def total_amount_due(self, obj):
        """Display total amount due"""
        return f"₹{obj.total_amount_due}"
    total_amount_due.short_description = 'Total Amount Due'
    
    def approve_loans(self, request, queryset):
        """Action to approve selected loans"""
        updated = queryset.filter(status='Pending').update(
            status='Approved',
            admin_notes=f"Approved by admin on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
        self.message_user(
            request, 
            f"Successfully approved {updated} loan application(s)."
        )
    approve_loans.short_description = "Approve selected loans"
    
    def reject_loans(self, request, queryset):
        """Action to reject selected loans"""
        updated = queryset.filter(status='Pending').update(
            status='Rejected',
            admin_notes=f"Rejected by admin on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        )
        self.message_user(
            request, 
            f"Successfully rejected {updated} loan application(s)."
        )
    reject_loans.short_description = "Reject selected loans"
    
    def mark_overdue(self, request, queryset):
        """Action to mark loans as overdue"""
        overdue_count = 0
        for loan in queryset.filter(status='Approved'):
            if loan.is_overdue:
                loan.admin_notes = f"{loan.admin_notes or ''}\nMarked as overdue on {timezone.now().strftime('%Y-%m-%d %H:%M')}"
                loan.save()
                overdue_count += 1
        
        self.message_user(
            request, 
            f"Successfully marked {overdue_count} loan(s) as overdue."
        )
    mark_overdue.short_description = "Mark selected loans as overdue"
    
    def get_queryset(self, request):
        """Custom queryset with related student data"""
        return super().get_queryset(request).select_related('student')
