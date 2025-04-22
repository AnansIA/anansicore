class AnFunction:
    def __init__(self, name, params, body, decorators=None):
        self.name = name
        self.params = params
        self.body = body
        self.decorators = decorators or []

    def to_python(self, indent=0):
        lines = []
        for d in self.decorators:
            lines.append("@" + d)
        lines.append(" " * indent + f"def {self.name}({', '.join(self.params)}):")
        if not self.body:
            lines.append(" " * (indent + 4) + "pass")
        else:
            for stmt in self.body:
                lines.append(stmt.to_python(indent + 4))
        return "\n".join(lines)


class AnMethod(AnFunction):
    pass


class AnClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def to_python(self, indent=0):
        lines = [f"{' ' * indent}class {self.name}:"]
        if not self.methods:
            lines.append(" " * (indent + 4) + "pass")
        else:
            for m in self.methods:
                lines.append(m.to_python(indent + 4))
        return "\n".join(lines)


class AnReturn:
    def __init__(self, value):
        self.value = value

    def to_python(self, indent=0):
        return " " * indent + f"return {self.value}"


class AnStatement:
    def __init__(self, value):
        self.value = value

    def to_python(self, indent=0):
        return " " * indent + self.value


class AnPass:
    def to_python(self, indent=0):
        return " " * indent + "pass"


class AnBreak:
    def to_python(self, indent=0):
        return " " * indent + "break"


class AnContinue:
    def to_python(self, indent=0):
        return " " * indent + "continue"


class AnAssert:
    def __init__(self, cond):
        self.cond = cond

    def to_python(self, indent=0):
        return " " * indent + f"assert {self.cond}"


class AnRaise:
    def __init__(self, expr):
        self.expr = expr

    def to_python(self, indent=0):
        return " " * indent + f"raise {self.expr}"


class AnAssign:
    def __init__(self, expr):
        self.expr = expr

    def to_python(self, indent=0):
        return " " * indent + self.expr


class AnIf:
    def __init__(self, cond, body, else_body=None):
        self.cond = cond
        self.body = body
        self.else_body = else_body

    def to_python(self, indent=0):
        lines = [f"{' ' * indent}if {self.cond}:"]
        if not self.body:
            lines.append(" " * (indent + 4) + "pass")
        else:
            for stmt in self.body:
                lines.append(stmt.to_python(indent + 4))
        if self.else_body is not None:
            lines.append(" " * indent + "else:")
            if not self.else_body:
                lines.append(" " * (indent + 4) + "pass")
            else:
                for stmt in self.else_body:
                    lines.append(stmt.to_python(indent + 4))
        return "\n".join(lines)


class AnLoop:
    def __init__(self, header, body):
        self.header = header
        self.body = body

    def to_python(self, indent=0):
        lines = [f"{' ' * indent}{self.header}:"]
        if not self.body:
            lines.append(" " * (indent + 4) + "pass")
        else:
            for stmt in self.body:
                lines.append(stmt.to_python(indent + 4))
        return "\n".join(lines)


class AnWith:
    def __init__(self, header, body):
        self.header = header
        self.body = body

    def to_python(self, indent=0):
        lines = [f"{' ' * indent}with {self.header}:"]
        if not self.body:
            lines.append(" " * (indent + 4) + "pass")
        else:
            for stmt in self.body:
                lines.append(stmt.to_python(indent + 4))
        return "\n".join(lines)


class AnTry:
    def __init__(self, body, except_blocks=None, finally_body=None):
        self.body = body
        self.except_blocks = except_blocks or []
        self.finally_body = finally_body or []

    def to_python(self, indent=0):
        lines = [f"{' ' * indent}try:"]
        if not self.body:
            lines.append(" " * (indent + 4) + "pass")
        else:
            for stmt in self.body:
                lines.append(stmt.to_python(indent + 4))

        for exc_type, block in self.except_blocks:
            lines.append(f"{' ' * indent}catch {exc_type or ''}:".replace("catch", "except"))
            if not block:
                lines.append(" " * (indent + 4) + "pass")
            else:
                for stmt in block:
                    lines.append(stmt.to_python(indent + 4))

        if self.finally_body:
            lines.append(f"{' ' * indent}finally:")
            if not self.finally_body:
                lines.append(" " * (indent + 4) + "pass")
            else:
                for stmt in self.finally_body:
                    lines.append(stmt.to_python(indent + 4))

        return "\n".join(lines)

class AnLambda:
    def __init__(self, expr):
        self.expr = expr        # «f = lambda x: x + 1»   (raw text)

    def to_python(self, indent=0):
        return " " * indent + self.expr

