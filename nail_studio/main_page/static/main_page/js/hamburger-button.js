document.querySelector('.hamburger-button').addEventListener('click', function() {
    this.classList.toggle('active');
    document.querySelector('.navigation').classList.toggle('open');
})
document.querySelector('.navigation').addEventListener('click', function() {
    this.classList.toggle('open');
    document.querySelector('.hamburger-button').classList.toggle('active');
})