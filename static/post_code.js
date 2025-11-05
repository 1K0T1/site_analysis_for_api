document.getElementById("AIgenerate").addEventListener("submit", function (e) {
    e.preventDefault(); // отменяем стандартную отправку формы

    const selectedOption = document.getElementById("fileList").value; // получаем выбранный элемент
    if (!selectedOption) {
        alert("Выберите файл из списка!");
        return;
    }

    const content = document.querySelector("#copy code").innerText; // содержимое файла
    const formData = new FormData();
    const blob = new Blob([content], { type: "text/plain" });

    // добавляем файл с именем из select
    formData.append("file", blob, selectedOption);

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