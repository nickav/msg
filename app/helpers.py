from flask import Response
from functools import wraps

# Function Decorators
def html(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='text/html; charset=utf-8')
    return decorated_function

def json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        r = f(*args, **kwargs)
        return Response(r, content_type='application/json; charset=utf-8')
    return decorated_function
