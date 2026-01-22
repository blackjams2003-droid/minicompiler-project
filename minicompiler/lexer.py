import re

TOKENS = [
    ('INT', r'int\b'),
    ('BOOL', r'bool\b'),
    ('IF', r'if\b'),
    ('WHILE', r'while\b'),

    # ✅ Boolean literals MUST be before ID
    ('TRUE', r'true\b'),
    ('FALSE', r'false\b'),

    ('NUMBER', r'\d+'),

    # Identifiers AFTER keywords
    ('ID', r'[a-zA-Z_]\w*'),

    ('EQ', r'=='),
    ('ASSIGN', r'='),
    ('OP', r'[+\-*/<>]'),
    ('SEMICOLON', r';'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),

    ('SKIP', r'[ \t]+'),
    ('NEWLINE', r'\n'),
    ('COMMENT', r'//.*'),
]

def tokenize(code):
    tokens = []
    pos = 0
    line = 1

    while pos < len(code):
        match = None
        for token_type, pattern in TOKENS:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                lexeme = match.group(0)
                if token_type in ('SKIP', 'COMMENT'):
                    pass
                elif token_type == 'NEWLINE':
                    line += 1
                else:
                    tokens.append((token_type, lexeme, line))
                pos = match.end()
                break

        if not match:
            raise Exception(
                f"Lexical Error at line {line}: Invalid character '{code[pos]}'"
            )

    return tokens
