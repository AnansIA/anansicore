class ASTNode:
    def to_python(self, indent=0):
        raise NotImplementedError()


class AnFunction(ASTNode):
    def __init__(self, name, params, body, decorators=None):
        self.name = name
        self.params = params
        self.body = body
        self.decorators = decorators or []

    def to_python(self, indent=0):
        ind = " " * indent
        decos = "\n".join(f"{ind}@{d}" for d in self.decorators)
        header = f"{ind}def {self.name}({', '.join(self.params)}):"
        body_lines = [stmt.to_python(indent + 4) for stmt in self.body]
        return "\n".join(filter(None, [decos, header] + body_lines))


class AnMethod(AnFunction):
    def to_python(self, indent=0):
        return super().to_python(indent)


class AnClass(ASTNode):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def to_python(self, indent=0):
        ind = " " * indent
        header = f"{ind}class {self.name}:"
        if not self.methods:
            return f"{header}\n{ind}    pass"
        body_lines = [m.to_python(indent + 4) for m in self.methods]
        return "\n".join([header] + body_lines)


class AnReturn(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def to_python(self, indent=0):
        return " " * indent + f"return {self.expr}"


class AnStatement(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def to_python(self, indent=0):
        return " " * indent + self.expr


class AnPass(ASTNode):
    def to_python(self, indent=0):
        return " " * indent + "pass"


class AnBreak(ASTNode):
    def to_python(self, indent=0):
        return " " * indent + "break"


class AnContinue(ASTNode):
    def to_python(self, indent=0):
        return " " * indent + "continue"


class AnIf(ASTNode):
    def __init__(self, cond, body, else_body=None):
        self.cond = cond
        self.body = body
        self.else_body = else_body or []

    def to_python(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}if {self.cond}:"]
        lines += [stmt.to_python(indent + 4) for stmt in self.body]
        if self.else_body:
            lines.append(f"{ind}else:")
            lines += [stmt.to_python(indent + 4) for stmt in self.else_body]
        return "\n".join(lines)


class AnLoop(ASTNode):
    def __init__(self, header, body):
        self.header = header
        self.body = body

    def to_python(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}{self.header}:"]
        lines += [stmt.to_python(indent + 4) for stmt in self.body]
        return "\n".join(lines)


class AnAssert(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def to_python(self, indent=0):
        return " " * indent + f"assert {self.expr}"


class AnRaise(ASTNode):
    def __init__(self, expr):
        self.expr = expr

    def to_python(self, indent=0):
        return " " * indent + f"raise {self.expr}"


class AnWith(ASTNode):
    def __init__(self, header, body):
        self.header = header
        self.body = body

    def to_python(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}with {self.header}:"]
        lines += [stmt.to_python(indent + 4) for stmt in self.body]
        return "\n".join(lines)


class AnTry(ASTNode):
    def __init__(self, body, except_blocks=None, finally_body=None):
        self.body = body
        self.excepts = except_blocks or []
        self.finally_body = finally_body or []

    def to_python(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}try:"]
        lines += [stmt.to_python(indent + 4) for stmt in self.body]

        for header, body in self.excepts:
            lines.append(f"{ind}catch {header}:" if 'catch' in header else f"{ind}except {header}:")
            lines += [stmt.to_python(indent + 4) for stmt in body]

        if self.finally_body:
            lines.append(f"{ind}finally:")
            lines += [stmt.to_python(indent + 4) for stmt in self.finally_body]

        return "\n".join(lines)

