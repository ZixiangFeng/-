const conditions = [
    { id: 1, taskValue: "victim", frameValue: "gain", empathyValue: "high", role: "受伤害者", frame: "收益框架", empathy: "高共情" },
    { id: 2, taskValue: "victim", frameValue: "gain", empathyValue: "low", role: "受伤害者", frame: "收益框架", empathy: "低共情" },
    { id: 3, taskValue: "victim", frameValue: "loss", empathyValue: "high", role: "受伤害者", frame: "损失框架", empathy: "高共情" },
    { id: 4, taskValue: "victim", frameValue: "loss", empathyValue: "low", role: "受伤害者", frame: "损失框架", empathy: "低共情" },
    { id: 5, taskValue: "transgressor", frameValue: "gain", empathyValue: "high", role: "过错方", frame: "收益框架", empathy: "高共情" },
    { id: 6, taskValue: "transgressor", frameValue: "gain", empathyValue: "low", role: "过错方", frame: "收益框架", empathy: "低共情" },
    { id: 7, taskValue: "transgressor", frameValue: "loss", empathyValue: "high", role: "过错方", frame: "损失框架", empathy: "高共情" },
    { id: 8, taskValue: "transgressor", frameValue: "loss", empathyValue: "low", role: "过错方", frame: "损失框架", empathy: "低共情" },
];

const drawButton = document.getElementById("drawConditionButton");
const randomResult = document.getElementById("randomResult");
const setupLink = document.getElementById("setupPresetLink");

drawButton.addEventListener("click", () => {
    const selected = conditions[Math.floor(Math.random() * conditions.length)];
    randomResult.innerHTML = `
        <strong>条件 ${selected.id}</strong>
        <span>${selected.role} / ${selected.frame} / ${selected.empathy}</span>
    `;
    setupLink.href = `/setup?condition=${selected.id}&task=${selected.taskValue}&frame=${selected.frameValue}&empathy=${selected.empathyValue}`;
    setupLink.textContent = `进入 setting 设置：条件 ${selected.id}`;
});
