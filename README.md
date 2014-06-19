# README

## Setup

Download the repo:

    git clone https://github.com/depaolim/django_smart_raw_id.git

Add this folder to your pythonpath

The app is tested on Django 1.6 and has no dependency from other packages (apart from django itsef)

## Usage in your projects

In your project do the following steps:

1. Add the app smart\_raw\_id to INSTALLED\_APPS in your settings.py

2. Use SmartRawIdMixin as a mixin class for your model admin classes

## Sample Usage

The following is an an example of usage in your admin.py

    from smart_raw_id_bl import SmartRawIdMixin
   
    class SingleSaleAdmin(SmartRawIdMixin, ModelAdmin):
        list_display = ('id', 'product', 'price')
        raw_id_fields = ('product', )

... thats all folks

## Deploy

To deploy remember to do:

    python manage.py collectstatic


## Test

To run tests you need selenium as stated by requirements\_dev.txt

    pip install -r requirements.txt
    cd django_smart_raw_id
    python manage.py test


LiveServerTestCase and selenium could have timeout problems.
In such case you must restart the test
