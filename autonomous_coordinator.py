from src.utils.logging_util import sanitize_text  # added import for emoji sanitization

# Example of updating a logger output to sanitize emojis
def log_status(message):
    # Replace direct prints with sanitized text
    print(sanitize_text(message))

# In various parts of the file, replace print calls with log_status, e.g.:
# print("Iniciando operación 😃...")
# becomes:
log_status("Iniciando operación 😃...")
