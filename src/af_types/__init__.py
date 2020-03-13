#
#   af_types.py     - Types for our language.
#

from typing import Dict, List, Tuple, Callable, Any, Optional
from dataclasses import dataclass

from continuation import Continuation, Stack, Operation, Op_name, op_nop


Type_name = str


@dataclass
class TypeSignature:
    stack_in : List["Type"]
    stack_out : List["Type"]

    def match_in(self, stack: Stack) -> bool:
        if not len(self.stack_in): return True
        stack_types = [s.type for s in stack.contents()[len(self.stack_in)*-1:] ]

        print("match_in: in_types = %s" % (self.stack_in))
        print("match_in: stack_types = %s" % stack_types)
        for in_type in reversed(self.stack_in):
            if in_type == TAny: continue
            """
            Should probably have TAny types transform to the discovered type
            so that manipulations across generics are still completely type safe.
            """
            stack_type = stack_types.pop()
            if in_type != stack_type:
                #print("match_in: Stack type %s doesn't match input arg type %s." % (type,in_type))
                return False
        #print("match_in: Found matching type for stack_in: %s" % self.stack_in)
        return True

    def match_out(self, on_stack_types: List["Type"]) -> bool:
        return True

@dataclass
class WordFlags:
    immediate : bool = False

Op_list = List[Tuple[Operation, TypeSignature, WordFlags]]

Op_map = List[Tuple[List["Type"],Operation]]



class Type:

    # Types is a dictionary of Type names to their respective
    # custom dictionaries.   

    types : Dict[Type_name, Op_list] = {}

    types["Any"] = [] # Global dictionary. 
    types["CodeCompile"] = []

    ctors : Dict[Type_name, Op_map] = {}


    def __init__(self, typename: Type_name):
        self.name = typename
        if not Type.ctors.get(self.name, False):
            Type.ctors[self.name] = []
        if not Type.types.get(self.name, False):
            Type.types[self.name] = []

    @staticmethod
    def register_ctor(name: Type_name, op: Operation, sig: List["Type"]) -> None:
        # Ctors only have TypeSignatures that return their own Type.
        # Register the ctor in the Global dictionary.
        Type.add_op(op, TypeSignature(sig,[Type("Any")]))

        # Append this ctor to our list of valid ctors.
        op_map = Type.ctors.get(name, None)
        assert op_map is not None, ("No ctor map for type %s found.\n\tCtors exist for the following types: %s." % (name, Type.ctors.keys()))
        op_map.append((sig,op))

    @staticmethod
    def find_ctor(name: Type_name, inputs : List["Type"]) -> Optional[Operation]:
        # Given a stack of input types, find the first matching ctor.
        #print("Attempting to find a ctor for Type '%s' using the following input types: %s." % (self.name, inputs))
        #print("Type '%s' has the following ctors: %s." % (self.name, self.ctors))
        for type_sig in Type.ctors.get(name,[]):

            matching = False
            types = inputs.copy()
            try:
                for ctor_type in type_sig[0]:
                    in_type = types.pop(0)
                    if in_type.name == "Any" or ctor_type == "Any":
                        #print("Matching ctor for Any type.")
                        matching = True
                        continue
                    if in_type == ctor_type:
                        #print("Matching ctor for specific %s type." % in_type)
                        matching = True
                    else:
                        #print("Failed match for %s and %s types." % (in_type, ctor_type))
                        matching = False
                        break
            except IndexError:
                # wasn't enough on the stack to match
                #print("Ran out of inputs to match a ctor for %s type." % self.name)
                matching = False
                break

            if matching == True:
                return type_sig[1]
        return None
                


    # Inserts a new operations for the given type name (or global for None).
    @staticmethod
    def add_op(op: Operation, sig: TypeSignature, flags: WordFlags = None, type: Type_name = "Any") -> None:
        assert Type.types.get(type) is not None, "No type '%s' found. We have: %s" % (type,Type.types.keys()) 
        if not flags:
            flags = WordFlags()
        type_list = Type.types.get(type,[])        
        type_list.insert(0,(op, sig, flags))
        #print("Added Op:'%s' to %s context : %s." % (op,type,type_list))

    # Returns the first matching operation for this named type.
    @staticmethod
    def find_op(name: Op_name, cont: Continuation, type: Type_name = "Any") -> Tuple[Operation, TypeSignature, WordFlags, bool]:
        print("Searching for op:'%s' in type: '%s'." % (name,type))
        assert Type.types.get(type) is not None, "No type '%s' found. We have: %s" % (type,Type.types.keys()) 
        name_found = False
        sigs_found : List[TypeSignature] = []
        op_list = Type.types.get(type,[])  
        print("\top_list = %s" % [(name,sig.stack_in) for (name, sig, flags) in op_list])
        for op, sig, flags in op_list:
            if op.name == name:
                name_found = True
                sigs_found.append(sig)
                # Now try to match the input stack...
                # Should it be an exception to match the name but not the 
                # stack input signature? Probably so.
                if sig.match_in(cont.stack):

                    print("Found! Returning %s, %s, %s, %s" % (op, sig, flags, True))
                    return op, sig, flags, True
        # Not found.
        if name_found:
            # Is this what we want to do?
            raise Exception("Continuation doesn't match Op %s with available signatures: %s." % (name, [s.stack_in for s in sigs_found]))

        print ("Not found!")
        # This is redundant for what interpret already does by default.
        return Operation("make_atom", make_atom), TypeSignature([],[TAtom]), WordFlags(), False

    @staticmethod    
    def op(name: Op_name, cont: Continuation, type: Type_name = "Any") -> Tuple[Operation, TypeSignature, WordFlags, bool]:
        tos = cont.stack.tos()        
        op : Operation = Operation("make_atom", make_atom)
        sig : TypeSignature = TypeSignature([],[])
        flags : WordFlags = WordFlags()
        found : bool = False

        if tos is not Stack.Empty:
            # We first look for an atom specialized for the type/value on TOS.
            op, sig, flags, found = Type.find_op(name, cont, tos.type.name)

        if not found:
            # If Stack is empty or no specialized atom exists then search the global dictionary.
            op, sig, flags, found = Type.find_op(name, cont)

        return op, sig, flags, found            

    def __eq__(self, type: object) -> bool:
        if isinstance(type, Type):
            return self.name == type.name
        return False

    def __str__(self) -> Type_name:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class StackObject:
    value: Any
    type: Type 


TAtom = Type("Atom")

TAny = Type("Any")


#
#   Generic operations
#
# Atom needs to take the symbol name to push on the stack.
def make_atom(c: Continuation, s_id: Op_name = "Unknown") -> None:
    c.stack.push(StackObject(s_id,TAtom))


# op_nop from continuation.
Type.add_op(Operation('nop', op_nop), TypeSignature([],[]))


def op_print(c: Continuation) -> None:
    op1 = c.stack.pop().value
    print("'%s'" % op1)
Type.add_op(Operation('print', op_print), TypeSignature([TAny],[]))


def op_stack(c: Continuation) -> None:
    if c.stack.depth() == 0:
        print("(stack empty)")
    else:
        for n in reversed(c.stack.contents()):
            print('%s'%str(n))

Type.add_op(Operation('stack', op_stack), TypeSignature([],[]))


def print_words() -> None:
    print("Global Dictionary : %s" % list(set([op[0].short_name() for op in Type.types["Any"]])) )
    for type in Type.types.keys():
        if type != "Any":
            ops = Type.types.get(type,[])
            if len(ops):
                print("%s Dictionary : %s" % (type,list(set([op[0].short_name() for op in ops]))) )

def op_words(c: Continuation) -> None:                
    print_words()
Type.add_op(Operation('words', op_words), TypeSignature([],[]))



#
#   Should dup, swap, drop and any other generic stack operators 
#   dynamically determine the actual stack types on the stack and
#   create dynamic type signatures based on what are found?
#
def op_dup(c: Continuation) -> None:
    op1 = c.stack.tos()
    c.stack.push(op1)
Type.add_op(Operation('dup', op_dup), TypeSignature([TAny],[TAny, TAny]))


def op_swap(c: Continuation) -> None:
    op1 = c.stack.pop()
    op2 = c.stack.pop()
    c.stack.push(op1)
    c.stack.push(op2)
Type.add_op(Operation('swap', op_swap), TypeSignature([TAny, TAny],[TAny, TAny]))


def op_drop(c: Continuation) -> None:
    op1 = c.stack.pop()
Type.add_op(Operation('drop', op_drop), TypeSignature([TAny],[]))


def op_2dup(c: Continuation) -> None:
    op1 = c.stack.tos()
    op_swap(c)
    op2 = c.stack.tos()
    op_swap(c)
    c.stack.push(op2)
    c.stack.push(op1)
Type.add_op(Operation('2dup', op_2dup), TypeSignature([TAny, TAny],[TAny, TAny]))
