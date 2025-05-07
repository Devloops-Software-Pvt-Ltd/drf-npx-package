from setuptools import setup, find_packages

setup(
    name='nps_payment_gateways',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=4.2.7',
        'djangorestframework'
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
    ],
)
