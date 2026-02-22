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
            showNotice(
                `Файл "${window.selectedFile}" отправлен на анализ. Скоро результат response.txt появится в списке.`
            );
        } else {
            showNotice('Ошибка при отправке на анализ', 3000);
        }

    } catch (error) {
        console.error('Ошибка:', error);
        showNotice('Ошибка соединения с сервером', 3000);
    }
});