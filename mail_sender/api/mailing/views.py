from celery import chain

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.contrib.rest_framework.authentication import AccessTokenAuthentication
from core.contrib.rest_framework.exceptions import Conflict
from mailings.models import SenderHistory
from mailings.tasks import create_mailing

from .serializers import SendMailingRequestSerializer


class SendMailingAPI(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):
        serializer = SendMailingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        host = request.auth.get_smtp_host()
        port = request.auth.get_smtp_port()
        if not host or not port:
            raise Conflict(detail='Для аккаунта не задан host или port.')

        sender_history_obj = SenderHistory.objects.create(
            total_mailings=len(validated_data['recipients']),
            from_name=validated_data['from_name'] or request.auth.email,
            subject=validated_data['subject'],
            profile=request.auth.profile,
            email_account=request.auth,
        )
        array_of_tasks = [create_mailing.s(
            (),
            history_id=sender_history_obj.id,
            recipients_list=validated_data['recipients'],
            host=host,
            port=port,
            username=request.auth.email,
            password=request.auth.get_password(),
            html_message_pattern=validated_data['html_body'],
            subject=validated_data['subject'],
            user_profile_id=request.auth.profile.id,
            html_template_id=None,
            email_account_id=request.auth.id,
            fromname=validated_data['from_name'],
            cooldown=validated_data.get('cooldown', 15) / 10.0,
        )]
        chain(*array_of_tasks).apply_async()

        return Response(status=204)
