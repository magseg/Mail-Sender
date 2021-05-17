from django.shortcuts import render

from core.utils import generate_breadcumbs


def handler404(request, exception):
    response = render(
        request,
        'pages/404.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Не найдено'},
            ]),
        }
    )
    response.status_code = 404
    return response


def handler403(request, exception):
    response = render(
        request,
        'pages/403.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Нет доступа'},
            ]),
        }
    )
    response.status_code = 403
    return response


def handler400(request, exception):
    response = render(
        request,
        'pages/400.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Ошибочный запрос'},
            ]),
        }
    )
    response.status_code = 400
    return response


def handler500(request):
    response = render(
        request,
        'pages/500.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Ошибка сервера'},
            ]),
        }
    )
    response.status_code = 500
    return response


from django.http.response import JsonResponse

from core.yandex_api import addr_query_yandex


def yandex_view(request):
    if request.GET.get('query', None):
        return JsonResponse(addr_query_yandex(request.GET.get('query')), safe=True)
    else:
        return JsonResponse({})
