from functools import wraps
from typing import Optional

def retry_on_exception(exception, max_retries: Optional[int] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            remaining_retries = max_retries  # Local copy of max_retries
            while True:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    if remaining_retries is None:
                        continue
                    if remaining_retries <= 0:
                        raise e
                    remaining_retries -= 1
        return wrapper
    return decorator


# not used
def supress_exception(exception, return_on_exc=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    return return_on_exc
        return wrapper
    return decorator