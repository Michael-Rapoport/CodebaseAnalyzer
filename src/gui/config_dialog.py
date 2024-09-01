from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialogButtonBox, QFileDialog

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # GitHub API Token
        github_layout = QHBoxLayout()
        github_layout.addWidget(QLabel("GitHub API Token:"))
        self.github_token = QLineEdit()
        github_layout.addWidget(self.github_token)
        layout.addLayout(github_layout)

        # OpenAI API Key
        openai_layout = QHBoxLayout()
        openai_layout.addWidget(QLabel("OpenAI API Key:"))
        self.openai_key = QLineEdit()
        openai_layout.addWidget(self.openai_key)
        layout.addLayout(openai_layout)

        # Anthropic API Key
        anthropic_layout = QHBoxLayout()
        anthropic_layout.addWidget(QLabel("Anthropic API Key:"))
        self.anthropic_key = QLineEdit()
        anthropic_layout.addWidget(self.anthropic_key)
        layout.addLayout(anthropic_layout)

        # Default output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Default Output Directory:"))
        self.output_dir = QLineEdit()
        output_layout.addWidget(self.output_dir)
        self.browse_output = QPushButton("Browse")
        self.browse_output.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.browse_output)
        layout.addLayout(output_layout)

        # OK and Cancel buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Default Output Directory")
        if directory:
            self.output_dir.setText(directory)