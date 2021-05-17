from django.http import HttpResponse
from django.utils.decorators import decorator_from_middleware

from core.middlewares import IsAuthenticatedMiddleware

from ..models import HTMLTemplate


@decorator_from_middleware(IsAuthenticatedMiddleware)
def get_html_template_representation(request):
    html_template_id = request.GET.get('html_template_id', 0)
    try:
        html_template_id = int(html_template_id)
        assert html_template_id > 0
    except (TypeError, ValueError, AssertionError):
        return HttpResponse("")
    html_template = HTMLTemplate.objects.filter(id=html_template_id).first()
    if not html_template:
        return HttpResponse("")
    return HttpResponse(html_template.template)
