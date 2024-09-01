import unittest
from unittest.mock import patch, MagicMock
from src.llm.feature_developer import FeatureDeveloper

class TestFeatureDeveloper(unittest.TestCase):
    def setUp(self):
        self.feature = {"name": "Test Feature", "description": "A test feature"}
        self.developer = FeatureDeveloper(self.feature, "OpenAI", "fake_api_key")

    @patch('src.llm.feature_developer.openai.ChatCompletion.create')
    def test_develop_with_openai(self, mock_create):
        mock_create.return_value.choices[0].message.content = '{"method": "def test_method(self):\\n    pass", "additions": ""}'
        result = self.developer.develop_feature()
        self.assertIn('method', result)
        self.assertIn('additions', result)

    @patch('src.llm.feature_developer.anthropic.Client')
    def test_develop_with_claude(self, mock_client):
        mock_client.return_value.completion.return_value.completion = '{"method": "def test_method(self):\\n    pass", "additions": ""}'
        self.developer.llm_provider = "Claude"
        result = self.developer.develop_feature()
        self.assertIn('method', result)
        self.assertIn('additions', result)

    @patch('src.llm.feature_developer.pipeline')
    def test_develop_with_huggingface(self, mock_pipeline):
        mock_pipeline.return_value.return_value = [{'generated_text': '{"method": "def test_method(self):\\n    pass", "additions": ""}'}]
        self.developer.llm_provider = "Hugging Face"
        result = self.developer.develop_feature()
        self.assertIn('method', result)
        self.assertIn('additions', result)

    def test_parse_and_validate_code(self):
        valid_response = '{"method": "def test_method(self):\\n    pass", "additions": ""}'
        result = self.developer.parse_and_validate_code(valid_response)
        self.assertIn('method', result)
        self.assertIn('additions', result)

        invalid_response = 'Not a valid JSON'
        result = self.developer.parse_and_validate_code(invalid_response)
        self.assertEqual(result['method'], "def error_method(self):\n    pass")

    @patch('src.llm.feature_developer.openai.ChatCompletion.create')
    def test_generate_self_healing_suggestions(self, mock_create):
        self.developer.feature = {"name": "Self Healing", "description": "Test self healing"}
        mock_create.return_value.choices[0].message.content = '{"file1.py": "improved code content"}'
        result = self.developer.develop_feature()
        self.assertIn('file1.py', result)