
from functools import singledispatch
import time

def do_nothing(func):
    def wrapper(*args, **kwargs):
        print("this code is execute before the function is called")
        result =  func(*args, **kwargs)
        print("this code is execute after the function is called")
        return result
    return wrapper

def validate_input(func):
    def wrapper(*args, **kwargs):
        for arg in args:
            if not isinstance(arg, (int, float)):
                raise ValueError("Only numbers are allowed")
        return func(*args, **kwargs)
    return wrapper


from functools import wraps

def timethis(func):
    '''
    Decorator that reports the execution time.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("this function took: ", end - start)
        return result
    return wrapper

# @do_nothing
# @validate_input
@timethis
def sum(a, b):
    return a + b


@singledispatch
def print_value(value):
    print("Value: ", value)

@print_value.register(int)
def _(value):
    print("Integer: ", value)

@print_value.register(str)
def _(value):
    print("string: ", value)

if __name__ == '__main__':
    result = sum(2, 3)
    # # print("Result: ", result) 

    # print_value("text")
