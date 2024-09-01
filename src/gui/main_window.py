import os
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, 
                             QLabel, QProgressBar, QLineEdit, QCheckBox, QGroupBox, QSpinBox, QTabWidget, 
                             QListWidget, QSplitter, QComboBox, QMessageBox, QTreeWidget, QTreeWidgetItem, 
                             QDialog, QDialogButtonBox, QPlainTextEdit)
from PyQt6.QtCore import Qt, QSettings, QSize, QPoint, QUrl
from PyQt6.QtGui import QIcon, QFont, QDesktopServices
from PyQt6.QtWebEngineWidgets import QWebEngineView

from .config_dialog import ConfigDialog
from ..analysis.code_analyzer import CodeAnalyzer
from ..visualization.knowledge_graph import KnowledgeGraphGenerator
from ..visualization.word_cloud import WordCloudGenerator
from ..llm.feature_suggester import FeatureSuggester
from ..llm.feature_developer import FeatureDeveloper

class MainWindow(QMainWindow):
    def __init__(self, initial_path=None):
        super().__init__()
        self.setWindowTitle("Codebase Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        self.settings = QSettings("CodebaseAnalyzer", "Settings")
        self.load_settings()

        self.setup_ui()
        self.setup_connections()

        self.output_dir = self.settings.value("default_output_dir", "")
        self.analysis_results = {}

        if initial_path:
            self.input_field.setText(initial_path)
            self.analyze_codebase()

    def setup_ui(self):
        # Main layout setup
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Input section
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter GitHub URL or local directory path")
        input_layout.addWidget(self.input_field)
        
        self.browse_button = QPushButton("Browse")
        input_layout.addWidget(self.browse_button)
        
        layout.addLayout(input_layout)

        # Tabs for different configurations and views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Analysis Tab
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout()
        analysis_widget.setLayout(analysis_layout)

        # File Extensions
        file_ext_group = QGroupBox("File Extensions")
        file_ext_layout = QVBoxLayout()
        self.file_ext_list = QListWidget()
        self.file_ext_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        common_extensions = [".py", ".js", ".java", ".cpp", ".html", ".css", ".php", ".rb", ".go", ".rs", ".ts"]
        self.file_ext_list.addItems(common_extensions)
        file_ext_layout.addWidget(self.file_ext_list)

        file_ext_input_layout = QHBoxLayout()
        self.new_ext_input = QLineEdit()
        self.new_ext_input.setPlaceholderText("Add new extension (e.g., .txt)")
        file_ext_input_layout.addWidget(self.new_ext_input)
        self.add_ext_button = QPushButton("Add")
        file_ext_input_layout.addWidget(self.add_ext_button)
        file_ext_layout.addLayout(file_ext_input_layout)
        file_ext_group.setLayout(file_ext_layout)
        analysis_layout.addWidget(file_ext_group)

        # Analysis Options
        options_group = QGroupBox("Analysis Options")
        options_layout = QVBoxLayout()
        
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Max depth for web scraping:"))
        self.max_depth_spinbox = QSpinBox()
        self.max_depth_spinbox.setRange(1, 10)
        self.max_depth_spinbox.setValue(3)
        depth_layout.addWidget(self.max_depth_spinbox)
        options_layout.addLayout(depth_layout)

        self.include_comments_checkbox = QCheckBox("Include comments in analysis")
        self.include_comments_checkbox.setChecked(True)
        options_layout.addWidget(self.include_comments_checkbox)

        self.case_sensitive_checkbox = QCheckBox("Case-sensitive analysis")
        options_layout.addWidget(self.case_sensitive_checkbox)

        self.fetch_dependency_docs_checkbox = QCheckBox("Fetch dependency documentation")
        options_layout.addWidget(self.fetch_dependency_docs_checkbox)

        self.dependency_depth_spinbox = QSpinBox()
        self.dependency_depth_spinbox.setRange(1, 5)
        self.dependency_depth_spinbox.setValue(1)
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Dependency fetch depth:"))
        depth_layout.addWidget(self.dependency_depth_spinbox)
        options_layout.addLayout(depth_layout)

        options_group.setLayout(options_layout)
        analysis_layout.addWidget(options_group)

        # LLM Options
        llm_group = QGroupBox("LLM Options")
        llm_layout = QVBoxLayout()
        self.llm_provider_combo = QComboBox()
        self.llm_provider_combo.addItems(["Hugging Face", "OpenAI", "Claude"])
        llm_layout.addWidget(QLabel("LLM Provider:"))
        llm_layout.addWidget(self.llm_provider_combo)
        llm_group.setLayout(llm_layout)
        analysis_layout.addWidget(llm_group)

        self.tab_widget.addTab(analysis_widget, "Analysis")

        # Visualization Tab
        viz_widget = QWidget()
        viz_layout = QVBoxLayout()
        viz_widget.setLayout(viz_layout)

        viz_options_group = QGroupBox("Visualization Options")
        viz_options_layout = QVBoxLayout()

        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Force-directed", "Circular", "Hierarchical"])
        viz_options_layout.addWidget(QLabel("Knowledge Graph Layout:"))
        viz_options_layout.addWidget(self.graph_type_combo)

        self.wordcloud_shape_combo = QComboBox()
        self.wordcloud_shape_combo.addItems(["Rectangle", "Circle", "Custom Mask"])
        viz_options_layout.addWidget(QLabel("Word Cloud Shape:"))
        viz_options_layout.addWidget(self.wordcloud_shape_combo)

        viz_options_group.setLayout(viz_options_layout)
        viz_layout.addWidget(viz_options_group)

        self.viz_area = QWebEngineView()
        viz_layout.addWidget(self.viz_area, 1)

        self.tab_widget.addTab(viz_widget, "Visualization")

        # Results Tab
        results_widget = QWidget()
        results_layout = QVBoxLayout()
        results_widget.setLayout(results_layout)

        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels(["Item", "Value"])
        results_layout.addWidget(self.result_tree)

        self.tab_widget.addTab(results_widget, "Results")

        # Log Tab
        log_widget = QWidget()
        log_layout = QVBoxLayout()
        log_widget.setLayout(log_layout)

        self.log_window = QTextEdit()
        self.log_window.setReadOnly(True)
        log_layout.addWidget(self.log_window)

        self.progress_bar = QProgressBar()
        log_layout.addWidget(self.progress_bar)

        self.tab_widget.addTab(log_widget, "Log")

        # Buttons
        button_layout = QHBoxLayout()
        self.analyze_button = QPushButton("Analyze Codebase")
        button_layout.addWidget(self.analyze_button)
        
        self.generate_graph_button = QPushButton("Generate Knowledge Graph")
        self.generate_graph_button.setEnabled(False)
        button_layout.addWidget(self.generate_graph_button)
        
        self.generate_wordcloud_button = QPushButton("Generate Word Cloud")
        self.generate_wordcloud_button.setEnabled(False)
        button_layout.addWidget(self.generate_wordcloud_button)

        self.suggest_features_button = QPushButton("Suggest New Features")
        button_layout.addWidget(self.suggest_features_button)

        self.self_heal_button = QPushButton("Self-Heal")
        button_layout.addWidget(self.self_heal_button)

        layout.addLayout(button_layout)

    def setup_connections(self):
        self.browse_button.clicked.connect(self.browse_directory)
        self.add_ext_button.clicked.connect(self.add_file_extension)
        self.analyze_button.clicked.connect(self.analyze_codebase)
        self.generate_graph_button.clicked.connect(self.generate_knowledge_graph)
        self.generate_wordcloud_button.clicked.connect(self.generate_word_cloud)
        self.suggest_features_button.clicked.connect(self.suggest_features)
        self.self_heal_button.clicked.connect(self.perform_self_healing)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.input_field.setText(directory)

    def add_file_extension(self):
        new_ext = self.new_ext_input.text().strip()
        if new_ext and not new_ext.startswith('.'):
            new_ext = '.' + new_ext
        if new_ext and new_ext not in [self.file_ext_list.item(i).text() for i in range(self.file_ext_list.count())]:
            self.file_ext_list.addItem(new_ext)
            self.new_ext_input.clear()

    def analyze_codebase(self):
        if not self.output_dir:
            self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not self.output_dir:
            return

        self.log_window.clear()
        self.progress_bar.setValue(0)
        self.analyze_button.setEnabled(False)
        self.generate_graph_button.setEnabled(False)
        self.generate_wordcloud_button.setEnabled(False)

        url_or_path = self.input_field.text()
        file_extensions = [item.text() for item in self.file_ext_list.selectedItems()]
        max_depth = self.max_depth_spinbox.value()
        include_comments = self.include_comments_checkbox.isChecked()
        case_sensitive = self.case_sensitive_checkbox.isChecked()

        self.analyzer = CodeAnalyzer(url_or_path, self.output_dir, file_extensions, max_depth, include_comments, case_sensitive)
        self.analyzer.analysis_progress.connect(self.update_log)
        self.analyzer.analysis_complete.connect(self.analysis_completed)
        self.analyzer.start()

    def analysis_completed(self, results):
        self.analysis_results = results
        self.update_log("Analysis completed.")
        self.update_result_tree()
        
        summary_report = self.analyzer.generate_summary_report(results)
        self.display_summary_report(summary_report)
        
        self.analyze_button.setEnabled(True)
        self.generate_graph_button.setEnabled(True)
        self.generate_wordcloud_button.setEnabled(True)

    def update_result_tree(self):
        self.result_tree.clear()
        for file_path, data in self.analysis_results.items():
            file_item = QTreeWidgetItem(self.result_tree, [file_path])
            for key, value in data.items():
                QTreeWidgetItem(file_item, [key, str(value)])
        self.result_tree.expandAll()

    def generate_knowledge_graph(self):
        self.graph_generator = KnowledgeGraphGenerator(self.analysis_results, self.output_dir)
        self.graph_generator.generation_progress.connect(self.update_log)
        self.graph_generator.generation_complete.connect(self.display_knowledge_graph)
        self.graph_generator.start()

    def display_knowledge_graph(self, graph_path):
        self.viz_area.load(QUrl.fromLocalFile(graph_path))
        self.update_log(f"Knowledge graph generated and displayed.")

    def generate_word_cloud(self):
        shape = self.wordcloud_shape_combo.currentText()
        self.wordcloud_generator = WordCloudGenerator(self.analysis_results, self.output_dir, shape)
        self.wordcloud_generator.generation_progress.connect(self.update_log)
        self.wordcloud_generator.generation_complete.connect(self.display_word_cloud)
        self.wordcloud_generator.start()

    def display_word_cloud(self, wordcloud_path):
        self.viz_area.load(QUrl.fromLocalFile(wordcloud_path))
        self.update_log(f"Word cloud generated and displayed.")

    def suggest_features(self):
        llm_provider = self.llm_provider_combo.currentText()
        api_key = self.get_api_key(llm_provider)

        if not api_key and llm_provider != "Hugging Face":
            self.update_log(f"API key for {llm_provider} is not set. Please configure it in the settings.")
            return

        self.feature_suggester = FeatureSuggester(llm_provider, api_key)
        self.feature_suggester.suggestion_progress.connect(self.update_log)
        self.feature_suggester.suggestion_complete.connect(self.display_feature_suggestions)
        self.feature_suggester.start()

    def display_feature_suggestions(self, suggestions):
        suggestion_dialog = QDialog(self)
        suggestion_dialog.setWindowTitle("Feature Suggestions")
        layout = QVBoxLayout()

        for i, suggestion in enumerate(suggestions, 1):
            layout.addWidget(QLabel(f"{i}. {suggestion['name']}: {suggestion['description']}"))

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(suggestion_dialog.accept)
        layout.addWidget(button_box)

        suggestion_dialog.setLayout(layout)
        suggestion_dialog.exec()

    def perform_self_healing(self):
        self.update_log("Starting self-healing process...")
        
        # Analyze the current codebase
        analyzer = CodeAnalyzer(os.path.dirname(__file__), self.output_dir, ['.py'], 10, True, False)
        analyzer.analysis_progress.connect(self.update_log)
        analyzer.analysis_complete.connect(self.self_healing_analysis_complete)
        analyzer.start()

    def self_healing_analysis_complete(self, results):
        self.update_log("Self-healing analysis complete. Generating improvement suggestions...")
        
        llm_provider = self.llm_provider_combo.currentText()
        api_key = self.get_api_key(llm_provider)
        
        developer = FeatureDeveloper({"name": "Self Healing", "description": "Suggest improvements for the analyzed codebase"}, llm_provider, api_key)
        developer.development_progress.connect(self.update_log)
        developer.development_complete.connect(self.apply_self_healing)
        developer.start()

    def apply_self_healing(self, suggestions):
        self.update_log("Received self-healing suggestions. Applying changes...")
        
        changes_applied = False
        for file_path, suggested_code in suggestions.items():
            original_code = self.safe_read_file(file_path)
            if original_code is None:
                self.update_log(f"Failed to read {file_path}")
                continue

            if original_code != suggested_code:
                if self.safe_write_file(file_path, suggested_code):
                    self.update_log(f"Applied changes to {file_path}")
                    changes_applied = True
                else:
                    self.update_log(f"Failed to apply changes to {file_path}")

        if changes_applied:
            self.update_log("Self-healing process completed. Please restart the application for changes to take effect.")
            QMessageBox.information(self, "Self-Healing Complete", "The self-healing process has completed. Please restart the application for changes to take effect.")
        else:
            self.update_log("Self-healing process completed. No changes were necessary.")
            QMessageBox.information(self, "Self-Healing Complete", "The self-healing process has completed. No changes were necessary.")

    def update_log(self, message):
        self.log_window.append(message)
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def load_settings(self):
        self.resize(self.settings.value("window_size", QSize(1200, 800)))
        self.move(self.settings.value("window_position", QPoint(100, 100)))

    def closeEvent(self, event):
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_position", self.pos())
        super().closeEvent(event)

    def get_api_key(self, llm_provider):
        if llm_provider == "OpenAI":
            return self.settings.value("openai_key", "")
        elif llm_provider == "Claude":
            return self.settings.value("anthropic_key", "")
        else:
            return None  # Hugging Face doesn't require an API key in this implementation

    def check_for_updates(self):
        self.update_log("Checking for updates...")
        # In a real application, you would check a server for new versions
        # For this example, we'll simulate an available update
        new_version_available = True
        if new_version_available:
            reply = QMessageBox.question(self, 'Update Available',
                                         "A new version is available. Would you like to update?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.perform_update()
        else:
            self.update_log("No updates available.")

    def perform_update(self):
        self.update_log("Performing update...")
        # In a real application, you would download and install the update here
        # For this example, we'll just simulate the process
        for i in range(1, 101):
            self.progress_bar.setValue(i)
            QApplication.processEvents()  # Ensures the UI updates
            time.sleep(0.05)  # Simulate some work being done
        self.update_log("Update completed. Please restart the application.")
        QMessageBox.information(self, "Update Complete", "The update has been installed. Please restart the application.")

    def display_summary_report(self, report):
        report_dialog = QDialog(self)
        report_dialog.setWindowTitle("Analysis Summary Report")
        layout = QVBoxLayout()
        
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(report)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(report_dialog.accept)
        layout.addWidget(button_box)
        
        report_dialog.setLayout(layout)
        report_dialog.resize(600, 400)
        report_dialog.exec()

    def safe_read_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except IOError as e:
            self.update_log(f"Error reading file {file_path}: {str(e)}")
            return None

    def safe_write_file(self, file_path, content):
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except IOError as e:
            self.update_log(f"Error writing to file {file_path}: {str(e)}")
            return False