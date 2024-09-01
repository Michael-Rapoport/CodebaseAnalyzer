import unittest
from src.analysis.complexity_analyzer import ComplexityAnalyzer

class TestComplexityAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = ComplexityAnalyzer()

    def test_calculate_complexity(self):
        code = '''
def simple_function():
    return 42

def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
    else:
        while x < 0:
            x += 1
    return x

class SimpleClass:
    def method(self):
        pass
'''
        complexity = self.analyzer.calculate_complexity(code)
        
        # 1 (base) + 3 (functions/methods) + 4 (if/for/while statements)
        self.assertEqual(complexity, 8)

    def test_empty_code(self):
        complexity = self.analyzer.calculate_complexity("")
        self.assertEqual(complexity, 1)  # Base complexity