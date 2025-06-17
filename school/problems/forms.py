from django import forms


class SubmitForm(forms.Form):
    file = forms.FileField()
