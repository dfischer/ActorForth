#
#   parser.py   -   Parser for our language.
#

from typing import List, TextIO, Optional, Iterator, Tuple
from io import StringIO


from af_types import Type 

class Parser:

    def __init__(self, filename: str = None) -> None:
        self.file_handle : Optional[TextIO] = None
        self.reset()
        if filename:
            self.open(filename)

    def reset(self) -> "Parser":
        self.filename = str("")
        if self.file_handle:
            self.file_handle.close()

        self.file_handle = None
        return self

    def open(self, filename: str) -> "Parser":
        self.reset()
        self.filename = filename
        self.file_handle = open(filename)
        assert self.file_handle
        return self

    def open_handle(self, handle : TextIO, filename: str = None) -> "Parser":
        self.reset()
        self.filename = filename or "Unknown"
        self.file_handle = handle
        assert self.file_handle
        return self

    def tokens(self) -> Iterator[Tuple[str, int, int]]:
        """
        Generator yielding tuples of 
          (token : str, linenum : int, token_column : int)
        """
        assert self.file_handle

        token = ""
        token_column = 0
        linenum = 1
        column = 1
        white_space = True
        
        while char := self.file_handle.read(1):

            if char == ' ' or char == '\t' or char == '\n':
                column += 1 # \n will reset column later.
                # Tabs are assumed to occur on every 4th character
                # for purposes of column counting.
                if char == '\t': column += 4 - (column % 4)
                white_space = True

            # Punctuation doesn't need whitespace!
            elif char == '.' or char == ':' or char == ';':
                white_space = False

                if token:
                    # Flush out the previous token.
                    yield (token, linenum, token_column)
                # Start a new token
                token = "".join(char)
                token_column = column
                column += 1

            else:
                if white_space:
                    token_column = column
                column += 1
                token += char
                white_space = False
                
            if token and white_space:
                yield (token, linenum, token_column)
                token = ""

            if char == '\n':
                linenum += 1
                column = 1  # reset the column as promised.

        # Handle any incremental token that may be left over.
        if token:
            yield (token, linenum, token_column)                      
