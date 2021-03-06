# Introspection of words
from . import *
from continuation import Continuation

def see_handler(cont: AF_Continuation) -> None:
    print("Calling see_handler")
    symbol : Optional[Symbol] = cont.symbol
    symbol_id : str = ""
    if symbol:
        symbol_id = symbol.s_id
    t = Type.types.get(symbol_id)
    if t:
        so = StackObject(value="Type", stype=Type(symbol_id))
        cont.stack.tos().value.push(so)
        return
    s : Stack = cont.stack.tos().value
    r : Stack = Stack()
    fcont = Continuation(s, r)
    cont.op, found = Type.op(symbol_id, fcont)
    if found:
        for i in cont.op.words:
            print(i.name, i.sig)
    else:
        print("See: Failed to find word {}".format(symbol_id))

    cont.stack.pop()


TSee = Type("See",see_handler)

def op_see(c: AF_Continuation) -> None:
    s = Stack()
    c.stack.push(StackObject(value=s, stype=TSee))
make_word_context('see', op_see)
