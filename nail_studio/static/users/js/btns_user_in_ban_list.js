function sendRequest (method, url, data) {
    return new Promise ((resolve, reject) => {
        const xhr = new XMLHttpRequest()

        xhr.open(method, url)

        xhr.responseType = 'json'
        xhr.setRequestHeader('Content-Type', 'application/json')

        xhr.onload = () => {
            if (xhr.status >= 400) {
                reject(xhr.response)
            } else {
                resolve(xhr.response)
            }
        }

        xhr.onerror = () => {
            reject(xhr.response)
        }
        xhr.send(JSON.stringify(data))
    })
}


const modal = document.querySelector('#modal');

window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = 'none';
  }
};

function clickOnButton (lName, pk) {
    modal.style.display = 'flex';
    document.getElementById("text-unblock").innerText = 'Разблокировать пользователя "' + lName + '"?'
    document.getElementById("yes").addEventListener("click", (e) => {
        sendRequest("post", "/users/unban_user/", pk)
            .then(result => {
                if (result["success"]){
                    location.reload()
                }
            })
    })
}

function clickBtnNo () {
    modal.style.display = 'none';
}