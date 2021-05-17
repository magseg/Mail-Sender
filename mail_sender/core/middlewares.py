from django.http import HttpResponseRedirect


class IsAuthenticatedMiddleware(object):
    def process_request(self, request):
        user = request.user
        if not bool(user.is_authenticated) \
                or not bool(user.is_active) \
                or not hasattr(user, 'profile') \
                or not bool(user.profile):
            return HttpResponseRedirect("/login?next=" + request.path)
        else:
            return None
