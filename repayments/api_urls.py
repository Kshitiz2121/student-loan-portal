from django.urls import path
from . import views

app_name = 'repayments_api'

urlpatterns = [
    # Repayment management API endpoints
    path('mark-paid/<int:repayment_id>/', views.mark_repayment_paid, name='mark_paid_api'),
    path('mark-failed/<int:repayment_id>/', views.mark_repayment_failed, name='mark_failed_api'),
    path('summary/', views.repayment_summary, name='summary_api'),
]
