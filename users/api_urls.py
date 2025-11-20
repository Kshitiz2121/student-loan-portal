from django.urls import path
from . import views

app_name = 'users_api'

urlpatterns = [
    # User profile API endpoints
    path('profile/', views.get_repayment_summary, name='profile_api'),
    path('loan-status/<int:loan_id>/', views.get_loan_status, name='loan_status_api'),
    path('repayment-summary/', views.get_repayment_summary, name='repayment_summary_api'),
]
