NPSPaymentGateway
NPSPaymentGateway is a Django app that provides a custom payment gateway integration for processing transactions through the NPS payment system.


Installation

Install the package using pip:

pip install nps-payment-gateway
Or add it directly to your requirements.txt file.

Setup

Add to INSTALLED_APPS
In your settings.py, include:

INSTALLED_APPS = [
...
'nps_payment_gateway',
]

Add URLs to your project in core
In your main urls.py, include the app's URLs:

from django.urls import path, include

urlpatterns = [
...
path('api/', include('nps_payment_gateway.urls')),
]

Run migrations
python manage.py makemigrations nps_payment_gateway
python manage.py migrate
