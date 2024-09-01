import unittest
from src.analysis.dependency_analyzer import DependencyAnalyzer

class TestDependencyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = DependencyAnalyzer()

    def test_analyze_dependencies(self):
        code = '''
import os
from sys import path
import numpy as np
from sklearn.model_selection import train_test_split
'''
        dependencies = self.analyzer.analyze_dependencies(code)
        
        self.assertIn('os', dependencies)
        self.assertIn('sys', dependencies)
        self.assertIn('numpy', dependencies)
        self.assertIn('sklearn.model_selection', dependencies)

    def test_no_dependencies(self):
        code = '''
def function():
    return 42
'''
        dependencies = self.analyzer.analyze_dependencies(code)
        self.assertEqual(dependencies, [])