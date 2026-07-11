#!/usr/bin/env python3
"""
Petal -- a small, Python-flavored scripting language.

Single-file implementation: lexer, parser, tree-walking interpreter,
and a CLI/REPL. See README.md for the language reference.

Usage:
    python3 petal.py script.petal      # run a file
    python3 petal.py                   # start the REPL
"""

import sys


# =====================================================================
# Errors
# =====================================================================

class PetalError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(self.format())

    def format(self):
        if self.line is not None:
            return f"line {self.line}: {self.message}"
        return self.message


class PetalSyntaxError(PetalError):
    pass


class PetalRuntimeError(PetalError):
    pass


# =====================================================================
# Lexer
# =====================================================================

KEYWORDS = {
    "if", "elif", "else", "while", "for", "in", "def", "return",
    "break", "continue", "and", "or", "not", "True", "False", "None",
}

TWO_CHAR_OPS = ("==", "!=", "<=", ">=", "//", "+=", "-=", "*=", "/=", "%=")
SINGLE_CHAR_OPS = set("+-*/%<>=,:.()[]{}!")


class Token:
    __slots__ = ("type", "value", "line")

    def __init__(self, type_, value, line):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, line={self.line})"


class Lexer:
    def __init__(self, source):
        self.lines = source.split("\n")
        self.tokens = []
        self.indents = [0]
        self.paren_depth = 0

    def error(self, msg, line):
        raise PetalSyntaxError(msg, line)

    def tokenize(self):
        for lineno, raw_line in enumerate(self.lines, start=1):
            self.tokenize_line(raw_line, lineno)
        last_line = len(self.lines) + 1
        while len(self.indents) > 1:
            self.indents.pop()
            self.tokens.append(Token("DEDENT", None, last_line))
        self.tokens.append(Token("EOF", None, last_line))
        return self.tokens

    def tokenize_line(self, raw_line, lineno):
        i = 0
        n = len(raw_line)

        if self.paren_depth == 0:
            indent = 0
            while i < n and raw_line[i] in (" ", "\t"):
                if raw_line[i] == "\t":
                    self.error("tabs are not allowed for indentation -- use spaces", lineno)
                indent += 1
                i += 1
            rest = raw_line[i:]
            if rest.strip() == "" or rest.strip().startswith("#"):
                return
            if indent > self.indents[-1]:
                self.indents.append(indent)
                self.tokens.append(Token("INDENT", None, lineno))
            else:
                while indent < self.indents[-1]:
                    self.indents.pop()
                    self.tokens.append(Token("DEDENT", None, lineno))
                if indent != self.indents[-1]:
                    self.error("inconsistent indentation", lineno)
        else:
            if raw_line.strip() == "":
                return

        while i < n:
            c = raw_line[i]
            if c in (" ", "\t"):
                i += 1
                continue
            if c == "#":
                break
            if c.isdigit():
                j = i
                is_float = False
                while j < n and (raw_line[j].isdigit() or raw_line[j] == "."):
                    if raw_line[j] == ".":
                        if is_float or j + 1 >= n or not raw_line[j + 1].isdigit():
                            break
                        is_float = True
                    j += 1
                text = raw_line[i:j]
                value = float(text) if is_float else int(text)
                self.tokens.append(Token("NUMBER", value, lineno))
                i = j
                continue
            if c.isalpha() or c == "_":
                j = i
                while j < n and (raw_line[j].isalnum() or raw_line[j] == "_"):
                    j += 1
                text = raw_line[i:j]
                if (c in ("f", "F")) and j - i == 1 and j < n and raw_line[j] in ("'", '"'):
                    token, i = self.read_string(raw_line, j, lineno, is_fstring=True)
                    self.tokens.append(token)
                    continue
                if text in KEYWORDS:
                    self.tokens.append(Token(text.upper(), text, lineno))
                else:
                    self.tokens.append(Token("NAME", text, lineno))
                i = j
                continue
            if c in ("'", '"'):
                token, i = self.read_string(raw_line, i, lineno, is_fstring=False)
                self.tokens.append(token)
                continue
            if raw_line[i:i + 2] == "**":
                self.tokens.append(Token("**", "**", lineno))
                i += 2
                continue
            two = raw_line[i:i + 2]
            if two in TWO_CHAR_OPS:
                self.tokens.append(Token(two, two, lineno))
                i += 2
                continue
            if c in SINGLE_CHAR_OPS:
                if c in "([{":
                    self.paren_depth += 1
                elif c in ")]}":
                    self.paren_depth = max(0, self.paren_depth - 1)
                self.tokens.append(Token(c, c, lineno))
                i += 1
                continue
            self.error(f"unexpected character {c!r}", lineno)

        if self.paren_depth == 0:
            if self.tokens and self.tokens[-1].type not in ("NEWLINE", "INDENT", "DEDENT"):
                self.tokens.append(Token("NEWLINE", None, lineno))

    def read_string(self, raw_line, i, lineno, is_fstring):
        quote = raw_line[i]
        i += 1
        n = len(raw_line)
        buf = []
        while i < n and raw_line[i] != quote:
            ch = raw_line[i]
            if ch == "\\" and i + 1 < n:
                nxt = raw_line[i + 1]
                escapes = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'", "{": "{", "}": "}"}
                buf.append(escapes.get(nxt, nxt))
                i += 2
                continue
            buf.append(ch)
            i += 1
        if i >= n:
            self.error("unterminated string literal", lineno)
        i += 1
        text = "".join(buf)
        ttype = "FSTRING" if is_fstring else "STRING"
        return Token(ttype, text, lineno), i


# =====================================================================
# AST Nodes
# =====================================================================

class Node:
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements


class NumLit(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line


class StrLit(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line


class FStrLit(Node):
    def __init__(self, parts, line):
        self.parts, self.line = parts, line


class BoolLit(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line


class NoneLit(Node):
    def __init__(self, line):
        self.line = line


class ListLit(Node):
    def __init__(self, elements, line):
        self.elements, self.line = elements, line


class DictLit(Node):
    def __init__(self, pairs, line):
        self.pairs, self.line = pairs, line


class Var(Node):
    def __init__(self, name, line):
        self.name, self.line = name, line


class Assign(Node):
    def __init__(self, target, value, line):
        self.target, self.value, self.line = target, value, line


class AugAssign(Node):
    def __init__(self, target, op, value, line):
        self.target, self.op, self.value, self.line = target, op, value, line


class BinOp(Node):
    def __init__(self, left, op, right, line):
        self.left, self.op, self.right, self.line = left, op, right, line


class LogicalOp(Node):
    def __init__(self, left, op, right, line):
        self.left, self.op, self.right, self.line = left, op, right, line


class UnaryOp(Node):
    def __init__(self, op, operand, line):
        self.op, self.operand, self.line = op, operand, line


class Call(Node):
    def __init__(self, callee, args, line):
        self.callee, self.args, self.line = callee, args, line


class Index(Node):
    def __init__(self, obj, index, line):
        self.obj, self.index, self.line = obj, index, line


class Slice(Node):
    def __init__(self, obj, start, stop, line):
        self.obj, self.start, self.stop, self.line = obj, start, stop, line


class Attribute(Node):
    def __init__(self, obj, name, line):
        self.obj, self.name, self.line = obj, name, line


class If(Node):
    def __init__(self, cond, body, elifs, orelse, line):
        self.cond, self.body, self.elifs, self.orelse, self.line = cond, body, elifs, orelse, line


class While(Node):
    def __init__(self, cond, body, line):
        self.cond, self.body, self.line = cond, body, line


class For(Node):
    def __init__(self, var, iterable, body, line):
        self.var, self.iterable, self.body, self.line = var, iterable, body, line


class FunctionDef(Node):
    def __init__(self, name, params, body, line):
        self.name, self.params, self.body, self.line = name, params, body, line


class Return(Node):
    def __init__(self, value, line):
        self.value, self.line = value, line


class Break(Node):
    def __init__(self, line):
        self.line = line


class Continue(Node):
    def __init__(self, line):
        self.line = line


class ExprStmt(Node):
    def __init__(self, expr, line):
        self.expr, self.line = expr, line


# =====================================================================
# Parser
# =====================================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        idx = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[idx]

    def at(self, *types):
        return self.peek().type in types

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, type_, msg=None):
        if not self.at(type_):
            tok = self.peek()
            raise PetalSyntaxError(msg or f"expected {type_!r} but found {tok.type!r}", tok.line)
        return self.advance()

    def skip_newlines(self):
        while self.at("NEWLINE"):
            self.advance()

    # ---- program / blocks ------------------------------------------------

    def parse_program(self):
        stmts = []
        self.skip_newlines()
        while not self.at("EOF"):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        return Program(stmts)

    def parse_block(self):
        self.expect("NEWLINE")
        self.expect("INDENT")
        stmts = []
        self.skip_newlines()
        while not self.at("DEDENT") and not self.at("EOF"):
            stmts.append(self.parse_statement())
            self.skip_newlines()
        self.expect("DEDENT")
        return stmts

    # ---- statements --------------------------------------------------

    def parse_statement(self):
        tok = self.peek()
        if tok.type == "IF":
            return self.parse_if()
        if tok.type == "WHILE":
            return self.parse_while()
        if tok.type == "FOR":
            return self.parse_for()
        if tok.type == "DEF":
            return self.parse_funcdef()
        if tok.type == "RETURN":
            return self.parse_return()
        if tok.type == "BREAK":
            self.advance()
            self.expect("NEWLINE")
            return Break(tok.line)
        if tok.type == "CONTINUE":
            self.advance()
            self.expect("NEWLINE")
            return Continue(tok.line)
        return self.parse_simple_stmt()

    def parse_if(self):
        line = self.advance().line
        cond = self.parse_expression()
        self.expect(":")
        body = self.parse_block()
        elifs = []
        while self.at("ELIF"):
            self.advance()
            econd = self.parse_expression()
            self.expect(":")
            ebody = self.parse_block()
            elifs.append((econd, ebody))
        orelse = []
        if self.at("ELSE"):
            self.advance()
            self.expect(":")
            orelse = self.parse_block()
        return If(cond, body, elifs, orelse, line)

    def parse_while(self):
        line = self.advance().line
        cond = self.parse_expression()
        self.expect(":")
        body = self.parse_block()
        return While(cond, body, line)

    def parse_for(self):
        line = self.advance().line
        varname = self.expect("NAME").value
        self.expect("IN")
        iterable = self.parse_expression()
        self.expect(":")
        body = self.parse_block()
        return For(varname, iterable, body, line)

    def parse_funcdef(self):
        line = self.advance().line
        name = self.expect("NAME").value
        self.expect("(")
        params = []
        if not self.at(")"):
            params.append(self.expect("NAME").value)
            while self.at(","):
                self.advance()
                params.append(self.expect("NAME").value)
        self.expect(")")
        self.expect(":")
        body = self.parse_block()
        return FunctionDef(name, params, body, line)

    def parse_return(self):
        line = self.advance().line
        value = None if self.at("NEWLINE") else self.parse_expression()
        self.expect("NEWLINE")
        return Return(value, line)

    def parse_simple_stmt(self):
        expr = self.parse_expression()
        line = expr.line
        if self.at("="):
            self.advance()
            value = self.parse_expression()
            self.check_assignable(expr)
            self.expect("NEWLINE")
            return Assign(expr, value, line)
        if self.at("+=", "-=", "*=", "/=", "%="):
            op = self.advance().type[0]
            value = self.parse_expression()
            self.check_assignable(expr)
            self.expect("NEWLINE")
            return AugAssign(expr, op, value, line)
        self.expect("NEWLINE")
        return ExprStmt(expr, line)

    def check_assignable(self, node):
        if not isinstance(node, (Var, Index)):
            raise PetalSyntaxError("invalid assignment target", getattr(node, "line", None))

    # ---- expressions (precedence climbing) ----------------------------

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.at("OR"):
            line = self.advance().line
            right = self.parse_and()
            left = LogicalOp(left, "or", right, line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.at("AND"):
            line = self.advance().line
            right = self.parse_not()
            left = LogicalOp(left, "and", right, line)
        return left

    def parse_not(self):
        if self.at("NOT"):
            line = self.advance().line
            operand = self.parse_not()
            return UnaryOp("not", operand, line)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_addition()
        while True:
            if self.at("NOT") and self.peek(1).type == "IN":
                self.advance()
                self.advance()
                right = self.parse_addition()
                left = BinOp(left, "not in", right, left.line)
            elif self.at("IN"):
                self.advance()
                right = self.parse_addition()
                left = BinOp(left, "in", right, left.line)
            elif self.at("==", "!=", "<", ">", "<=", ">="):
                op = self.advance().type
                right = self.parse_addition()
                left = BinOp(left, op, right, left.line)
            else:
                break
        return left

    def parse_addition(self):
        left = self.parse_term()
        while self.at("+", "-"):
            op = self.advance().type
            right = self.parse_term()
            left = BinOp(left, op, right, left.line)
        return left

    def parse_term(self):
        left = self.parse_unary()
        while self.at("*", "/", "//", "%"):
            op = self.advance().type
            right = self.parse_unary()
            left = BinOp(left, op, right, left.line)
        return left

    def parse_unary(self):
        if self.at("-", "+"):
            op = self.advance().type
            operand = self.parse_unary()
            return UnaryOp(op, operand, operand.line)
        return self.parse_power()

    def parse_power(self):
        base = self.parse_postfix()
        if self.at("**"):
            line = self.advance().line
            exponent = self.parse_unary()
            return BinOp(base, "**", exponent, line)
        return base

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.at("("):
                line = self.advance().line
                args = []
                if not self.at(")"):
                    args.append(self.parse_expression())
                    while self.at(","):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(")")
                expr = Call(expr, args, line)
            elif self.at("["):
                line = self.advance().line
                start = None if self.at(":") else self.parse_expression()
                if self.at(":"):
                    self.advance()
                    stop = None if self.at("]") else self.parse_expression()
                    self.expect("]")
                    expr = Slice(expr, start, stop, line)
                else:
                    self.expect("]")
                    expr = Index(expr, start, line)
            elif self.at("."):
                self.advance()
                name_tok = self.expect("NAME")
                expr = Attribute(expr, name_tok.value, name_tok.line)
            else:
                break
        return expr

    def parse_primary(self):
        tok = self.peek()
        if tok.type == "NUMBER":
            self.advance(); return NumLit(tok.value, tok.line)
        if tok.type == "STRING":
            self.advance(); return StrLit(tok.value, tok.line)
        if tok.type == "FSTRING":
            self.advance(); return self.parse_fstring(tok.value, tok.line)
        if tok.type == "TRUE":
            self.advance(); return BoolLit(True, tok.line)
        if tok.type == "FALSE":
            self.advance(); return BoolLit(False, tok.line)
        if tok.type == "NONE":
            self.advance(); return NoneLit(tok.line)
        if tok.type == "NAME":
            self.advance(); return Var(tok.value, tok.line)
        if tok.type == "(":
            self.advance()
            expr = self.parse_expression()
            self.expect(")")
            return expr
        if tok.type == "[":
            self.advance()
            elements = []
            if not self.at("]"):
                elements.append(self.parse_expression())
                while self.at(","):
                    self.advance()
                    if self.at("]"):
                        break
                    elements.append(self.parse_expression())
            self.expect("]")
            return ListLit(elements, tok.line)
        if tok.type == "{":
            self.advance()
            pairs = []
            if not self.at("}"):
                k = self.parse_expression()
                self.expect(":")
                v = self.parse_expression()
                pairs.append((k, v))
                while self.at(","):
                    self.advance()
                    if self.at("}"):
                        break
                    k = self.parse_expression()
                    self.expect(":")
                    v = self.parse_expression()
                    pairs.append((k, v))
            self.expect("}")
            return DictLit(pairs, tok.line)
        raise PetalSyntaxError(f"unexpected token {tok.type!r}", tok.line)

    def parse_fstring(self, text, line):
        parts = []
        buf = []
        i, n = 0, len(text)
        while i < n:
            c = text[i]
            if c == "{":
                if buf:
                    parts.append(("str", "".join(buf))); buf = []
                depth = 1
                j = i + 1
                start = j
                while j < n and depth > 0:
                    if text[j] == "{":
                        depth += 1
                    elif text[j] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                if depth != 0:
                    raise PetalSyntaxError("unterminated '{' in f-string", line)
                expr_src = text[start:j]
                sub_tokens = Lexer(expr_src).tokenize()
                expr_node = Parser(sub_tokens).parse_expression()
                parts.append(("expr", expr_node))
                i = j + 1
            else:
                buf.append(c)
                i += 1
        if buf:
            parts.append(("str", "".join(buf)))
        return FStrLit(parts, line)


# =====================================================================
# Runtime
# =====================================================================

class PetalFunction:
    def __init__(self, name, params, body, closure):
        self.name, self.params, self.body, self.closure = name, params, body, closure

    def __repr__(self):
        return f"<function {self.name}>"


class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def get(self, name, line):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise PetalRuntimeError(f"name '{name}' is not defined", line)

    def assign(self, name, value):
        self.vars[name] = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self, input_fn=None, output_fn=None):
        self.globals = Environment()
        self.input_fn = input_fn or (lambda prompt="": input(prompt))
        self.output_fn = output_fn or (lambda text: print(text))
        self.setup_builtins()

    # ---- display / coercion helpers -----------------------------------

    def petal_repr(self, value):
        if value is None:
            return "None"
        if value is True:
            return "True"
        if value is False:
            return "False"
        if isinstance(value, str):
            return value
        if isinstance(value, float):
            return repr(value)
        if isinstance(value, list):
            return "[" + ", ".join(self.petal_debug(v) for v in value) + "]"
        if isinstance(value, dict):
            items = ", ".join(f"{self.petal_debug(k)}: {self.petal_debug(v)}" for k, v in value.items())
            return "{" + items + "}"
        if isinstance(value, range):
            return f"range({value.start}, {value.stop}, {value.step})"
        if isinstance(value, PetalFunction):
            return f"<function {value.name}>"
        return str(value)

    def petal_debug(self, value):
        if isinstance(value, str):
            return f'"{value}"'
        return self.petal_repr(value)

    def is_truthy(self, value):
        if value is None or value is False:
            return False
        if value is True:
            return True
        if isinstance(value, (int, float, str, list, dict)):
            return len(value) != 0 if isinstance(value, (str, list, dict)) else value != 0
        return True

    def type_name(self, value):
        if value is None: return "None"
        if isinstance(value, bool): return "bool"
        if isinstance(value, int): return "int"
        if isinstance(value, float): return "float"
        if isinstance(value, str): return "str"
        if isinstance(value, list): return "list"
        if isinstance(value, dict): return "dict"
        if isinstance(value, range): return "range"
        if isinstance(value, PetalFunction): return "function"
        return type(value).__name__

    # ---- built-ins ------------------------------------------------------

    def setup_builtins(self):
        def b_print(*args):
            self.output_fn(" ".join(self.petal_repr(a) for a in args))
            return None

        def b_len(x):
            try:
                return len(x)
            except TypeError:
                raise PetalRuntimeError(f"object of type '{self.type_name(x)}' has no len()")

        def b_str(x=""):
            return self.petal_repr(x)

        def b_int(x=0):
            try:
                return int(x)
            except (ValueError, TypeError):
                raise PetalRuntimeError(f"cannot convert {self.petal_debug(x)} to int")

        def b_float(x=0):
            try:
                return float(x)
            except (ValueError, TypeError):
                raise PetalRuntimeError(f"cannot convert {self.petal_debug(x)} to float")

        def b_bool(x=False):
            return self.is_truthy(x)

        def b_sorted(x, reverse=False):
            return sorted(x, reverse=bool(reverse))

        def b_round(x, n=0):
            return round(x, n) if n else round(x)

        self.builtins = {
            "print": b_print, "len": b_len, "range": range,
            "str": b_str, "int": b_int, "float": b_float, "bool": b_bool,
            "type": self.type_name, "abs": abs, "min": min, "max": max, "sum": sum,
            "sorted": b_sorted, "round": b_round,
            "input": lambda prompt="": self.input_fn(prompt),
        }
        for name, fn in self.builtins.items():
            self.globals.assign(name, fn)

    # ---- statement execution --------------------------------------------

    def run(self, program):
        self.exec_block(program.statements, self.globals)

    def exec_block(self, statements, env):
        for stmt in statements:
            self.exec_stmt(stmt, env)

    def exec_stmt(self, node, env):
        method = getattr(self, "exec_" + type(node).__name__, None)
        if method is None:
            raise PetalRuntimeError(f"cannot execute {type(node).__name__}", getattr(node, "line", None))
        return method(node, env)

    def exec_ExprStmt(self, node, env):
        self.eval_expr(node.expr, env)

    def exec_Assign(self, node, env):
        value = self.eval_expr(node.value, env)
        self.assign_target(node.target, value, env)

    def exec_AugAssign(self, node, env):
        current = self.eval_expr(node.target, env)
        rhs = self.eval_expr(node.value, env)
        value = self.apply_binop(node.op, current, rhs, node.line)
        self.assign_target(node.target, value, env)

    def assign_target(self, target, value, env):
        if isinstance(target, Var):
            env.assign(target.name, value)
        elif isinstance(target, Index):
            obj = self.eval_expr(target.obj, env)
            idx = self.eval_expr(target.index, env)
            try:
                obj[idx] = value
            except (TypeError, IndexError, KeyError) as e:
                raise PetalRuntimeError(str(e), target.line)
        else:
            raise PetalRuntimeError("invalid assignment target", getattr(target, "line", None))

    def exec_If(self, node, env):
        if self.is_truthy(self.eval_expr(node.cond, env)):
            self.exec_block(node.body, env)
            return
        for econd, ebody in node.elifs:
            if self.is_truthy(self.eval_expr(econd, env)):
                self.exec_block(ebody, env)
                return
        if node.orelse:
            self.exec_block(node.orelse, env)

    def exec_While(self, node, env):
        while self.is_truthy(self.eval_expr(node.cond, env)):
            try:
                self.exec_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_For(self, node, env):
        iterable = self.eval_expr(node.iterable, env)
        try:
            it = iter(iterable)
        except TypeError:
            raise PetalRuntimeError(f"'{self.type_name(iterable)}' object is not iterable", node.line)
        for item in it:
            env.assign(node.var, item)
            try:
                self.exec_block(node.body, env)
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def exec_FunctionDef(self, node, env):
        env.assign(node.name, PetalFunction(node.name, node.params, node.body, env))

    def exec_Return(self, node, env):
        value = self.eval_expr(node.value, env) if node.value is not None else None
        raise ReturnSignal(value)

    def exec_Break(self, node, env):
        raise BreakSignal()

    def exec_Continue(self, node, env):
        raise ContinueSignal()

    # ---- expression evaluation -------------------------------------------

    def eval_expr(self, node, env):
        method = getattr(self, "eval_" + type(node).__name__, None)
        if method is None:
            raise PetalRuntimeError(f"cannot evaluate {type(node).__name__}", getattr(node, "line", None))
        return method(node, env)

    def eval_NumLit(self, node, env): return node.value
    def eval_StrLit(self, node, env): return node.value
    def eval_BoolLit(self, node, env): return node.value
    def eval_NoneLit(self, node, env): return None

    def eval_FStrLit(self, node, env):
        out = []
        for kind, val in node.parts:
            out.append(val if kind == "str" else self.petal_repr(self.eval_expr(val, env)))
        return "".join(out)

    def eval_ListLit(self, node, env):
        return [self.eval_expr(e, env) for e in node.elements]

    def eval_DictLit(self, node, env):
        result = {}
        for k, v in node.pairs:
            result[self.eval_expr(k, env)] = self.eval_expr(v, env)
        return result

    def eval_Var(self, node, env):
        return env.get(node.name, node.line)

    def eval_UnaryOp(self, node, env):
        if node.op == "not":
            return not self.is_truthy(self.eval_expr(node.operand, env))
        val = self.eval_expr(node.operand, env)
        if node.op == "-":
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise PetalRuntimeError(f"cannot negate '{self.type_name(val)}'", node.line)
            return -val
        return val  # unary '+'

    def eval_LogicalOp(self, node, env):
        left = self.eval_expr(node.left, env)
        if node.op == "and":
            return left if not self.is_truthy(left) else self.eval_expr(node.right, env)
        return left if self.is_truthy(left) else self.eval_expr(node.right, env)

    def eval_BinOp(self, node, env):
        left = self.eval_expr(node.left, env)
        right = self.eval_expr(node.right, env)
        return self.apply_binop(node.op, left, right, node.line)

    def apply_binop(self, op, left, right, line):
        try:
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/":
                if right == 0: raise ZeroDivisionError()
                return left / right
            if op == "//":
                if right == 0: raise ZeroDivisionError()
                return left // right
            if op == "%":
                if right == 0: raise ZeroDivisionError()
                return left % right
            if op == "**": return left ** right
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "<": return left < right
            if op == ">": return left > right
            if op == "<=": return left <= right
            if op == ">=": return left >= right
            if op == "in": return left in right
            if op == "not in": return left not in right
        except TypeError:
            raise PetalRuntimeError(
                f"unsupported operand types for '{op}': '{self.type_name(left)}' and '{self.type_name(right)}'", line)
        except ZeroDivisionError:
            raise PetalRuntimeError("division by zero", line)
        raise PetalRuntimeError(f"unknown operator '{op}'", line)

    def eval_Call(self, node, env):
        args = [self.eval_expr(a, env) for a in node.args]
        if isinstance(node.callee, Attribute):
            obj = self.eval_expr(node.callee.obj, env)
            return self.call_method(obj, node.callee.name, args, node.line)
        callee = self.eval_expr(node.callee, env)
        return self.call_function(callee, args, node.line)

    def call_function(self, callee, args, line):
        if isinstance(callee, PetalFunction):
            call_env = Environment(callee.closure)
            if len(args) != len(callee.params):
                raise PetalRuntimeError(
                    f"{callee.name}() takes {len(callee.params)} argument(s) but {len(args)} were given", line)
            for pname, aval in zip(callee.params, args):
                call_env.assign(pname, aval)
            try:
                self.exec_block(callee.body, call_env)
            except ReturnSignal as r:
                return r.value
            return None
        if callable(callee):
            try:
                return callee(*args)
            except PetalError:
                raise
            except (TypeError, ValueError) as e:
                raise PetalRuntimeError(f"invalid arguments: {e}", line)
        raise PetalRuntimeError(f"'{self.type_name(callee)}' object is not callable", line)

    def eval_Index(self, node, env):
        obj = self.eval_expr(node.obj, env)
        idx = self.eval_expr(node.index, env)
        try:
            return obj[idx]
        except (IndexError, KeyError) as e:
            raise PetalRuntimeError(f"index error: {e}", node.line)
        except TypeError:
            raise PetalRuntimeError(f"'{self.type_name(obj)}' object is not subscriptable", node.line)

    def eval_Slice(self, node, env):
        obj = self.eval_expr(node.obj, env)
        start = self.eval_expr(node.start, env) if node.start is not None else None
        stop = self.eval_expr(node.stop, env) if node.stop is not None else None
        try:
            return obj[start:stop]
        except TypeError:
            raise PetalRuntimeError(f"'{self.type_name(obj)}' object is not sliceable", node.line)

    def eval_Attribute(self, node, env):
        raise PetalRuntimeError(
            f"'.{node.name}' must be called as a method, e.g. .{node.name}(...)", node.line)

    # ---- built-in methods on list / str / dict ---------------------------

    def call_method(self, obj, name, args, line):
        try:
            if isinstance(obj, list):
                return self.list_method(obj, name, args, line)
            if isinstance(obj, str):
                return self.str_method(obj, name, args, line)
            if isinstance(obj, dict):
                return self.dict_method(obj, name, args, line)
        except (IndexError, ValueError, KeyError) as e:
            raise PetalRuntimeError(str(e), line)
        raise PetalRuntimeError(f"'{self.type_name(obj)}' object has no method '{name}'", line)

    def list_method(self, obj, name, args, line):
        if name == "append": obj.append(args[0]); return None
        if name == "pop": return obj.pop(*args)
        if name == "insert": obj.insert(args[0], args[1]); return None
        if name == "remove": obj.remove(args[0]); return None
        if name == "index": return obj.index(args[0])
        if name == "count": return obj.count(args[0])
        if name == "reverse": obj.reverse(); return None
        if name == "sort": obj.sort(reverse=self.is_truthy(args[0]) if args else False); return None
        if name == "clear": obj.clear(); return None
        raise PetalRuntimeError(f"list has no method '{name}'", line)

    def str_method(self, obj, name, args, line):
        if name == "upper": return obj.upper()
        if name == "lower": return obj.lower()
        if name == "strip": return obj.strip()
        if name == "split": return obj.split(*args) if args else obj.split()
        if name == "join": return obj.join(args[0])
        if name == "replace": return obj.replace(args[0], args[1])
        if name == "startswith": return obj.startswith(args[0])
        if name == "endswith": return obj.endswith(args[0])
        if name == "find": return obj.find(args[0])
        raise PetalRuntimeError(f"str has no method '{name}'", line)

    def dict_method(self, obj, name, args, line):
        if name == "keys": return list(obj.keys())
        if name == "values": return list(obj.values())
        if name == "items": return [list(pair) for pair in obj.items()]
        if name == "get": return obj.get(args[0], args[1] if len(args) > 1 else None)
        if name == "pop": return obj.pop(*args)
        raise PetalRuntimeError(f"dict has no method '{name}'", line)


# =====================================================================
# Public API + CLI
# =====================================================================

def run_source(source, input_fn=None, output_fn=None):
    """Tokenize, parse, and execute Petal source code."""
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse_program()
    interp = Interpreter(input_fn=input_fn, output_fn=output_fn)
    interp.run(program)
    return interp


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path, "r") as f:
                source = f.read()
        except OSError as e:
            print(f"could not read {path}: {e}", file=sys.stderr)
            sys.exit(1)
        try:
            run_source(source)
        except PetalError as e:
            print(f"Petal Error -- {e.format()}", file=sys.stderr)
            sys.exit(1)
    else:
        repl()


def repl():
    print("Petal REPL -- type 'exit' to quit, Ctrl+D to exit")
    interp = Interpreter()
    while True:
        try:
            line = input("petal> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip() == "exit":
            break
        buffer = line
        if line.rstrip().endswith(":"):
            while True:
                try:
                    cont = input("  ...> ")
                except (EOFError, KeyboardInterrupt):
                    print()
                    break
                if cont.strip() == "":
                    break
                buffer += "\n" + cont
        if buffer.strip() == "":
            continue
        try:
            tokens = Lexer(buffer).tokenize()
            program = Parser(tokens).parse_program()
            interp.run(program)
        except PetalError as e:
            print(f"Petal Error -- {e.format()}")


if __name__ == "__main__":
    main()
