// Отслеживаем изменение выбора файла в списке
document.getElementById("fileList").addEventListener('change', (event) => {
    const selectedOption = event.target.value;

    if (selectedOption) {
        window.selectedFile = selectedOption; // сохраняем выбранный файл глобально
        console.log('Файл выбран:', window.selectedFile);
    } else {
        window.selectedFile = null; // сбрасываем если ничего не выбрано
    }
});

// Обработка отправки формы
document.getElementById("post_code").addEventListener("submit", function (e) {
    e.preventDefault(); // отменяем стандартную отправку формы

    if (!window.selectedFile) {
        alert("Выберите файл из списка!");
        return;
    }

    const content = document.querySelector("#copy code").innerText; // содержимое файла
    const formData = new FormData();
    const blob = new Blob([content], { type: "text/plain" });

    // добавляем файл с именем из window.selectedFile
    formData.append("file", blob, window.selectedFile);

    fetch(this.action, {
        method: "POST",
        body: formData
    })
        .then(response => response.json()) // если сервер возвращает JSON
        .then(data => {
            console.log("Файл успешно отправлен:", data);
            alert("Файл отправлен на анализ!");
        })
        .catch(error => {
            console.error("Ошибка:", error);
            alert("Ошибка при отправке файла");
        });
});