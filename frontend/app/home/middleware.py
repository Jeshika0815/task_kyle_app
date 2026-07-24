# middleware.py
# It is request user customize
import os
import jwt

class APIUser:
    is_authenticated = True
    def __init__(self, payload, token):
        self.id = payload['sub']
        self.username = payload.get('username', payload['sub'])
        self.token = token

class AnonymousUser:
    is_authenticated = False

class APIAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        token = request.session.get('token')
        if token:
            try:
                payload = verify_token(token)
                request.user = APIUser(payload, token)
            except jwt.PyJWTError:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()

        return self.get_response(request)

def verify_token(token):
    payload = jwt.decode(
        token,
        key = os.environ.get('PRIVATE_KEY'),
        algorithms = [os.environ.get('ALGORITHM')],
        issuer = os.environ.get('ISSUER'),
        audience = os.environ.get('AUDIENCE'),
    )
    return payload
