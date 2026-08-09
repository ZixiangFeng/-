"""Opening messages and example user task statements."""

WELCOME_MESSAGES = {
    "victim": [
        "你好。我会帮助你一起梳理事情的经过，分析可能的原因，并根据你的情况提供一些建议。",
        "可以先说说这次让你受伤的事情是怎么发生的吗？",
    ],
    "transgressor": [
        "你好。我会帮助你一起梳理事情的经过，分析可能的原因，并根据你的情况提供一些建议。",
        "可以先说说这次你伤到对方的事情是怎么发生的吗？",
    ],
}

SCENARIOS = {
    "victim": "我的伴侣昨天说了很多伤人的话，现在也不和我说话了。",
    "transgressor": "我昨天没控制住脾气，说了伤害伴侣的话。",
}


def get_scenario(task_condition):
    """Return the example user statement for the relationship-role condition."""
    return SCENARIOS[task_condition]


def get_welcome_message(task_condition):
    """Return the role-specific fixed welcome message as one text block."""
    return "\n".join(WELCOME_MESSAGES[task_condition])


def get_welcome_messages(task_condition):
    """Return role-specific fixed welcome messages as separate chat bubbles."""
    return WELCOME_MESSAGES[task_condition]
