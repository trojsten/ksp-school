from django.shortcuts import render, redirect


def login(request):
    return redirect("social:begin", "trojsten")
