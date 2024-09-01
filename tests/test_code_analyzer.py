import unittest
from src.analysis.code_analyzer import CodeAnalyzer
import tempfile
import os

class TestCodeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sample_file = os.path.join(self.temp_dir, "sample.py")
        with open(self.sample_file, 'w') as f:
            f.write('''
import os
import sys

def sample_function():
    print("Hello, World!")

class SampleClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
''')

    def tearDown(self):
        os.remove(self.sample_file)
        os.rmdir(self.temp_dir)

    def test_analyze_file(self):
        analyzer = CodeAnalyzer(self.temp_dir, self.temp_dir, ['.py'], 1, True, True)
        results = analyzer.analyze_directory(self.temp_dir)

        self.assertIn(self.sample_file, results)
        file_analysis = results[self.sample_file]

        self.assertEqual(file_analysis['lines_of_code'], 13)
        self.assertGreater(file_analysis['complexity'], 1)
        self.assertIn('os', file_analysis['dependencies'])
        self.assertIn('sys', file_analysis['dependencies'])

    def test_remove_comments(self):
        code_with_comments = '''
# This is a comment
def function():  # This is an inline comment
    """
    This is a docstring
    """
    return 42
'''
        analyzer = CodeAnalyzer("", "", [], 1, False, True)
        code_without_comments = analyzer.remove_comments(code_with_comments)
        
        self.assertNotIn("#", code_without_comments)
        self.assertNotIn("This is a comment", code_without_comments)
        self.assertNotIn("This is an inline comment", code_without_comments)
        self.assertNotIn("This is a docstring", code_without_comments)

    def test_generate_summary_report(self):
        analyzer = CodeAnalyzer(self.temp_dir, self.temp_dir, ['.py'], 1, True, True)
        results = {
            'file1.py': {'lines_of_code': 100, 'complexity': 5, 'dependencies': ['os', 'sys']},
            'file2.py': {'lines_of_code': 200, 'complexity': 8, 'dependencies': ['numpy', 'pandas']}
        }
        report = analyzer.generate_summary_report(results)
        
        self.assertIn("Total files analyzed: 2", report)
        self.assertIn("Total lines of code: 300", report)
        self.assertIn("Average complexity: 6.50", report)
        self.assertIn("Unique dependencies: numpy, os, pandas, sys", report)