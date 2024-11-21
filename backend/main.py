from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict
import os
import logging
from dotenv import load_dotenv

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
gemini_session = None
ssh_manager = None

class PromptRequest(BaseModel):
    prompt: str

class GenerateResponse(BaseModel):
    response: str
    error: Optional[str] = None

def parse_keychain_file(filepath: str) -> Dict[str, str]:
    """Parse the keychain file safely"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        # Initialize default values
        credentials = {
            'GOOGLE_API_KEY': None,
            'SSH_USERNAME': None,
            'SSH_PASSWORD': None
        }
        
        # Parse file content safely
        for i, line in enumerate(lines):
            line = line.strip()
            if i == 2 and line and not line.startswith('#'):
                credentials['GOOGLE_API_KEY'] = line
            elif i == 5 and line and not line.startswith('#'):
                credentials['SSH_USERNAME'] = line
            elif i == 8 and line and not line.startswith('#'):
                credentials['SSH_PASSWORD'] = line
                
        return credentials
        
    except Exception as e:
        logger.error(f"Error parsing keychain file: {str(e)}")
        return None

def load_credentials() -> Dict[str, str]:
    """Load credentials from file or environment variables"""
    credentials = {
        'GOOGLE_API_KEY': None,
        'SSH_USERNAME': None,
        'SSH_PASSWORD': None
    }
    
    try:
        # Try to load from keychain file
        keychain_path = os.path.join(os.path.dirname(__file__), "Temp_Keychain.txt")
        if os.path.exists(keychain_path):
            logger.info("Loading credentials from keychain file")
            file_credentials = parse_keychain_file(keychain_path)
            if file_credentials:
                credentials.update(file_credentials)
        
        # Try to load from environment variables if any credentials are still None
        if not all(credentials.values()):
            logger.info("Loading credentials from environment variables")
            env_credentials = {
                'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
                'SSH_USERNAME': os.getenv('SSH_USERNAME'),
                'SSH_PASSWORD': os.getenv('SSH_PASSWORD')
            }
            # Update only None values
            credentials.update({k: v for k, v in env_credentials.items() if v is not None})
        
        return credentials
        
    except Exception as e:
        logger.error(f"Error loading credentials: {str(e)}")
        return credentials

def initialize_connections() -> bool:
    """Initialize all necessary connections"""
    global gemini_session
    
    try:
        # Load credentials
        credentials = load_credentials()
        logger.info("Credentials loaded successfully")
        
        # Initialize Gemini if API key is available
        if credentials['GOOGLE_API_KEY']:
            try:
                import google.generativeai as genai
                genai.configure(api_key=credentials['GOOGLE_API_KEY'])
                model = genai.GenerativeModel('gemini-pro')
                gemini_session = model.start_chat(history=[])
                logger.info("Gemini initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {str(e)}")
                return False
        else:
            logger.warning("No Google API key found - Gemini features will be disabled")
        
        # Initialize SSH if credentials are available
        if all([credentials['SSH_USERNAME'], credentials['SSH_PASSWORD']]):
            try:
                import paramiko
                from scp import SCPClient
                global ssh_manager
                hostname = "JamesOMEN"
                # Add your SSH initialization code here
                logger.info("SSH initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SSH: {str(e)}")
                # Continue even if SSH fails - we might not need it for all operations
        else:
            logger.warning("No SSH credentials found - SSH features will be disabled")
        
        return True
        
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    if not initialize_connections():
        logger.warning("Starting in limited mode due to missing or invalid credentials")
        # Continue startup - we'll handle missing services in the endpoints

@app.get("/")
async def root():
    return {
        "message": "PLC Code Generator API",
        "status": {
            "gemini": "available" if gemini_session else "unavailable",
            "ssh": "available" if ssh_manager else "unavailable"
        }
    }

@app.post("/api/generate")
async def generate_code(request: PromptRequest):
    try:
        if not gemini_session:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Check your API key configuration."
            )

        # Get response from Gemini
        response = gemini_session.send_message(request.prompt).text
        return {"response": response}
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating code: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/status")
async def check_status():
    """Endpoint to check service status"""
    return {
        "services": {
            "gemini": {"status": "up" if gemini_session else "down"},
            "ssh": {"status": "up" if ssh_manager else "down"}
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)