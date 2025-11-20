from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import StudentUser


@admin.register(StudentUser)
class StudentUserAdmin(UserAdmin):
    """Admin configuration for StudentUser model"""
    
    list_display = [
        'email', 'first_name', 'last_name', 'student_id', 
        'university', 'gpa', 'is_active', 'date_joined'
    ]
    
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 
        'university', 'gpa', 'date_joined'
    ]
    
    search_fields = [
        'email', 'first_name', 'last_name', 'student_id', 
        'university', 'phone_number'
    ]
    
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'student_id', 'university', 
                'gpa', 'phone_number', 'address', 'date_of_birth', 'profile_picture'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'first_name', 'last_name', 'student_id', 'university', 
                'gpa', 'phone_number', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def get_queryset(self, request):
        """Custom queryset with loan eligibility info"""
        return super().get_queryset(request).select_related()
    
    def is_eligible_for_loan(self, obj):
        """Display loan eligibility status"""
        return obj.is_eligible_for_loan
    is_eligible_for_loan.boolean = True
    is_eligible_for_loan.short_description = 'Eligible for Loan'
    
    def has_active_loan(self, obj):
        """Display active loan status"""
        return obj.has_active_loan
    has_active_loan.boolean = True
    has_active_loan.short_description = 'Has Active Loan'
