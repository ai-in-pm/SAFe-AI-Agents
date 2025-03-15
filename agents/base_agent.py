import os
import json
from abc import ABC, abstractmethod
import re

import openai
import anthropic
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY

# Initialize API clients
openai.api_key = OPENAI_API_KEY

# Initialize Anthropic client
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Initialize Google Gemini client
genai.configure(api_key=GOOGLE_API_KEY)
gemini_safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

class BaseAgent(ABC):
    """Base class for all AI agents in the SAFe implementation."""
    
    def __init__(self, name, role, model_provider="openai", model_name=None):
        """Initialize a new agent.
        
        Args:
            name (str): The name of the agent
            role (str): The role of the agent (e.g., "SAFe Coach", "Scrum Master", "Developer")
            model_provider (str): The AI model provider ("openai", "anthropic", or "google")
            model_name (str, optional): Specific model name to use
        """
        self.name = name
        self.role = role
        self.model_provider = model_provider
        self.model_name = model_name or self._get_default_model()
        self.context = []
        self.conversation_history = []
        
        # Load agent-specific prompt templates
        self.system_prompt = self._load_system_prompt()
    
    def _load_system_prompt(self):
        """Load the system prompt for this agent role."""
        return f"You are {self.name}, a {self.role} in a SAFe Agile implementation. Respond to queries and make decisions according to SAFe principles and your role's responsibilities."
    
    def _get_default_model(self):
        """Get the default model name based on the provider."""
        if self.model_provider == "openai":
            return "gpt-4o"
        elif self.model_provider == "anthropic":
            return "claude-3-opus-20240229"
        elif self.model_provider == "google":
            return "gemini-1.5-pro-latest"
        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")
    
    def add_to_context(self, message):
        """Add a message to the agent's context."""
        self.context.append(message)
        
    def _prepare_conversation_history(self):
        """Prepare the conversation history for the model."""
        return [{"role": "system", "content": self.system_prompt}] + self.conversation_history
    
    @abstractmethod
    def generate_response(self, user_input):
        """Generate a response to user input. To be implemented by subclasses."""
        pass
    
    def call_openai(self, messages):
        """Call the OpenAI API to generate a response."""
        response = openai.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    def call_anthropic(self, messages):
        """Call the Anthropic API to generate a response."""
        # Convert messages to Anthropic format
        system_message = next((m for m in messages if m["role"] == "system"), None)
        system_content = system_message["content"] if system_message else ""
        
        user_assistant_messages = [m for m in messages if m["role"] != "system"]
        
        response = anthropic_client.messages.create(
            model=self.model_name,
            system=system_content,
            messages=user_assistant_messages,
            max_tokens=1000
        )
        return response.content[0].text
    
    def call_google(self, messages):
        """Call the Google Gemini API to generate a response."""
        # Format messages for Gemini
        system_message = next((m for m in messages if m["role"] == "system"), None)
        system_content = system_message["content"] if system_message else ""
        
        # Format conversation for Gemini
        formatted_messages = []
        for message in messages:
            if message["role"] == "system":
                continue  # Skip system message as we handle it separately
            
            role = "user" if message["role"] == "user" else "model"
            formatted_messages.append({"role": role, "parts": [{"text": message["content"]}]})
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=gemini_safety_settings
        )
        
        chat = model.start_chat(history=formatted_messages)
        response = chat.send_message(system_content)
        return response.text
    
    def process_message(self, user_input):
        """Process a user message and generate a response."""
        # Add user input to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Generate response
        response = self.generate_response(user_input)
        
        # Add agent response to conversation history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response

    def generate_chain_of_thought_response(self, question, include_steps=True):
        """
        Generate a response with visible chain of thought reasoning steps.
        
        Args:
            question (str): The question or prompt for the agent.
            include_steps (bool): Whether to include reasoning steps in the response.
            
        Returns:
            dict: Dictionary containing 'thought_process' (list of reasoning steps) and 'conclusion' (final answer)
        """
        # Define the system message to encourage chain of thought reasoning
        system_message = f"""You are {self.name}, a {self.role} in a SAFe environment.
        
        When answering the question, think step-by-step and show your reasoning process. 
        Organize your response in the following format:
        
        THOUGHT PROCESS:
        Step 1: [First reasoning step]
        Step 2: [Second reasoning step]
        Step 3: [Third reasoning step]
        ... (more steps as needed)
        
        CONCLUSION:
        [Your final answer based on the above reasoning]
        """
        
        # Create a messages array in the format needed for the models
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
        
        # Call the appropriate API based on the model provider
        if self.model_provider == "openai":
            response = self.call_openai(messages)
        elif self.model_provider == "anthropic":
            response = self.call_anthropic(messages)
        elif self.model_provider == "google":
            response = self.call_google(messages)
        else:
            # Default to OpenAI if provider is unknown
            response = self.call_openai(messages)
        
        # Parse the response to separate thought process from conclusion
        thought_process = []
        conclusion = ""
        
        # Split by thought process and conclusion sections
        sections = response.split("CONCLUSION:")
        
        if len(sections) > 1:
            # Extract thought process steps
            thought_section = sections[0].split("THOUGHT PROCESS:")[-1].strip()
            steps = re.findall(r'Step \d+:\s*(.*?)(?=Step \d+:|$)', thought_section, re.DOTALL)
            thought_process = [step.strip() for step in steps if step.strip()]
            
            # Extract conclusion
            conclusion = sections[1].strip()
        else:
            # If the formatting isn't as expected, use the whole response as conclusion
            conclusion = response
        
        return {
            'thought_process': thought_process,
            'conclusion': conclusion
        }
