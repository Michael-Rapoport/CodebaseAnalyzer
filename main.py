import sys
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.gui.main_window import MainWindow

VERSION = "1.0.0"

def setup_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='codebase_analyzer.log',
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def check_version():
    # In a real application, you would check a server for the latest version
    # For this example, we'll just return the current version
    return VERSION

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        app = QApplication(sys.argv)
        
        current_version = check_version()
        logger.info(f"Current version: {current_version}")
        
        initial_path = None
        if len(sys.argv) > 1:
            initial_path = sys.argv[1]
        
        window = MainWindow(initial_path)
        window.show()
        
        # Check for updates after a short delay to allow the main window to load
        QTimer.singleShot(1000, window.check_for_updates)
        
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        sys.exit(1)

if __name__ == "__main__":
    main()