from macrolibs.typemacros import tupler

#==================================================================================
#Lazy Evaluation

class Bind():
    """
    Used for delayed evaluation.
    Creates a callable list of function / argument pairs in the form:
    [<function>, (args), {kwargs}]  ->  function(*args, **kwargs)

    - Calling a Bind object with additional args/kwargs will append (curry) them to its initial args/kwargs.

      Bind(func, args1, kwargs1)(args2, kwargs2) -> func(*args1, *args2, **kwargs1, **kwargs2)

    - Use Bind(func, *args, **kwargs).fix() to toggle currying.
    """

    class Wrapper(list):
        def __init__(self, data=()):
            super().__init__(data)
            self.fixed = False

        def __call__(self, *args, **kwargs):
            if self.fixed:
                return Bind.lazy_eval(self[0], self[1], self[2])
            else:
                return Bind.lazy_eval(self[0], self[1] + args, self[2] | kwargs)

        def fix(self):
            self.fixed = not self.fixed
            return self

    def __new__(cls, func, *args, **kwargs) -> Wrapper:
        return cls.Wrapper([func, args, kwargs])

    @staticmethod
    def lazy_eval(func, args=(), kwargs={}):
        """Depth-first evaluation of nested function/argument bindings."""
        func = func() if isinstance(func, Bind.Wrapper) else func
        args = tupler(arg() if isinstance(arg, Bind.Wrapper) else arg for arg in tupler(args))
        kwargs = {k: v() if isinstance(v, Bind.Wrapper) else v for k, v in kwargs.items()}

        return func(*args, **kwargs)


"""""
Do this to evaluate Binds recursively through ALL data structures, not just immediate Bind nestings.
This might not be the best usage because the user cannot use Bind objects in a data structure without evaluating
everything at the same time.  Adding a keyword argument to change the desired behaviour might be the right course
but for menucmd, it does not matter.


    def lazy_eval(func, args = (), kwargs = {}):
        func = func() if isinstance(func, Bind.Wrapper) else func

        def r_eval(data):
            if isinstance(data, Bind.Wrapper):
                return data()
            elif isinstance(data, list | tuple):
                return type(data)(r_eval(x) for x in data)
            else:
                return data

        args = tupler(r_eval(arg) for arg in tupler(args))
        kwargs = {k:r_eval(v) for k, v in kwargs.items()}

        return func(*args, **kwargs)
"""""
