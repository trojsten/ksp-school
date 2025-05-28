from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from school.pages.models import Page


class HomepageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["home_code"] = """def get_root(node):
    parent = parents[node]
    weight = weights[node]
    if parent == node:
        return node, 0
    else:
        root, parent_weight_to_root = getRoot(parent)
        weight_to_root = weight + parent_weight_to_root
        parents[node] = root
        weights[node] = weight_to_root

        return root, weight_to_root"""

        return ctx


class PageView(TemplateView):
    template_name = "pages/page.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page"] = get_object_or_404(Page, slug=kwargs["slug"])
        return ctx
