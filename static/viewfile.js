const socket = io();

// 🔹 Обновление списка файлов
socket.on('update_files', (files) => {
    const select = document.getElementById('fileList');
    if (!select) return;

    select.innerHTML = '';
    files.forEach(file => {
        const option = document.createElement('option');
        option.value = file;
        option.textContent = file;
        select.appendChild(option);
    });
});

// 🔹 Запрос списка файлов каждые 3 секунды
setInterval(() => {
    socket.emit("request_files");
}, 3000);

// 🔹 Выбор файла
document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('fileList');
    if (!select) return;

    select.addEventListener('change', (e) => {
        const selectedFile = e.target.value;
        socket.emit('file_selected', selectedFile);
    });

    socket.emit('request_files'); // запрос сразу при загрузке
});

// 🔹 Отображение выбранного файла
socket.on('file_chosen', (data) => {
    const fileMsg = data.fileMessage;
    const view = document.querySelector('.viewcode');

    const code = view.querySelector('code');
    const img = view.querySelector('img');
    const audio = view.querySelector('audio');
    const video = view.querySelector('video');

    // скрываем всё по умолчанию
    [code, img, audio, video].forEach(el => {
        el.style.display = 'none';
        if (el.tagName !== 'CODE') el.src = '';
    });
    code.textContent = '';

    if (fileMsg.startsWith('data:')) {
        const mime = fileMsg.split(';')[0].split(':')[1];
        if (mime.startsWith('image/')) {
            img.src = fileMsg;
            img.style.display = 'block';
        } else if (mime.startsWith('audio/')) {
            audio.src = fileMsg;
            audio.controls = true;
            audio.style.display = 'block';
        } else if (mime.startsWith('video/')) {
            video.src = fileMsg;
            video.controls = true;
            video.style.display = 'block';
        } else {
            code.textContent = fileMsg;
            code.style.display = 'block';
        }
    } else {
        code.textContent = fileMsg;
        code.style.display = 'block';
    }
});
