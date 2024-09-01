import ast

class ComplexityAnalyzer:
    def calculate_complexity(self, code):
        tree = ast.parse(code)
        analyzer = ComplexityVisitor()
        analyzer.visit(tree)
        return analyzer.complexity

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.complexity += 1
        self.generic_visit(node)