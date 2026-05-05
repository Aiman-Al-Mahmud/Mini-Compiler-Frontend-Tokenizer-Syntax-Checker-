import re

def read_src_file(filename):
    with open(filename, 'r') as f:
        return f.read()

def tokenize(source_code):
    pattern = r'"[^"\n]*"|//.*|==|!=|<=|>=|&&|\|\||-?\d+(?:\.\d+)?|[A-Za-z_]\w*|[^\s]'
    tokens = re.findall(pattern, source_code)
    return tokens


KEYWORDS = {
    'int', 'float', 'double', 'char', 'string', 'bool',
    'if', 'else', 'while', 'for', 'return', 'void',
    'print', 'input', 'true', 'false', 'class', 'def'
}

TYPE_KEYWORDS = {
    'int', 'float', 'double', 'char', 'string', 'bool', 'void'
}

BOOLEAN_LITERALS = {'true', 'false'}

OPERATORS = {
    '+', '-', '*', '/', '%',
    '=', '==', '!=', '<', '>', '<=', '>=',
    '&&', '||', '!'
}

SPECIAL_CHARACTERS = {
    '(', ')', '{', '}', '[', ']',
    ';', ',', '.', ':', '#'
}


def classify_token(token):
    if token.startswith('//'):
        return 'Comment'
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return 'String'
    if token in BOOLEAN_LITERALS:
        return 'Boolean'
    if re.match(r'^-?\d+(?:\.\d+)?$', token):
        return 'Operand'
    if token in KEYWORDS:
        return 'Keyword'
    if token in OPERATORS:
        return 'Operator'
    if token in SPECIAL_CHARACTERS:
        return 'Special Character'
    if re.match(r'^[A-Za-z_]\w*$', token):
        return 'Identifier'
    return 'Unknown'


def remove_outer_quotes(token):
    if len(token) >= 2 and token[0] == '"' and token[-1] == '"':
        return token[1:-1]
    return token


def classify_all_tokens(tokens):
    return [(tok, classify_token(tok)) for tok in tokens] #lin3 31


def is_valid_expression(tokens, declared_ids):
    """
    expr = term (op term)*
    term = number | string | identifier | (expr)
    supports unary: -a, !a
    """
    if not tokens:
        return False, "empty expression"

    binary_ops = {
        "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||"
    }
    unary_ops = {"-", "!"}

    expect_term = True
    stack = []
    i = 0

    while i < len(tokens):
        tok = tokens[i]
        cat = classify_token(tok)

        if tok == "(":
            stack.append("(")
            expect_term = True
            i += 1
            continue

        if tok == ")":
            if not stack:
                return False, "unmatched ')'"
            if expect_term:
                return False, "empty parentheses or operator before ')'"
            stack.pop()
            expect_term = False
            i += 1
            continue

        if expect_term:
            if tok in unary_ops:
                i += 1
                continue
            if cat in ("Operand", "String", "Boolean"):
                expect_term = False
            elif cat == "Identifier":
                if tok not in declared_ids:
                    return False, f"undeclared identifier '{tok}'"
                expect_term = False
            else:
                return False, f"expected term, got '{tok}'"
        else:
            if tok in binary_ops:
                expect_term = True
            else:
                return False, f"expected operator, got '{tok}'"

        i += 1

    if stack:
        return False, "unmatched ("
    if expect_term:
        return False, "expression cannot end with operator"
    return True, ""


def validate_loop_header(tokens):
    if "(" not in tokens or ")" not in tokens:
        return False, "loop missing '(' or ')'"

    lpar = tokens.index("(")
    rpar = len(tokens) - 1 - tokens[::-1].index(")")
    if rpar <= lpar + 1:
        return False, "empty loop condition"

    if tokens[0] == "for":
        inner = tokens[lpar + 1 : rpar]
        if inner.count(";") != 2:
            return False, "invalid 'for' header; expected 2 ';'"

    return True, ""


def syntax_analysis(source_code):
    declared_ids = set()
    errors = []
    lines = source_code.splitlines()

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):   #(//...) are skipped immediately
            continue

        toks = tokenize(line)
        # drop comment token if present
        toks = [t for t in toks if not t.startswith("//")]
        if not toks:
            continue

        # --- loop headers: for (...) {  /  while (...) { ---
        if toks[0] in ("for", "while"):
            ok, msg = validate_loop_header(toks)
            if not ok:
                errors.append(f"Line {lineno}: {msg}")
            continue

        # --- declarations: int x = 10 ; ---
        if toks[0] in TYPE_KEYWORDS:
            if len(toks) < 3:
                errors.append(f"Line {lineno}: incomplete declaration")
                continue

            type_kw = toks[0]
            name = toks[1]

            if classify_token(name) != "Identifier":
                errors.append(
                    f"Line {lineno}: invalid identifier '{name}' after type '{type_kw}'"
                )
                continue

            if name in declared_ids:
                errors.append(f"Line {lineno}: redeclaration of identifier '{name}'")
            else:
                declared_ids.add(name)

            # just `int x ;`
            if len(toks) == 3 and toks[2] == ";":
                continue

            # expect `int x = expr ;`
            if "=" not in toks:
                errors.append(f"Line {lineno}: expected '=' in initialization of '{name}'")
                continue
            if toks[-1] != ";":
                errors.append(f"Line {lineno}: missing ';' at end of declaration")
                continue

            eq_index = toks.index("=")   #split left and right of =
            expr_tokens = toks[eq_index + 1 : -1]
            ok, msg = is_valid_expression(expr_tokens, declared_ids)
            if not ok:
                errors.append(f"Line {lineno}: invalid init expression: {msg}")
            continue

        # --- print statements: print ( expr ) ; ---
        if toks[0] == "print":
            if len(toks) < 4:
                errors.append(f"Line {lineno}: incomplete print statement")
                continue
            if toks[1] != "(" or toks[-2] != ")" or toks[-1] != ";":
                errors.append(f"Line {lineno}: invalid print statement syntax")
                continue

            expr_tokens = toks[2:-2]
            ok, msg = is_valid_expression(expr_tokens, declared_ids)
            if not ok:
                errors.append(f"Line {lineno}: invalid expression in print: {msg}")
            continue

        # --- assignments: id = expr ; ---
        if "=" in toks:
            if toks[-1] != ";":
                errors.append(f"Line {lineno}: missing ';' at end of assignment")
                continue

            name = toks[0]
            if classify_token(name) != "Identifier":
                errors.append(
                    f"Line {lineno}: invalid identifier, got '{name}'"
                )
                continue
            if name not in declared_ids:
                errors.append(
                    f"Line {lineno}: assignment to undeclared identifier '{name}'"
                )

            eq_index = toks.index("=")
            expr_tokens = toks[eq_index + 1 : -1]
            ok, msg = is_valid_expression(expr_tokens, declared_ids)
            if not ok:
                errors.append(f"Line {lineno}: invalid expression in assignment: {msg}")
            continue


    return errors

def main():
    src_file = "src code.txt"
    source_code = read_src_file(src_file)

    print("  SOURCE CODE")

    print(source_code)

    print("\n")

    tokens = tokenize(source_code) #line 7

    print("  TASK 1 : Token list")
    print("-" * 50)

    print(tokens)

    # Task 2 : identify 
    classified = classify_all_tokens(tokens)  #line 55

    print("\n")
    
    print("TASK 2 : Token identify")

    print("-" * 50)
    
    categories = {}
    for token, category in classified:
        if token not in categories.get(category, []):
            categories.setdefault(category, []).append(token)

    for cat, toks in categories.items():
        if cat == "String":
            display_toks = [remove_outer_quotes(t) for t in toks]
        else:
            display_toks = toks
        print(f"  {cat}s : {display_toks}")

    print("\n  TASK 3 : Syntax analysis")
    print("-" * 50)
    errors = syntax_analysis(source_code)
    if not errors:
        print("  No syntax errors found.")
    else:
        for e in errors:
            print(" ", e)

if __name__ == "__main__":
    main()
