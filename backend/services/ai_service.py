# backend/services/ai_service.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

from backend.prompts.prompts import get_system_prompt, get_analysis_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Configure OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable not set!")
    raise ValueError("OPENAI_API_KEY environment variable not set.")

client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
logger.info("OpenAI client initialized successfully")

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
        logger.info(f"Received chat request: themeMode={request.themeMode}, language={request.language}, isAnalysis={request.isAnalysis}")
        logger.info(f"History length: {len(request.history)}")
        
        if request.isAnalysis:
            logger.info("Processing analysis request")
            system_prompt = get_analysis_prompt(request.themeMode, request.language)
            # For analysis, the user message is often empty, history is the main context
            user_messages = request.history
            messages = [{"role": "system", "content": system_prompt}] + user_messages
        else:
            logger.info("Processing regular chat request")
            system_prompt = get_system_prompt(request.themeMode, request.language, len(request.history))
            user_messages = request.history
            messages = [{"role": "system", "content": system_prompt}] + user_messages
            if request.message:
                messages.append({"role": "user", "content": request.message})
        
        logger.info(f"Prepared {len(messages)} messages for OpenAI")
        logger.debug(f"System prompt: {system_prompt[:100]}...")
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500 if request.isAnalysis else 1000,
            temperature=0.7,
            response_format={"type": "json_object"} if request.isAnalysis else None,
        )

        response_content = completion.choices[0].message.content
        logger.info("Successfully received response from OpenAI")
        return {"response": response_content}

    except Exception as e:
        logger.error(f"Error in handle_chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the AI service
    """
    try:
        # Test OpenAI connection
        test_response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "openai_connection": "success",
            "message": "AI service is working correctly"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "openai_connection": "failed",
            "error": str(e)
        } 