document.getElementById('reverse_obfuscated').addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!window.selectedFile) {
        alert('Файл не выбран!');
        return;
    }

    const formData = new FormData();
    formData.append('filename', window.selectedFile);
    formData.append('code', document.getElementById('fileMessage').innerText);

    await fetch('/view_analysis_api/reverse_obfuscated', {
        method: 'POST',
        body: formData
    });
});