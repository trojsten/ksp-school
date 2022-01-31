from django import forms


class MaterialForm(forms.Form):
    materials = forms.FileField()
