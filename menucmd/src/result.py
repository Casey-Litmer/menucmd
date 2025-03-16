from macrolibs.typemacros import copy_type
from types import FunctionType


#----------------------------------------------------------------------------------------------------------------------
#Result Type

class Result():

    _undecided_ = object()

    def __init__(self, n: int):
        self.__n__ = n
        self.name = None
        self.value = self._undecided_
        #self.attributes = set() 
        self.callstack = []
        self.tail = self.tail_error

    def __getitem__(self, n: int):
        return type(self)(n).__getattr__(self.name)

    def __repr__(self):
        return f"<class Result[{self.__n__}]>"

    def __eq__(self, other):
        """Compare by attribute if both self and other have attributes"""
        if self.name is not None and hasattr(other, "name") and other.name is not None:
            return type(self) == type(other) and self.name == other.name
        else:
            return type(self) == type(other) and self.__n__ == other.__n__

    def expand(self):
        """Type to replace and expand in place.   *result <=> result.expand()"""
        return copy_type(type(self), "expand")(self.__n__).__getattr__(self.name)

    def __getattr__(self, tag):
        if tag != self.name:
            self.callstack.push({'name': tag, 'args': (), 'kwargs': ()})
            self.tail = tag
        return self
    
    def __call__(self, *args, **kwargs):
        #Turn attributes into a list.
        #Then in here, create a virtual callstack
        #which the Menu call will handle in replace_keywords.
        #Use the callback on replace_value_nested to find
        #results with a non empty callstack will run
        #all logged syntactic calls
        self.callstack[-1].update({'args': args, 'kwargs': kwargs})

        return self
    

    def evaluate_callstack(self, *args, **kwargs):
        if self.value == self._undecided_:
            raise Exception(f'{self} has not been evaluated!')
        
        evaulation = self.value
        
        for attr in self.callstack:
            evaulation = eval(f'{evaulation}.{attr['name']}')

            if type(evaulation == FunctionType):
                evaulation = eval(f'{evaulation}(*{attr['args']}, **{attr['kwargs']})')
        
        return evaulation
    
    
    def name(self, name):
        """Set the exclusive name attribute.  'result[n].ABC' will be instead referenced as 'result.ABC'"""
        new_result = type(self)(self.__n__)
        new_result.name = name
        return new_result


    def tail_error(*args, **kwargs):
        raise SyntaxError("Result object cannot be called without an arrtibute")