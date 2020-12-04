import sys

INT = 1
FLOAT = 2
ID = 3
KEYWORD = 4
OPERATOR = 5
COMMA = 6
EOI = 7
INVALID = 8

LETTER = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGIT = "0123456789"

def typeToString(tp):
    if tp == INT:
        return "Int"
    elif tp == FLOAT:
        return "Float"
    elif tp == ID:
        return "ID"
    elif tp == KEYWORD:
        return "Keyword"
    elif tp == OPERATOR:
        return "Operator"
    elif tp == COMMA:
        return "Comma"
    elif tp == EOI:
        return "EOI"
    return "Invalid"


class Token:
    # """ The Token class takes in two parameters, the token's type, and
    # its value. The init function initializes those values. """

    def __init__(self, tokenType, tokenVal):
        self.type = tokenType
        self.val = tokenVal

    """ this method just returns the token's type. """

    def getTokenType(self):
        return self.type

    """ this method just returns the token's value. """

    def getTokenValue(self):
        return self.val


class Lexer:
    # """ The lexer class takes in one parameter: the input string. It
    # initializes that string along with the index withing the string.
    # It finishes by calling the function nextChar() """

    def __init__(self, s):
        self.stmt = s
        self.index = 0
        self.nextChar()

    # """ This method, when called, moves through the string and constructs the
    # next token. This method moves through the string character by character
    # constucting the token based off of what the characters are using the
    # best fit. """

    def nextToken(self):
        while True:
            """ The first if statement checks if the first char in the token is
            in LETTER. If it is, it then calls consumeChars to get all of the
            characters that follow it that are either in LETTER or DIGIT. At
            the end, it checks if it created token val is SELECT, FROM, WHERE
            or AND. If it is, it is a keyword with that value, else, it is just
            and ID with the value. """
            if self.ch.isalpha():
                id = self.consumeChars(LETTER + DIGIT)
                if id == "SELECT" or id == "FROM" or id == "WHERE" or id == "AND":
                    return Token(KEYWORD, id)
                return Token(ID, id)
                # """ If the first char in the token is a digit, then it calls consumeChars
            # to check if the following chars are digits. After that, we check if
            # the next char is a ".". If so we check again if the following are
            # digits. If they are digits, then the token is a FLOAT. If there are
            # no tokens following the ".", then it is INVALID. If there is no ".",
            # then is is an INT. """
            elif self.ch.isdigit():
                num = self.consumeChars(DIGIT)
                if self.ch != ".":
                    return Token(INT, num)
                num += self.ch
                self.nextChar()
                if self.ch.isdigit():
                    num += self.consumeChars(DIGIT)
                    return Token(FLOAT, num)
                else:
                    return Token(INVALID, num)
            #     """ These last few if statements just check if the chars are white spaces,
            # commas, operators, or end-of-input, and returns the appropriate token """
            elif self.ch == ' ' or self.ch == '\n':
                self.nextChar()
            elif self.ch == ',':
                self.nextChar()
                return Token(COMMA, ",")
            elif self.ch == '=' or self.ch == '>' or self.ch == '<':
                token = Token(OPERATOR, self.ch)
                self.nextChar()
                return token
            elif self.ch == '$':
                return Token(EOI, "")
            else:
                self.nextChar()
                return Token(INVALID, self.ch)

        # """ This method simply just moves to the next char in the input string and increments

    # the index by one """

    def nextChar(self):
        self.ch = self.stmt[self.index]
        self.index = self.index + 1

    #        """ this method moves through the the input statement adding all of the characters
    #    to a string until it reaches a char that is not in the charset. It then returns 
    #    that string. """

    def consumeChars(self, charSet):
        r = self.ch
        self.nextChar()
        while self.ch in charSet:
            r = r + self.ch
            self.nextChar()
        return r


class Parser:
    #    """ The parser class takes in an input string. It initializes a lexer with that
    # string. It also initializes a token to keep track what token the lexer is
    # on """
    option_space_after_comma = "true"
    option_collapse_statements = "false"

    def __init__(self, s, config):
        Parser.option_space_after_comma = config['coma']
        Parser.option_collapse_statements = config['collapse']

        self.lexer = Lexer(s + "$")
        self.token = self.lexer.nextToken()

    """ The run method simply just begins the parsing of the input string. """

    def run(self):
        self.query()

    def format(self):
        return self.query_format()

    #    """ The following 5 methods build the ouput based off of the given E-BNF Grammar.
    # 
    # Query checks and builds the Query output, making sure the input string follows:
    # SELECT <IDLIST> FROM <IDLIST> [WHERE <CONDLIST>]. Any deviation from this
    # will result in a syntax error. """

    def query(self):
        print("<Query>")
        val = self.match_exact(KEYWORD, "SELECT")
        print("\t<Keyword>" + val + "</Keyword>")
        self.IDList()
        val = self.match_exact(KEYWORD, "FROM")
        print("\t<Keyword>" + val + "</Keyword>")
        self.IDList()
        if self.token.getTokenType() != EOI:
            val = self.match_exact(KEYWORD, "WHERE")
            print("\t<Keyword>" + val + "</Keyword>")
            self.condList()
        print("</Query>")

    def query_format(self):
        # query
        val = self.match_exact(KEYWORD, "SELECT")
        result = val

        idlist = self.IDList_format()

        if Parser.option_collapse_statements == 'false':
            result = result + ' ' + idlist + '\n'
        else:
            result = result + ' ' + idlist + ' '

        val = self.match_exact(KEYWORD, "FROM")
        result = result + val

        idlist = self.IDList_format()
        if Parser.option_collapse_statements == 'false':
            result = result + ' ' + idlist + '\n'
        else:
            result = result + ' ' + idlist + ' '

        if self.token.getTokenType() != EOI:
            val = self.match_exact(KEYWORD, "WHERE")
            result = result + val
            condlist = self.condList_format()
            result = result + ' ' + condlist

        return result

    #    """ IDList checks and builds the IDList output, making sure the input string 
    # follows: <id> {, <id>}. Any deviation from this will result in a syntax error. """

    def IDList(self):
        print("\t<IdList>")
        val = self.match_type(ID)
        print("\t\t<Id>" + val + "</Id>")

        """ This while loop deals with the optional reapeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != KEYWORD and self.token.getTokenType() != EOI:
            print("\t\t<Comma>" + self.match_type(COMMA) + "</Comma>")
            print("\t\t<Id>" + self.match_type(ID) + "</Id>")
        print("\t</IdList>")

    def IDList_format(self):
        val = self.match_type(ID)
        result = val

        """ This while loop deals with the optional reapeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != KEYWORD and self.token.getTokenType() != EOI:
            result = result + self.match_type(COMMA)
            if Parser.option_space_after_comma == 'true':
                result = result + ' ' + self.match_type(ID)
            else:
                result = result + self.match_type(ID)
        return result

    # """ CondList checks and builds the CondList output, making sure the input 
    # string follows: <Cond> {AND <Cond>}. Any deviation from this will result 
    # in a syntax error. """

    def condList(self):
        print("\t<CondList>")
        self.cond()
        """ This while loop deals with the optional reapeating part of CondList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != EOI:
            print("\t\t<Keyword>" + self.match_exact(KEYWORD, "AND") + "</Keyword")
            self.cond()
        print("\t</CondList>")

    def condList_format(self):
        cond = self.cond_format()
        result = cond

        """ This while loop deals with the optional reapeating part of CondList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != EOI:
            result = result + ' ' + self.match_exact(KEYWORD, "AND")
            cond = self.cond_format()
            result = result + ' ' + cond
        return result

    #    """ Cond checks and builds the Cond output, making sure the input string follows:
    # <id> <operator> <Term>. Any deviation from this will result in a syntax error. """

    def cond(self):
        print("\t\t<Cond>")
        val = self.match_type(ID)
        print("\t\t\t<Id>" + val + "</Id>")
        val = self.match_type(OPERATOR)
        print("\t\t\t<Operator>" + val + "</Operator>")
        self.Term()
        print("\t\t</Cond>")

    def cond_format(self):
        val = self.match_type(ID)
        result = val

        val = self.match_type(OPERATOR)
        result = result + ' ' + val

        term = self.Term_format()
        result = result + ' ' + term

        return result

    #    """ Term checks and builds the Term output, making sure the input string follows:
    # <id> | <int> | <float>. Any deviation from this will result in a syntax error. """

    def Term(self):
        print("\t\t\t<Term>")
        token = self.token.getTokenType()
        val = self.token.getTokenValue()
        if token == ID:
            print("\t\t\t\t<Id>" + val + "</Id>")
        elif token == INT:
            print("\t\t\t\t<Int>" + val + "</Int>")
        elif token == FLOAT:
            print("\t\t\t\t<Float>" + val + "</Float>")
        else:
            self.error_type(token)
        self.token = self.lexer.nextToken()
        print("\t\t\t</Term>")

    def Term_format(self):
        token = self.token.getTokenType()
        val = self.token.getTokenValue()
        result = ''
        if token == ID:
            result = result + val
        elif token == INT:
            result = result + val
        elif token == FLOAT:
            result = result + val
        else:
            self.error_type(token)
        self.token = self.lexer.nextToken()
        return result

    #    """ Match_type is a method that checks to make sure the the input token type value
    # (which is what the token should be) matches the actual token type. If they
    # do match it just moves to the next token, if not it calls the error_type. """

    def match_type(self, tp):
        val = self.token.getTokenValue()
        if self.token.getTokenType() == tp:
            self.token = self.lexer.nextToken()
        else:
            self.error_type(tp)
        return val

    #    """ Match_exact does the same as match _type, but instead of only checking if the
    # type is correct it also check to make sure that the value is correct. If it
    # fails either case, it calls one of the error methods. """

    def match_exact(self, tp, check):
        val = self.token.getTokenValue()
        if self.token.getTokenType() == tp:
            if val == check:
                self.token = self.lexer.nextToken()
            else:
                self.error_exact(check)
        else:
            self.error_type(tp)
        return val

    #    """ Error_type is the error method called if the type is wrong. It prints out an
    # error statement and then kills the program. """

    def error_type(self, tp):
        print("Syntax error: expecting: "
              + typeToString(tp)
              + "; saw type: "
              + typeToString(self.token.getTokenType())
              + "; value: "
              + typeToString(self.token.getTokenValue()))
        sys.exit(1)

    #    """ Error_exact is the error method called if the value is wrong. It prints out an
    # error statement and then kills the program. """

    def error_exact(self, check):
        print("Syntax error: expecting: "
              + typeToString(tp)
              + "; saw type: "
              + typeToString(self.token.getTokenType())
              + "; value: "
              + typeToString(self.token.getTokenValue()))
        sys.exit(1)
