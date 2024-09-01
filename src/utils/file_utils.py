import os
import shutil
import logging

logger = logging.getLogger(__name__)

def safe_read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        return None

def safe_write_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {str(e)}")
        return False

def safe_delete_file(file_path):
    try:
        os.remove(file_path)
        return True
    except OSError as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False

def safe_copy_file(src_path, dst_path):
    try:
        shutil.copy2(src_path, dst_path)
        return True
    except IOError as e:
        logger.error(f"Error copying file from {src_path} to {dst_path}: {str(e)}")
        return False

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)