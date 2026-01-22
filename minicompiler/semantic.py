class SemanticAnalyzer:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.symbol_table = {}

    # ---------------------------------
    # Utility Functions
    # ---------------------------------
    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        token = self.current_token()
        if token and token[0] == token_type:
            self.pos += 1
            return token
        else:
            line = token[2] if token else "EOF"
            raise Exception(f"Semantic Error at line {line}: Expected {token_type}")

    # ---------------------------------
    # Analyzer Entry Point
    # ---------------------------------
    def analyze(self):
        while self.current_token() is not None:
            self.statement()

        print("Semantic Analysis Completed Successfully")
        print("Symbol Table:", self.symbol_table)

    # ---------------------------------
    # Statements
    # ---------------------------------
    def statement(self):
        token = self.current_token()

        if token[0] in ('INT', 'BOOL'):
            self.decl_stmt()
        elif token[0] == 'ID':
            self.assign_stmt()
        elif token[0] == 'IF':
            self.if_stmt()
        elif token[0] == 'WHILE':
            self.while_stmt()
        else:
            raise Exception(
                f"Semantic Error at line {token[2]}: Invalid statement"
            )

    def stmt_list(self):
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.statement()

    # ---------------------------------
    # Declarations
    # ---------------------------------
    def decl_stmt(self):
        var_type = self.type_spec()
        var_token = self.eat('ID')
        var_name = var_token[1]

        if var_name in self.symbol_table:
            raise Exception(
                f"Semantic Error at line {var_token[2]}: Redeclaration of '{var_name}'"
            )

        self.symbol_table[var_name] = var_type

        # Optional initialization
        if self.current_token() and self.current_token()[0] == 'ASSIGN':
            self.eat('ASSIGN')
            expr_type = self.expr()

            if expr_type != var_type:
                raise Exception(
                    f"Semantic Error at line {var_token[2]}: Type mismatch in declaration"
                )

        self.eat('SEMICOLON')

    def type_spec(self):
        token = self.current_token()

        if token[0] == 'INT':
            self.eat('INT')
            return 'int'
        elif token[0] == 'BOOL':
            self.eat('BOOL')
            return 'bool'
        else:
            raise Exception(
                f"Semantic Error at line {token[2]}: Invalid type"
            )

    # ---------------------------------
    # Assignment
    # ---------------------------------
    def assign_stmt(self):
        var_token = self.eat('ID')
        var_name = var_token[1]

        if var_name not in self.symbol_table:
            raise Exception(
                f"Semantic Error at line {var_token[2]}: '{var_name}' not declared"
            )

        self.eat('ASSIGN')
        expr_type = self.expr()

        if expr_type != self.symbol_table[var_name]:
            raise Exception(
                f"Semantic Error at line {var_token[2]}: Type mismatch"
            )

        self.eat('SEMICOLON')

    # ---------------------------------
    # Expressions (Arithmetic)
    # ---------------------------------
    def expr(self):
        expr_type = self.term()

        while (self.current_token() and
               self.current_token()[0] == 'OP' and
               self.current_token()[1] in ('+', '-')):
            self.eat('OP')
            right_type = self.term()

            if expr_type != right_type:
                raise Exception("Semantic Error: Type mismatch in expression")

        return expr_type

    def term(self):
        term_type = self.factor()

        while (self.current_token() and
               self.current_token()[0] == 'OP' and
               self.current_token()[1] in ('*', '/')):
            self.eat('OP')
            right_type = self.factor()

            if term_type != right_type:
                raise Exception("Semantic Error: Type mismatch in term")

        return term_type

    def factor(self):
        token = self.current_token()

        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return 'int'

        elif token[0] == 'ID':
            var_name = token[1]
            if var_name not in self.symbol_table:
                raise Exception(
                    f"Semantic Error at line {token[2]}: '{var_name}' not declared"
                )
            self.eat('ID')
            return self.symbol_table[var_name]

        elif token[0] in ('TRUE', 'FALSE'):
            self.eat(token[0])
            return 'bool'

        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            expr_type = self.expr()
            self.eat('RPAREN')
            return expr_type

        else:
            raise Exception(
                f"Semantic Error at line {token[2]}: Invalid factor '{token[1]}'"
            )

    # ---------------------------------
    # Boolean / Relational Expressions
    # ---------------------------------
    def bool_expr(self):
        left_type = self.expr()

        if (self.current_token() and
            self.current_token()[0] == 'OP' and
            self.current_token()[1] in ('<', '>', '==')):

            self.eat('OP')
            right_type = self.expr()

            if left_type != right_type:
                raise Exception(
                    "Semantic Error: Type mismatch in relational expression"
                )

            return 'bool'
        else:
            raise Exception(
                "Semantic Error: Relational operator expected"
            )

    # ---------------------------------
    # Control Statements
    # ---------------------------------
    def if_stmt(self):
        self.eat('IF')
        self.eat('LPAREN')
        cond_type = self.bool_expr()

        if cond_type != 'bool':
            raise Exception("Semantic Error: if condition must be boolean")

        self.eat('RPAREN')
        self.eat('LBRACE')
        self.stmt_list()
        self.eat('RBRACE')

    def while_stmt(self):
        self.eat('WHILE')
        self.eat('LPAREN')
        cond_type = self.bool_expr()

        if cond_type != 'bool':
            raise Exception("Semantic Error: while condition must be boolean")

        self.eat('RPAREN')
        self.eat('LBRACE')
        self.stmt_list()
        self.eat('RBRACE')
