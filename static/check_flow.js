document.getElementById("flow_view").addEventListener("click", async () => {
    try {
        const response = await fetch("/view_analysis_api/flow_view");
        const data = await response.json();
        const statusEl = document.getElementById("status");

        if (data.status === true) {
            statusEl.textContent = "Смотрим поток...";
            statusEl.style.display = "inline";
            setTimeout(() => {
                statusEl.textContent = "";
            }, 5000);
        } else {
            statusEl.textContent = "Ошибка: поток не найден.";
            setTimeout(() => {
                statusEl.textContent = "";
            }, 3000);
        }
    } catch (err) {
        console.error("Ошибка запроса:", err);
    }
});