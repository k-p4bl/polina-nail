let button = document.querySelector('.button');

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

function sendData(form) {
    return new Promise ((resolve, reject) => {
        const XHR = new XMLHttpRequest();

        const FD = new FormData(form);

        XHR.open("POST", "/users/forgot_password/");

        XHR.responseType = 'json'

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

        XHR.send(FD);
    })

}

function validatePhoneNomber(e) {
    let telInput = document.querySelector('#phone-number');
    if (telInput.value.length > 10) {

        let phone = reformPhone(telInput.value)

        sendRequest("POST", '/users/phone-check/', phone)
            .then(result => {
                if (!result['phone_is_busy']) {
                    document.querySelector('#phone-is-busy').setAttribute('style', 'display: block;')
                }else {
                    sendRequest('POST', '/users/flash_call/', telInput.value)
                    .then(res => {
                        nextStepValidate(res['data']['phone'], res['data']['pincode']);
                    })
                    .catch(err => console.log(err))
                }
            })        
    }
}

function reformPhone(phone) {
    let firstSimbol = phone[0]
    if (firstSimbol === '8') {
        phone = "+7" + phone.substring(1)
    }
    let countryCode = phone[1]
    if (countryCode === '7') {
        phone = phone.replace(' (', '')
        phone = phone.replace(') ', '')
        phone = phone.replace('-', '')
        phone = phone.replace('-', '')
    }

    return phone
}

function getInputCodeValue(input) {
    return input.value.replace(/\D/g, "");
}

function onCodeInput(e) {
    let input = e.target,
        inputCodeValue = getInputCodeValue(input);
    let formattedInputValue = ""
    let selectionStart = input.selectionStart;

    if (!inputCodeValue) {
        return input.value = '';
    }

    if (input.value.length !== selectionStart) {
        if (e.data && /\D/g.test(e.data)) {
            input.value = inputCodeValue;
        }
        return;
    }
    

    if (inputCodeValue.length > 0){
        formattedInputValue += inputCodeValue.substring(0, 1);
    }
    if (inputCodeValue.length >= 2) {
        formattedInputValue += inputCodeValue.substring(1, 2);
    }
    if (inputCodeValue.length >= 3) {
        formattedInputValue += inputCodeValue.substring(2, 3);
    }
    if (inputCodeValue.length > 3) {
        formattedInputValue += inputCodeValue.substring(3, 4);
    }
    input.value = formattedInputValue;
}

function nextStepValidate(phone, pincode) {
    phoneForText = phone.substring(0, 2) + ' ' + phone.substring(2, 5) + ' ' + phone.substring(5, 8) + '-' + phone.substring(8, 10) + '-' + phone.substring(10, 12);

    document.querySelector('.phone-number').remove();
    document.querySelector('.button-wrap').remove();
    
    let text = document.querySelector('.text');
    text.innerHTML = 'Введите последние 4 цифры входящего номера';

    let additionalText = document.querySelector('.additional-text');
    additionalText.innerHTML = 'Звоним на ' + phoneForText + ' —<br>отвечать не нужно';

    let newDiv = document.createElement('div');
    newDiv.setAttribute('class', 'code-wrap');
    newDiv.classList.add('code-wrap');

    newInput = document.createElement('input');
    newInput.setAttribute('class', 'code-input')
    newInput.setAttribute('type', 'tel');
    newInput.setAttribute('maxlength', '4');
    newInput.setAttribute('aria-invalid', 'false');
    newInput.setAttribute('placeholder', '____');

    newInput.addEventListener('input', onCodeInput)

    let newButton = document.createElement('button')
    newButton.setAttribute('type', 'button')
    newButton.setAttribute('class', 'button-conf button')
    newButton.insertAdjacentText('afterbegin', 'Продолжить')
    newButton.addEventListener('click', (e) => {validate(newDiv, newInput.value, pincode, phone)})

    additionalText.insertAdjacentElement('afterend', newDiv)
    newDiv.insertAdjacentElement('afterbegin', newInput)
    newDiv.insertAdjacentElement('beforeend', newButton)
}

let countTryes = 3

function validate (div, pincode, correctPin, phone) {
    if (pincode === correctPin) {
        // nextStepRegistration(div, phone)
        switchThePassword(div, phone)
    } else {
        countTryes = countTryes - 1
        if (countTryes === 0) {
            alert('Превышено количество ошибок')
            window.location.href = '/users/register/'
        }
    }
}

function switchThePassword (div, phone) {
    newForm = document.createElement('form');
    div.insertAdjacentElement('afterend', newForm);
    div.remove();

    let text = document.querySelector('.text'),
        additionalText = document.querySelector('.additional-text');
    text.innerHTML = "Введите новый пароль";
    additionalText.innerHTML = "Он не должен совпадать<br>с вашим номером телефона";

    let phoneNumber = document.createElement('input'),
        password = document.createElement('input'),
        shield = document.createElement('p'),
        sixPlus = document.createElement('p'),
        letters = document.createElement('p'),
        numbers = document.createElement('p'),
        otherSymbols = document.createElement('p'),
        button = document.createElement('button');

    phoneNumber.type = 'hidden';
    password.type = 'password';

    phoneNumber.name = 'phone_number';
    password.name = 'password'
    password.required = true

    newForm.setAttribute('class', 'form');
    password.setAttribute('class', 'input');
    password.setAttribute('autocomplete', 'on');

    shield.setAttribute('class', 'pass-text shield');
    sixPlus.setAttribute('class', 'pass-text six-plus');
    letters.setAttribute('class', 'pass-text letters');
    numbers.setAttribute('class', 'pass-text numbers');
    otherSymbols.setAttribute('class', 'pass-text other-symbols');

    phoneNumber.value = phone;

    shield.innerText = "Надёжный пароль включает:";
    sixPlus.innerText = "Минимум 6 символов";
    letters.innerText = "Строчные и прописные буквы";
    numbers.innerText = "Цифры";
    otherSymbols.innerText = "Другие символы";

    button.setAttribute('type', 'submit')
    button.setAttribute('class', 'button')
    button.innerText = "Готово"

    newForm.insertAdjacentElement('beforeend', phoneNumber);
    newForm.insertAdjacentElement('beforeend', password);
    newForm.insertAdjacentElement('beforeend', shield);
    newForm.insertAdjacentElement('beforeend', sixPlus);
    newForm.insertAdjacentElement('beforeend', letters);
    newForm.insertAdjacentElement('beforeend', numbers);
    newForm.insertAdjacentElement('beforeend', otherSymbols);
    newForm.insertAdjacentElement('beforeend', button);

    newForm.addEventListener('submit', (e) => {
        // button.disabled = true;

        e.preventDefault();

        let re = /(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z]{6,}/g;

        if (!re.test(e.target[1].value)) {
            let res = confirm("Пароль не надёжен! Оставить?")
            if (res) {
                sendData(newForm)
                    .then(result => {
                        location.href = "/users/login/"
                    })
            }
        }else {
            sendData(newForm)
                .then(result => {
                    location.href = "/users/login/"
                })
        }
    });
}

button.addEventListener('click', validatePhoneNomber);