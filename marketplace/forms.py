from django import forms
from .models import Product, Review, User, Order

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'manufacturer', 'description', 'price', 'image']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'avatar', 'bio', 'address']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')



from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'tracking_number']
        widgets = {
            'tracking_number': forms.TextInput(attrs={
                'placeholder': 'Номер отслеживания'
            }),
            'status': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].initial = 'shipped'