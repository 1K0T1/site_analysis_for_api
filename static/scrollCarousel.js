let currentIndex = 0;

function scrollCarousel(direction) {
    const carousel = document.getElementById('Carousel');
    const forms = carousel.querySelectorAll('form');
    const itemsToShow = 6;

    currentIndex += direction;

    // Ограничиваем индекс
    if (currentIndex < 0) {
        currentIndex = 0;
    }
    if (currentIndex > forms.length - itemsToShow) {
        currentIndex = forms.length - itemsToShow;
    }

    // Скрываем все
    forms.forEach(form => form.style.display = 'none');

    // Показываем нужные элементы
    for (let i = currentIndex; i < currentIndex + itemsToShow && i < forms.length; i++) {
        forms[i].style.display = 'block';
    }
}