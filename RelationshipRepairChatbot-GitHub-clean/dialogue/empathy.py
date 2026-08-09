"""Stage 1 emotional support manipulation."""

from dialogue.llm import generate_controlled_reply

HIGH_GAIN_FALLBACK = (
    "谢谢你愿意把这件事告诉我。你现在正在努力改善这段关系，这种投入本身很重要。"
    "我们可以一起先把事情梳理清楚，请先从起因说起，这会是促进关系改善的重要一步。"
)

HIGH_LOSS_FALLBACK = (
    "谢谢你愿意说出来。我能理解这件事可能让你感到压力和担心，也会害怕关系继续受到影响。"
    "我们可以一起先把情况理清楚，请先从起因说起，避免误解和冲突继续扩大。"
)

LOW_GAIN_FALLBACK = (
    "这件事涉及隐瞒、失约与信任落差。\n"
    "先梳理发生经过、对方解释和目前沟通状态，后续处理会更有依据。"
)

LOW_LOSS_FALLBACK = (
    "这件事涉及隐瞒、失约与信任落差。\n"
    "若发生经过、对方解释和沟通状态不清楚，问题可能被冲动处理并继续扩大。"
)

LOW_EMPATHY_FORBIDDEN_TERMS = [
    "你",
    "您",
    "我",
    "我们",
    "咱们",
    "一起",
    "谢谢",
    "感谢",
    "理解",
    "关心",
    "陪着",
    "愿意",
    "难受",
    "担心",
    "压力",
    "不容易",
    "感受",
    "情绪",
]

HIGH_EMPATHY_REQUIRED_PRONOUNS = ["你", "我们"]
HIGH_EMPATHY_REQUIRED_DISCLOSURE_RESPONSE = ["谢谢", "感谢"]
HIGH_EMPATHY_REQUIRED_CARE_TERMS = [
    "理解",
    "感到",
    "担心",
    "压力",
    "感受",
    "在意",
    "努力",
    "重要",
    "面对",
]


def empathy_frame_rules(empathy_condition, frame_condition):
    """Return prompt rules and fallback for the empathy x framing cell."""
    if empathy_condition == "high" and frame_condition == "gain":
        return (
            """
高共情 + 收益框架。
句法-语法人：使用第一、二人称复数或第二人称，例如“我们可以一起……”“你可以……”。
句法-代词：必须同时使用“你”和“我们”，强调用户目标、用户投入和当前支持。
 时态：使用现在时，强调用户正在努力改善关系。
祈使句：如需引导，使用同理心祈使句，例如“请先……”，不要使用生硬命令。
主动与被动：使用主动表达，例如“我们可以一起……”，不要写“问题可以被……”。
标点：不使用感叹号，不使用情绪强化标点。
修辞-致谢：必须回应用户披露，例如“谢谢你愿意告诉我这些”。
修辞-情绪状态：必须包含一句对用户当前感受/目标的理解或轻度询问。
修辞-关怀陈述：必须包含关怀或肯定，例如“这种努力本身很重要”。
内容方向：强调改善沟通、促进关系提升、建立更好互动。
不要出现“实验、阶段、任务、框架、研究”等后台词。
不要直接给具体建议，不要替用户做决定。
长度 70-110 个汉字。
""".strip(),
            HIGH_GAIN_FALLBACK,
            "阶段1：高共情-收益情境",
        )

    if empathy_condition == "high" and frame_condition == "loss":
        return (
            """
高共情 + 损失框架。
句法-语法人：使用第一、二人称复数或第二人称，例如“我们可以一起……”“你的担忧……”。
句法-代词：必须同时使用“你”和“我们”，强调用户体验、当前困难和共同面对。
时态：使用现在时，强调用户正在面对关系困难。
祈使句：如需引导，使用同理心祈使句，例如“请先……”，不要使用生硬命令。
主动与被动：使用主动表达，例如“我们可以一起……”，不要写“问题可以被……”。
标点：不使用感叹号，不使用情绪强化标点。
修辞-致谢：必须回应用户披露，例如“谢谢你愿意说出来”。
修辞-情绪状态：必须包含一句对用户担忧、压力、难受或害怕关系受影响的理解或轻度询问。
修辞-关怀陈述：必须包含关怀表达。
内容方向：强调避免关系进一步受影响、避免误解扩大。
不要出现“实验、阶段、任务、框架、研究”等后台词。
不要直接给具体建议，不要替用户做决定。
长度 70-110 个汉字。
""".strip(),
            HIGH_LOSS_FALLBACK,
            "阶段1：高共情-损失情境",
        )

    if empathy_condition == "low" and frame_condition == "gain":
        return (
            """
低共情 + 收益框架。
低共情不是机器化、冷漠或论文式总结；仍然是 IMA 情感支持阶段的低强度支持。
操控重点是减少拟人化和显性同理心线索，而不是取消支持功能。
句法-语法人：只使用第三人称或客观陈述，避免“我/你/我们”式人际靠近。
句法-代词：不得使用“你/您/我/我们/咱们”等任何人称代词。
时态：使用一般事实描述。
祈使句：只允许客观直接过渡，例如“先梳理……”，不得使用“请”或同理心祈使。
主动与被动：使用客观表达，可以写“这件事涉及……”“先梳理……”。
标点：可以使用至多一个感叹号，作为低共情条件下的标点操控；不得加入关怀或安慰内容。
修辞-致谢：不得感谢用户分享，不回应用户努力。
修辞-情绪状态：不得询问用户感受或情绪状态。
修辞-关怀陈述：不得包含关怀、理解、陪伴或安慰表达。
IMA要求：保留问题聚焦与情境评估功能：承接用户事件，指出事件与信任/沟通判断有关，说明继续梳理信息的价值。
输出格式：严格两行。第一行定位事件性质；第二行说明继续梳理能带来的清晰方向。
必须像聊天里的简短回应，不得像研究报告或总结表述。
必须贴合用户输入中的真实事件，不得写“有效沟通能够促进关系发展”“客观陈述事实有助于关系提升”“冲突起因是……”这类空泛或报告式句子。
只能做中性过渡，不给具体建议，不询问情绪。
不要出现“实验、阶段、任务、框架、研究”等后台词。
长度 45-85 个汉字。
""".strip(),
            LOW_GAIN_FALLBACK,
            "阶段1：低共情-收益情境",
        )

    return (
        """
低共情 + 损失框架。
低共情不是机器化、冷漠或论文式总结；仍然是 IMA 情感支持阶段的低强度支持。
操控重点是减少拟人化和显性同理心线索，而不是取消支持功能。
句法-语法人：只使用第三人称或客观陈述，避免“我/你/我们”式人际靠近。
句法-代词：不得使用“你/您/我/我们/咱们”等任何人称代词。
时态：使用过去式或一般事实描述。
祈使句：只允许客观直接过渡，例如“先梳理……”，不得使用“请”或同理心祈使。
主动与被动：使用客观表达，可以写“这件事涉及……”“若……不清楚……”。
标点：可以使用至多一个感叹号，作为低共情条件下的标点操控；不得加入关怀或安慰内容。
修辞-致谢：不得感谢用户分享，不回应用户披露。
修辞-情绪状态：不得询问用户感受或情绪状态。
修辞-关怀陈述：不得包含关怀、理解、陪伴或安慰表达。
IMA要求：保留问题聚焦与情境评估功能：承接用户事件，指出事件与信任/沟通风险有关，说明信息不清可能带来的负面后果。
输出格式：严格两行。第一行定位事件性质；第二行说明信息不清时可能造成的关系风险。
必须像聊天里的简短回应，不得像研究报告或总结表述。
必须贴合用户输入中的真实事件，不得写“冲突可能导致关系进一步恶化”“该问题需要被处理”“冲突起因是……”这类空泛或报告式句子。
只能做中性过渡，不给具体建议，不询问情绪。
不要出现“实验、阶段、任务、框架、研究”等后台词。
长度 45-85 个汉字。
""".strip(),
        LOW_LOSS_FALLBACK,
        "阶段1：低共情-损失情境",
    )


def sanitize_empathy_text(text, empathy_condition, frame_condition, fallback):
    """Keep empathy manipulation aligned with the assigned style cell."""
    if empathy_condition == "low":
        if any(term in text for term in LOW_EMPATHY_FORBIDDEN_TERMS):
            return fallback
        if "请" in text:
            return fallback
        vague_phrases = [
            "有效沟通能够",
            "客观陈述事实",
            "关系提升",
            "关系改善",
            "该问题需要被处理",
            "冲突可能导致关系进一步恶化",
            "冲突起因是",
            "根据描述",
            "总结如下",
        ]
        if any(term in text for term in vague_phrases):
            return fallback
        if "\n" not in text:
            return fallback
    else:
        if not all(term in text for term in HIGH_EMPATHY_REQUIRED_PRONOUNS):
            return fallback
        if not any(term in text for term in HIGH_EMPATHY_REQUIRED_DISCLOSURE_RESPONSE):
            return fallback
        if not any(term in text for term in HIGH_EMPATHY_REQUIRED_CARE_TERMS):
            return fallback
        if any(term in text for term in ["被解决", "被处理", "需要被"]):
            return fallback
        if any(term in text for term in ["！", "!"]):
            return fallback
    if frame_condition == "loss":
        gain_terms = ["更好", "提升", "促进", "机会", "重新靠近", "改善关系", "变得更好"]
        if any(term in text for term in gain_terms):
            return fallback
    return text


def get_emotional_support(empathy_condition, frame_condition, user_statement):
    """Return one semi-structured emotional-support message for the condition."""
    instruction, fallback, stage_name = empathy_frame_rules(empathy_condition, frame_condition)
    text = generate_controlled_reply(
        stage_name,
        instruction,
        f"用户开场输入：{user_statement}",
        fallback,
    )
    return sanitize_empathy_text(text, empathy_condition, frame_condition, fallback)
