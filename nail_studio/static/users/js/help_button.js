const btns = document.querySelectorAll(".help")
const modal = document.querySelector('#modal');
const close = document.querySelector('.close');

for (let i = 0; i < btns.length; i++) {
  btns[i].addEventListener('click', (e) => {
      modal.style.display = 'flex';
  })
}

// btn.onclick = function () {
//   modal.style.display = 'block';
// };

close.onclick = function () {
  modal.style.display = 'none';
};

window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = 'none';
  }
};