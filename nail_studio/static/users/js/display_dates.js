function displayDates(obj) {
    console.log(obj)

    const div = document.querySelector(".container")
    for (let year in obj) {
        let newButton = document.createElement("button")
        newButton.setAttribute("class", "year btn close")
        newButton.insertAdjacentText("beforeend", year)
        newButton.addEventListener("click", (e) => {
            let elem = document.querySelectorAll('button[before= "' + year + '"]');
            if (elem.length === 0){
                newButton.setAttribute("class", "year btn open")
                for (let month in obj[year]){
                    let btn = document.createElement("button")
                    btn.setAttribute("class", "month btn close")
                    btn.setAttribute("before", year)
                    btn.insertAdjacentText("beforeend", month)
                    btn.addEventListener("click", (e) =>{
                        let elem = document.querySelectorAll('button[before= "'+ year + month +'"]');
                        if (elem.length === 0){
                            btn.setAttribute("class", "month btn open")
                            for (let day in obj[year][month]){
                                let nextBtn = document.createElement("button")
                                nextBtn.setAttribute("class", "day btn close")
                                nextBtn.setAttribute("before", year + month)
                                nextBtn.insertAdjacentText("beforeend", day)
                                nextBtn.addEventListener("click", (e) =>{
                                    let elem = document.querySelectorAll('button[before= "'+ year + month + day +'"]');
                                    if (elem.length === 0){
                                        nextBtn.setAttribute("class", "day btn open")
                                        for (let time in obj[year][month][day]){
                                                let timeBtn = document.createElement("button")
                                                timeBtn.setAttribute("class", "time btn")
                                                timeBtn.setAttribute("before", year + month + day)
                                                timeBtn.insertAdjacentText("beforeend", time)
                                                timeBtn.insertAdjacentText("beforeend", ":00")
                                                timeBtn.addEventListener("click", (e) => {
                                                    location.href = "/users/sign_up/" + obj[year][month][day][time]
                                                })
                                                nextBtn.insertAdjacentElement("afterend", timeBtn)
                                        }
                                    }else {
                                        nextBtn.setAttribute("class", "day btn close")
                                        for (let i = 0; i < elem.length; i++){
                                            elem[i].remove()
                                        }
                                    }
                                })
                                btn.insertAdjacentElement("afterend", nextBtn)
                            }
                        }else {
                            btn.setAttribute("class", "month btn close")
                            for (let i = 0; i < elem.length; i++){
                                times = document.querySelectorAll('button[before= "'+ elem[i].getAttribute("before") + elem[i].innerHTML +'"]');
                                for (let j = 0; j < times.length; j++){
                                    times[j].remove()
                                }
                                elem[i].remove()
                            }
                        }
                    })
                    newButton.insertAdjacentElement("afterend", btn)
                }
            }else {
                newButton.setAttribute("class", "year btn close")
                for (let i = 0; i < elem.length; i++){
                    days = document.querySelectorAll('button[before= "'+ elem[i].getAttribute("before") + elem[i].innerHTML +'"]');
                    for (let j = 0; j < days.length; j++){
                        times = document.querySelectorAll('button[before= "'+ days[j].getAttribute("before") + days[j].innerHTML +'"]');
                        for (let k = 0; k < times.length; k++){
                            times[k].remove()
                        }
                        days[j].remove()
                    }
                    elem[i].remove()
                }
            }
            
        })
        div.insertAdjacentElement("beforeend", newButton)
    }

}