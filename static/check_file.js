document.getElementById("download-list").addEventListener("submit", async (e) => {
    e.preventDefault();
    const status = document.getElementById("status");
    status.textContent = "⏳ Создание файла...";

    // запускаем генерацию
    await fetch("/view_analysis_api/link", { method: "POST" });

    // проверяем каждые 3 секунды
    const interval = setInterval(async () => {
        const res = await fetch("/check_file");
        const data = await res.json();

        if (data.exists) {
            clearInterval(interval);
            status.textContent = "✅ Скачивание...";
            window.location.href = "/download_list";
        }
    }, 3000);
});
