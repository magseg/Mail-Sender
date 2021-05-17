import os
from constance import config
from functools import reduce

from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse

from accounts.commands import RegisterClientQuestion

from .models import FAQ, Feedback
from .tasks import send_email_to_admin_async
from .utils import generate_breadcumbs


def index(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(
        request,
        'pages/index.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
            ]),
            'signup_url': reverse('signup'),
            'login_url': reverse('login'),
        },
    )


def faq(request):
    this_url = reverse('faq')
    errors = []
    if request.method == 'POST' and 'ask_question' in request.POST:
        errors = RegisterClientQuestion(request.user.id, request.POST.get('ask_question', '')).execute()
        if not errors:
            return redirect('faq_ask')

    return render(
        request,
        'pages/faq.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'FAQ'},
            ]),
            'questions': FAQ.objects.filter(is_published=True),
            'ask_url': this_url,
            'errors': errors,
        },
    )


def faq_ask(request):
    return render(
        request,
        'pages/faq_ask.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': reverse('faq'), 'title': 'FAQ'},
                {'url': '', 'title': 'Новый вопрос'},
            ]),
        },
    )


def api_docs(request):
    return render(
        request,
        'pages/api_docs.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Документация API'},
            ]),
            'external_mailing_url': settings.HTTP_DOMAIN + reverse('api_send_mailing'),
            'base_url': settings.HTTP_DOMAIN,
        },
    )


def feedback(request):
    feedback_obj = None
    name = None
    email = None

    if request.method == 'POST' and request.user.is_authenticated \
            and hasattr(request.user, 'profile') and 'feedback' in request.POST.keys():
        name = request.user.profile.__str__()
        email = request.user.email
        feedback_obj = Feedback.objects.create(
            profile=request.user.profile,
            email=email,
            name=name,
            feedback_text=request.POST.get('feedback'),
        )
    elif request.method == 'POST' and reduce(lambda x, y: x and y in request.POST.keys(), ['feedback', 'email', 'name'], True):
        name = request.POST.get('name')
        email = request.POST.get('email')
        feedback_obj = Feedback.objects.create(
            email=email,
            name=name,
            feedback_text=request.POST.get('feedback'),
        )

    if feedback_obj:
        send_email_to_admin_async.apply_async((
            render_to_string('pages/feedback_email.html', {
                'name': name,
                'email': email,
                'feedback': request.POST.get('feedback'),
                'mail_sender_site': settings.HTTP_DOMAIN,
            }),
            config.FEEDBACK_EMAIL_SUBJECT
        ),)
        return redirect('feedback_done')

    return render(
        request,
        'pages/feedback.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Обратная связь'},
            ]),
            'ask_url': reverse('feedback'),
        },
    )


def feedback_done(request):
    return render(
        request,
        'pages/feedback_done.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '', 'title': 'Обращение принято'},
            ]),
        },
    )


def favicon(request):
    try:
        image_data = open(os.path.join(settings.BASE_DIR, "static", "favicon.ico.png"), "rb").read()
        return HttpResponse(image_data, content_type="image/png")
    except FileNotFoundError:
        raise Http404
