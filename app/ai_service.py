import json
import google.generativeai as genai
from app.config import settings

# Configure the Gemini SDK
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_subtasks(title: str, description: str = None) -> list[str]:
    # Return a message if the API key is not configured
    if not settings.GEMINI_API_KEY:
        return ["Gemini API Key is missing. Please configure it in your .env file."]
        
    prompt = f"""
    You are an expert productivity coach.
    Analyze the following task and break it down into 3 to 6 logical, actionable, and sequential subtasks.
    
    Task: {title}
    Description: {description or 'No description provided'}
    
    Return the response ONLY as a JSON array of strings.
    Example Output format:
    ["Step 1 content", "Step 2 content", "Step 3 content"]
    """
    
    try:
        # Initialize Gemini 3.5 Flash model
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        # Query the model and request a structured JSON response
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse and return the JSON array
        subtasks = json.loads(response.text.strip())
        if isinstance(subtasks, list):
            return [str(item).strip() for item in subtasks]
        return []
    except Exception as e:
        print(f"Error generating subtasks via Gemini: {e}")
        return [f"Could not generate subtasks: {str(e)}"]
