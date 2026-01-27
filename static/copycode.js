document.addEventListener('DOMContentLoaded', () => {
    // Находим кнопку по ID
    const copyBtn = document.getElementById('copyCode');

    // Проверяем, существует ли кнопка, прежде чем вешать событие
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const copyTarget = document.getElementById("copy");

            if (copyTarget) {
                const code = copyTarget.innerText;

                navigator.clipboard.writeText(code)
                    .then(() => alert("Код скопирован!"))
                    .catch(err => console.error("Ошибка при копировании:", err));
            } else {
                console.error("Элемент с id='copy' не найден");
            }
        });
    }
});