document.getElementById('reverse_minification').addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!window.selectedFile) {
        alert('Файл не выбран!');
        return;
    }

    const formData = new FormData();
    formData.append('filename', window.selectedFile);
    formData.append('code', document.getElementById('fileMessage').innerText);

    // 🔥 уведомление сразу при нажатии
    showNotice(`Файл "${window.selectedFile}" отправлен на восстановление кода. Результат скоро появится в списке.`);

    try {
        await fetch('/view_analysis_api/reverse_minification', {
            method: 'POST',
            body: formData
        });
    } catch (error) {
        console.error(error);
        showNotice('Ошибка соединения с сервером', 3000);
    }
});