// all script
function submitForm(actionUrl, data) 
{
    const form = document.createElement("form");
    form.method = "POST";
    form.action = actionUrl;
    form.acceptCharset = "UTF-8";
    form.setAttribute("accept-charset", "UTF-8");

    Object.keys(data).forEach(key => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = key;
        input.value = data[key];
        form.appendChild(input);
    });

    document.body.appendChild(form);
    form.submit();
}
function getHashkeyCookie() 
{
    const cookie = document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('hashkey='));
    return cookie ? cookie.split('=')[1] : null;
}
function renderButtons(buttonConfigs) 
{
    buttonConfigs.forEach(cfg => {
        const container = document.getElementById(cfg.containerId);
        if (!container) return;

        container.innerHTML = "";

        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = cfg.className || "";
        btn.textContent = cfg.text || "Кнопка";
        if (typeof cfg.onClick === "function")
        {
            btn.onclick = cfg.onClick;
        }
        container.appendChild(btn);
    });
}
function showToast(message, type = "error") 
{
    let container = document.querySelector(".toast-container");
    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;

    const closeBtn = document.createElement("button");
    closeBtn.className = "close-btn";
    closeBtn.innerHTML = "&times;";
    closeBtn.onclick = () => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    };
    toast.appendChild(closeBtn);

    container.appendChild(toast);
    setTimeout(() => toast.classList.add("show"), 100);
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
