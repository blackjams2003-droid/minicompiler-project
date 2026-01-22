class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tree = []

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

    def parse(self):
        self.tree = self.stmt_list()
        print("Syntax Analysis Completed Successfully")
        print("\n--- Parse Tree ---")
        self.print_tree(self.tree)

    def print_tree(self, node, level=0):
        print("  " * level + node[0])
        for child in node[1]:
            self.print_tree(child, level + 1)

    # -----------------------------
    # Statements
    # -----------------------------
    def stmt_list(self):
        children = []
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            children.append(self.statement())
        return ("stmt_list", children)

    def statement(self):
        token = self.current_token()
        if token[0] in ('INT', 'BOOL'):
            return self.decl_stmt()
        elif token[0] == 'ID':
            return self.assign_stmt()
        elif token[0] == 'IF':
            return self.if_stmt()
        elif token[0] == 'WHILE':
            return self.while_stmt()
        else:
            raise Exception(f"Syntax Error at line {token[2]}: Invalid statement")

    # -----------------------------
    # Declarations
    # -----------------------------
    def decl_stmt(self):
        children = []
        children.append(("TYPE", [("TOKEN", [(self.eat(self.current_token()[0])[1], [])])]))
        children.append(("ID", [("TOKEN", [(self.eat('ID')[1], [])])]))

        if self.current_token() and self.current_token()[0] == 'ASSIGN':
            children.append(("ASSIGN", [("TOKEN", [(self.eat('ASSIGN')[1], [])])]))
            children.append(self.expr())

        children.append(("SEMICOLON", [("TOKEN", [(self.eat('SEMICOLON')[1], [])])]))
        return ("decl_stmt", children)

    def assign_stmt(self):
        children = []
        children.append(("ID", [("TOKEN", [(self.eat('ID')[1], [])])]))
        children.append(("ASSIGN", [("TOKEN", [(self.eat('ASSIGN')[1], [])])]))
        children.append(self.expr())
        children.append(("SEMICOLON", [("TOKEN", [(self.eat('SEMICOLON')[1], [])])]))
        return ("assign_stmt", children)

    # -----------------------------
    # Expressions
    # -----------------------------
    def expr(self):
        children = [self.term()]
        while (self.current_token() and
               self.current_token()[0] == 'OP' and
               self.current_token()[1] in ('+', '-')):
            children.append(("OP", [("TOKEN", [(self.eat('OP')[1], [])])]))
            children.append(self.term())
        return ("expr", children)

    def term(self):
        children = [self.factor()]
        while (self.current_token() and
               self.current_token()[0] == 'OP' and
               self.current_token()[1] in ('*', '/')):
            children.append(("OP", [("TOKEN", [(self.eat('OP')[1], [])])]))
            children.append(self.factor())
        return ("term", children)

    def factor(self):
        token = self.current_token()

        if token[0] == 'NUMBER':
            val = self.eat('NUMBER')[1]
            return ("NUMBER", [("TOKEN", [(val, [])])])

        elif token[0] == 'ID':
            val = self.eat('ID')[1]
            return ("ID", [("TOKEN", [(val, [])])])

        elif token[0] in ('TRUE', 'FALSE'):   # ✅ ADDED
            val = self.eat(token[0])[1]
            return ("BOOL_CONST", [("TOKEN", [(val, [])])])

        elif token[0] == 'LPAREN':
            self.eat('LPAREN')
            node = self.expr()
            self.eat('RPAREN')
            return ("paren_expr", [node])

        else:
            raise Exception(
                f"Syntax Error at line {token[2]}: Invalid factor '{token[1]}'"
            )

    # -----------------------------
    # Boolean Expressions
    # -----------------------------
    def bool_expr(self):
        children = [self.expr()]
        if (self.current_token() and
            self.current_token()[0] == 'OP' and
            self.current_token()[1] in ('<', '>', '==')):
            children.append(("OP", [("TOKEN", [(self.eat('OP')[1], [])])]))
            children.append(self.expr())
            return ("bool_expr", children)
        else:
            token = self.current_token()
            raise Exception(
                f"Syntax Error at line {token[2]}: Relational operator expected"
            )

    # -----------------------------
    # Control Statements
    # -----------------------------
    def if_stmt(self):
        children = []
        children.append(("IF", [("TOKEN", [(self.eat('IF')[1], [])])]))
        children.append(("LPAREN", [("TOKEN", [(self.eat('LPAREN')[1], [])])]))
        children.append(self.bool_expr())
        children.append(("RPAREN", [("TOKEN", [(self.eat('RPAREN')[1], [])])]))
        children.append(("LBRACE", [("TOKEN", [(self.eat('LBRACE')[1], [])])]))
        children.append(self.stmt_list())
        children.append(("RBRACE", [("TOKEN", [(self.eat('RBRACE')[1], [])])]))
        return ("if_stmt", children)

    def while_stmt(self):
        children = []
        children.append(("WHILE", [("TOKEN", [(self.eat('WHILE')[1], [])])]))
        children.append(("LPAREN", [("TOKEN", [(self.eat('LPAREN')[1], [])])]))
        children.append(self.bool_expr())
        children.append(("RPAREN", [("TOKEN", [(self.eat('RPAREN')[1], [])])]))
        children.append(("LBRACE", [("TOKEN", [(self.eat('LBRACE')[1], [])])]))
        children.append(self.stmt_list())
        children.append(("RBRACE", [("TOKEN", [(self.eat('RBRACE')[1], [])])]))
        return ("while_stmt", children)
