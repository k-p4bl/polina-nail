const users = document.querySelectorAll('.btn-user')

const input = document.getElementById("searth")
input.addEventListener("input", (e) => {

    if (e.target.value.length === 0){
        for (let i = 0; i < users.length; i++){
            users[i].setAttribute("style", "display: block;")
        }
    }

    if (e.target.value[0] == "+"){
        let str = e.target.value.replace(/\W|_/g, '');
        console.log(str)
        for (let i = 0; i < users.length; i++){
            if (users[i].innerHTML.match(str)){
                users[i].setAttribute("style", "display: block;")
            }else{
                users[i].setAttribute("style", "display: none;")
            }
        }
    }else{
        let str = e.target.value.split(" ")

        for (let i = 0; i < users.length; i++){
            for (let j = 0; j < str.length; j++) {
                if (str[j].length > 0) {
                    if (users[i].innerHTML.match(str[j])){
                        users[i].setAttribute("style", "display: block;")
                        continue
                    }else{
                        users[i].setAttribute("style", "display: none;")
                        break
                    }
                }
            }
        }
    }



})