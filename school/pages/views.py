from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from school.pages.models import Page


class HomepageView(TemplateView):
    template_name = 'pages/home.html'


class PageView(TemplateView):
    template_name = 'pages/page.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page'] = get_object_or_404(Page, slug=kwargs['slug'])
        return ctx
