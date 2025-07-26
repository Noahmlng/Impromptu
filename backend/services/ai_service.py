# backend/services/ai_service.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict
from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
import uuid

from backend.prompts.prompts import get_system_prompt, get_analysis_prompt, get_initial_prompts
from backend.services.database_service import conversation_db
from backend.services.auth_service import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

# Configure OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL")
moonshot_api_key = os.getenv("MOONSHOT_API_KEY")
moonshot_base_url = os.getenv("MOONSHOT_BASE_URL")

if not openai_api_key:
    logger.error("OPENAI_API_KEY environment variable not set!")
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)
client = OpenAI(api_key=moonshot_api_key, base_url=moonshot_base_url)
logger.info("OpenAI client initialized successfully")

class ChatRequest(BaseModel):
    message: Optional[str]
    history: List[Dict[str, str]]
    themeMode: str = 'romantic'
    language: str = 'en'
    isAnalysis: bool = False
    sessionId: Optional[str] = None

class SaveConversationRequest(BaseModel):
    history: List[Dict[str, str]]
    themeMode: str = 'romantic'
    language: str = 'zh'
    sessionId: Optional[str] = None
    status: str = 'completed'  # 'completed' or 'terminated'
    triggerTagGeneration: bool = True

class ConversationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

@router.post("/chat")
async def handle_chat(request: ChatRequest):
    """
    Handles AI chat requests by proxying them to OpenAI.
    """
    try:
        logger.info(f"Received chat request: themeMode={request.themeMode}, language={request.language}, isAnalysis={request.isAnalysis}")
        logger.info(f"History length: {len(request.history)}")
        
        # 初始对话引导
        initial_prompts = []
        if len(request.history) == 0 and not request.isAnalysis:
            logger.info("This is a new conversation. Adding initial prompts.")
            initial_prompts = get_initial_prompts(request.themeMode, request.language)

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
            messages = [{"role": "system", "content": system_prompt}] + initial_prompts + user_messages
            if request.message:
                messages.append({"role": "user", "content": request.message})
        
        logger.info(f"Prepared {len(messages)} messages for OpenAI")
        logger.debug(f"System prompt: {system_prompt[:100]}...")
        
        completion = client.chat.completions.create(
            # model="gpt-4.1-mini",
            model = "kimi-k2-0711-preview",
            messages=messages,
            max_tokens=1500 if request.isAnalysis else 1000,
            # temperature=0.7,
            temperature=0.6,
            response_format={"type": "json_object"} if request.isAnalysis else None,
        )

        response_content = completion.choices[0].message.content
        logger.info("Successfully received response from OpenAI")
        return {"response": response_content}

    except Exception as e:
        logger.error(f"Error in handle_chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/conversation/save", response_model=ConversationResponse)
async def save_conversation(
    request: SaveConversationRequest,
    current_user: Dict = Depends(get_current_user)
):
    """保存对话记录并可选择触发标签生成"""
    try:
        user_id = current_user['user_id']
        logger.info(f"💬 保存用户 {user_id} 的对话记录，状态: {request.status}")
        
        # 生成session_id如果没有提供
        session_id = request.sessionId or str(uuid.uuid4())
        
        # 保存对话记录
        conversation_data = {
            'theme_mode': request.themeMode,
            'language': request.language,
            'history': request.history,
            'session_id': session_id,
            'status': request.status
        }
        
        saved_conversation = await conversation_db.save_conversation(user_id, conversation_data)
        
        if not saved_conversation:
            raise HTTPException(status_code=500, detail="保存对话记录失败")
        
        result_data = {
            "conversation_id": saved_conversation.get('id'),
            "session_id": session_id,
            "message_count": len(request.history),
            "status": request.status
        }
        
        # 如果请求触发标签生成
        if request.triggerTagGeneration:
            try:
                # 导入标签服务
                from backend.services.tag_service import generate_user_tags_with_conversation, GenerateTagsRequest
                
                # 创建标签生成请求
                tag_request = GenerateTagsRequest(
                    request_type=request.themeMode,
                    include_conversation=True
                )
                
                # 生成标签
                tag_result = await generate_user_tags_with_conversation(tag_request, current_user)
                
                result_data["tag_generation"] = {
                    "success": tag_result.success,
                    "message": tag_result.message,
                    "generated_tags_count": len(tag_result.data.get("generated_tags", [])) if tag_result.data else 0
                }
                
                logger.info(f"✅ 对话记录保存成功，并触发了标签生成")
                
            except Exception as tag_error:
                logger.error(f"⚠️ 标签生成失败: {tag_error}")
                result_data["tag_generation"] = {
                    "success": False,
                    "message": f"标签生成失败: {str(tag_error)}",
                    "generated_tags_count": 0
                }
        
        return ConversationResponse(
            success=True,
            message="对话记录保存成功" + ("，并已触发标签生成" if request.triggerTagGeneration else ""),
            data=result_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存对话记录错误: {e}")
        raise HTTPException(status_code=500, detail=f"保存对话记录失败: {str(e)}")

@router.post("/conversation/end-and-generate-tags", response_model=ConversationResponse)
async def end_conversation_and_generate_tags(
    request: SaveConversationRequest,
    current_user: Dict = Depends(get_current_user)
):
    """结束对话并生成标签的便捷接口"""
    # 设置状态为completed并触发标签生成
    request.status = 'completed'
    request.triggerTagGeneration = True
    
    return await save_conversation(request, current_user)

@router.get("/conversation/history")
async def get_conversation_history(
    limit: int = 10,
    current_user: Dict = Depends(get_current_user)
):
    """获取用户的对话历史"""
    try:
        user_id = current_user['user_id']
        conversations = await conversation_db.get_user_conversations(user_id, limit)
        
        return {
            "success": True,
            "data": {
                "conversations": conversations,
                "total": len(conversations)
            }
        }
        
    except Exception as e:
        logger.error(f"获取对话历史错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}") 

"""
使用示例：

1. 正常对话流程：
   POST /api/ai/chat
   {
     "message": "你好",
     "history": [],
     "themeMode": "romantic",
     "language": "zh",
     "sessionId": "session_123"
   }

2. 保存对话记录并生成标签：
   POST /api/ai/conversation/save
   {
     "history": [
       {"role": "user", "content": "我喜欢音乐和旅行"},
       {"role": "assistant", "content": "很棒！你最喜欢什么类型的音乐？"}
     ],
     "themeMode": "romantic",
     "language": "zh",
     "sessionId": "session_123",
     "status": "completed",
     "triggerTagGeneration": true
   }

3. 便捷的结束对话并生成标签：
   POST /api/ai/conversation/end-and-generate-tags
   {
     "history": [...],
     "themeMode": "romantic",
     "language": "zh",
     "sessionId": "session_123"
   }

4. 直接基于对话记录生成标签：
   POST /api/tags/generate/with-conversation
   {
     "request_type": "romantic",
     "include_conversation": true
   }

对话记录将自动存储到数据库中，并可以用于标签生成，提高标签的准确性和个性化程度。
""" 