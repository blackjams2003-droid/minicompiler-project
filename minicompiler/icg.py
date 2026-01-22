class IntermediateCodeGenerator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.temp_count = 0
        self.label_count = 0
        self.code = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type):
        token = self.current_token()
        if token and token[0] == token_type:
            self.pos += 1
            return token
        else:
            line = token[2] if token else 'EOF'
            raise Exception(f"Syntax Error at line {line}: Expected {token_type}")

    def generate(self):
        while self.current_token() is not None:
            self.statement()
        return self.code

    # -----------------------------
    # Statements
    # -----------------------------
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
                f"ICG Error at line {token[2]}: Invalid statement '{token[1]}'"
            )

    def stmt_list(self):
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.statement()

    # -----------------------------
    # Declarations
    # -----------------------------
    def decl_stmt(self):
        self.eat(self.current_token()[0])  # INT or BOOL
        var_token = self.eat('ID')
        var_name = var_token[1]

        # support initialization
        if self.current_token() and self.current_token()[0] == 'ASSIGN':
            self.eat('ASSIGN')
            result, _ = self.expr()
            self.code.append(f"{var_name} = {result}")

        self.eat('SEMICOLON')

    # -----------------------------
    # Assignment
    # -----------------------------
    def assign_stmt(self):
        var_token = self.eat('ID')
        var_name = var_token[1]
        self.eat('ASSIGN')
        result, _ = self.expr()
        self.eat('SEMICOLON')
        self.code.append(f"{var_name} = {result}")

    # -----------------------------
    # Arithmetic Expressions with Constant Folding
    # -----------------------------
    def expr(self):
        left_val, left_code = self.term()
        while (self.current_token() and
               self.current_token()[0] == 'OP' and
               self.current_token()[1] in ('+', '-')):
            op = self.eat('OP')[1]
            right_val, right_code = self.term()

            # Constant folding
            if left_val.isdigit() and right_val.isdigit():
                left_val = str(eval(f"{left_val}{op}{right_val}"))
            else:
                temp = self.new_temp()
                self.code.append(f"{temp} = {left_val} {op} {right_val}")
                left_val = temp

        return left_val, []

    def term(self):
        left_val, left_code = self.factor()
        while (self.current_token() and
               self.current_token()[0] == 'OP' and
               self.current_token()[1] in ('*', '/')):
            op = self.eat('OP')[1]
            right_val, right_code = self.factor()

            # Constant folding
            if left_val.isdigit() and right_val.isdigit():
                left_val = str(eval(f"{left_val}{op}{right_val}"))
            else:
                temp = self.new_temp()
                self.code.append(f"{temp} = {left_val} {op} {right_val}")
                left_val = temp

        return left_val, []

    def factor(self):
        token = self.current_token()
        if token[0] == 'NUMBER':
            self.eat('NUMBER')
            return token[1], []
        elif token[0] == 'ID':
            self.eat('ID')
            return token[1], []
        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            val, _ = self.expr()
            self.eat('RPAREN')
            return val, []
        else:
            raise Exception(
                f"ICG Error at line {token[2]}: Invalid factor '{token[1]}'"
            )

    # -----------------------------
    # Boolean / Relational Expression
    # -----------------------------
    def bool_expr(self):
        left = self.expr()[0]

        if (self.current_token() and
            self.current_token()[0] == 'OP' and
            self.current_token()[1] in ('<', '>', '==')):

            op = self.eat('OP')[1]
            right = self.expr()[0]
            temp = self.new_temp()
            self.code.append(f"{temp} = {left} {op} {right}")
            return temp
        else:
            raise Exception("ICG Error: Relational operator expected")

    # -----------------------------
    # Control Statements
    # -----------------------------
    def if_stmt(self):
        self.eat('IF')
        self.eat('LPAREN')
        cond = self.bool_expr()
        self.eat('RPAREN')

        label_end = self.new_label()
        self.code.append(f"IF_FALSE {cond} GOTO {label_end}")

        self.eat('LBRACE')
        self.stmt_list()
        self.eat('RBRACE')

        self.code.append(f"{label_end}:")

    def while_stmt(self):
        self.eat('WHILE')
        start_label = self.new_label()
        end_label = self.new_label()

        self.code.append(f"{start_label}:")

        self.eat('LPAREN')
        cond = self.bool_expr()
        self.eat('RPAREN')

        self.code.append(f"IF_FALSE {cond} GOTO {end_label}")

        self.eat('LBRACE')
        self.stmt_list()
        self.eat('RBRACE')

        self.code.append(f"GOTO {start_label}")
        self.code.append(f"{end_label}:")
