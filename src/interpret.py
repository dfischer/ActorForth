"""
    interpret.py - outer interpreter for ActorForth.

    INTRO 2 : The interpreter parses the input stream and executes it in 
              the context of the Continuation.
"""
from typing import TextIO, Optional

from continuation import Continuation 
from parser import Parser
from af_types import Symbol, Location

def interpret(cont: Continuation, input_stream: TextIO, filename: Optional[str] = None, prompt: Optional[str] = None) -> Continuation:    
    """
    INTRO 2.1 : Setup a parser for the input stream (passed from repl.py).
    """
    p = Parser()
    p.open_handle(input_stream, filename)

    interpret_mode = True

    if prompt: print(prompt,end='',flush=True)    

    """
    INTRO 2.2 : For each token in the input stream...
    """
    for s_id, linenum, column in p.tokens():        
        """
        INTRO 2.3 : Constructs a symbol from the token and updates the
                   Continuation's symbol.
        """
        cont.symbol = Symbol(s_id, Location(p.filename,linenum,column) ) #, TAtom)

        if p.filename != "stdin":
            print(s_id)

        try:
            """
            INTRO 2.4 : Calls execute on the Continuation...
            """
            old_tos = cont.stack.tos()
            cont.execute()
            print("%s" % cont)

            """
            INTRO 2.5:  ...until the end of tokens or an execution occurs
                        then it returns the Continuation.
            """
                
        except Exception as x:
            print("Exception %s" % x)
            print("Interpreting symbol %s" % cont.symbol)
            print(cont)
            
            # See what happens if we just keep going...
            #break
            raise
        if prompt: print(prompt,end='',flush=True)    

    return cont

    """
    INTRO 2.6 : Continue to continuation.py for INTRO stage 3.
    """
