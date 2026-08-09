"""Stage 3 advice framing manipulation."""

from dialogue.llm import generate_controlled_reply


VICTIM_GAIN_FRAME_FALLBACK = (
    "可以先把重点放在表达事实和边界上：说明对方隐瞒外出这件事影响了信任，并希望对方给出清楚解释。"
    "\n\n"
    "这样做有助于让沟通回到具体事件本身，也更有机会促成对方正面回应和后续修复。"
)

VICTIM_LOSS_FRAME_FALLBACK = (
    "可以先把重点放在表达事实和边界上：说明对方隐瞒外出这件事影响了信任，并希望对方给出清楚解释。"
    "\n\n"
    "如果沟通焦点转向评价说话方式，可能会让对方回避核心问题，也会让关系里的信任裂痕继续扩大。"
)

TRANSGRESSOR_GAIN_FRAME_FALLBACK = (
    "可以先明确承认自己造成的影响，再说明愿意承担责任，并给对方留出回应空间。"
    "\n\n"
    "这样做有助于让对方看到修复诚意，也更有机会让后续沟通回到稳定、可修复的方向。"
)

TRANSGRESSOR_LOSS_FRAME_FALLBACK = (
    "可以先明确承认自己造成的影响，再说明愿意承担责任，并给对方留出回应空间。"
    "\n\n"
    "如果继续回避责任或急着要求对方回应，可能会让对方更抗拒，也会增加关系继续恶化的风险。"
)

VICTIM_GAIN_REINFORCEMENT_FALLBACK = (
    "如果问题不在自身表达上，就不需要替没有发生的行为认错。可以只表达被隐瞒后的信任落差，并要求对方解释事实。"
    "\n\n"
    "这样做有助于把沟通焦点放回对方的隐瞒行为，也更有机会让对方正面回应。"
)

VICTIM_LOSS_REINFORCEMENT_FALLBACK = (
    "如果问题不在自身表达上，就不需要替没有发生的行为认错。可以只表达被隐瞒后的信任落差，并要求对方解释事实。"
    "\n\n"
    "如果把重点放成自我认错，可能会模糊真正需要回应的问题，也会让信任裂痕继续存在。"
)

TRANSGRESSOR_GAIN_REINFORCEMENT_FALLBACK = (
    "可以围绕已经发生的过错本身回应，不要新增没有发生的情节。先承认造成的影响，再说明愿意承担和调整。"
    "\n\n"
    "这样做有助于让对方看到修复诚意，也更有机会恢复后续沟通。"
)

TRANSGRESSOR_LOSS_REINFORCEMENT_FALLBACK = (
    "可以围绕已经发生的过错本身回应，不要新增没有发生的情节。先承认造成的影响，再说明愿意承担和调整。"
    "\n\n"
    "如果继续回避责任或编造解释，可能会让对方更难相信修复诚意。"
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
    "\n\n"
    "先确认安全，才有机会让后续沟通回到更稳定的状态。"
)

LOSS_MISSING_PERSON_FALLBACK = (
    "她现在不回消息、也没回家时，先不要把重点放在道歉或补救上，应该先确认她是否安全。"
    "你可以联系她信任的朋友或家人，确认她可能去的地方；如果长时间联系不上，或你担心她有危险，就及时寻求现实帮助。"
    "\n\n"
    "如果现在只反复发消息或只想着怎么道歉，可能会错过确认她安全的时机，也会让情况变得更不可控。"
)


def sanitize_advice_text(text, fallback):
    """Keep advice in recommendation-plus-persuasion format."""
    hallucinated_terms = ["游戏", "威胁", "推你", "推她", "推对方", "爆发争吵", "吵架", "争吵", "讽刺"]
    if any(term in text for term in hallucinated_terms):
        return fallback
    return format_advice_paragraphs(remove_section_labels(text))


def sanitize_reinforcement_text(text, fallback, frame_condition, task_condition):
    """Keep follow-up advice aligned with the assigned gain/loss frame."""
    hallucinated_terms = ["游戏", "威胁", "推你", "推她", "推对方", "爆发争吵", "吵架", "争吵", "讽刺"]
    if any(term in text for term in hallucinated_terms):
        return fallback
    if task_condition == "victim":
        victim_forbidden = ["我语气不好", "我没控制住", "是我没控制住", "是我不对", "我错了", "对不起"]
        if any(term in text for term in victim_forbidden):
            return fallback
    if "建议：" not in text and "作用：" not in text:
        return format_advice_paragraphs(remove_section_labels(text))
    if frame_condition == "loss":
        gain_phrases = ["这样做能降低", "这样做可以降低", "这样做有助于", "更有机会", "更稳妥", "更容易"]
        if any(phrase in text for phrase in gain_phrases):
            return fallback
    return format_advice_paragraphs(remove_section_labels(text))


def remove_section_labels(text):
    return text.replace("建议：", "").replace("作用：", "").strip()


def format_advice_paragraphs(text):
    """Separate the recommendation from the persuasive framing paragraph."""
    cleaned = "\n".join(line.strip() for line in text.strip().splitlines())
    while "\n\n\n" in cleaned:
        cleaned = cleaned.replace("\n\n\n", "\n\n")
    if "\n\n" in cleaned:
        return cleaned

    split_markers = [
        "这样做有助于",
        "这样说出来",
        "如果继续",
        "如果现在",
        "如果把重点",
        "如果沟通焦点",
        "若发生经过",
        "先确认安全",
    ]
    for marker in split_markers:
        index = cleaned.find(marker)
        if index > 0:
            return f"{cleaned[:index].strip()}\n\n{cleaned[index:].strip()}"
    return cleaned


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
    if task_condition == "victim":
        role_rule = """
用户处于受伤害者任务。
建议必须站在受伤害者视角：表达事实、感受边界、要求对方解释或承担。
不得让用户为对方的过错认错，不得写“我语气不好/我没控制住/是我不对/对不起”。
不得新增“爆发争吵、吵架、语气不好、没控制住”等用户没说过的事实。
""".strip()
        fallback = VICTIM_GAIN_FRAME_FALLBACK if frame_condition == "gain" else VICTIM_LOSS_FRAME_FALLBACK
    else:
        role_rule = """
用户处于过错方任务。
建议必须站在过错方视角：承认自身行为影响、承担责任、给对方回应空间。
不得把主要责任转移给对方。
不得新增“爆发争吵、吵架、推搡、暴力”等用户没说过的事实。
""".strip()
        fallback = TRANSGRESSOR_GAIN_FRAME_FALLBACK if frame_condition == "gain" else TRANSGRESSOR_LOSS_FRAME_FALLBACK

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
必须分成两段，中间用一个空行隔开：第一段给具体行动建议，第二段解释该建议的作用。
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
{role_rule}
不得新增用户没有说过的事实。
不得替用户写完整消息。
不得出现“建议：”“作用：”这两个标题词。
{no_reply_rule}
说服部分必须强调积极结果、关系改善、未来好处。
不要使用损失框架。
必须分成两段，中间用一个空行隔开：第一段给具体行动建议，第二段解释该建议的作用。
长度 120-190 个汉字。
""".strip().format(no_reply_rule=no_reply_rule, role_rule=role_rule)
        text = generate_controlled_reply(
            "阶段3：建议给予-收益框架",
            instruction,
            shared_context,
            fallback,
        )
        return sanitize_advice_text(text, fallback)

    instruction = """
生成 1 段建议。
你是聊天机器人，不是用户本人。
必须先提出一个贴合用户输入和当前沟通状态的具体建议，然后用损失框架解释不采纳该建议、继续不当行为可能带来的负面后果。
建议本身不能因为收益/损失条件而改变；收益/损失只体现在“作用”部分的说服方式。
{role_rule}
不得新增用户没有说过的事实。
不得替用户写完整消息。
不得出现“建议：”“作用：”这两个标题词。
{no_reply_rule}
说服部分必须使用“如果继续……可能会……”或“如果现在……可能会……”这类句式。
不得使用“这样做有助于”“更有机会”“更稳妥”等收益式表达。
必须分成两段，中间用一个空行隔开：第一段给具体行动建议，第二段解释该建议的作用。
长度 120-200 个汉字。
""".strip().format(no_reply_rule=no_reply_rule, role_rule=role_rule)
    text = generate_controlled_reply(
        "阶段3：建议给予-损失框架",
        instruction,
        shared_context,
        fallback,
    )
    return sanitize_advice_text(text, fallback)


def get_advice_reinforcement(frame_condition, task_condition, user_followup, conversation_context):
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
必须分成两段，中间用一个空行隔开：第一段给具体行动建议，第二段解释该建议的作用。
长度 100-170 个汉字。
""".strip()
        text = generate_controlled_reply(
            "阶段3：建议强化-失联安全优先",
            instruction,
            combined_context,
            fallback,
        )
        return sanitize_reinforcement_text(text, fallback, frame_condition, task_condition)

    if frame_condition == "gain":
        frame_rule = """
必须使用收益框架。
说服部分必须强调采纳该建议可能带来的积极结果，例如恢复沟通、增加理解、改善关系。
可以使用“这样做有助于……”“更有机会……”等表达。
不得强调不这样做的负面后果。
""".strip()
        fallback = VICTIM_GAIN_REINFORCEMENT_FALLBACK if task_condition == "victim" else TRANSGRESSOR_GAIN_REINFORCEMENT_FALLBACK
    else:
        frame_rule = """
必须使用损失框架。
说服部分必须强调如果不采纳该建议、继续冲动追问或继续回避，可能带来的负面后果。
必须使用“如果继续……可能会……”或“如果现在……可能会……”这类句式。
不得使用“这样做能降低风险”“这样做有助于”“更有机会”“更稳妥”等收益式表达。
""".strip()
        fallback = VICTIM_LOSS_REINFORCEMENT_FALLBACK if task_condition == "victim" else TRANSGRESSOR_LOSS_REINFORCEMENT_FALLBACK

    if task_condition == "victim":
        role_rule = """
用户处于受伤害者任务。
必须根据用户最新纠正调整建议：如果用户说没有争吵或不是自身语气问题，必须承认不应让用户为不存在的行为认错。
建议应围绕表达被隐瞒后的信任落差、要求对方解释事实或承担责任。
不得生成用户向对方道歉或承认“语气不好/没控制住”的话术。
""".strip()
    else:
        role_rule = """
用户处于过错方任务。
建议应围绕用户已经承认或描述的自身行为，承认影响、承担责任、给对方回应空间。
不得新增用户没说过的过错情节。
""".strip()

    instruction = f"""
生成 1 段建议强化回复。
必须回应用户最新追问。
你是聊天机器人，不是用户本人。
必须先提出一个具体可执行建议，回应用户的问题，再解释这个建议在当前框架中的作用。
{role_rule}
不得出现“建议：”“作用：”这两个标题词。
不得新增用户没有明确说过的事实，例如游戏、威胁、推搡、暴力等。
如果用户说“不适合/做不到”，必须根据用户说出的原因调整建议，而不是重复上一轮建议。
如需提供具体话术，必须先写“可以这样表达：”。受伤害者任务的话术只能表达事实、边界和要求解释，不得道歉认错；过错方任务的话术才可以包含道歉和承担责任。
{frame_rule}
不得新增实验阶段，不得提出超过 1 个新行动。
必须分成两段，中间用一个空行隔开：第一段给具体行动建议，第二段解释该建议的作用。
长度 90-150 个汉字。
""".strip()
    text = generate_controlled_reply(
        "阶段3：建议强化",
        instruction,
        combined_context,
        fallback,
    )
    return sanitize_reinforcement_text(text, fallback, frame_condition, task_condition)
