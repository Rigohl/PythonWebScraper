import os

def list_files(directory="."):
    """Lists files in a directory."""
    return os.listdir(directory)