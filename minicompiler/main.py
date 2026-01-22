# main.py
from lexer import tokenize
from syntax_parser import Parser         # replace with your parser file/module
from semantic import SemanticAnalyzer   # replace with your semantic analyzer file/module
from icg import IntermediateCodeGenerator

def main():
    # Read program from file
    try:
        with open("test.min", "r") as f:
            source_code = f.read()
    except FileNotFoundError:
        print("Error: test.min file not found")
        return

    # -------------------------
    # Step 1: Lexical Analysis
    # -------------------------
    try:
        tokens = tokenize(source_code)
        print("Tokens:")
        for t in tokens:
            print(t)
        print("\n--- Lexical Analysis Completed ---\n")
    except Exception as e:
        print("Lexical Error:", e)
        return

    # -------------------------
    # Step 2: Syntax Analysis
    # -------------------------
    try:
        parser = Parser(tokens)
        parser.parse()  # Parser should print only once internally
    except Exception as e:
        print("Syntax Error:", e)
        return

    # -------------------------
    # Step 3: Semantic Analysis
    # -------------------------
    try:
        analyzer = SemanticAnalyzer(tokens)
        analyzer.analyze()  # Analyzer prints only once internally
    except Exception as e:
        print("Semantic Error:", e)
        return

    # -------------------------
    # Step 4: Intermediate Code Generation
    # -------------------------
    try:
        icg = IntermediateCodeGenerator(tokens)
        code = icg.generate()
        print("\n--- Intermediate Code (3-address code) ---")
        for line in code:
            print(line)
    except Exception as e:
        print("ICG Error:", e)
        return


if __name__ == "__main__":
    main()
