from django.http.response import JsonResponse

from ..commands import GetPreupdateMessage


def get_email_account_preupdate_message(request):
    has_errors, needs_update, html_template = GetPreupdateMessage(
        request.POST.get('user_id', 0),
        request.POST.get('email_account_id', 0),
        request.POST.get('new_smtp_host', ''),
        request.POST.get('new_smtp_port', 0),
        request.POST.get('new_password', ''),
    ).execute()
    return JsonResponse({
        'has_errors': has_errors,
        'html_template': html_template,
        'needs_update': needs_update,
    })
