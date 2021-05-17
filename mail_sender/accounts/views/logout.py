from django.contrib.auth.views import LogoutView
from django.utils.decorators import decorator_from_middleware

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs


class CustomLogoutView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/logout', 'title': 'Выход из аккаунта'},
            ])
        })
        return context


@decorator_from_middleware(IsAuthenticatedMiddleware)
def logout(request):
    return CustomLogoutView.as_view(
        template_name='pages/logout.html'
    )(request)
