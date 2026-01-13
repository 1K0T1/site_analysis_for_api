function scrollCarousel(direction) {
    const carousel = document.getElementById('Carousel');
    const itemWidth = 76; 

    const scrollAmount = itemWidth * direction;
    
    carousel.scrollBy({
        left: scrollAmount,
        behavior: 'smooth'
    });
}