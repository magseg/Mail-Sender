from rest_framework import serializers

from core.utils import clean_html


class HTMLSanitilizedCharField(serializers.CharField):
    def to_internal_value(self, data):
        if isinstance(data, bool) or not isinstance(data, (str, int, float,)):
            self.fail('invalid')
        value = clean_html(data)
        return value.strip() if self.trim_whitespace else value


class SendMailingRequestSerializer(serializers.Serializer):
    from_name = serializers.CharField(min_length=1, max_length=900, required=True)
    subject = serializers.CharField(min_length=1, max_length=900, required=True)
    recipients = serializers.ListField(
        child=serializers.EmailField(allow_blank=False),
        allow_empty=False,
        required=True,
    )
    html_body = HTMLSanitilizedCharField(required=True)
    cooldown = serializers.IntegerField(required=False, min_value=1)
