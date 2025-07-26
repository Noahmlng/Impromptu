# backend/prompts.py

def get_system_prompt(theme_mode: str, language: str, history_length: int) -> str:
    """
    根据主题、语言和对话历史长度生成动态系统提示词。
    """
    is_romantic = theme_mode == 'romantic'
    round_num = history_length // 2 + 1
    
    # 为了简洁，这里省略了完整的提示词内容，只保留结构
    if language == 'zh':
        if is_romantic:
            return f"你是Linker，一个专业的恋爱人格分析师... 当前是第 {round_num} 轮对话。"
        else:
            return f"你是Linker，一个专业的团队技能分析师... 当前是第 {round_num} 轮对话。"
    else: # English
        if is_romantic:
            return f"You are Linker, a professional romantic personality analyst... This is round {round_num} of the conversation."
        else:
            return f"You are Linker, a professional team skills analyst... This is round {round_num} of the conversation."


def get_analysis_prompt(theme_mode: str, language: str) -> str:
    """
    根据主题和语言生成用于最终分析报告的系统提示词。
    """
    is_romantic = theme_mode == 'romantic'

    # 省略完整的JSON格式化提示词
    if language == 'zh':
        if is_romantic:
            return "请基于提供的对话历史，生成一个详细的恋爱人格分析JSON报告..."
        else:
            return "请基于提供的对话历史，生成一个详细的团队合作技能分析JSON报告..."
    else: # English
        if is_romantic:
            return "Based on the provided conversation history, generate a detailed romantic personality analysis JSON report..."
        else:
            return "Based on the provided conversation history, generate a detailed team collaboration skills analysis JSON report..." 