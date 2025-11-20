from django.urls import path
from . import views

app_name = 'loans_api'

urlpatterns = [
    # Loan management API endpoints
    path('approve/<int:loan_id>/', views.approve_loan, name='approve_api'),
    path('reject/<int:loan_id>/', views.reject_loan, name='reject_api'),
]
