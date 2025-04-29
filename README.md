# Django Payment Gateway

A Django package for managing payment gateways in e-commerce applications.

## Features

- Multiple payment gateway support
- Secure API endpoints
- Easy integration with Django projects
- RESTful API interface
- Admin interface support

## Installation

1. Install the package:
```bash
pip install -e .
```

2. Add 'payment_gateway' to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'payment_gateway',
]
```

3. Include payment gateway URLs in your main urls.py:
```python
path('api/payment/', include('payment_gateway.urls')),
```

4. Run migrations:
```bash
python manage.py migrate
```

## License

This project is licensed under the MIT License. "# drf-npx-package" 
