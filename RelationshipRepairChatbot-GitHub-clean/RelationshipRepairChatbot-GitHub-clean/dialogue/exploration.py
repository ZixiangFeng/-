"""Stage 2 problem exploration and analysis."""

from dialogue.llm import generate_controlled_reply

FIRST_QUESTIONS = {
    "victim": "当时她这样做之后，你们之间又说了些什么吗？",
    "transgressor": "当时你是怎么表达的，对方后来有什么反应吗？",
}

FOLLOWUP_QUESTIONS = [
    "类似的情况以前发生过吗？",
    "你们现在还在沟通吗？",
]

SUMMARY_FALLBACK = (
    "谢谢你的回答。根据你的描述，这次冲突涉及事件起因、是否反复出现，以及你们目前的沟通状态。"
)

VICTIM_ANALYSIS_FALLBACK = (
    "从你的描述来看，这次矛盾的关键可能在于对方的话让你感到被伤害，也让你们之间的沟通暂时中断。"
    "当一方感到被冒犯或不被理解时，关系中的安全感会下降，也更容易影响后续是否愿意主动交流。"
)

TRANSGRESSOR_ANALYSIS_FALLBACK = (
    "从你的描述来看，这次矛盾的关键可能在于你当时的表达方式伤害了对方，也影响了对方继续沟通的意愿。"
    "当情绪表达超过对方能够承受的范围时，关系中的信任感会受到冲击，修复也需要更清楚地回应自己的责任。"
)


def get_question(index, task_condition="victim"):
    """Return one of the three fixed exploration questions by zero-based index."""
    if index == 0:
        return FIRST_QUESTIONS[task_condition]
    return FOLLOWUP_QUESTIONS[index - 1]


def get_exploration_turn(question_index, previous_answer=None, task_condition="victim"):
    """Return a semi-structured exploration turn containing the fixed question."""
    question = get_question(question_index, task_condition)
    if previous_answer is None:
        return question

    instruction = f"""
生成 1 段问题探索回复。
必须先用不超过 1 句中文简短承接用户刚才的回答。
承接口吻必须像自然聊天，可以说“明白了”“我了解了”“听起来是这样”。
不得出现“实验、阶段、任务、框架、研究、推进实验、请继续提供更多细节”等词。
承接只能复述或确认用户刚才回答的内容，不得推断用户没有说过的信息。
如果用户回答“没有过/没有/不是”，只能承接为“明白了，之前没有类似情况”这一类意思。
不得把“没有过”解释成“很久没联系”“沟通中断”“关系疏远”等其他事实。
然后必须逐字包含这个固定问题：{question}
不得新增其他问题。
不得给建议。
总长度 45-75 个汉字。
""".strip()
    fallback = f"我了解了。{question}"
    return generate_controlled_reply(
        "阶段2：问题探索",
        instruction,
        f"用户刚才的回答：{previous_answer}",
        fallback,
    )


def get_problem_analysis(task_condition, user_statement, answers):
    """Return one analysis response based on the real user-provided content."""
    if task_condition == "victim":
        role_instruction = """
用户处于受伤害者任务。
分析重点必须放在：对方言语造成的受伤感、沟通中断、被理解/被尊重的需要。
不得暗示用户应承担主要过错。
""".strip()
        fallback = VICTIM_ANALYSIS_FALLBACK
        stage_name = "阶段2：问题分析-受伤害者任务"
    else:
        role_instruction = """
用户处于过错方任务。
分析重点必须放在：用户自身表达失控、对伴侣造成影响、承担责任与修复信任的必要性。
不得把主要责任转移给对方。
""".strip()
        fallback = TRANSGRESSOR_ANALYSIS_FALLBACK
        stage_name = "阶段2：问题分析-过错方任务"

    instruction = """
生成 1 段问题分析。
必须基于用户已经说过的内容，分析冲突可能包含的互动模式或沟通问题。
必须体现当前任务角色的视角差异。
不得新增事实，不得给具体建议，不得提问。
长度 80-130 个汉字。
""".strip()
    context = f"任务角色：{task_condition}\n用户开场输入：{user_statement}\n已有回答：{answers}"
    return generate_controlled_reply(
        stage_name,
        f"{role_instruction}\n\n{instruction}",
        context,
        fallback,
    )


def get_fixed_summary(answers):
    """Return a semi-structured summary based only on the three exploration answers."""
    instruction = """
生成 1 段简短总结。
只能总结用户已提供的信息，不得添加新事实。
必须覆盖：冲突起因、是否曾发生、当前沟通状态。
不要给建议，不要提问。
长度 60-100 个汉字。
""".strip()
    context = (
        f"冲突起因：{answers[0]}\n"
        f"是否发生过：{answers[1]}\n"
        f"当前沟通状态：{answers[2]}"
    )
    return generate_controlled_reply("阶段2：固定总结", instruction, context, SUMMARY_FALLBACK)
