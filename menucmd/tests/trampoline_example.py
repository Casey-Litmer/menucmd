from ast import *
from inspect import getsource

def factorial(n, acc=1):
    if n == 1: return acc
    return factorial(n-1, n*acc)

ast = parse(getsource(factorial))

#==================================================================================

class TrampolineTransform(NodeTransformer):
    def visit_return(self, node):
        return_val = node.value

        if return_val.__class__ == Call:
            func = return_val.func
            args = return_val.args

            return copy_location(Return(
                value = Tuple(elts=[
                    str(s='__trampoline'),
                    func,
                    List(elts=args, ctx=Load())
                ], ctx=Load()), ctx=Load()
            ), node)
        
        return node
    
#==================================================================================

tco_ast = fix_missing_locations(TrampolineTransform().visit(ast))
exec(compile(tco_ast, __name__, 'exec'))

def trampoline(start):
    ret = start()
    while isinstance(ret, tuple) and ret[0] == '__trampoline':
        _, func, args = ret
        ret = func(*args)
    return ret

#==================================================================================

trampoline(lambda: factorial(10000))