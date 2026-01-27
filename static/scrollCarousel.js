document.addEventListener('DOMContentLoaded', () => {
    let currentIndex = 0;
    const itemsToShow = 6;

    // Находим элементы один раз, чтобы не искать их при каждом клике (оптимизация)
    const carousel = document.getElementById('Carousel');
    const forms = carousel.querySelectorAll('form');
    const prevBtn = document.getElementById('leftBtn');
    const nextBtn = document.getElementById('rightBtn');

    function updateCarousel() {
        // Ограничиваем индекс
        if (currentIndex < 0) {
            currentIndex = 0;
        }
        if (currentIndex > forms.length - itemsToShow) {
            // Если форм меньше, чем itemsToShow, индекс станет 0 или больше
            currentIndex = Math.max(0, forms.length - itemsToShow);
        }

        // Скрываем все формы
        forms.forEach(form => form.style.display = 'none');

        // Показываем нужные элементы
        for (let i = currentIndex; i < currentIndex + itemsToShow && i < forms.length; i++) {
            forms[i].style.display = 'block';
        }
    }

    // Назначаем обработчики клика через JS
    prevBtn.addEventListener('click', () => {
        currentIndex -= 1; // direction -1
        updateCarousel();
    });

    nextBtn.addEventListener('click', () => {
        currentIndex += 1; // direction 1
        updateCarousel();
    });

    // Инициализация (показываем первые элементы сразу)
    updateCarousel();
});