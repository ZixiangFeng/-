import csv
import json
import os
import re
import uuid
from datetime import UTC, datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

load_dotenv()

from dialogue.advice import get_advice, get_advice_reinforcement
from dialogue.empathy import get_emotional_support
from dialogue.exploration import get_exploration_turn, get_fixed_summary, get_problem_analysis
from dialogue.llm import get_llm_status
from dialogue.scenarios import get_scenario, get_welcome_messages


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "relationship-repair-chatbot-dev-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_PATH = os.path.join(DATA_DIR, "conversations.csv")

STATE_OPENING = 0
STATE_WAIT_INITIAL_PROBLEM = 1
STATE_WAIT_CAUSE = 2
STATE_WAIT_HISTORY = 3
STATE_WAIT_COMMUNICATION = 4
STATE_WAIT_ADVICE_FOLLOWUP = 5
STATE_CONTINUED_FOLLOWUP = 6
STATE_COMPLETED = 7

VALID_TASKS = {"victim", "transgressor"}
VALID_FRAMES = {"gain", "loss"}
VALID_EMPATHY = {"high", "low"}

CSV_FIELDS = [
    "participant_id",
    "timestamp",
    "task",
    "frame",
    "empathy",
    "user_messages",
    "chatbot_messages",
]

MEANINGLESS_INPUTS = {
    "1",
    "2",
    "3",
    "11",
    "111",
    "嗯",
    "哦",
    "啊",
    "好",
    "好的",
    "不知道",
    "没有",
    "没",
    "无",
    "test",
    "测试",
}

RESOLUTION_INTENT_MARKERS = [
    "明白了",
    "懂了",
    "理解了",
    "知道了",
    "好的好的",
    "好吧",
    "有道理",
    "你说得对",
    "我试试",
    "我会试",
    "我愿意",
    "我接受",
    "我准备",
    "我打算",
    "我会按照",
    "按你说的",
    "听你的",
    "相信你",
    "谢谢",
]

CONTINUATION_INTENT_MARKERS = [
    "不适合",
    "不行",
    "不是",
    "但是",
    "可是",
    "不过",
    "问题是",
    "怎么办",
    "怎么做",
    "什么时候",
    "为什么",
    "吗",
    "？",
    "?",
]

STATE_RETRY_MESSAGES = {
    STATE_WAIT_INITIAL_PROBLEM: "我可能还没理解你的情况。可以具体说说最近发生了什么关系冲突吗？",
    STATE_WAIT_CAUSE: "我还不太清楚当时双方后来的表达和反应。可以再具体说说吗？",
    STATE_WAIT_HISTORY: "我想确认一下类似情况之前有没有发生过。可以回答“发生过/没有发生过”，也可以简单说明一下吗？",
    STATE_WAIT_COMMUNICATION: "我想确认你们现在是否还在沟通。可以说说目前有没有联系、对方有没有回应吗？",
}


def ensure_csv_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
            writer.writeheader()


def reset_conversation(task, frame, empathy):
    session.clear()
    session["participant_id"] = str(uuid.uuid4())
    session["timestamp"] = datetime.now(UTC).isoformat(timespec="seconds")
    session["task"] = task
    session["frame"] = frame
    session["empathy"] = empathy
    session["state"] = STATE_OPENING
    session["user_messages"] = []
    session["chatbot_messages"] = []
    session["exploration_answers"] = []
    session["recorded"] = False
    session["finished"] = False


def append_chatbot_messages(messages):
    chatbot_messages = session.get("chatbot_messages", [])
    chatbot_messages.extend(messages)
    session["chatbot_messages"] = chatbot_messages


def append_user_message(message):
    user_messages = session.get("user_messages", [])
    user_messages.append(message)
    session["user_messages"] = user_messages


def make_bot_message(text, labels=None):
    return {"sender": "bot", "text": text, "labels": labels or []}


def make_user_message(text):
    return {"sender": "user", "text": text}


def append_bot_turn(message):
    append_chatbot_messages([message["text"]])
    return message


def normalize_for_validation(message):
    return re.sub(r"\s+", "", message).lower()


def is_meaningless_input(message, state):
    compact = normalize_for_validation(message)
    if not compact:
        return True
    if compact in MEANINGLESS_INPUTS:
        return state != STATE_WAIT_HISTORY
    if re.fullmatch(r"[\d\W_]+", compact):
        return True
    if len(compact) < 3:
        return True
    return False


def validate_user_message(message, state):
    if state in STATE_RETRY_MESSAGES and is_meaningless_input(message, state):
        return False, STATE_RETRY_MESSAGES[state]
    return True, ""


def has_resolution_intent(message):
    """Detect acceptance, action intention, or trust intention after advice."""
    compact = normalize_for_validation(message)
    if any(marker in compact for marker in CONTINUATION_INTENT_MARKERS):
        return False
    return any(marker in compact for marker in RESOLUTION_INTENT_MARKERS)


def frame_label():
    return "Gain Frame" if session["frame"] == "gain" else "Loss Frame"


def build_conversation_context():
    return (
        f"任务角色：{session['task']}\n"
        f"用户开场：{session.get('initial_problem', '')}\n"
        f"探索回答：{session.get('exploration_answers', [])}\n"
        f"全部用户消息：{session.get('user_messages', [])}"
    )


def start_turn():
    """Send only the opening turn, then wait for real user input."""
    texts = get_welcome_messages(session["task"])
    session["state"] = STATE_WAIT_INITIAL_PROBLEM
    return [append_bot_turn(make_bot_message(text, ["Opening"])) for text in texts]


def next_bot_turn(user_message):
    """Generate exactly one chatbot turn from the current FSM state."""
    state = session.get("state", STATE_WAIT_INITIAL_PROBLEM)

    if state in {STATE_WAIT_ADVICE_FOLLOWUP, STATE_CONTINUED_FOLLOWUP} and has_resolution_intent(user_message):
        session["state"] = STATE_COMPLETED
        session["finished"] = True
        return append_bot_turn(make_bot_message("好的，那我们先停在这里。", ["Closing"]))

    if state == STATE_WAIT_INITIAL_PROBLEM:
        session["initial_problem"] = user_message
        support = get_emotional_support(session["empathy"], session["frame"], user_message)
        question = get_exploration_turn(0, task_condition=session["task"])
        session["state"] = STATE_WAIT_CAUSE
        return append_bot_turn(
            make_bot_message(
                f"{support}\n\n{question}",
                ["Acknowledgement", "Emotional Support", "Problem Inquiry"],
            )
        )

    if state == STATE_WAIT_CAUSE:
        exploration_answers = session.get("exploration_answers", [])
        exploration_answers.append(user_message)
        session["exploration_answers"] = exploration_answers
        analysis = get_problem_analysis(
            session["task"],
            session["initial_problem"],
            exploration_answers,
        )
        question = get_exploration_turn(1, user_message, session["task"])
        session["state"] = STATE_WAIT_HISTORY
        return append_bot_turn(
            make_bot_message(
                f"{analysis}\n\n{question}",
                ["Problem Inquiry", "Problem Analysis"],
            )
        )

    if state == STATE_WAIT_HISTORY:
        exploration_answers = session.get("exploration_answers", [])
        exploration_answers.append(user_message)
        session["exploration_answers"] = exploration_answers
        question = get_exploration_turn(2, user_message, session["task"])
        session["state"] = STATE_WAIT_COMMUNICATION
        return append_bot_turn(make_bot_message(question, ["Problem Inquiry"]))

    if state == STATE_WAIT_COMMUNICATION:
        exploration_answers = session.get("exploration_answers", [])
        exploration_answers.append(user_message)
        session["exploration_answers"] = exploration_answers
        summary = get_fixed_summary(exploration_answers)
        advice = get_advice(
            session["frame"],
            session["task"],
            session["initial_problem"],
            exploration_answers,
        )
        session["state"] = STATE_WAIT_ADVICE_FOLLOWUP
        return append_bot_turn(
            make_bot_message(
                f"{summary}\n\n{advice}\n\n你觉得这种方式适合你的情况吗？",
                ["Advice", frame_label()],
            )
        )

    followup = get_advice_reinforcement(
        session["frame"],
        session["task"],
        user_message,
        build_conversation_context(),
    )
    session["state"] = STATE_CONTINUED_FOLLOWUP
    return append_bot_turn(make_bot_message(followup, ["Advice Reinforcement"]))


def record_conversation_once():
    if session.get("recorded"):
        return

    ensure_csv_exists()
    row = {
        "participant_id": session["participant_id"],
        "timestamp": session["timestamp"],
        "task": session["task"],
        "frame": session["frame"],
        "empathy": session["empathy"],
        "user_messages": json.dumps(session.get("user_messages", []), ensure_ascii=False),
        "chatbot_messages": json.dumps(session.get("chatbot_messages", []), ensure_ascii=False),
    }

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS)
        writer.writerow(row)

    session["recorded"] = True


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        task = request.form.get("task")

        if task not in VALID_TASKS:
            return render_template(
                "setup.html",
                error="请选择一个关系角色。",
            )

        session.clear()
        session["pending_task"] = task
        return redirect(url_for("conditions"))

    return render_template("setup.html")


@app.route("/conditions", methods=["GET", "POST"])
def conditions():
    task = session.get("pending_task")
    if task not in VALID_TASKS:
        return redirect(url_for("index"))

    if request.method == "POST":
        frame = request.form.get("frame")
        empathy = request.form.get("empathy")

        if frame not in VALID_FRAMES or empathy not in VALID_EMPATHY:
            return render_template(
                "conditions.html",
                task=task,
                error="请选择信息框架和共情沟通条件。",
            )

        reset_conversation(task, frame, empathy)
        return redirect(url_for("chat"))

    return render_template("conditions.html", task=task)


@app.route("/chat")
def chat():
    if "participant_id" not in session:
        return redirect(url_for("index"))
    return render_template("chat.html", example_statement=get_scenario(session["task"]))


@app.route("/api/start", methods=["POST"])
def api_start():
    if "participant_id" not in session:
        return jsonify({"error": "当前没有进行中的对话。"}), 400
    if session.get("chatbot_messages"):
        return jsonify({"messages": [], "finished": False})
    return jsonify(
        {
            "messages": start_turn(),
            "finished": False,
        }
    )


@app.route("/api/message", methods=["POST"])
def api_message():
    if "participant_id" not in session:
        return jsonify({"error": "当前没有进行中的对话。"}), 400

    payload = request.get_json(silent=True, force=True) or {}
    message = payload.get("message", "").strip()
    if not message:
        return jsonify({"error": "请输入回答。"}), 400

    state = session.get("state", STATE_WAIT_INITIAL_PROBLEM)
    is_valid, retry_message = validate_user_message(message, state)
    if not is_valid:
        return jsonify(
            {
                "messages": [make_bot_message(retry_message, ["Clarification"])],
                "finished": False,
                "accepted": False,
            }
        )

    append_user_message(message)
    bot_message = next_bot_turn(message)
    finished = bool(session.get("finished"))
    return jsonify(
        {
            "messages": [bot_message],
            "finished": finished,
            "accepted": True,
        }
    )


@app.route("/api/finish", methods=["POST"])
def api_finish():
    if "participant_id" not in session:
        return jsonify({"error": "当前没有进行中的对话。"}), 400
    record_conversation_once()
    return jsonify({"redirect": url_for("finish")})


@app.route("/api/llm_turn", methods=["POST"])
def api_llm_turn():
    payload = request.get_json(silent=True, force=True) or {}
    stage = payload.get("stage")
    role = payload.get("role", "victim")
    frame = payload.get("frame", "gain")
    empathy = payload.get("empathy", "high")
    user_message = payload.get("userMessage", "")
    initial_problem = payload.get("initialProblem", "")
    answers = payload.get("answers", [])
    context = payload.get("context", "")

    if role not in VALID_TASKS or frame not in VALID_FRAMES or empathy not in VALID_EMPATHY:
        return jsonify({"error": "实验条件无效。"}), 400

    if stage == "emotional_support":
        text = get_emotional_support(empathy, frame, user_message)
    elif stage == "exploration_turn_1":
        text = get_exploration_turn(1, user_message, role)
    elif stage == "exploration_turn_2":
        text = get_exploration_turn(2, user_message, role)
    elif stage == "problem_analysis":
        text = get_problem_analysis(role, initial_problem, answers)
    elif stage == "summary":
        text = get_fixed_summary(answers)
    elif stage == "advice":
        text = get_advice(frame, role, initial_problem, answers)
    elif stage == "advice_reinforcement":
        text = get_advice_reinforcement(frame, role, user_message, context)
    else:
        return jsonify({"error": "未知生成阶段。"}), 400

    return jsonify({"text": text})


@app.route("/api/llm_status")
def api_llm_status():
    return jsonify(get_llm_status())


@app.route("/finish")
def finish():
    if "participant_id" in session:
        record_conversation_once()
    return render_template("finish.html")


if __name__ == "__main__":
    ensure_csv_exists()
    app.run(debug=True)
