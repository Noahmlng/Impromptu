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

# Configure OpenAI client - 让API Key变为可选
openai.api_key = os.getenv("OPENAI_API_KEY")

# 检查API Key状态但不阻止应用启动
OPENAI_AVAILABLE = bool(openai.api_key)
if not OPENAI_AVAILABLE:
    print("⚠️ OPENAI_API_KEY 未设置，AI聊天功能将不可用")
    print("💡 如需使用AI功能，请设置环境变量: OPENAI_API_KEY=your_key")

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
    # 检查API Key是否可用
    if not OPENAI_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail={
                "error": "AI服务不可用",
                "message": "OPENAI_API_KEY 环境变量未设置",
                "solution": "请设置 OPENAI_API_KEY 环境变量后重启应用"
            }
        )
    
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

# 添加AI服务状态检查路由
@router.get("/status")
async def ai_service_status():
    """检查AI服务状态"""
    return {
        "openai_available": OPENAI_AVAILABLE,
        "status": "ready" if OPENAI_AVAILABLE else "unavailable",
        "message": "AI服务正常" if OPENAI_AVAILABLE else "需要设置 OPENAI_API_KEY"
    } 