from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from decimal import Decimal
from .models import Business, ComplianceRequest
from .forms import (
    BusinessSearchForm,
    ComplianceRequestForm,
    CorporateBylawsForm,
    OperatingAgreementForm,
    FederalEINForm,
    LaborLawPosterForm,
    CertificateExistenceForm
)
from django.db import models
from django.http import JsonResponse
from django.db.models import Q
from django import forms
import time
from django.conf import settings
import logging
from globalpayments.api.builders import Address
from globalpayments.api.payment_methods import CreditCardData
from globalpayments.api import PorticoConfig, ServicesContainer

logger = logging.getLogger(__name__)

# Create your views here.

class HomeView(FormView):
    template_name = 'core/home.html'
    form_class = BusinessSearchForm
    success_url = '/search-results/'

    def form_valid(self, form):
        search_query = form.cleaned_data['search_query']
        # Store search query in session for results page
        self.request.session['search_query'] = search_query
        return super().form_valid(form)

class SearchResultsView(TemplateView):
    template_name = 'core/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.session.get('search_query', '')
        
        # Search in both reference number and business name
        businesses = Business.objects.filter(
            models.Q(reference_number__icontains=search_query) |
            models.Q(name__icontains=search_query)
        )
        
        context['businesses'] = businesses
        context['search_query'] = search_query
        return context

class ComplianceRequestView(FormView):
    template_name = 'core/compliance_form.html'
    form_class = ComplianceRequestForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        business_id = self.kwargs.get('business_id')
        business = get_object_or_404(Business, id=business_id)
        
        # Update service choices based on business type
        if business.business_type == 'CORP':
            form.fields['services'].choices = [
                ('CORPORATE_BYLAWS', 'Corporate Bylaws - $249.95'),
                ('FEDERAL_EIN', 'Federal EIN Application - $149.95'),
                ('LABOR_LAW_POSTER_CERT', 'Labor Law Poster & Certificate of Existence - $149.95'),
            ]
        elif business.business_type == 'LLC':
            form.fields['services'].choices = [
                ('OPERATING_AGREEMENT', 'Operating Agreement - $249.95'),
                ('FEDERAL_EIN', 'Federal EIN Application - $149.95'),
                ('LABOR_LAW_POSTER_CERT', 'Labor Law Poster & Certificate of Existence - $149.95'),
            ]
        else:
            form.fields['services'].choices = [
                ('FEDERAL_EIN', 'Federal EIN Application - $149.95'),
                ('LABOR_LAW_POSTER_CERT', 'Labor Law Poster & Certificate of Existence - $149.95'),
            ]
        
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_id = self.kwargs.get('business_id')
        business = get_object_or_404(Business, id=business_id)
        context['business'] = business
        
        # Calculate initial prices
        prices = {
            'CORPORATE_BYLAWS': Decimal('249.95'),
            'OPERATING_AGREEMENT': Decimal('249.95'),
            'FEDERAL_EIN': Decimal('149.95'),
            'LABOR_LAW_POSTER_CERT': Decimal('149.95'),
        }
        
        # Get selected services from form data
        selected_services = self.request.POST.getlist('services', [])
        if not selected_services and self.request.method == 'GET':
            selected_services = self.request.GET.getlist('services', [])
        
        # Calculate subtotal
        subtotal = sum(prices.get(service, Decimal('0')) for service in selected_services)
        
        # Calculate discount if all services are selected
        discount = Decimal('49.90')
        total = Decimal('0')
        if business.business_type in ['CORP', 'LLC']:
            all_services = ['CORPORATE_BYLAWS', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT'] if business.business_type == 'CORP' else ['OPERATING_AGREEMENT', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT']
            if all(service in selected_services for service in all_services):
                total = subtotal - discount
        
        context.update({
            'subtotal': subtotal,
            'discount': discount,
            'total': total,
            'show_discount': discount > 0,
        })
        
        # Add duplicate_services to context if present
        if hasattr(self, 'duplicate_services'):
            context['duplicate_services'] = self.duplicate_services
            
        return context

    def form_valid(self, form):
        business_id = self.kwargs.get('business_id')
        business = get_object_or_404(Business, id=business_id)
        services = form.cleaned_data['services']
        existing_types = set(ComplianceRequest.objects.filter(
            business=business, 
            status__in=['PENDING', 'PAYMENT_PENDING']
        ).values_list('request_type', flat=True))
        compliance_requests = []
        duplicate_services = []
        
        # Calculate prices for selected services
        prices = {
            'CORPORATE_BYLAWS': Decimal('249.95'),
            'OPERATING_AGREEMENT': Decimal('249.95'),
            'FEDERAL_EIN': Decimal('149.95'),
            'LABOR_LAW_POSTER_CERT': Decimal('149.95'),
        }
        
        subtotal = sum(prices.get(service, Decimal('0')) for service in services)
        
        # Calculate discount if all services are selected
        discount = Decimal('49.90')
        total = Decimal('0')
        if business.business_type in ['CORP', 'LLC']:
            all_services = ['CORPORATE_BYLAWS', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT'] if business.business_type == 'CORP' else ['OPERATING_AGREEMENT', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT']
            if all(service in services for service in all_services):
                total = subtotal - discount
        
        for service in services:
            if service == 'LABOR_LAW_POSTER_CERT':
                for service_type in ['LABOR_LAW_POSTER', 'CERTIFICATE_EXISTENCE']:
                    if service_type not in existing_types:
                        compliance_request = ComplianceRequest(
                            business=business,
                            request_type=service_type,
                            price=Decimal('74.98')  # Split the $149.95 between the two services
                        )
                        compliance_request.save()
                        compliance_requests.append(compliance_request)
                        existing_types.add(service_type)
                    else:
                        duplicate_services.append(service_type)
            else:
                if service not in existing_types:
                    compliance_request = ComplianceRequest(
                        business=business,
                        request_type=service,
                        price=prices.get(service, Decimal('0'))
                    )
                    compliance_request.save()
                    compliance_requests.append(compliance_request)
                    existing_types.add(service)
                else:
                    duplicate_services.append(service)
        
        if not compliance_requests:
            # Format duplicate_services for display
            display_names = {
                'OPERATING_AGREEMENT': 'Operating Agreement',
                'CORPORATE_BYLAWS': 'Corporate Bylaws',
                'FEDERAL_EIN': 'Federal EIN Application',
                'LABOR_LAW_POSTER': 'Labor Law Poster',
                'CERTIFICATE_EXISTENCE': 'Certificate of Existence',
            }
            formatted_duplicates = [display_names.get(s, s.replace('_', ' ').title()) for s in duplicate_services]
            self.duplicate_services = formatted_duplicates
            return self.render_to_response(self.get_context_data(form=form))
        
        # Store the total price in the session
        self.request.session['total_price'] = str(total)
        
        self.request.session['compliance_request_ids'] = [cr.id for cr in compliance_requests]
        if compliance_requests:
            return redirect('core:service_form', request_id=compliance_requests[0].id)
        return redirect('core:home')

class PaymentForm(forms.Form):
    agrees_to_terms_digital_signature = forms.BooleanField(required=True)
    client_signature_text = forms.CharField(max_length=255)

class PaymentView(FormView):
    template_name = 'core/payment.html'
    form_class = PaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        context['compliance_request'] = compliance_request
        context['business'] = compliance_request.business
        context['heartland_public_key'] = settings.HEARTLAND_PUBLIC_KEY
        
        # Get all pending requests
        request_ids = self.request.session.get('compliance_request_ids', [])
        pending_requests = ComplianceRequest.objects.filter(id__in=request_ids)
        
        # Group bundled services
        bundled_services = []
        individual_services = []
        has_labor_law = any(r.request_type == 'LABOR_LAW_POSTER' for r in pending_requests)
        has_certificate = any(r.request_type == 'CERTIFICATE_EXISTENCE' for r in pending_requests)
        
        for request in pending_requests:
            if request.request_type not in ['LABOR_LAW_POSTER', 'CERTIFICATE_EXISTENCE']:
                individual_services.append(request)
        
        if has_labor_law and has_certificate:
            bundled_services.append({
                'name': 'Labor Law Poster & Certificate of Existence',
                'price': Decimal('149.95')
            })
        else:
            if has_labor_law:
                individual_services.append(next(r for r in pending_requests if r.request_type == 'LABOR_LAW_POSTER'))
            if has_certificate:
                individual_services.append(next(r for r in pending_requests if r.request_type == 'CERTIFICATE_EXISTENCE'))
        
        # Calculate subtotal
        subtotal = sum(service['price'] for service in bundled_services)
        subtotal += sum(request.price or Decimal('0') for request in individual_services)
        
        # Calculate discount if all services are selected
        discount = Decimal('49.90')
        total_price = subtotal
        show_discount = False
        
        if compliance_request.business.business_type in ['CORP', 'LLC']:
            all_services = ['CORPORATE_BYLAWS', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT'] if compliance_request.business.business_type == 'CORP' else ['OPERATING_AGREEMENT', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT']
            if all(any(r.request_type == s or (s == 'LABOR_LAW_POSTER_CERT' and (r.request_type == 'LABOR_LAW_POSTER' or r.request_type == 'CERTIFICATE_EXISTENCE')) for r in pending_requests) for s in all_services):
                total_price = subtotal - discount
                show_discount = True
        
        context.update({
            'bundled_services': bundled_services,
            'individual_services': individual_services,
            'subtotal': subtotal,
            'discount': discount,
            'total_price': total_price,
            'show_discount': show_discount
        })
        
        return context

    def form_valid(self, form):
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Get payment token from form
        payment_token = self.request.POST.get('payment_token')
        if not payment_token:
            logger.error("Payment token missing from form submission")
            messages.error(self.request, 'Payment processing failed. Please try again.')
            return self.form_invalid(form)
        
        try:
            # Configure GlobalPayments service
            config = PorticoConfig()
            config.secret_api_key = settings.HEARTLAND_SECRET_KEY
            config.developer_id = settings.HEARTLAND_DEVELOPER_ID
            config.version_number = settings.HEARTLAND_VERSION_NUMBER
            config.service_url = settings.HEARTLAND_SERVICE_URL

            ServicesContainer.configure(config)
            
            # Get total price from context
            total_price = self.get_context_data()['total_price']
            
            # Log payment attempt
            logger.info(f"Processing payment for compliance request {request_id}")
            logger.info(f"Amount: ${total_price}")
            
            # Create card data from token
            card = CreditCardData()
            card.token = payment_token
            
            # Create address object
            address = Address()
            address.postal_code = self.request.POST.get('billing_zip')
            
            # Process payment
            response = card.charge(amount=str(total_price)) \
                .with_currency("USD") \
                .with_address(address) \
                .execute()
            
            # Log payment response
            print(f"Payment response: {response.response_code} - {response.response_message}")
            print(f"Transaction ID: {response.transaction_id}")
            print(f"Amount: ${self.get_context_data()['total_price']}")
            
            if response.response_code == '00':  # Success
                # Save the agreement and signature
                compliance_request.agrees_to_terms_digital_signature = form.cleaned_data['agrees_to_terms_digital_signature']
                compliance_request.client_signature_text = form.cleaned_data['client_signature_text']
                compliance_request.status = 'COMPLETED'
                compliance_request.save()
                
                # Update all related compliance requests
                request_ids = self.request.session.get('compliance_request_ids', [])
                ComplianceRequest.objects.filter(id__in=request_ids).update(status='PAID')
                
                # Store payment information in session
                self.request.session['payment_info'] = {
                    'user_email': self.request.user.email if self.request.user.is_authenticated else 'guest@example.com',
                    'order_reference': f"ORD-{compliance_request.id}-{int(time.time())}",
                    'amount': str(total_price),
                    'service_type': compliance_request.get_request_type_display(),
                    'business_name': compliance_request.business.name,
                    'transaction_id': response.transaction_id,
                    'payment_status': 'success',
                    'payment_message': response.response_message
                }
                
                logger.info(f"Payment successful for compliance request {request_id}")
                return redirect('core:payment_confirmation', request_id=request_id)
            else:
                error_message = f"Payment failed: {response.response_message}"
                logger.error(error_message)
                messages.error(self.request, error_message)
                return self.form_invalid(form)
                
        except Exception as e:
            error_message = f"Payment processing error: {str(e)}"
            logger.error(error_message)
            messages.error(self.request, error_message)
            return self.form_invalid(form)

class PaymentConfirmationView(TemplateView):
    template_name = 'core/payment_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Get payment information from session
        payment_info = self.request.session.get('payment_info', {})
        
        # Get all related compliance requests
        request_ids = self.request.session.get('compliance_request_ids', [request_id])
        pending_requests = ComplianceRequest.objects.filter(id__in=request_ids)
        
        # Group bundled services (similar to PaymentView)
        bundled_services = []
        individual_services = []
        has_labor_law = any(r.request_type == 'LABOR_LAW_POSTER' for r in pending_requests)
        has_certificate = any(r.request_type == 'CERTIFICATE_EXISTENCE' for r in pending_requests)
        
        for request in pending_requests:
            if request.request_type not in ['LABOR_LAW_POSTER', 'CERTIFICATE_EXISTENCE']:
                individual_services.append(request)
        
        if has_labor_law and has_certificate:
            bundled_services.append({
                'name': 'Labor Law Poster & Certificate of Existence',
                'price': Decimal('149.95')
            })
        else:
            if has_labor_law:
                individual_services.append(next(r for r in pending_requests if r.request_type == 'LABOR_LAW_POSTER'))
            if has_certificate:
                individual_services.append(next(r for r in pending_requests if r.request_type == 'CERTIFICATE_EXISTENCE'))
        
        # Calculate subtotal
        subtotal = sum(service['price'] for service in bundled_services)
        subtotal += sum(request.price or Decimal('0') for request in individual_services)
        
        # Calculate discount if all services are selected
        discount = Decimal('49.90')
        total_price = Decimal('0')
        if compliance_request.business.business_type in ['CORP', 'LLC']:
            all_services = ['CORPORATE_BYLAWS', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT'] if compliance_request.business.business_type == 'CORP' else ['OPERATING_AGREEMENT', 'FEDERAL_EIN', 'LABOR_LAW_POSTER_CERT']
            if all(any(r.request_type == s or (s == 'LABOR_LAW_POSTER_CERT' and (r.request_type == 'LABOR_LAW_POSTER' or r.request_type == 'CERTIFICATE_EXISTENCE')) for r in pending_requests) for s in all_services):
                total_price = subtotal - discount
        
        context.update({
            'user_email': payment_info.get('user_email'),
            'order_reference': payment_info.get('order_reference'),
            'amount': str(total_price),
            'subtotal': subtotal,
            'discount': discount,
            'bundled_services': bundled_services,
            'individual_services': individual_services,
            'business_name': payment_info.get('business_name'),
            'compliance_request': compliance_request,
            'business': compliance_request.business,
            'show_discount': discount > 0
        })
        
        # Clear payment info from session after retrieving it
        if 'payment_info' in self.request.session:
            del self.request.session['payment_info']
        
        return context

class ServiceFormView(FormView):
    template_name = 'core/service_form_base.html'

    def get_form_class(self):
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Map request types to form classes
        form_map = {
            'OPERATING_AGREEMENT': OperatingAgreementForm,
            'CORPORATE_BYLAWS': CorporateBylawsForm,
            'FEDERAL_EIN': FederalEINForm,
            'LABOR_LAW_POSTER': LaborLawPosterForm,
            'CERTIFICATE_EXISTENCE': CertificateExistenceForm,
        }
        
        return form_map.get(compliance_request.request_type)

    def get_template_names(self):
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Map request types to templates
        template_map = {
            'OPERATING_AGREEMENT': 'core/operating_agreement.html',
            'CORPORATE_BYLAWS': 'core/corporate_bylaws.html',
            'FEDERAL_EIN': 'core/federal_ein.html',
            'LABOR_LAW_POSTER': 'core/labor_law_poster.html',
            'CERTIFICATE_EXISTENCE': 'core/certificate_existence.html',
        }
        
        return [template_map.get(compliance_request.request_type, 'core/service_form_base.html')]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        if self.request.method in ('POST', 'PUT'):
            kwargs['instance'] = compliance_request
        
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        context['compliance_request'] = compliance_request
        context['business'] = compliance_request.business
        
        # Get all pending requests
        request_ids = self.request.session.get('compliance_request_ids', [])
        context['pending_requests'] = ComplianceRequest.objects.filter(id__in=request_ids)
        context['current_request'] = compliance_request
        
        # Add service name to context
        service_names = {
            'OPERATING_AGREEMENT': 'Operating Agreement',
            'CORPORATE_BYLAWS': 'Corporate Bylaws',
            'FEDERAL_EIN': 'Federal EIN Application',
            'LABOR_LAW_POSTER': 'Labor Law Poster',
            'CERTIFICATE_EXISTENCE': 'Certificate of Existence',
        }
        context['service_name'] = service_names.get(compliance_request.request_type, 'Service')
        
        return context

    def form_valid(self, form):
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Update the existing compliance request with form data
        for field, value in form.cleaned_data.items():
            setattr(compliance_request, field, value)
        compliance_request.save()
        
        # Get remaining requests
        request_ids = self.request.session.get('compliance_request_ids', [])
        remaining_ids = [rid for rid in request_ids if rid != request_id]
        
        if remaining_ids:
            # Redirect to next service form
            self.request.session['compliance_request_ids'] = remaining_ids
            return redirect('core:service_form', request_id=remaining_ids[0])
        else:
            # All forms completed, proceed to payment
            # Store all request IDs in session for payment page
            self.request.session['compliance_request_ids'] = [cr.id for cr in ComplianceRequest.objects.filter(business=compliance_request.business)]
            return redirect('core:payment', request_id=request_id)
        

class InsuranceInfoView(TemplateView):
    template_name = 'core/insurance_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any additional context data needed for the insurance info page
        return context

def business_search_autocomplete(request):
    query = request.GET.get('query', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    businesses = Business.objects.filter(
        Q(name__icontains=query) | Q(reference_number__icontains=query)
    ).values('id', 'name', 'reference_number', 'state_code')[:10]
    
    results = [{
        'id': business['id'],
        'text': f"{business['name']} ({business['reference_number']}) - {business['state_code']}"
    } for business in businesses]
    
    return JsonResponse({'results': results})
