import ast


class CodeMetricsVisitor(ast.NodeVisitor):
    def __init__(self):
        self.loops = 0
        self.conditionals = 0
        self.functions = 0
        self.cyclomatic = 1
        self.recursive_calls = 0
        self.current_function = None
        self.max_loop_depth = 0
        self.current_loop_depth = 0
        self.globals = set()

    def generic_visit(self, node):
        if isinstance(node, (ast.If, ast.IfExp)):
            self.conditionals += 1
            self.cyclomatic += 1
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            self.loops += 1
            self.cyclomatic += 1
            self.current_loop_depth += 1
            if self.current_loop_depth > self.max_loop_depth:
                self.max_loop_depth = self.current_loop_depth
            super().generic_visit(node)
            self.current_loop_depth -= 1
            return
        if isinstance(node, (ast.And, ast.Or)):
            self.cyclomatic += 1
        if isinstance(node, (ast.Try, ast.ExceptHandler)):
            self.cyclomatic += 1
        return super().generic_visit(node)

    def visit_FunctionDef(self, node):
        prev_function = self.current_function
        self.current_function = node.name
        self.functions += 1
        self.generic_visit(node)
        self.current_function = prev_function

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == self.current_function:
            self.recursive_calls += 1
        self.generic_visit(node)

    def visit_Global(self, node):
        for name in node.names:
            self.globals.add(name)
        self.generic_visit(node)


def analyze_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return {"error": f"Syntax error: {exc}"}
    metrics = CodeMetricsVisitor()
    metrics.visit(tree)
    total_lines = len([line for line in code.splitlines() if line.strip()])
    recursion = metrics.recursive_calls > 0
    return {
        "total_lines": total_lines,
        "loops": metrics.loops,
        "conditionals": metrics.conditionals,
        "functions": metrics.functions,
        "cyclomatic_complexity": metrics.cyclomatic,
        "is_recursive": recursion,
        "nested_loop_depth": metrics.max_loop_depth,
        "global_variables": sorted(metrics.globals),
    }

