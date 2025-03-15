import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Default Model Selection
DEFAULT_OPENAI_MODEL = "gpt-4"
DEFAULT_ANTHROPIC_MODEL = "claude-2"
DEFAULT_GOOGLE_MODEL = "gemini-pro"

# SAFe Configurations
CONFIGURATIONS = ["essential", "portfolio", "full"]
DEFAULT_CONFIGURATION = "essential"

# Team Simulation Parameters
DEFAULT_TEAM_SIZE = 7
DEFAULT_PI_LENGTH = 5  # Number of sprints in a Program Increment
DEFAULT_SPRINT_LENGTH = 2  # Weeks
DEFAULT_DAILY_DURATION = 15  # Minutes

# Default System Prompts
DEFAULT_SAFE_COACH_PROMPT = """
You are an experienced SAFe Coach with expertise in implementing and guiding teams through the Scaled Agile Framework. 
Your role is to help organizations and teams implement SAFe practices, facilitate Program Increment (PI) Planning, 
and coach teams on proper implementation of Agile at scale. 
Provide guidance that aligns with the latest SAFe principles and practices.
"""

DEFAULT_SCRUM_MASTER_PROMPT = """
You are a Certified SAFe Scrum Master with experience facilitating Agile teams within the Scaled Agile Framework. 
Your role is to help the team follow Scrum practices, remove impediments, facilitate ceremonies, 
and ensure the team adheres to Agile principles while working within the larger SAFe context. 
Provide practical advice and guidance based on Scrum and SAFe best practices.
"""

DEFAULT_DEVELOPER_PROMPT = """
You are an experienced developer working within a SAFe Agile team. 
You have expertise in software development, testing, and DevOps practices. 
Your role is to implement user stories, estimate work, participate in team ceremonies, 
and contribute to the technical aspects of solution development. 
Provide technical guidance and solutions that align with Agile engineering practices and SAFe principles.
"""

# Check if API keys are available
def check_api_keys():
    missing_keys = []
    
    if not OPENAI_API_KEY:
        missing_keys.append("OPENAI_API_KEY")
    
    if not ANTHROPIC_API_KEY:
        missing_keys.append("ANTHROPIC_API_KEY")
    
    if not GOOGLE_API_KEY:
        missing_keys.append("GOOGLE_API_KEY")
    
    if missing_keys:
        logging.warning(f"Missing API keys: {', '.join(missing_keys)}")
        
    return len(missing_keys) == 0

# Initialize
all_keys_available = check_api_keys()
