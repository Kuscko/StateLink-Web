from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import TemplateView, FormView
from decimal import Decimal
from .models import Business, ComplianceRequest, FederalEINRequest, OperatingAgreementRequest, CorporateBylawsRequest, LaborLawPosterRequest, CertificateExistenceRequest
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
from django.http import Http404

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
            models.Q(reference_id__icontains=search_query) |
            models.Q(name__icontains=search_query)
        )
        
        context['businesses'] = businesses
        context['search_query'] = search_query
        return context

class ComplianceRequestView(FormView):
    template_name = 'core/compliance_form.html'
    form_class = ComplianceRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business_id = self.kwargs.get('business_id')
        business = get_object_or_404(Business, reference_id=business_id)
        context['business'] = business
        
        # Define available services based on business type
        if business.business_type == 'LLC':
            available_services = [
                ('OPERATING_AGREEMENT', 'Operating Agreement ($249.95)'),
                ('FEDERAL_EIN', 'Federal EIN Application ($149.95)'),
                ('LABOR_LAW_POSTER_CERT', 'Labor Law Posters & Certificate of Existence ($149.95)'),
            ]
        elif business.business_type == 'CORP':
            available_services = [
                ('CORPORATE_BYLAWS', 'Corporate Bylaws ($249.95)'),
                ('FEDERAL_EIN', 'Federal EIN Application ($149.95)'),
                ('LABOR_LAW_POSTER_CERT', 'Labor Law Posters & Certificate of Existence ($149.95)'),
            ]
        else:
            available_services = [
                ('FEDERAL_EIN', 'Federal EIN Application ($149.95)'),
                ('LABOR_LAW_POSTER_CERT', 'Labor Law Posters & Certificate of Existence ($149.95)'),
            ]
        
        # Update form's service choices
        self.form_class.base_fields['services'].choices = available_services
        context['form'] = self.get_form()
        
        return context

    def form_valid(self, form):
        business_id = self.kwargs.get('business_id')
        business = get_object_or_404(Business, reference_id=business_id)
        services = form.cleaned_data.get('services', [])
        
        # Get or create a single compliance request for this business
        compliance_request, created = ComplianceRequest.objects.get_or_create(
            business=business,
            defaults={'status': 'PENDING'}
        )
        
        # Store the selected services in session
        self.request.session['selected_services'] = services
        
        # If this is a new request, set the first service type
        if created and services:
            compliance_request.request_type = services[0]
            compliance_request.save()
        
        # Store the compliance request ID in session
        self.request.session['compliance_request_id'] = compliance_request.id
        
        # Redirect to the first service form
        if services:
            return redirect('core:service_form', request_id=compliance_request.id)
        
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
        
        # Generate order reference if not exists
        if 'order_reference' not in self.request.session:
            self.request.session['order_reference'] = f"ORD-{compliance_request.business.reference_id}-{int(time.time())}"
        
        # Get all related service requests
        service_requests = []
        
        # Check for Federal EIN request
        has_federal_ein = False
        try:
            federal_ein = FederalEINRequest.objects.get(compliance_request=compliance_request)
            service_requests.append({
                'name': 'Federal EIN Application',
                'price': Decimal('149.95')
            })
            has_federal_ein = True
        except FederalEINRequest.DoesNotExist:
            pass

        # Check for Operating Agreement request
        has_operating_agreement = False
        try:
            operating_agreement = OperatingAgreementRequest.objects.get(compliance_request=compliance_request)
            service_requests.append({
                'name': 'Operating Agreement',
                'price': Decimal('249.95')
            })
            has_operating_agreement = True
        except OperatingAgreementRequest.DoesNotExist:
            pass

        # Check for Corporate Bylaws request
        has_corporate_bylaws = False
        try:
            corporate_bylaws = CorporateBylawsRequest.objects.get(compliance_request=compliance_request)
            service_requests.append({
                'name': 'Corporate Bylaws',
                'price': Decimal('249.95')
            })
            has_corporate_bylaws = True
        except CorporateBylawsRequest.DoesNotExist:
            pass

        # Check for Labor Law Poster and Certificate of Existence
        has_labor_law = False
        has_certificate = False
        try:
            labor_law = LaborLawPosterRequest.objects.get(compliance_request=compliance_request)
            has_labor_law = True
        except LaborLawPosterRequest.DoesNotExist:
            pass

        try:
            certificate = CertificateExistenceRequest.objects.get(compliance_request=compliance_request)
            has_certificate = True
        except CertificateExistenceRequest.DoesNotExist:
            pass

        # If both are present, add as bundled service
        if has_labor_law and has_certificate:
            service_requests.append({
                'name': 'Labor Law Posters & Certificate of Existence',
                'price': Decimal('149.95')
            })
        else:
            if has_labor_law:
                service_requests.append({
                    'name': 'Labor Law Posters',
                    'price': Decimal('99.95')
                })
            if has_certificate:
                service_requests.append({
                    'name': 'Certificate of Existence',
                    'price': Decimal('99.95')
                })

        # Calculate subtotal
        subtotal = sum(service['price'] for service in service_requests)
        
        # Calculate discount if all services are selected
        discount = Decimal('49.90')
        total_price = subtotal
        show_discount = False
        
        # Check if all three services are selected
        if compliance_request.business.business_type == 'CORP':
            if has_federal_ein and has_corporate_bylaws and (has_labor_law and has_certificate):
                total_price = subtotal - discount
                show_discount = True
        elif compliance_request.business.business_type == 'LLC':
            if has_federal_ein and has_operating_agreement and (has_labor_law and has_certificate):
                total_price = subtotal - discount
                show_discount = True

        # Store the calculated prices in the session for later use
        self.request.session['payment_calculation'] = {
            'subtotal': str(subtotal),
            'discount': str(discount) if show_discount else '0',
            'total_price': str(total_price),
            'show_discount': show_discount
        }

        context.update({
            'service_requests': service_requests,
            'subtotal': subtotal,
            'discount': discount,
            'total_price': total_price,
            'show_discount': show_discount,
            'has_labor_law_poster': has_labor_law,
            'order_reference': self.request.session.get('order_reference')
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
            
            # Get payment calculation from session
            payment_calculation = self.request.session.get('payment_calculation', {})
            total_price = Decimal(payment_calculation.get('total_price', '0'))
            
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
            print(f"Amount: ${total_price}")
            
            if response.response_code == '00':  # Success
                # Update compliance request with payment information
                compliance_request.agrees_to_terms_digital_signature = form.cleaned_data['agrees_to_terms_digital_signature']
                compliance_request.client_signature_text = form.cleaned_data['client_signature_text']
                compliance_request.status = 'PAID'
                compliance_request.price = total_price  # Save the total price
                compliance_request.order_reference_number = self.request.session.get('order_reference')  # Save the order reference
                compliance_request.save()
                
                # Store payment information in session
                self.request.session['payment_info'] = {
                    'user_email': self.request.user.email if self.request.user.is_authenticated else 'guest@example.com',
                    'order_reference': self.request.session.get('order_reference'),
                    'amount': str(total_price),
                    'subtotal': payment_calculation.get('subtotal'),
                    'discount': payment_calculation.get('discount'),
                    'show_discount': payment_calculation.get('show_discount'),
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
        
        # Get all related service requests
        service_requests = []
        
        # Check for Federal EIN request
        try:
            federal_ein = FederalEINRequest.objects.get(compliance_request=compliance_request)
            service_requests.append({
                'name': 'Federal EIN Application',
                'price': Decimal('149.95')
            })
        except FederalEINRequest.DoesNotExist:
            pass

        # Check for Operating Agreement request
        try:
            operating_agreement = OperatingAgreementRequest.objects.get(compliance_request=compliance_request)
            service_requests.append({
                'name': 'Operating Agreement',
                'price': Decimal('249.95')
            })
        except OperatingAgreementRequest.DoesNotExist:
            pass

        # Check for Corporate Bylaws request
        try:
            corporate_bylaws = CorporateBylawsRequest.objects.get(compliance_request=compliance_request)
            service_requests.append({
                'name': 'Corporate Bylaws',
                'price': Decimal('249.95')
            })
        except CorporateBylawsRequest.DoesNotExist:
            pass

        # Check for Labor Law Poster and Certificate of Existence
        has_labor_law = False
        has_certificate = False
        try:
            labor_law = LaborLawPosterRequest.objects.get(compliance_request=compliance_request)
            has_labor_law = True
        except LaborLawPosterRequest.DoesNotExist:
            pass

        try:
            certificate = CertificateExistenceRequest.objects.get(compliance_request=compliance_request)
            has_certificate = True
        except CertificateExistenceRequest.DoesNotExist:
            pass

        # If both are present, add as bundled service
        if has_labor_law and has_certificate:
            service_requests.append({
                'name': 'Labor Law Posters & Certificate of Existence',
                'price': Decimal('149.95')
            })
        else:
            if has_labor_law:
                service_requests.append({
                    'name': 'Labor Law Posters',
                    'price': Decimal('99.95')
                })
            if has_certificate:
                service_requests.append({
                    'name': 'Certificate of Existence',
                    'price': Decimal('99.95')
                })

        # Calculate subtotal
        subtotal = sum(service['price'] for service in service_requests)
        
        # Calculate discount if all services are selected
        discount = Decimal('49.90')
        total_price = subtotal
        show_discount = False
        
        # Check if all three services are selected
        if compliance_request.business.business_type == 'CORP':
            if (any(s['name'] == 'Federal EIN Application' for s in service_requests) and
                any(s['name'] == 'Corporate Bylaws' for s in service_requests) and
                any(s['name'] == 'Labor Law Posters & Certificate of Existence' for s in service_requests)):
                total_price = subtotal - discount
                show_discount = True
        elif compliance_request.business.business_type == 'LLC':
            if (any(s['name'] == 'Federal EIN Application' for s in service_requests) and
                any(s['name'] == 'Operating Agreement' for s in service_requests) and
                any(s['name'] == 'Labor Law Posters & Certificate of Existence' for s in service_requests)):
                total_price = subtotal - discount
                show_discount = True

        context.update({
            'user_email': payment_info.get('user_email'),
            'order_reference': payment_info.get('order_reference'),
            'amount': str(total_price),
            'subtotal': subtotal,
            'discount': discount,
            'service_requests': service_requests,
            'business_name': payment_info.get('business_name'),
            'compliance_request': compliance_request,
            'business': compliance_request.business,
            'show_discount': show_discount
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
            'LABOR_LAW_POSTER_CERT': LaborLawPosterForm,  # Initial form for bundled service
        }
        
        # Check if we're on the second form of the bundled service
        if compliance_request.request_type == 'LABOR_LAW_POSTER_CERT' and self.request.session.get('showing_certificate_form', False):
            form_map['LABOR_LAW_POSTER_CERT'] = CertificateExistenceForm
        
        form_class = form_map.get(compliance_request.request_type)
        if not form_class:
            raise Http404(f"No form class found for request type: {compliance_request.request_type}")
        
        return form_class

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
            'LABOR_LAW_POSTER_CERT': 'core/labor_law_poster.html',  # Initial template for bundled service
        }
        
        # Check if we're on the second form of the bundled service
        if compliance_request.request_type == 'LABOR_LAW_POSTER_CERT' and self.request.session.get('showing_certificate_form', False):
            template_map['LABOR_LAW_POSTER_CERT'] = 'core/certificate_existence.html'
        
        template = template_map.get(compliance_request.request_type, 'core/service_form_base.html')
        return [template]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        context['compliance_request'] = compliance_request
        context['business'] = compliance_request.business
        
        # Get selected services from session
        selected_services = self.request.session.get('selected_services', [])
        current_service_index = selected_services.index(compliance_request.request_type) if compliance_request.request_type in selected_services else -1
        
        # Add service name to context
        service_names = {
            'OPERATING_AGREEMENT': 'Operating Agreement',
            'CORPORATE_BYLAWS': 'Corporate Bylaws',
            'FEDERAL_EIN': 'Federal EIN Application',
            'LABOR_LAW_POSTER': 'Labor Law Poster',
            'CERTIFICATE_EXISTENCE': 'Certificate of Existence',
            'LABOR_LAW_POSTER_CERT': 'Labor Law Posters & Certificate of Existence',
        }
        
        # Adjust service name for bundled service second form
        if compliance_request.request_type == 'LABOR_LAW_POSTER_CERT':
            if self.request.session.get('showing_certificate_form', False):
                service_names['LABOR_LAW_POSTER_CERT'] = 'Certificate of Existence'
            else:
                service_names['LABOR_LAW_POSTER_CERT'] = 'Labor Law Poster'
        
        context.update({
            'service_name': service_names.get(compliance_request.request_type, 'Service'),
            'current_service_index': current_service_index + 1,
            'total_services': len(selected_services),
            'selected_services': selected_services,
            'is_bundled_service': compliance_request.request_type == 'LABOR_LAW_POSTER_CERT',
            'showing_certificate_form': self.request.session.get('showing_certificate_form', False),
        })
        
        return context

    def form_valid(self, form):
        request_id = self.kwargs.get('request_id')
        compliance_request = get_object_or_404(ComplianceRequest, id=request_id)
        
        # Get the model fields for the specific service request type
        if compliance_request.request_type == 'FEDERAL_EIN':
            # First update the parent ComplianceRequest with applicant info
            applicant_fields = [
                'applicant_reference_id',
                'applicant_first_name',
                'applicant_last_name',
                'applicant_email',
                'applicant_phone_number'
            ]
            for field in applicant_fields:
                if field in form.cleaned_data:
                    setattr(compliance_request, field, form.cleaned_data[field])
            compliance_request.save()

            # Then save the FederalEINRequest specific fields
            model_fields = [f.name for f in FederalEINRequest._meta.get_fields()]
            filtered_data = {k: v for k, v in form.cleaned_data.items() if k in model_fields}
            service_request, created = FederalEINRequest.objects.get_or_create(
                compliance_request=compliance_request,
                defaults=filtered_data
            )
            if not created:
                for field, value in filtered_data.items():
                    setattr(service_request, field, value)
                service_request.save()
        
        elif compliance_request.request_type == 'OPERATING_AGREEMENT':
            model_fields = [f.name for f in OperatingAgreementRequest._meta.get_fields()]
            filtered_data = {k: v for k, v in form.cleaned_data.items() if k in model_fields}
            service_request, created = OperatingAgreementRequest.objects.get_or_create(
                compliance_request=compliance_request,
                defaults=filtered_data
            )
            if not created:
                for field, value in filtered_data.items():
                    setattr(service_request, field, value)
                service_request.save()
        
        elif compliance_request.request_type == 'CORPORATE_BYLAWS':
            # Filter only the corporate structure fields
            filtered_data = {
                'corporate_officers': form.cleaned_data.get('corporate_officers'),
                'board_of_directors': form.cleaned_data.get('board_of_directors'),
                'authorized_shares': form.cleaned_data.get('authorized_shares'),
                'par_value_per_share': form.cleaned_data.get('par_value_per_share'),
            }
            
            service_request, created = CorporateBylawsRequest.objects.get_or_create(
                compliance_request=compliance_request,
                defaults=filtered_data
            )
            if not created:
                for field, value in filtered_data.items():
                    setattr(service_request, field, value)
                service_request.save()
        
        elif compliance_request.request_type == 'LABOR_LAW_POSTER_CERT':
            # Handle the bundled service forms
            if not self.request.session.get('showing_certificate_form', False):
                # First form (Labor Law Poster)
                model_fields = [f.name for f in LaborLawPosterRequest._meta.get_fields()]
                filtered_data = {k: v for k, v in form.cleaned_data.items() if k in model_fields}
                service_request, created = LaborLawPosterRequest.objects.get_or_create(
                    compliance_request=compliance_request,
                    defaults=filtered_data
                )
                if not created:
                    for field, value in filtered_data.items():
                        setattr(service_request, field, value)
                    service_request.save()
                
                # Set flag to show certificate form next
                self.request.session['showing_certificate_form'] = True
                return redirect('core:service_form', request_id=compliance_request.id)
            else:
                # Second form (Certificate of Existence)
                model_fields = [f.name for f in CertificateExistenceRequest._meta.get_fields()]
                filtered_data = {k: v for k, v in form.cleaned_data.items() if k in model_fields}
                service_request, created = CertificateExistenceRequest.objects.get_or_create(
                    compliance_request=compliance_request,
                    defaults=filtered_data
                )
                if not created:
                    for field, value in filtered_data.items():
                        setattr(service_request, field, value)
                    service_request.save()
                
                # Clear the flag
                self.request.session['showing_certificate_form'] = False
        
        elif compliance_request.request_type == 'LABOR_LAW_POSTER':
            model_fields = [f.name for f in LaborLawPosterRequest._meta.get_fields()]
            filtered_data = {k: v for k, v in form.cleaned_data.items() if k in model_fields}
            service_request, created = LaborLawPosterRequest.objects.get_or_create(
                compliance_request=compliance_request,
                defaults=filtered_data
            )
            if not created:
                for field, value in filtered_data.items():
                    setattr(service_request, field, value)
                service_request.save()
        
        elif compliance_request.request_type == 'CERTIFICATE_EXISTENCE':
            model_fields = [f.name for f in CertificateExistenceRequest._meta.get_fields()]
            filtered_data = {k: v for k, v in form.cleaned_data.items() if k in model_fields}
            service_request, created = CertificateExistenceRequest.objects.get_or_create(
                compliance_request=compliance_request,
                defaults=filtered_data
            )
            if not created:
                for field, value in filtered_data.items():
                    setattr(service_request, field, value)
                service_request.save()
        
        # Update the compliance request status
        compliance_request.status = 'IN_PROGRESS'
        compliance_request.save()
        
        # Get remaining services from session
        selected_services = self.request.session.get('selected_services', [])
        current_service_index = selected_services.index(compliance_request.request_type)
        
        if current_service_index < len(selected_services) - 1:
            # Set the next service type
            next_service = selected_services[current_service_index + 1]
            compliance_request.request_type = next_service
            compliance_request.save()
            
            # Redirect to the same form view with updated request type
            return redirect('core:service_form', request_id=compliance_request.id)
        else:
            # All forms completed, proceed to payment
            return redirect('core:payment', request_id=compliance_request.id)

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
        Q(name__icontains=query) | Q(reference_id__icontains=query)
    ).values('id', 'name', 'reference_id', 'state_code')[:10]
    
    results = [{
        'id': business['id'],
        'text': f"{business['name']} ({business['reference_id']}) - {business['state_code']}"
    } for business in businesses]
    
    return JsonResponse({'results': results})
