from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
PAYMENT_CHOICES = (
    ('S','Stripe'),
    ('p','Paypal')
)

class CheckoutForm(forms.Form):
    street_adress = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class':'form-control'
    }))
    apartment_adress = forms.CharField(required = False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class':'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    same_shipping_adress = forms.CharField(required = False)
    save_info = forms.CharField(required = False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)