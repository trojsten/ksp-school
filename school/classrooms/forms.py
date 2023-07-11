from django import forms
from django.core.exceptions import ValidationError

from school.classrooms.models import Classroom


class JoinForm(forms.Form):
    code = forms.CharField(max_length=8)

    def clean(self):
        data = super().clean()

        classroom = Classroom.objects.filter(join_code=data["code"]).first()
        if not classroom:
            raise ValidationError("Trieda s daným kódom neexistuje.")

        data["classroom"] = classroom

        return data
