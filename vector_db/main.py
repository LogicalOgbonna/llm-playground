import os

import dotenv
import uvicorn
from src.constants import Constants

dotenv.load_dotenv(".env", override=True)


if __name__ == "__main__":
    # Start the FastAPI server
    PORT = os.getenv("PORT", 5002)
    # Check if the server is in development mode
    # and set the reload option accordingly
    RELOAD = Constants.isDevelopment()
    if PORT is None:
        raise ValueError("PORT environment variable not set")
    try:
        PORT = int(PORT)
    except ValueError:
        raise ValueError("PORT environment variable must be an integer")
    uvicorn.run('src.app:app', port=PORT, reload=RELOAD, host='0.0.0.0')