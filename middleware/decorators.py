from functools import wraps
from typing import List

def require_token(require_token: bool = True, scopes_required: List[str] = None):
    """
    Decorator used only as an annotation to the endpoints that require a token. The params
    must be accessible in the request context.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator
