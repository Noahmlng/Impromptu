# backend/services/ai_service.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import openai
import os
from dotenv import load_dotenv

from backend.prompts.prompts import get_system_prompt, get_analysis_prompt

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Configure OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

class ChatRequest(BaseModel):
    message: Optional[str]
    history: List[Dict[str, str]]
    themeMode: str = 'romantic'
    language: str = 'en'
    isAnalysis: bool = False

@router.post("/chat")
async def handle_chat(request: ChatRequest):
    """
    Handles AI chat requests by proxying them to OpenAI.
    """
    try:
        if request.isAnalysis:
            system_prompt = get_analysis_prompt(request.themeMode, request.language)
            # For analysis, the user message is often empty, history is the main context
            user_messages = request.history
            messages = [{"role": "system", "content": system_prompt}] + user_messages
        else:
            system_prompt = get_system_prompt(request.themeMode, request.language, len(request.history))
            user_messages = request.history
            messages = [{"role": "system", "content": system_prompt}] + user_messages
            if request.message:
                messages.append({"role": "user", "content": request.message})
        
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500 if request.isAnalysis else 1000,
            temperature=0.7,
            response_format={"type": "json_object"} if request.isAnalysis else None,
        )

        response_content = completion.choices[0].message.content
        return {"response": response_content}

    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}") 