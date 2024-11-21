import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables if you have any
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5555,
        reload=True,
        log_level="info"
    )