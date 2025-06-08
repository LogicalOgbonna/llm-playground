import os


class Constants:
    """
    A class to hold constant values used in the application.
    """

    # Constants for the application
    VERSION = "1.0"
    OPEN_AI_EMBEDDING_MODEL = "nomic-embed-text"

    @staticmethod
    def isDevelopment() -> bool:
        """
        Check if the application is in development mode.
        :return: True if in development mode, False otherwise.
        """
        env = os.getenv("env")
        if env is None:
            return False
        if env.lower() == "development":
            return True
        return False