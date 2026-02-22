function showNotice(message, duration = 9000) {
    const notice = document.getElementById('globalNotice');
    notice.textContent = message;
    notice.classList.add('show');

    setTimeout(() => {
        notice.classList.remove('show');
    }, duration);
}