from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from decimal import Decimal
from .models import (
    Business, 
    ComplianceRequest,
    FederalEINRequest,
    OperatingAgreementRequest,
    CorporateBylawsRequest,
    CertificateExistenceRequest,
    LaborLawPosterRequest
)
from .forms import (
    BusinessSearchForm,
    ComplianceRequestForm,
    OperatingAgreementForm,
    FederalEINForm,
    LaborLawPosterForm,
    CertificateExistenceForm,
    CorporateBylawsForm,
    PaymentForm
)
from django.db import models
from django.http import JsonResponse
from django.db.models import Q
from django import forms
import time

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
            # Get the related request object based on request_type
            if compliance_request.request_type == 'FEDERAL_EIN':
                instance = compliance_request.federal_ein_request
            elif compliance_request.request_type == 'OPERATING_AGREEMENT':
                instance = compliance_request.operating_agreement_request
            elif compliance_request.request_type == 'CORPORATE_BYLAWS':
                instance = compliance_request.corporate_bylaws_request
            elif compliance_request.request_type == 'CERTIFICATE_EXISTENCE':
                instance = compliance_request.certificate_existence_request
            elif compliance_request.request_type == 'LABOR_LAW_POSTER':
                instance = compliance_request.labor_law_poster_request
            else:
                instance = None
            
            if instance:
                kwargs['instance'] = instance
        
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
        
        # Extract common fields from the form data
        form_data = form.cleaned_data
        
        # Update compliance request with common fields
        if 'requestor_first_name' in form_data:
            compliance_request.applicant_first_name = form_data['requestor_first_name']
        if 'requestor_last_name' in form_data:
            compliance_request.applicant_last_name = form_data['requestor_last_name']
        if 'requestor_email' in form_data:
            compliance_request.applicant_email = form_data['requestor_email']
        if 'requestor_phone_number' in form_data:
            compliance_request.applicant_phone_number = form_data['requestor_phone_number']
        if 'business_reference_number' in form_data:
            compliance_request.applicant_reference_number = form_data['business_reference_number']
        
        # Save the form data to the appropriate related model
        if compliance_request.request_type == 'FEDERAL_EIN':
            if not compliance_request.federal_ein_request:
                federal_ein_request = form.save()
                compliance_request.federal_ein_request = federal_ein_request
            else:
                form.save()
        elif compliance_request.request_type == 'OPERATING_AGREEMENT':
            if not compliance_request.operating_agreement_request:
                operating_agreement_request = form.save()
                compliance_request.operating_agreement_request = operating_agreement_request
            else:
                form.save()
        elif compliance_request.request_type == 'CORPORATE_BYLAWS':
            if not compliance_request.corporate_bylaws_request:
                corporate_bylaws_request = form.save()
                compliance_request.corporate_bylaws_request = corporate_bylaws_request
            else:
                form.save()
        elif compliance_request.request_type == 'CERTIFICATE_EXISTENCE':
            if not compliance_request.certificate_existence_request:
                certificate_existence_request = form.save()
                compliance_request.certificate_existence_request = certificate_existence_request
            else:
                form.save()
        elif compliance_request.request_type == 'LABOR_LAW_POSTER':
            if not compliance_request.labor_law_poster_request:
                labor_law_poster_request = form.save()
                compliance_request.labor_law_poster_request = labor_law_poster_request
            else:
                form.save()
        
        # Update compliance request status
        compliance_request.status = 'IN_PROGRESS'
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

class PaymentView(FormView):
    template_name = 'core/payment.html'
    form_class = PaymentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        context['compliance_request'] = compliance_request
        context['business'] = compliance_request.business
        request_ids = self.request.session.get('compliance_request_ids', [])
        if not request_ids:
            request_ids = [request_id]
        pending_requests = ComplianceRequest.objects.filter(id__in=request_ids)
        # Deduplicate by request_type
        unique_requests = {}
        for req in pending_requests:
            unique_requests[req.request_type] = req
        pending_requests = list(unique_requests.values())
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
        context['bundled_services'] = bundled_services
        context['individual_services'] = individual_services
        
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
            'subtotal': subtotal,
            'discount': discount,
            'total_price': total_price,
            'show_discount': discount > 0
        })
        
        return context

    def form_valid(self, form):
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Save the agreement and signature to the compliance request
        compliance_request.agrees_to_terms_digital_signature = form.cleaned_data['agrees_to_terms_digital_signature']
        compliance_request.client_signature_text = form.cleaned_data['client_signature_text']
        compliance_request.save()
        
        # Mock payment processing - in real implementation, process payment here
        # Update compliance request status
        compliance_request.status = 'COMPLETED'
        compliance_request.save()
        
        # Store necessary information in session for confirmation page
        self.request.session['payment_info'] = {
            'user_email': self.request.user.email if self.request.user.is_authenticated else 'guest@example.com',
            'order_reference': f"ORD-{compliance_request.id}-{int(time.time())}",
            'amount': str(self.get_context_data()['total_price']),
            'discount': str(self.get_context_data()['discount']),
            'service_type': compliance_request.get_request_type_display(),
            'business_name': compliance_request.business.name
        }
        
        # Redirect to confirmation page
        return redirect('core:payment_confirmation', request_id=request_id)

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
