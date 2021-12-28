from django.shortcuts import redirect, render


def login(request):
    return redirect("social:begin", "trojsten")
