NPSPaymentGateway
NPSPaymentGateway is a Django app that provides a custom payment gateway integration for processing transactions through the NPS payment system.
Features

Seamless integration with Django projects
Multi-tenant support via header-based authentication
RESTful API endpoints for payment processing
Database models for transaction tracking and management

Installation

Install the package using pip:

bashpip install nps-payment-gateway
Or add it directly to your requirements.txt file.
Setup

Add to INSTALLED_APPS
In your settings.py, include:
pythonINSTALLED_APPS = [
...
'nps_payment_gateway',
]

Add URLs to your project in core
In your main urls.py, include the app's URLs:
pythonfrom django.urls import path, include

urlpatterns = [
...
path('api/', include('nps_payment_gateway.urls')),
]

Run migrations
bashpython manage.py makemigrations nps_payment_gateway
python manage.py migrate

Apis
path('', include(router.urls)),
path('payment-instruments/', PaymentInstrumentView.as_view(), name='payment-instruments'),
path('process-id/', ProcessIdView.as_view(), name='process-id'),
path('notification/', NotificationView.as_view(), name='notification'),
path('service-charge/', ServiceChargeView.as_view(), name='service-charge'),
]
