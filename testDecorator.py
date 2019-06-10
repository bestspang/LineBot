import functools

def check_permission(number):
    def my_decorator(func):
        @functools.wraps(func)
        def is_user_allow(*args, **kwargs):
            if number in [0,4]:
                func(*args, **kwargs)
            else:
                print("You have no permission!")
        return is_user_allow
    return my_decorator

@check_permission(0)
def checkin():
    print("DONE!")

checkin()
