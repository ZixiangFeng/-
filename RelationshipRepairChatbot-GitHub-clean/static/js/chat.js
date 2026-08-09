const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const finishButton = document.getElementById("finishButton");

function appendMessage(sender, text, labels = []) {
    const lastMessageRow = chatLog.querySelector(".message-row:not(.typing-row):last-child");
    const isGrouped = lastMessageRow && lastMessageRow.classList.contains(sender);

    const row = document.createElement("div");
    row.className = `message-row ${sender}`;
    if (isGrouped) {
        row.classList.add("grouped");
    }

    const avatar = document.createElement("div");
    avatar.className = isGrouped ? "avatar-spacer" : `avatar ${sender}`;
    avatar.textContent = isGrouped ? "" : sender === "bot" ? "AI" : "我";

    const bubble = document.createElement("div");
    bubble.className = `message ${sender}`;
    bubble.textContent = text;

    const content = document.createElement("div");
    content.className = "message-content";
    content.appendChild(bubble);

    if (sender === "bot" && labels.length > 0) {
        if (isGrouped) {
            const previousLabels = lastMessageRow.querySelector(".message-labels");
            if (previousLabels) {
                previousLabels.remove();
            }
        }
        const labelWrap = document.createElement("div");
        labelWrap.className = "message-labels";
        labels.forEach((label) => {
            const pill = document.createElement("span");
            pill.className = `stage-label ${label.toLowerCase().replaceAll(" ", "-")}`;
            pill.textContent = label;
            labelWrap.appendChild(pill);
        });
        content.appendChild(labelWrap);
    }

    if (sender === "bot") {
        row.appendChild(avatar);
        row.appendChild(content);
    } else {
        row.appendChild(content);
        row.appendChild(avatar);
    }
    chatLog.appendChild(row);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function setInputEnabled(enabled) {
    messageInput.disabled = !enabled;
    chatForm.querySelector("button").disabled = !enabled;
    if (enabled) {
        messageInput.focus();
    }
}

function appendTypingMessage() {
    const row = document.createElement("div");
    row.className = "message-row bot typing-row";

    const avatar = document.createElement("div");
    avatar.className = "avatar bot";
    avatar.textContent = "AI";

    const bubble = document.createElement("div");
    bubble.className = "message bot typing-indicator";
    bubble.setAttribute("aria-label", "AI 正在输入");
    bubble.innerHTML = "<span></span><span></span><span></span>";

    const content = document.createElement("div");
    content.className = "message-content";
    content.appendChild(bubble);

    row.appendChild(avatar);
    row.appendChild(content);
    chatLog.appendChild(row);
    chatLog.scrollTop = chatLog.scrollHeight;
    return row;
}

function removeTypingMessage(row) {
    if (row && row.parentNode) {
        row.parentNode.removeChild(row);
    }
}

function delay(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, ms);
    });
}

async function displayBotMessages(messages, keepInputDisabled = false) {
    setInputEnabled(false);
    for (const message of messages) {
        appendMessage(message.sender, message.text, message.labels || []);
        await delay(180);
    }
    setInputEnabled(!keepInputDisabled);
}

async function waitForMinimum(startedAt, minimumMs = 700) {
    const elapsed = Date.now() - startedAt;
    if (elapsed < minimumMs) {
        await delay(minimumMs - elapsed);
    }
}

async function postJson(url, payload = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }
    return data;
}

async function handleBotResponse(data) {
    await displayBotMessages(data.messages || [], Boolean(data.finished));
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = messageInput.value.trim();
    if (!message) {
        return;
    }

    appendMessage("user", message);
    messageInput.value = "";
    setInputEnabled(false);

    const startedAt = Date.now();
    const typingRow = appendTypingMessage();
    try {
        const data = await postJson("/api/message", { message });
        await waitForMinimum(startedAt);
        removeTypingMessage(typingRow);
        await handleBotResponse(data);
    } catch (error) {
        removeTypingMessage(typingRow);
        appendMessage("bot", error.message);
        setInputEnabled(true);
    }
});

finishButton.addEventListener("click", async () => {
    setInputEnabled(false);
    try {
        const data = await postJson("/api/finish");
        window.location.href = data.redirect || "/finish";
    } catch (error) {
        appendMessage("bot", error.message);
        setInputEnabled(true);
    }
});

document.addEventListener("DOMContentLoaded", async () => {
    setInputEnabled(false);
    const startedAt = Date.now();
    const typingRow = appendTypingMessage();
    try {
        const data = await postJson("/api/start");
        await waitForMinimum(startedAt, 500);
        removeTypingMessage(typingRow);
        await handleBotResponse(data);
    } catch (error) {
        removeTypingMessage(typingRow);
        appendMessage("bot", error.message);
    }
});
