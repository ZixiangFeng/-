"""Stage 3 advice framing manipulation."""

from dialogue.llm import generate_controlled_reply


GAIN_FRAME_FALLBACK = (
    "如果对方目前不回复消息，你先不要继续追发，可以先整理一份具体补救方案，例如说明愿意承担损失、赔偿或弥补，并等待更合适的沟通机会。"
    "这样做有助于让对方看到你的责任感，也更有机会为之后恢复沟通和修复关系留下空间。"
)

LOSS_FRAME_FALLBACK = (
    "如果对方目前不回复消息，你先不要继续追发，可以先整理一份具体补救方案，例如说明愿意承担损失、赔偿或弥补，并等待更合适的沟通机会。"
    "如果现在继续追发消息或只停留在道歉上，可能会让对方更抗拒，也会让对方觉得你没有真正处理损失，从而增加关系继续恶化的风险。"
)

GAIN_REINFORCEMENT_FALLBACK = (
    "如果对方暂时没有回应，你可以先等待一段时间，再只发送一次简短、平和的信息，表达你愿意冷静沟通。"
    "这样做有助于让对方感到被尊重，也更有机会让后续交流回到稳定、可修复的方向。"
)

LOSS_REINFORCEMENT_FALLBACK = (
    "如果对方暂时没有回应，你可以先等待一段时间，不要连续追问或用更强烈的语气催促。"
    "如果现在反复发消息或情绪化表达，可能会让对方更抗拒沟通，使误解加深，并增加关系继续恶化的风险。"
)

FORBIDDEN_FIRST_PERSON_PATTERNS = [
    "我是",
    "我有点",
    "我没能",
    "我没有",
    "我会改",
    "“",
    "”",
    "\"",
]

ADVICE_MESSAGE_MARKERS = [
    "我推荐你可以给对方发以下内容",
    "我推荐你可以给她发以下内容",
    "我推荐你可以给他发以下内容",
    "你可以给对方发以下内容",
    "你可以给她发以下内容",
    "你可以给他发以下内容",
]

NO_REPLY_MARKERS = ["不回", "没回", "没有回", "不回复", "没回复", "没有回复", "不理", "没理", "不联系", "没有联系"]
MISSING_PERSON_MARKERS = ["没回家", "没有回家", "不见了", "找不到", "联系不上", "失联", "不知道去哪", "不知道去哪里"]

GAIN_MISSING_PERSON_FALLBACK = (
    "她现在不回消息、也没回家时，先不要把重点放在道歉或补救上，应该先确认她是否安全。"
    "你可以联系她信任的朋友或家人，确认她可能去的地方；如果长时间联系不上，或你担心她有危险，就及时寻求现实帮助。"
    "先确认安全，才有机会让后续沟通回到更稳定的状态。"
)

LOSS_MISSING_PERSON_FALLBACK = (
    "她现在不回消息、也没回家时，先不要把重点放在道歉或补救上，应该先确认她是否安全。"
    "你可以联系她信任的朋友或家人，确认她可能去的地方；如果长时间联系不上，或你担心她有危险，就及时寻求现实帮助。"
    "如果现在只反复发消息或只想着怎么道歉，可能会错过确认她安全的时机，也会让情况变得更不可控。"
)


def sanitize_advice_text(text, fallback):
    """Keep advice in recommendation-plus-persuasion format."""
    hallucinated_terms = ["游戏", "威胁", "推你", "推她", "推对方"]
    if any(term in text for term in hallucinated_terms):
        return fallback
    return remove_section_labels(text)


def sanitize_reinforcement_text(text, fallback, frame_condition):
    """Keep follow-up advice aligned with the assigned gain/loss frame."""
    hallucinated_terms = ["游戏", "威胁", "推你", "推她", "推对方"]
    if any(term in text for term in hallucinated_terms):
        return fallback
    if "建议：" not in text and "作用：" not in text:
        return remove_section_labels(text)
    if frame_condition == "loss":
        gain_phrases = ["这样做能降低", "这样做可以降低", "这样做有助于", "更有机会", "更稳妥", "更容易"]
        if any(phrase in text for phrase in gain_phrases):
            return fallback
    return remove_section_labels(text)


def remove_section_labels(text):
    return text.replace("建议：", "").replace("作用：", "").strip()


def get_advice(frame_condition, task_condition, user_statement, answers):
    """Return semi-structured advice for the assigned framing condition."""
    current_communication = answers[2]
    shared_context = (
        f"任务角色：{task_condition}\n"
        f"用户开场输入：{user_statement}\n"
        f"冲突起因：{answers[0]}\n"
        f"是否发生过：{answers[1]}\n"
        f"当前沟通状态：{current_communication}"
    )
    no_reply_rule = (
        "当前沟通状态显示对方不回复或不联系。建议部分不得把继续发消息作为主要建议；"
        "应优先建议停止连续追发、准备具体补救/赔偿/承担责任方案、等待合适沟通机会。"
        if any(marker in current_communication for marker in NO_REPLY_MARKERS)
        else "如果当前仍可沟通，建议可以包含一次简短、平和的沟通表达。"
    )
    missing_person = any(marker in current_communication for marker in MISSING_PERSON_MARKERS)

    if missing_person:
        fallback = GAIN_MISSING_PERSON_FALLBACK if frame_condition == "gain" else LOSS_MISSING_PERSON_FALLBACK
        frame_rule = (
            "最后一句用收益框架，强调先确认安全能带来的积极结果，例如后续沟通更稳定。"
            if frame_condition == "gain"
            else "最后一句用损失框架，强调如果只反复发消息或只想着道歉，可能错过确认安全时机、让情况更不可控。"
        )
        instruction = f"""
生成 1 段建议。
用户表示对方不回消息且没回家/找不到人/联系不上。
此时建议必须优先确认对方安全，而不是普通关系修复、道歉、送礼、做饭或补救关系。
必须包括：停止连续追问、联系对方信任的朋友或家人、确认可能位置；如果长时间联系不上或担心危险，及时寻求现实帮助。
不得新增用户没说过的事实。
不得出现“建议：”“作用：”这两个标题词。
{frame_rule}
长度 110-180 个汉字。
""".strip()
        text = generate_controlled_reply(
            "阶段3：建议给予-失联安全优先",
            instruction,
            shared_context,
            fallback,
        )
        return sanitize_advice_text(text, fallback)

    if frame_condition == "gain":
        instruction = """
生成 1 段建议。
你是聊天机器人，不是用户本人。
必须先提出一个贴合用户输入和当前沟通状态的具体建议，然后用收益框架解释采纳该建议可能带来的积极结果。
建议本身不能因为收益/损失条件而改变；收益/损失只体现在“作用”部分的说服方式。
不得新增用户没有说过的事实。
不得替用户写完整消息。
不得出现“建议：”“作用：”这两个标题词。
{no_reply_rule}
说服部分必须强调积极结果、关系改善、未来好处。
不要使用损失框架。
长度 120-190 个汉字。
""".strip().format(no_reply_rule=no_reply_rule)
        text = generate_controlled_reply(
            "阶段3：建议给予-收益框架",
            instruction,
            shared_context,
            GAIN_FRAME_FALLBACK,
        )
        return sanitize_advice_text(text, GAIN_FRAME_FALLBACK)

    instruction = """
生成 1 段建议。
你是聊天机器人，不是用户本人。
必须先提出一个贴合用户输入和当前沟通状态的具体建议，然后用损失框架解释不采纳该建议、继续不当行为可能带来的负面后果。
建议本身不能因为收益/损失条件而改变；收益/损失只体现在“作用”部分的说服方式。
不得新增用户没有说过的事实。
不得替用户写完整消息。
不得出现“建议：”“作用：”这两个标题词。
{no_reply_rule}
说服部分必须使用“如果继续……可能会……”或“如果现在……可能会……”这类句式。
不得使用“这样做有助于”“更有机会”“更稳妥”等收益式表达。
长度 120-200 个汉字。
""".strip().format(no_reply_rule=no_reply_rule)
    text = generate_controlled_reply(
        "阶段3：建议给予-损失框架",
        instruction,
        shared_context,
        LOSS_FRAME_FALLBACK,
    )
    return sanitize_advice_text(text, LOSS_FRAME_FALLBACK)


def get_advice_reinforcement(frame_condition, user_followup, conversation_context):
    """Return a follow-up response after advice, grounded in the user's latest message."""
    combined_context = f"{conversation_context}\n用户最新追问：{user_followup}"
    if any(marker in combined_context for marker in MISSING_PERSON_MARKERS):
        fallback = GAIN_MISSING_PERSON_FALLBACK if frame_condition == "gain" else LOSS_MISSING_PERSON_FALLBACK
        frame_rule = (
            "最后一句用收益框架，强调先确认安全能带来的积极结果，例如后续沟通更稳定。"
            if frame_condition == "gain"
            else "最后一句用损失框架，强调如果只反复发消息或只想着道歉，可能错过确认安全时机、让情况更不可控。"
        )
        instruction = f"""
生成 1 段建议强化回复。
用户提到对方没回家/找不到人/联系不上时，必须优先安全确认，不要继续普通关系修复建议。
必须包括：先不要连续追问；联系共同朋友或家人；确认可能去处；如果长时间联系不上或担心危险，及时寻求现实帮助。
不得新增用户没说过的事实。
不得出现“建议：”“作用：”这两个标题词。
{frame_rule}
长度 100-170 个汉字。
""".strip()
        text = generate_controlled_reply(
            "阶段3：建议强化-失联安全优先",
            instruction,
            combined_context,
            fallback,
        )
        return sanitize_reinforcement_text(text, fallback, frame_condition)

    if frame_condition == "gain":
        frame_rule = """
必须使用收益框架。
说服部分必须强调采纳该建议可能带来的积极结果，例如恢复沟通、增加理解、改善关系。
可以使用“这样做有助于……”“更有机会……”等表达。
不得强调不这样做的负面后果。
""".strip()
        fallback = GAIN_REINFORCEMENT_FALLBACK
    else:
        frame_rule = """
必须使用损失框架。
说服部分必须强调如果不采纳该建议、继续冲动追问或继续回避，可能带来的负面后果。
必须使用“如果继续……可能会……”或“如果现在……可能会……”这类句式。
不得使用“这样做能降低风险”“这样做有助于”“更有机会”“更稳妥”等收益式表达。
""".strip()
        fallback = LOSS_REINFORCEMENT_FALLBACK

    instruction = f"""
生成 1 段建议强化回复。
必须回应用户最新追问。
你是聊天机器人，不是用户本人。
必须先提出一个具体可执行建议，回应用户的问题，再解释这个建议在当前框架中的作用。
不得出现“建议：”“作用：”这两个标题词。
不得新增用户没有明确说过的事实，例如游戏、威胁、推搡、暴力等。
如果用户说“不适合/做不到”，必须根据用户说出的原因调整建议，而不是重复上一轮建议。
如需提供具体话术，必须先写“你可以给对方发以下内容：”，第一人称只能出现在冒号后的建议发送内容中。
{frame_rule}
不得新增实验阶段，不得提出超过 1 个新行动。
长度 90-150 个汉字。
""".strip()
    text = generate_controlled_reply(
        "阶段3：建议强化",
        instruction,
        combined_context,
        fallback,
    )
    return sanitize_reinforcement_text(text, fallback, frame_condition)
