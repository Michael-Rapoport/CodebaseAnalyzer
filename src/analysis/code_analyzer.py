from PyQt6.QtCore import QThread, pyqtSignal
import os
import re
from github import Github
from ..utils.file_utils import safe_read_file, ensure_dir
import base64
from .dependency_analyzer import DependencyAnalyzer
from .complexity_analyzer import ComplexityAnalyzer

class CodeAnalyzer(QThread):
    analysis_progress = pyqtSignal(str)
    analysis_complete = pyqtSignal(dict)

    def __init__(self, url_or_path, output_dir, file_extensions, max_depth, include_comments, case_sensitive):
        super().__init__()
        self.url_or_path = url_or_path
        self.output_dir = output_dir
        self.file_extensions = file_extensions
        self.max_depth = max_depth
        self.include_comments = include_comments
        self.case_sensitive = case_sensitive
        self.dependency_analyzer = DependencyAnalyzer()
        self.complexity_analyzer = ComplexityAnalyzer()

    def run(self):
        results = {}
        if os.path.isdir(self.url_or_path):
            results = self.analyze_directory(self.url_or_path)
        elif self.url_or_path.startswith("https://github.com"):
            results = self.analyze_github_repo(self.url_or_path)
        else:
            self.analysis_progress.emit(f"Invalid input: {self.url_or_path}")

        self.analysis_complete.emit(results)

    def analyze_directory(self, directory):
        results = {}
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    file_path = os.path.join(root, file)
                    results[file_path] = self.analyze_file(file_path)
        return results

    def analyze_github_repo(self, repo_url):
        results = {}
        try:
            g = Github()  # Assumes GitHub API token is set in environment variable
            repo_name = repo_url.split('github.com/')[-1]
            repo = g.get_repo(repo_name)
            
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    if any(file_content.name.endswith(ext) for ext in self.file_extensions):
                        file_data = base64.b64decode(file_content.content).decode('utf-8')
                        results[file_content.path] = self.analyze_content(file_data)
                        
                        # Save content to local file
                        local_path = os.path.join(self.output_dir, file_content.path)
                        ensure_dir(os.path.dirname(local_path))
                        with open(local_path, 'w', encoding='utf-8') as f:
                            f.write(file_data)
                        
                        self.analysis_progress.emit(f"Analyzed: {file_content.path}")
        except Exception as e:
            self.analysis_progress.emit(f"Error analyzing GitHub repo: {str(e)}")
        
        return results

    def analyze_file(self, file_path):
        self.analysis_progress.emit(f"Analyzing file: {file_path}")
        content = safe_read_file(file_path)
        if content is None:
            return None
        return self.analyze_content(content)

    def analyze_content(self, content):
        if not self.case_sensitive:
            content = content.lower()
        
        if not self.include_comments:
            content = self.remove_comments(content)
        
        dependencies = self.dependency_analyzer.analyze_dependencies(content)
        complexity = self.complexity_analyzer.calculate_complexity(content)
        
        lines_of_code = len(content.splitlines())
        word_count = len(re.findall(r'\w+', content))

        return {
            "dependencies": dependencies,
            "complexity": complexity,
            "lines_of_code": lines_of_code,
            "word_count": word_count,
            "content": content  # Include content for word cloud generation
        }

    def remove_comments(self, content):
        # Remove single-line comments
        content = re.sub(r'#.*', '', content)
        # Remove multi-line comments
        content = re.sub(r'"""[\s\S]*?"""', '', content)
        content = re.sub(r"'''[\s\S]*?'''", '', content)
        return content

    def generate_summary_report(self, results):
        total_files = len(results)
        total_lines = sum(result['lines_of_code'] for result in results.values())
        avg_complexity = sum(result['complexity'] for result in results.values()) / total_files
        all_dependencies = set()
        for result in results.values():
            all_dependencies.update(result['dependencies'])
        
        report = f"""
Codebase Analysis Summary
-------------------------
Total files analyzed: {total_files}
Total lines of code: {total_lines}
Average complexity: {avg_complexity:.2f}
Unique dependencies: {', '.join(sorted(all_dependencies))}

Files by complexity:
"""
        for file_path, result in sorted(results.items(), key=lambda x: x[1]['complexity'], reverse=True):
            report += f"  {file_path}: Complexity {result['complexity']}, Lines: {result['lines_of_code']}\n"

        return report