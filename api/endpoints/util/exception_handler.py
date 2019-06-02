from functools import wraps


def handle_500(func):
    """Handle 500 errors."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            return {'message': str(e)}, 500
        return func(*args, **kwargs)
    return wrapper
