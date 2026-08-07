"""Opening messages and example user task statements."""

WELCOME_MESSAGE = (
    "你好，很高兴和你交流。\n"
    "如果你最近遇到了关系中希望分析、解决或做出决定的问题，可以告诉我。"
    "我会帮助你一起梳理事情的经过，分析可能的原因，并根据你的情况提供一些建议。\n"
    "最近发生了什么事情，让你想和我聊聊？"
)

SCENARIOS = {
    "victim": "我的伴侣昨天说了很多伤人的话，现在也不和我说话了。",
    "transgressor": "我昨天没控制住脾气，说了伤害伴侣的话。",
}


def get_scenario(task_condition):
    """Return the example user statement for the relationship-role condition."""
    return SCENARIOS[task_condition]


def get_welcome_message():
    """Return the fixed welcome message."""
    return WELCOME_MESSAGE
