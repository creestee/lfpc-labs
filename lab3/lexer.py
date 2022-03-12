import string

DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

TT_INT				= 'INT'   
TT_FLOAT    	    = 'FLOAT' 
TT_STRING			= 'STRING'
TT_IDENTIFIER	    = 'IDENTIFIER'
TT_KEYWORD		    = 'KEYWORD'
TT_ASSIGN			= 'ASSIGN'      # =
TT_PLUS     	    = 'PLUS'        # + 
TT_MINUS    	    = 'MINUS'       # -
TT_MUL      	    = 'MULTIPLY'    # *
TT_DIV      	    = 'DIVIDE'      # /
TT_EE				= 'EQUAL_SIGN'  # ==
TT_LPAREN   	    = 'LPAREN'      # (
TT_RPAREN   	    = 'RPAREN'      # )
TT_COMMA			= 'COMMA'       # ,
TT_QUOTE            = "QUOTE"       # "
TT_NE				= 'NE'          # !=
TT_LT				= 'LESS_THAN'   # <
TT_GT				= 'GREATER_THAN'# >
TT_LTE				= 'LTE'         # <=
TT_GTE				= 'GTE'         # >=
TT_EOF				= 'EOF' 

KEYWORDS = [
	'VAR',
	'AND',
	'OR',
	'NOT',
	'IF',
	'ELSE',
	'FOR',
	'TO',
	'WHILE',
	'FUNCTION',
	'THEN',
    'RETURN',
    'DO'
]

class Position:
	def __init__(self, idx, ln, col, ftxt):
		self.idx = idx
		self.ln = ln
		self.col = col
		self.ftxt = ftxt

	def advance(self, current_char=None):
		self.idx += 1
		self.col += 1

		if current_char == '\n':
			self.ln += 1
			self.col = 0

		return self

	def copy(self):
		return Position(self.idx, self.ln, self.col, self.ftxt)


class Token:
	def __init__(self, type_, value=None, pos_start=None, pos_end=None):
		self.type = type_
		self.value = value

		if pos_start:
			self.pos_start = pos_start.copy()
			self.pos_end = pos_start.copy()
			self.pos_end.advance()

		if pos_end:
			self.pos_end = pos_end.copy()

	def matches(self, type_, value):
		return self.type == type_ and self.value == value
	
	def __str__(self):
		if self.value: return f'({self.type} : {self.value})'
		return f'{self.type}'

class Lexer:
	def __init__(self, text):
		self.text = text
		self.pos = Position(-1, 0, -1, text)
		self.current_char = None
		self.advance()
	
	def advance(self):
		self.pos.advance(self.current_char)
		self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

	def make_tokens(self):
		tokens = []

		while self.current_char != None:
			if self.current_char in ' \t':
				self.advance()
			elif self.current_char in DIGITS:
				tokens.append(self.make_number())
			elif self.current_char in LETTERS:
				tokens.append(self.make_identifier())
			elif self.current_char == '"':
				tokens.append(self.make_string())
			elif self.current_char == '+':
				tokens.append(Token(TT_PLUS, pos_start=self.pos))
				self.advance()
			elif self.current_char == '-':
				tokens.append(self.make_minus_or_arrow())
			elif self.current_char == '*':
				tokens.append(Token(TT_MUL, pos_start=self.pos))
				self.advance()
			elif self.current_char == '/':
				tokens.append(Token(TT_DIV, pos_start=self.pos))
				self.advance()
			elif self.current_char == '(':
				tokens.append(Token(TT_LPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_char == ')':
				tokens.append(Token(TT_RPAREN, pos_start=self.pos))
				self.advance()
			elif self.current_char == '!':
				token, error = self.make_not_equals()
				if error: return [], error
				tokens.append(token)
			elif self.current_char == '=':
				tokens.append(self.make_assign())
			elif self.current_char == '<':
				tokens.append(self.make_less_than())
			elif self.current_char == '>':
				tokens.append(self.make_greater_than())
			elif self.current_char == ',':
				tokens.append(Token(TT_COMMA, pos_start=self.pos))
				self.advance()
			else:
				self.advance()

		tokens.append(Token(TT_EOF, pos_start=self.pos))
		return tokens

	def make_number(self):
		num_str = ''
		dot_count = 0
		pos_start = self.pos.copy()

		while self.current_char != None and self.current_char in DIGITS + '.':
			if self.current_char == '.':
				if dot_count == 1: break
				dot_count += 1
			num_str += self.current_char
			self.advance()

		if dot_count == 0:
			return Token(TT_INT, int(num_str), pos_start, self.pos)
		else:
			return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

	def make_string(self):
		string = ''
		pos_start = self.pos.copy()
		escape_character = False
		self.advance()

		escape_characters = {
			'n': '\n',
			't': '\t'
		}

		while self.current_char != None and (self.current_char != '"' or escape_character):
			if escape_character:
				string += escape_characters.get(self.current_char, self.current_char)
			else:
				if self.current_char == '\\':
					escape_character = True
				else:
					string += self.current_char
			self.advance()
			escape_character = False
		
		self.advance()
		return Token(TT_STRING, string, pos_start, self.pos)

	def make_identifier(self):
		id_str = ''
		pos_start = self.pos.copy()

		while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
			id_str += self.current_char
			self.advance()

		tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
		return Token(tok_type, id_str, pos_start, self.pos)

	def make_minus(self):
		tok_type = TT_MINUS
		pos_start = self.pos.copy()
		self.advance()

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def make_not_equals(self):
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

		self.advance()
		return None
	
	def make_assign(self):
		tok_type = TT_ASSIGN
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_EE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def make_less_than(self):
		tok_type = TT_LT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_LTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

	def make_greater_than(self):
		tok_type = TT_GT
		pos_start = self.pos.copy()
		self.advance()

		if self.current_char == '=':
			self.advance()
			tok_type = TT_GTE

		return Token(tok_type, pos_start=pos_start, pos_end=self.pos)
    

with open("source.txt") as text:
	text = text.read()
# print(text)
lexer = Lexer(text)
tokens = lexer.make_tokens()
for token in tokens:
	print(token)