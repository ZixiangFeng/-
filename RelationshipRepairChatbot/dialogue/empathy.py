"""Stage 1 emotional support manipulation."""

from dialogue.llm import generate_controlled_reply

HIGH_EMPATHY_FALLBACK = (
    "谢谢你愿意和我分享这件事情。听起来，这件事已经困扰你一段时间了，而这段关系对你来说应该也很重要。"
    "我会先和你一起分析这件事情，不急着下结论。"
)

LOW_EMPATHY_FALLBACK = "我会先了解这次关系冲突的基本情况，然后再给出处理建议。"


def get_emotional_support(empathy_condition, user_statement):
    """Return one semi-structured emotional-support message for the condition."""
    if empathy_condition == "high":
        instruction = """
生成 1 段高共情回复。
必须包含：情绪承认、关心、合理化/理解。
必须像自然聊天，不得出现“实验、阶段、任务、框架、研究、请继续提供更多细节”等词。
不要给建议，不要提问，不要分析原因。
长度 70-110 个汉字。
""".strip()
        return generate_controlled_reply(
            "阶段1：情绪支持-高共情",
            instruction,
            f"用户开场输入：{user_statement}",
            HIGH_EMPATHY_FALLBACK,
        )

    instruction = """
生成 1 段低共情/中性回复。
不得包含情绪验证、安慰、关心语言。
只做自然聊天式过渡：说明会先了解这次关系冲突的基本情况。
必须像聊天助手，不得像问卷或研究者。
不得出现“实验、阶段、任务、框架、研究、推进实验、请继续提供更多细节”等词。
不要给建议，不要提问。
长度 35-60 个汉字。
""".strip()
    return generate_controlled_reply(
        "阶段1：情绪支持-低共情",
        instruction,
        f"用户开场输入：{user_statement}",
        LOW_EMPATHY_FALLBACK,
    )
