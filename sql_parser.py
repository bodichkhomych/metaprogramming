import sys

ID = 2
KEYWORD = 4
OPERATOR = 5
COMMA = 6
EOI = 7
INVALID = 8
TYPE_DEFINITION = 9
SEPARATOR = 10

LETTER = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-*"
DIGIT = "0123456789"

def typeToString(tp):
    if tp == ID:
        return "id"
    elif tp == KEYWORD:
        return "Keyword"
    elif tp == OPERATOR:
        return "Operator"
    elif tp == COMMA:
        return "Comma"
    elif tp == EOI:
        return "EOI"
    elif tp == TYPE_DEFINITION:
        return "Type definition"
    elif tp == SEPARATOR:
        return "Separator"
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
                if id.upper() == "INSERT" or id.upper() == "INTO" \
                        or id.upper() == "VALUES" or id.upper() == "SELECT" \
                        or id.upper() == "FROM" or id.upper() == "WHERE" \
                        or id.upper() == "AND" or id.upper() == "CREATE" \
                        or id.upper() == "TABLE":
                    return Token(KEYWORD, id)
                if id.upper() == "INT" or id.upper() == "FLOAT" \
                        or id.upper() == "STRING" or id.upper() == "DATE":
                    return Token(TYPE_DEFINITION, id)
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
                    return Token(ID, num)
                num += self.ch
                self.nextChar()
                if self.ch.isdigit():
                    num += self.consumeChars(DIGIT)
                    return Token(ID, num)
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
            elif self.ch == '(' or self.ch == ')' or self.ch == ';':
                token = Token(SEPARATOR, self.ch)
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
    option_space_after_separator = "false"
    option_collapse_statements = "false"
    option_indent_lines_number = 2

    def __init__(self, s, config):
        Parser.option_space_after_comma = config['coma']
        Parser.option_space_after_separator = config['separator']
        Parser.option_collapse_statements = config['collapse']
        Parser.option_indent_lines_number = config['lines']

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
        result = ''
        while self.token.getTokenType() != EOI:
            val = self.token.getTokenValue()

            if val == "SELECT":
                self.query_select()

            if val == "INSERT":
                self.query_insert()

            if val == "CREATE":
                self.query_create()

            for i in range(Parser.option_indent_lines_number+1):
                print("\n")

        return result

    def query_select(self):
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

        val = self.match_exact(SEPARATOR, ";")
        print("<Separator>" + val + "</Separator>")

        print("</Query>")

    def query_insert(self):
        print("<Query>")

        val = self.match_exact(KEYWORD, "INSERT")
        print("\t<Keyword>" + val + "</Keyword>")
        

        val = self.match_exact(KEYWORD, "INTO")
        print("\t<Keyword>" + val + "</Keyword>")

        self.ID()

        if self.token.getTokenValue() == '(':
            val = self.match_exact(SEPARATOR, "(")
            print("<Separator>" + val + "</Separator>")

            self.IDList()

            val = self.match_exact(SEPARATOR, ")")
            print("<Separator>" + val + "</Separator>")

        val = self.match_exact(KEYWORD, "VALUES")
        print("\t<Keyword>" + val + "</Keyword>")

        while self.token.getTokenValue() != ";":
            val = self.match_exact(SEPARATOR, "(")
            print("<Separator>" + val + "</Separator>")
            self.IDList()
            val = self.match_exact(SEPARATOR, ")")
            print("<Separator>" + val + "</Separator>")

            if self.token.getTokenValue() == ',':
                val = self.match_exact(COMMA, ",")

        val = self.match_exact(SEPARATOR, ";")
        print("<Separator>" + val + "</Separator>")

        print("</Query>")

    def query_create(self):
        print("<Query>")

        val = self.match_exact(KEYWORD, "CREATE")
        print("\t<Keyword>" + val + " ")

        val = self.match_exact(KEYWORD, "TABLE")
        print(val + "</Keyword>")

        val = self.match_type(ID)
        print("\t\t<Id>" + val + "</Id>")

        val = self.match_exact(SEPARATOR, "(")
        print("<Separator>" + val + "</Separator>")

        self.DefineIDList()

        val = self.match_exact(SEPARATOR, ")")
        print("<Separator>" + val + "</Separator>")

        val = self.match_exact(SEPARATOR, ";")
        print("<Separator>" + val + "</Separator>")

        print("</Query>")


    def query_format(self):

        result = ''
        while self.token.getTokenType() != EOI:
            val = self.token.getTokenValue()

            if val == "SELECT":
                result = result + self.query_format_select()

            if val == "INSERT":
                result = result + self.query_format_insert()

            if val == "CREATE":
                result = result + self.query_format_create()

            for i in range(Parser.option_indent_lines_number+1):
                result = result + "\n"

        return result

    def query_format_select(self):
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

        val = self.match_exact(SEPARATOR, ";")
        result = result + val

        return result

    def query_format_insert(self):
        result = self.match_exact(KEYWORD, "INSERT")

        result += ' ' + self.match_exact(KEYWORD, "INTO")

        val = self.ID_format()
        result = result + ' ' + val

        val = self.match_exact(SEPARATOR, "(")
        result = result + ' ' + val

        val = self.IDList_format()
        result = result + ' ' + val

        val = self.match_exact(SEPARATOR, ")")
        result = result + ' ' + val

        val = self.match_exact(KEYWORD, "VALUES")
        result = result + ' ' + val

        while self.token.getTokenValue() != ";":
            val = self.match_exact(SEPARATOR, "(")
            result = result + ' ' + val

            val = self.IDList_format()
            result = result + ' ' + val

            val = self.match_exact(SEPARATOR, ")")
            result = result + ' ' + val

            if self.token.getTokenValue() == ',':
                val = self.match_exact(COMMA, ",")
                result = result + ' ' + val
            else:
                break

        val = self.match_exact(SEPARATOR, ";")
        result = result + ' ' + val

        return result

    def query_format_create(self):
        val = self.match_exact(KEYWORD, "CREATE")
        result = val

        val = self.match_exact(KEYWORD, "TABLE")
        result = result + ' ' + val

        val = self.match_type(ID)
        result = result + ' ' + val

        val = self.match_exact(SEPARATOR, "(")
        if Parser.option_space_after_separator == 'true':
            result = result + ' ' + val + ' '
        else:
            result = result + ' ' + val

        val = self.DefineIDList_format()
        result = result + val

        val = self.match_exact(SEPARATOR, ")")
        if Parser.option_space_after_separator == 'true':
            result = result + ' ' + val
        else:
            result = result + val

        val = self.match_exact(SEPARATOR, ";")
        result = result + val

        return result


    def ID(self):
        val = self.match_type(ID)
        print("\t\t<Id>" + val + "</Id>")

    def ID_format(self):
        val = self.match_type(ID)
        return val

    #    """ IDList checks and builds the IDList output, making sure the input string 
    # follows: <id> {, <id>}. Any deviation from this will result in a syntax error. """

    def IDList(self):
        print("\t<IdList>")
        val = self.match_type(ID)
        print("\t\t<Id>" + val + "</Id>")

        """ This while loop deals with the optional reapeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != KEYWORD and self.token.getTokenValue() != ")" \
                and self.token.getTokenType() != EOI and self.token.getTokenValue() != ";":
            print("\t\t<Comma>" + self.match_type(COMMA) + "</Comma>")
            print("\t\t<Id>" + self.match_type(ID) + "</Id>")
        print("\t</IdList>")

    def IDList_format(self):
        val = self.match_type(ID)
        result = val

        """ This while loop deals with the optional reapeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != KEYWORD and self.token.getTokenValue() != ")"\
                and self.token.getTokenType() != EOI and self.token.getTokenValue() != ";":
            result = result + self.match_type(COMMA)
            if Parser.option_space_after_comma == 'true':
                result = result + ' ' + self.match_type(ID)
            else:
                result = result + self.match_type(ID)
        return result

    def ID_format(self):
        val = self.match_type(ID)
        return val

    def DefineIDList(self):
        print("\t<IdList>")

        val = self.match_type(TYPE_DEFINITION)
        print("\t\t<Type>" + val + "</Type>")
        print("\t\t<Id>" + self.match_type(ID) + "</Id>")


        """ This while loop deals with the optional repeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != SEPARATOR \
                and self.token.getTokenType() != KEYWORD and self.token.getTokenType() != EOI:
            print("\t\t<Comma>" + self.match_type(COMMA) + "</Comma>")
            print("\t\t<Type>" + self.match_type(TYPE_DEFINITION) + "</Type>")
            print("\t\t<Id>" + self.match_type(ID) + "</Id>")

        print("\t</IdList>")

    def DefineIDList_format(self):
        val = self.match_type(TYPE_DEFINITION)
        result = val

        val = self.match_type(ID)
        result = result + ' ' + val

        """ This while loop deals with the optional repeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != SEPARATOR \
                and self.token.getTokenType() != KEYWORD and self.token.getTokenType() != EOI:
            result = result + self.match_type(COMMA)

            if Parser.option_space_after_comma == 'true':
                result = result + self.match_type(TYPE_DEFINITION)
            else:
                result = result + self.match_type(TYPE_DEFINITION)

            result = result + ' ' + self.match_type(ID)
        return result

    def ValuesList(self):
        print("\t<IdList>")
        val = self.match_type(ID)
        print("\t\t<Id>" + val + "</Id>")

        """ This while loop deals with the optional reapeating part of IDList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != KEYWORD and self.token.getTokenValue() != ")" \
                and self.token.getTokenType() != EOI and self.token.getTokenValue() != ";":
            print("\t\t<Comma>" + self.match_type(COMMA) + "</Comma>")
            print("\t\t<Id>" + self.match_type(ID) + "</Id>")
        print("\t</IdList>")

    # """ CondList checks and builds the CondList output, making sure the input 
    # string follows: <Cond> {AND <Cond>}. Any deviation from this will result 
    # in a syntax error. """

    def condList(self):
        print("\t<CondList>")
        self.cond()
        """ This while loop deals with the optional reapeating part of CondList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != EOI and self.token.getTokenValue() != ";":
            print("\t\t<Keyword>" + self.match_exact(KEYWORD, "AND") + "</Keyword")
            self.cond()
        print("\t</CondList>")

    def condList_format(self):
        cond = self.cond_format()
        result = cond

        """ This while loop deals with the optional reapeating part of CondList, making sure
        that, if there are input values, they are correct and in the correct order """
        while self.token.getTokenType() != EOI and self.token.getTokenValue() != ";":
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
        else:
            self.error_type(token)
        self.token = self.lexer.nextToken()
        return result

    #    """ Match_type is a method that checks to make sure the the input token type value
    # (which is what the token should be) matches the actual token type. If they
    # do match it just moves to the next token, if not it calls the error_type. """

    def match_type(self, tp):
        print('match_exact: ', tp, ' value: ', self.token.getTokenValue())
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
        print('match_exact: ', tp, ' check: ', check, ' value: ', self.token.getTokenValue())
        val = self.token.getTokenValue()

        if (tp == KEYWORD):
            val = val.upper()

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
        print("Syntax error (type): expecting: "
              + typeToString(tp)
              + " ||| saw type: "
              + typeToString(self.token.getTokenType())
              + " ||| value: "
              + self.token.getTokenValue())
        sys.exit(1)

    #    """ Error_exact is the error method called if the value is wrong. It prints out an
    # error statement and then kills the program. """

    def error_exact(self, check):
        print("Syntax error (value): expecting: "
              + check
              + " ||| saw type: "
              + typeToString(self.token.getTokenType())
              + " ||| value: "
              + self.token.getTokenValue())
        sys.exit(1)
