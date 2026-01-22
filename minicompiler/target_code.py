class TargetCodeGenerator:
    def __init__(self, icg_code):
        self.icg_code = icg_code
        self.target_code = []

    def generate(self):
        for line in self.icg_code:
            if '=' in line:
                left, right = line.split('=', 1)
                left = left.strip()
                right = right.strip()

                # Simple assignment (number or variable)
                if ' ' not in right:  
                    self.target_code.append(f"PUSH {right}")
                    self.target_code.append(f"POP {left}")
                else:  
                    # arithmetic operation, possibly involving temps
                    # detect if right contains temp variable
                    parts = right.split()
                    op1, op, op2 = parts

                    # If op1 is a temp and not used elsewhere, we can ignore storing it
                    self.target_code.append(f"PUSH {op1}")
                    self.target_code.append(f"PUSH {op2}")

                    if op == '+':
                        self.target_code.append("ADD")
                    elif op == '-':
                        self.target_code.append("SUB")
                    elif op == '*':
                        self.target_code.append("MUL")
                    elif op == '/':
                        self.target_code.append("DIV")

                    # Directly POP to the final variable if it's not a temp
                    if not left.startswith('t'):
                        self.target_code.append(f"POP {left}")
                    else:
                        # if left is temp, we may skip it
                        self.target_code.append(f"POP {left}")  # optional, depends on further use
        return self.target_code
