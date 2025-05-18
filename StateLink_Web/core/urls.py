from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('search-results/', views.SearchResultsView.as_view(), name='search_results'),
    path('compliance-request/<int:business_id>/', views.ComplianceRequestView.as_view(), name='compliance_request'),
    path('service-form/<int:request_id>/', views.ServiceFormView.as_view(), name='service_form'),
    path('annual-report/<int:business_id>/', views.AnnualReportView.as_view(), name='annual_report'),
    path('payment/<int:request_id>/', views.PaymentView.as_view(), name='payment'),
    path('payment-confirmation/<int:request_id>/', views.PaymentConfirmationView.as_view(), name='payment_confirmation'),
    path('insurance-info/', views.InsuranceInfoView.as_view(), name='insurance_info'),
    path('business-search/', views.business_search_autocomplete, name='business_search_autocomplete'),
] 