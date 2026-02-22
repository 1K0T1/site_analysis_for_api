document.getElementById('reverse_obfuscated').addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!window.selectedFile) {
        alert('Файл не выбран!');
        return;
    }

    const formData = new FormData();
    formData.append('filename', window.selectedFile);
    formData.append('code', document.getElementById('fileMessage').innerText);

    // 🔔 Уведомление сразу при нажатии
    showNotice(
        `Файл "${window.selectedFile}" отправлен на деобфускацию. Результат скоро появится в списке.`
    );

    try {
        const response = await fetch('/view_analysis_api/reverse_obfuscated', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            showNotice('Ошибка при отправке файла на деобфускацию', 3000);
        }

    } catch (error) {
        console.error(error);
        showNotice('Ошибка соединения с сервером', 3000);
    }
});