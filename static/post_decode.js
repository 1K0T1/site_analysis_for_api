document.getElementById('reverse_minification').addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData();
    // Добавляем данные
    formData.append('filename', document.getElementById('fileList').value);
    formData.append('code', document.getElementById('fileMessage').innerText);

    await fetch('/view_analysis_api/reverse_minification', {
        method: 'POST',
        body: formData // Отправляем как форму, а не JSON
    });
});