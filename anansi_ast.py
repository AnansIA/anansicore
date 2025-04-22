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

class AnIf(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def to_python(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}if {self.cond}:"]
        lines += [stmt.to_python(indent + 4) for stmt in self.body]
        return "\n".join(lines)

class AnIf(ASTNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def to_python(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}if {self.cond}:"]
        lines += [stmt.to_python(indent + 4) for stmt in self.body]
        return "\n".join(lines)
