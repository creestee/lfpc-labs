import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

TOKENS = {
    "INT": 'INT',
    "FLOAT": 'FLOAT',
    "STRING": 'STRING',
    "IDENTIFIER": 'IDENTIFIER',
    "KEYWORD": 'KEYWORD',
    "ASSIGN": 'ASSIGN',       # :
    "PLUS": 'PLUS',           # +
    "MINUS": 'MINUS',         # -
    "MUL": 'MULTIPLY',        # *
    "DIV": 'DIVIDE',          # /
    "EE": 'EQUAL_SIGN',       # :
    "LPAREN": 'LPAREN',       # (
    "RPAREN": 'RPAREN',       # )
    "COMMA": 'COMMA',         # ,
    "NE": 'NE',               # !:
    "LT": 'LESS_THAN',        # <
    "GT": 'GREATER_THAN',     # >
    "LTE": 'LTE',             # <:
    "GTE": 'GTE',             # >:
    "EOF": 'EOF',
}

KEYWORDS = ['var', 'and', 'or', 'not', 'if', 'else', 'for',
            'to', 'while', 'function', 'then', 'return', 'do']


class Position:
    def __init__(self, index, line, column, text):
        self.index = index
        self.line = line
        self.column = column
        self.text = text

    def next_pos(self, current_char=None):
        self.index += 1
        self.column += 1

        if current_char == '\n':
            self.line += 1
            self.column = 0

        return self

    def copy(self):
        return Position(self.index, self.line, self.column, self.text)


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.next_pos()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __str__(self):
        if self.value:
            return f'({self.type} : {self.value})'
        return f'{self.type}'


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = Position(-1, 0, -1, text)
        self.current_char = None
        self.next_pos()

    def next_pos(self):
        self.pos.next_pos(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(
            self.text) else None

    def create_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.next_pos()
            elif self.current_char in DIGITS:
                tokens.append(self.create_number())
            elif self.current_char in LETTERS:
                tokens.append(self.create_identifier())
            elif self.current_char == '"':
                tokens.append(self.create_string())
            elif self.current_char == '+':
                tokens.append(Token(TOKENS["PLUS"], pos_start=self.pos))
                self.next_pos()
            elif self.current_char == '-':
                tokens.append(Token(TOKENS["MINUS"], pos_start=self.pos))
                self.next_pos()
            elif self.current_char == '*':
                tokens.append(Token(TOKENS["MUL"], pos_start=self.pos))
                self.next_pos()
            elif self.current_char == '/':
                tokens.append(Token(TOKENS["DIV"], pos_start=self.pos))
                self.next_pos()
            elif self.current_char == '(':
                tokens.append(Token(TOKENS["LPAREN"], pos_start=self.pos))
                self.next_pos()
            elif self.current_char == ')':
                tokens.append(Token(TOKENS["RPAREN"], pos_start=self.pos))
                self.next_pos()
            elif self.current_char == '!':
                token, error = self.make_not_equals()
                if error:
                    return [], error
                tokens.append(token)
            elif self.current_char == '=':
                tokens.append(self.make_assign())
            elif self.current_char == '<':
                tokens.append(self.make_less_than())
            elif self.current_char == '>':
                tokens.append(self.make_greater_than())
            elif self.current_char == ',':
                tokens.append(Token(TOKENS["COMMA"], pos_start=self.pos))
                self.next_pos()
            else:
                self.next_pos()

        tokens.append(Token(TOKENS["EOF"], pos_start=self.pos))
        return tokens

    def create_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.next_pos()

        if dot_count == 0:
            return Token(TOKENS["INT"], int(num_str), pos_start, self.pos)
        else:
            return Token(TOKENS["FLOAT"], float(num_str), pos_start, self.pos)

    def create_string(self):
        string = ''
        pos_start = self.pos.copy()
        escape_character = False
        self.next_pos()

        escape_characters = {
            'n': '\n',
            't': '\t'
        }

        while self.current_char != None and (self.current_char != '"' or escape_character):
            if escape_character:
                string += escape_characters.get(self.current_char,
                                                self.current_char)
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.next_pos()
            escape_character = False

        self.next_pos()
        return Token(TOKENS["STRING"], string, pos_start, self.pos)

    def create_identifier(self):
        id_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.next_pos()

        tok_type = TOKENS["KEYWORD"] if id_str in KEYWORDS else TOKENS["IDENTIFIER"]
        return Token(tok_type, id_str, pos_start, self.pos)

    def make_not_equals(self):
        pos_start = self.pos.copy()
        self.next_pos()

        if self.current_char == '=':
            self.next_pos()
            return Token(TOKENS["NE"], pos_start=pos_start, pos_end=self.pos), None

        self.next_pos()
        return None

    def make_assign(self):
        tok_type = TOKENS["ASSIGN"]
        pos_start = self.pos.copy()
        self.next_pos()

        if self.current_char == '=':
            self.next_pos()
            tok_type = TOKENS["EE"]

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_less_than(self):
        tok_type = TOKENS["LT"]
        pos_start = self.pos.copy()
        self.next_pos()

        if self.current_char == '=':
            self.next_pos()
            tok_type = TOKENS["LTE"]

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

    def make_greater_than(self):
        tok_type = TOKENS["GT"]
        pos_start = self.pos.copy()
        self.next_pos()

        if self.current_char == '=':
            self.next_pos()
            tok_type = TOKENS["GTE"]

        return Token(tok_type, pos_start=pos_start, pos_end=self.pos)


with open("source.txt") as text:
    text = text.read()
# print(text)
lexer = Lexer(text)
tokens = lexer.create_tokens()
for token in tokens:
    print(token)
