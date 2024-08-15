let form = document.querySelector("form")
let btn_dis = document.querySelector("#move")
let btn_sub = document.querySelector("#cancel")
form.addEventListener('submit', (e) => {
    btn_dis.disabled = true
    btn_sub.disabled = true
})