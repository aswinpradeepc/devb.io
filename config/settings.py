import json
import os
import threading

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central configuration management"""
    # GITHUB_API_TOKEN = os.getenv("API_TOKEN_GITHUB")
    # GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    #
    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    HTML_OUTPUT_DIR = os.path.join(BASE_DIR, 'docs')
    DATA_TO_PROCESS = os.path.join(DATA_DIR, 'users.json')
    PROCESSED_USERS_DIR = os.path.join(BASE_DIR, 'docs/data')
    PROCESSED_USERS_FILE = os.path.join(PROCESSED_USERS_DIR, 'processed_users.json')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    TEMPLATE_FILES = [file for file in os.listdir(TEMPLATES_DIR) if file.endswith('.html')]
    if 'index.html' in TEMPLATE_FILES:
        TEMPLATE_FILES.remove('index.html')
    # Generation settings
    MAX_USERS_PER_RUN = 10
    CONTRIBUTION_DAYS = 120
    with open(os.path.join(DATA_DIR, 'blacklist.json'), 'r') as f:
        BLACKLISTED_USERS = json.load(f)

    BLACKLISTED_USERS = {user.lower() for user in BLACKLISTED_USERS}
    REDIS_HOST = "redis://redis:6379/0"
    API_URL = "https://user.devb.io"

    _GITHUB_API_TOKENS = os.getenv("API_TOKEN_GITHUB", "").split(',')
    _GROQ_API_KEYS = os.getenv("GROQ_API_KEY", "").split(',')

    _github_token_index = 0
    _groq_key_index = 0
    _lock = threading.Lock()


    @classmethod
    def get_github_token(cls):
        """
        Retrieve and rotate GitHub API tokens in a thread-safe manner.

        Returns:
            str: A GitHub API token
        """
        with cls._lock:
            if not cls._GITHUB_API_TOKENS:
                raise ValueError("No GitHub API tokens configured")

            token = cls._GITHUB_API_TOKENS[cls._github_token_index]
            cls._github_token_index = (cls._github_token_index + 1) % len(cls._GITHUB_API_TOKENS)
            return token

    @classmethod
    def get_groq_key(cls):
        """
        Retrieve and rotate Groq API keys in a thread-safe manner.

        Returns:
            str: A Groq API key
        """
        with cls._lock:
            if not cls._GROQ_API_KEYS:
                raise ValueError("No Groq API keys configured")

            key = cls._GROQ_API_KEYS[cls._groq_key_index]
            cls._groq_key_index = (cls._groq_key_index + 1) % len(cls._GROQ_API_KEYS)
            return key

if __name__ == "__main__":
    Settings()
