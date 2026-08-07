const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const typingIndicator = document.getElementById("typingIndicator");
const finishButton = document.getElementById("finishButton");

function appendMessage(sender, text, labels = []) {
    const row = document.createElement("div");
    row.className = `message-row ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = `avatar ${sender}`;
    avatar.textContent = sender === "bot" ? "AI" : "我";

    const bubble = document.createElement("div");
    bubble.className = `message ${sender}`;
    bubble.textContent = text;

    const content = document.createElement("div");
    content.className = "message-content";
    content.appendChild(bubble);

    if (sender === "bot" && labels.length > 0) {
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

function showTyping() {
    typingIndicator.hidden = false;
    chatLog.scrollTop = chatLog.scrollHeight;
}

function hideTyping() {
    typingIndicator.hidden = true;
}

function delay(ms) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, ms);
    });
}

async function displayBotMessages(messages) {
    setInputEnabled(false);
    for (const message of messages) {
        showTyping();
        await delay(450);
        hideTyping();
        appendMessage(message.sender, message.text, message.labels || []);
    }
    setInputEnabled(true);
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
    await displayBotMessages(data.messages || []);
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

    try {
        const data = await postJson("/api/message", { message });
        await handleBotResponse(data);
    } catch (error) {
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
    try {
        const data = await postJson("/api/start");
        await handleBotResponse(data);
    } catch (error) {
        appendMessage("bot", error.message);
    }
});
