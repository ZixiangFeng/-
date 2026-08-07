"""Controlled LLM generation for semi-structured chatbot turns."""

import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


LAST_LLM_STATUS = {
    "used_api": False,
    "provider": "not_configured",
    "model": "",
    "base_url": "",
    "error": "",
}

BASE_SYSTEM_PROMPT = """
你是一个中文关系修复聊天助手。
你的任务是根据用户当前说的话，生成简短、自然、像聊天一样的回复。

必须遵守：
1. 只能回复中文。
2. 只能处理当前阶段要求，不得提前进入下一阶段。
3. 不得自由增加实验阶段。
4. 不得提供心理诊断、法律建议、医学建议或危机干预。
5. 不得声称自己记住了实验外的信息。
6. 回复必须像真实关系修复聊天，不能像问卷、访谈、研究者或实验说明。
7. 如果提示要求保留某个固定问题，必须逐字包含该问题。
8. 绝对不要向用户提到：实验、研究、操纵、条件、框架、阶段、标签、任务、推进实验、请继续提供更多细节。
""".strip()

FORBIDDEN_USER_VISIBLE_TERMS = [
    "实验",
    "研究",
    "操纵",
    "条件",
    "框架",
    "阶段",
    "标签",
    "推进实验",
    "请继续提供更多细节",
    "你的描述已收到",
    "接下来我会先了解",
]


def clean_user_visible_text(text, fallback):
    """Hide study/backend language from participant-facing replies."""
    if any(term in text for term in FORBIDDEN_USER_VISIBLE_TERMS):
        return fallback
    return text


def generate_controlled_reply(stage_name, instruction, context, fallback):
    """Generate one controlled chatbot reply, or return fallback without an API key."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        LAST_LLM_STATUS.update(
            {
                "used_api": False,
                "provider": "missing_key_or_sdk",
                "model": os.environ.get("OPENAI_MODEL", ""),
                "base_url": os.environ.get("OPENAI_BASE_URL", ""),
                "error": "OPENAI_API_KEY 或 openai SDK 不可用",
            }
        )
        return fallback

    model = os.environ.get("OPENAI_MODEL", "gpt-5.6-sol")
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url

    client = OpenAI(**client_kwargs)
    prompt = f"{BASE_SYSTEM_PROMPT}\n\n当前阶段：{stage_name}\n\n阶段规则：\n{instruction}"
    user_context = f"实验上下文：\n{context}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_context},
            ],
            max_tokens=420,
            extra_body={"thinking": {"type": "disabled"}} if "deepseek" in base_url else None,
        )
    except Exception as exc:
        LAST_LLM_STATUS.update(
            {
                "used_api": False,
                "provider": "api_error",
                "model": model,
                "base_url": base_url,
                "error": str(exc),
            }
        )
        return fallback

    text = (response.choices[0].message.content or "").strip()
    if not text:
        LAST_LLM_STATUS.update(
            {
                "used_api": False,
                "provider": "empty_response",
                "model": model,
                "base_url": base_url,
                "error": "API 返回了空文本",
            }
        )
        return fallback

    LAST_LLM_STATUS.update(
        {
            "used_api": True,
            "provider": "deepseek" if "deepseek" in base_url else "openai_compatible",
            "model": model,
            "base_url": base_url,
            "error": "",
        }
    )
    return clean_user_visible_text(text, fallback)


def get_llm_status():
    return dict(LAST_LLM_STATUS)
