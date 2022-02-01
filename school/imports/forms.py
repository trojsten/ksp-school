from django import forms


class ZipImportForm(forms.Form):
    file = forms.FileField()
