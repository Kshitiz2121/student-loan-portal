from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # Loan application URLs
    path('apply/', views.apply_loan, name='apply'),
    path('apply/class/', views.LoanApplicationCreateView.as_view(), name='apply_class'),
    path('list/', views.LoanApplicationListView.as_view(), name='list'),
    path('detail/<int:pk>/', views.LoanApplicationDetailView.as_view(), name='detail'),
    
    # Admin management URLs
    path('admin/', views.admin_loan_management, name='admin_management'),
    path('statistics/', views.loan_statistics, name='statistics'),
    
    # API endpoints for loan management
    path('api/approve/<int:loan_id>/', views.approve_loan, name='approve_api'),
    path('api/reject/<int:loan_id>/', views.reject_loan, name='reject_api'),
]
