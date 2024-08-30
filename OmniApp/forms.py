from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *


class CustomerCreationForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = (
            "email",
            "username",
            "user_type",
            "full_name",
            "company",
            "country",
            "postal_code",
            "address",
            "phone_number",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "user_type": forms.Select(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class CustomerChangeForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = (
            "email",
            "username",
            "user_type",
            "full_name",
            "address",
            "phone_number",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "user_type": forms.Select(attrs={"class": "form-select"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_name",
            "quantity",
            "product_image",
            "unit_weight",
            "product_description",
            "product_short_description",
            "unit_price",
            "categories",
            "tags",
        ]
        widgets = {
            "product_name": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "product_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "unit_weight": forms.NumberInput(attrs={"class": "form-control"}),
            "product_description": forms.Textarea(attrs={"class": "form-control"}),
            "product_short_description": forms.Textarea(
                attrs={"class": "form-control", "required": False}
            ),
            "unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "categories": forms.SelectMultiple(attrs={"class": "form-control"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-control"}),
        }


class ProductEditrm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "product_name",
            "quantity",
            "product_image",
            "unit_weight",
            "product_description",
            "product_short_description",
            "unit_price",
            "categories",
            "tags",
        ]
        widgets = {
            "product_name": forms.TextInput(
                attrs={"class": "form-control", "required": False}
            ),
            "quantity": forms.NumberInput(
                attrs={"class": "form-control", "required": False}
            ),
            "product_image": forms.ClearableFileInput(
                attrs={"class": "form-control", "required": False}
            ),
            "unit_weight": forms.NumberInput(
                attrs={"class": "form-control", "required": False}
            ),
            "product_description": forms.Textarea(
                attrs={"class": "form-control", "required": False}
            ),
            "product_short_description": forms.Textarea(
                attrs={"class": "form-control", "required": False}
            ),
            "unit_price": forms.NumberInput(
                attrs={"class": "form-control", "required": False}
            ),
            "categories": forms.SelectMultiple(attrs={"class": "form-control"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-control"}),
        }
