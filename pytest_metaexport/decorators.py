PROTECTED_KEYS = ["duration", "status", "parametrize", "location"]


def make_dynamic_decorator(key):
    def decorator(value):
        def wrapper(func):
            if not hasattr(func, "_custom_meta"):
                setattr(func, "_custom_meta", {})

            if key in PROTECTED_KEYS:
                raise ValueError(f"Decorator with name '{key}' is protected")

            func._custom_meta[key] = value
            return func

        return wrapper

    return decorator


def __getattr__(name):
    return make_dynamic_decorator(name)
