from django.forms import forms


class SubmitForm(forms.Form):
    file = forms.FileField()
