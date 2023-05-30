from django import forms
from django.core.exceptions import ValidationError


class SubmitForm(forms.Form):
    file = forms.FileField()


class ProtocolForm(forms.Form):
    submit = forms.CharField()
    protocol = forms.FileField()

    def clean_submit(self):
        data = self.cleaned_data["submit"]
        if not data.startswith("SCHOOL-"):
            raise ValidationError("Submit ID has wrong format.")

        return int(data[7:])
