function sendData() {
    return new Promise ((resolve, reject) => {
        const XHR = new XMLHttpRequest();

        // Bind the FormData object and the form element
        const FD = new FormData(form);

        // Define what happens on successful data submission
        // XHR.addEventListener("load", function (event) {
        //     alert(event.target.responseText);
        // });

        //Define what happens in case of error
        // XHR.addEventListener("error", function (event) {
        //     alert("Oops! Something went wrong.");
        // });

        // Set up our request
        XHR.open("POST", requestURL);

        XHR.responseType = 'json'
        // XHR.setRequestHeader('Content-Type', 'application/json')
        //
        XHR.onload = () => {
            if (XHR.status >= 400) {
                reject(XHR.response)
            } else {
                resolve(XHR.response)
            }
        }

        XHR.onerror = () => {
            reject(XHR.response)
        }

        // The data sent is what the user provided in the form
        XHR.send(FD);
    })

}

const form = document.querySelector('form');

// ...and take over its submit event.
form.addEventListener("submit", function (event) {
    let btn = this.querySelector("input[type=submit], button[type=submit]");
    btn.disabled = true;

    event.preventDefault();

    sendData()
        .then(response => {
            //Инициализация виджета. Все параметры обязательные.
            const checkout = new window.YooMoneyCheckoutWidget({
                confirmation_token: response["confirmation_token"], //Токен, который перед проведением оплаты нужно получить от ЮKassa

                //При необходимости можно изменить цвета виджета, подробные настройки см. в документации
                customization: {
                    modal: true

                    //Настройка цветовой схемы, минимум один параметр, значения цветов в HEX
                    //colors: {
                    //Цвет акцентных элементов: кнопка Заплатить, выбранные переключатели, опции и текстовые поля
                    //control_primary: '#00BF96', //Значение цвета в HEX

                    //Цвет платежной формы и ее элементов
                    //background: '#F2F3F5' //Значение цвета в HEX
                    //}

                },
                error_callback: function(error) {
                    console.log(error)
                }
            });

            checkout.on('success', () => {
                //Код, который нужно выполнить после успешной оплаты.

                const sign_up = {
                    last_name: response.data['last_name'],
                    first_name: response.data['first_name'],
                    patronymic: response.data['patronymic'],
                    phone_number: response.data['phone_number'],
                    year: response.data['year'],
                    month: response.data['month'],
                    day: response.data['day'],
                    time: response.data['time'],
                    service: response.data['service'],
                    add_services_id: response.data['add_services_id'],
                    payment_id: response.data['payment_id']
                };
                sendRequest('POST', requestURL + "create_obj_of_sign_up/", sign_up)
                    .then(data => {
                        //Удаление инициализированного виджета
                        checkout.destroy();

                        window.location.href = 'finish/' + data['pk'];
                    })
                    .catch(err => console.log(err))
            });

            checkout.on('fail', () => {
                //Удаление инициализированного виджета
                checkout.destroy();
                window.location.href = requestURL + "error/";
            });

            //Отображение платежной формы в контейнере
            checkout.render('payment-form');
        })
});