document.getElementById('AIgenerate').addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!window.selectedFile) {
        alert('Выберите файл из списка!');
        return;
    }

    const formData = new FormData(event.target);
    formData.append('filename', window.selectedFile);

    try {
        const response = await fetch('/view_analysis_api/generate/analysis', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            console.log('Анализ успешно отправлен');
        } else {
            alert('Ошибка при отправке на анализ');
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка соединения с сервером');
    }
});