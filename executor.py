from anansi_ast import (
    AnFunction, AnMethod, AnClass,
    AnReturn, AnStatement, AnPass, AnBreak, AnContinue,
    AnIf, AnLoop, AnAssert, AnRaise, AnWith, AnTry, AnAssign
)


class ExecutionContext:
    def __init__(self):
        self.vars = {}
        self.output = []

    def get(self, name):
        return self.vars.get(name)

    def set(self, name, value):
        self.vars[name] = value


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


def eval_expr(expr, context):
    try:
        return eval(expr, {}, context.vars)
    except Exception as e:
        raise RuntimeError(f"Error evaluando expresión: {expr} → {e}")


def exec_stmt(stmt, context):
    if isinstance(stmt, AnAssign):
        parts = stmt.expr.split("=", 1)
        if len(parts) == 2:
            var, value = parts
            context.set(var.strip(), eval_expr(value.strip(), context))

    elif isinstance(stmt, AnStatement):
        if stmt.value.startswith("print"):
            val = eval_expr(stmt.value[5:].strip("() "), context)
            print(val)
            context.output.append(val)

    elif isinstance(stmt, AnReturn):
        raise ReturnSignal(eval_expr(stmt.value, context))

    elif isinstance(stmt, AnAssert):
        assert eval_expr(stmt.cond, context)

    elif isinstance(stmt, AnRaise):
        raise RuntimeError(eval_expr(stmt.expr, context))

    elif isinstance(stmt, AnIf):
        cond = eval_expr(stmt.cond, context)
        body = stmt.body if cond else stmt.else_body or []
        for s in body:
            exec_stmt(s, context)

    elif isinstance(stmt, AnLoop):
        if stmt.header.startswith("for"):
            parts = stmt.header.split(" in ")
            if len(parts) == 2:
                var = parts[0].replace("for", "").strip()
                iterable = eval_expr(parts[1], context)
                for val in iterable:
                    context.set(var, val)
                    for s in stmt.body:
                        exec_stmt(s, context)

    elif isinstance(stmt, AnTry):
        try:
            for s in stmt.body:
                exec_stmt(s, context)
        except Exception:
            for _, block in stmt.except_blocks:
                for s in block:
                    exec_stmt(s, context)
        finally:
            for s in stmt.finally_body:
                exec_stmt(s, context)

    elif isinstance(stmt, AnWith):
        # Ignorar el contexto en esta versión básica
        for s in stmt.body:
            exec_stmt(s, context)

    elif isinstance(stmt, AnPass):
        pass

    elif isinstance(stmt, AnBreak):
        pass

    elif isinstance(stmt, AnContinue):
        pass


def run_function(fn, args):
    context = ExecutionContext()
    for name, val in zip(fn.params, args):
        context.set(name, val)

    try:
        for stmt in fn.body:
            exec_stmt(stmt, context)
    except ReturnSignal as r:
        return r.value

    return None

