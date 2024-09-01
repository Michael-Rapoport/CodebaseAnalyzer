import unittest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

class TestMainWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        self.window = MainWindow()

    def test_init(self):
        self.assertIsNotNone(self.window)
        self.assertEqual(self.window.windowTitle(), "Codebase Analyzer")

    @patch('src.gui.main_window.CodeAnalyzer')
    def test_analyze_codebase(self, mock_analyzer):
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        
        self.window.input_field.setText("/test/path")
        self.window.analyze_codebase()
        
        mock_analyzer.assert_called_once()
        mock_analyzer_instance.start.assert_called_once()

    @patch('src.gui.main_window.KnowledgeGraphGenerator')
    def test_generate_knowledge_graph(self, mock_generator):
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        
        self.window.analysis_results = {"test": "data"}
        self.window.generate_knowledge_graph()
        
        mock_generator.assert_called_once()
        mock_generator_instance.start.assert_called_once()

    @patch('src.gui.main_window.WordCloudGenerator')
    def test_generate_word_cloud(self, mock_generator):
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        
        self.window.analysis_results = {"test": "data"}
        self.window.generate_word_cloud()
        
        mock_generator.assert_called_once()
        mock_generator_instance.start.assert_called_once()

    @patch('src.gui.main_window.FeatureSuggester')
    def test_suggest_features(self, mock_suggester):
        mock_suggester_instance = MagicMock()
        mock_suggester.return_value = mock_suggester_instance
        
        self.window.suggest_features()
        
        mock_suggester.assert_called_once()
        mock_suggester_instance.start.assert_called_once()

    @patch('src.gui.main_window.CodeAnalyzer')
    @patch('src.gui.main_window.FeatureDeveloper')
    def test_perform_self_healing(self, mock_developer, mock_analyzer):
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        
        mock_developer_instance = MagicMock()
        mock_developer.return_value = mock_developer_instance
        
        self.window.perform_self_healing()
        
        mock_analyzer.assert_called_once()
        mock_analyzer_instance.start.assert_called_once()

    def test_update_log(self):
        test_message = "Test log message"
        self.window.update_log(test_message)
        self.assertIn(test_message, self.window.log_window.toPlainText())