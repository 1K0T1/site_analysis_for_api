const socket = io();

// 🔹 При получении нового списка файлов
socket.on('update_files', (files) => {
    const select = document.getElementById('fileList');
    if (!select) return;

    select.innerHTML = ''; // очищаем старые элементы

    files.forEach(file => {
        const option = document.createElement('option');
        option.value = file;
        option.textContent = file;
        select.appendChild(option);
    });
});


// 🔹 Обновляем список каждые 3 секунды
setInterval(() => {
  socket.emit("request_files");
}, 3000);

// 🔹 При выборе файла
document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('fileList');
    if (!select) return;

    select.addEventListener('change', (e) => {
        const selectedFile = e.target.value;
        socket.emit('file_selected', selectedFile);
    });

    // при загрузке сразу запросим список
    socket.emit('request_files');
});

// 🔹 При подтверждении выбора
socket.on('file_chosen', (data) => {
    const fileMsg = data.fileMessage; 
    document.querySelector('.viewcode').textContent = fileMsg;
});
