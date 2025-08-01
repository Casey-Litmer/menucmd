from macrolibs.typemacros import copy_type;


#==================================================================================
#Result Type

class Result():
    def __init__(self, n: int, expanded = False):
        self.__n__ = n;
        self.__attr__ = None;

    def __getitem__(self, n: int):
        return type(self)(n).__getattr__(self.__attr__);

    def __repr__(self):
        return f"<class Result[{self.__n__}]>";

    def __eq__(self, other):
        """Compare by attribute if both self and other have attributes"""
        if self.__attr__ is not None and hasattr(other, "__attr__") and other.__attr__ is not None:
            return type(self) == type(other) and self.__attr__ == other.__attr__;
        else:
            return type(self) == type(other) and self.__n__ == other.__n__;

    def expand(self):
        """Type to replace and expand in place.   *result <=> result.expand()"""
        return copy_type(type(self), "expand", {'__repr__': self.__repr__})(self.__n__).__getattr__(self.__attr__);
        #return type(self)(self.__n__, expanded = True).__getattr__(self.__attr__)

    def __getattr__(self, tag):
        """Index by attribute first.  If no attribute, index by index"""
        new_result = type(self)(self.__n__);
        new_result.__attr__ = tag;
        return new_result;



#I have no clue what the fuck I was doing here
"""""
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
        '''Compare by attribute if both self and other have attributes'''
        if self.name is not None and hasattr(other, "name") and other.name is not None:
            return type(self) == type(other) and self.name == other.name
        else:
            return type(self) == type(other) and self.__n__ == other.__n__

    def expand(self):
        '''Type to replace and expand in place.   *result <=> result.expand()'''
        return copy_type(type(self), "expand")(self.__n__).__getattr__(self.name)

    def __getattr__(self, tag):
        if tag != self.name:
            self.callstack.append({'name': tag, 'args': (), 'kwargs': ()})
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
        
        evaluation = self.value
        
        for attr in self.callstack:
            evaluation = eval(f'{evaluation}.{attr['name']}')

            if type(evaluation == FunctionType):
                evaluation = eval(f'{evaluation}(*{attr['args']}, **{attr['kwargs']})')
        
        return evaluation
    
    
    def name(self, name):
        '''Set the exclusive name attribute.  'result[n].ABC' will be instead referenced as 'result.ABC''''
        new_result = type(self)(self.__n__)
        new_result.name = name
        return new_result


    def tail_error(*args, **kwargs):
        raise SyntaxError("Result object cannot be called without an arrtibute")
    
"""""