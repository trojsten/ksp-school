from django import forms
from django.core.exceptions import ValidationError

from school.classrooms.models import Classroom, ClassroomUser


class JoinForm(forms.Form):
    code = forms.CharField(max_length=8)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(JoinForm, self).__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()

        classroom = Classroom.objects.filter(join_code=data["code"]).first()
        if not classroom:
            raise ValidationError("Trieda s daným kódom neexistuje.")

        if ClassroomUser.objects.filter(user=self.request.user, classroom=classroom):
            raise ValidationError("V tejto triede už si zapísaný/zapísaná.")

        data["classroom"] = classroom

        return data
