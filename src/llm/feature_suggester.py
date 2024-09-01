from PyQt6.QtCore import QThread, pyqtSignal
import openai
import anthropic
from transformers import pipeline

class FeatureSuggester(QThread):
    suggestion_progress = pyqtSignal(str)
    suggestion_complete = pyqtSignal(list)

    def __init__(self, llm_provider, api_key):
        super().__init__()
        self.llm_provider = llm_provider
        self.api_key = api_key

    def run(self):
        self.suggestion_progress.emit("Generating feature suggestions...")
        suggestions = self.generate_suggestions()
        self.suggestion_complete.emit(suggestions)

    def generate_suggestions(self):
        prompt = (
            "Generate 5 innovative feature suggestions for a Python-based codebase analyzer application. "
            "Each suggestion should be feasible to implement and provide value to users. "
            "Format your response as a list of dictionaries, where each dictionary has 'name' and 'description' keys."
        )

        if self.llm_provider == "OpenAI":
            return self.generate_with_openai(prompt)
        elif self.llm_provider == "Claude":
            return self.generate_with_claude(prompt)
        else:
            return self.generate_with_huggingface(prompt)

    def generate_with_openai(self, prompt):
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that suggests new features for software applications."},
                {"role": "user", "content": prompt}
            ]
        )
        return eval(response.choices[0].message.content.strip())

    def generate_with_claude(self, prompt):
        client = anthropic.Client(api_key=self.api_key)
        response = client.completion(
            prompt=f"Human: {prompt}\n\nAssistant:",
            model="claude-2",
            max_tokens_to_sample=1000,
        )
        return eval(response.completion.strip())

    def generate_with_huggingface(self, prompt):
        generator = pipeline('text-generation', model='gpt2')
        response = generator(prompt, max_length=1000, num_return_sequences=1)[0]['generated_text']
        # Note: This is a simplification. In practice, you'd need more sophisticated parsing for HuggingFace output.
        return [{"name": "Feature suggestion", "description": "Description of the feature"}] * 5