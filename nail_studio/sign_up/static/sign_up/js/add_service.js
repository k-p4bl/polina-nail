function addElementSelect(e) {
    let newDiv = document.createElement('div')
    newDiv.setAttribute('class', 'wrapper-add-select');
    newDiv.setAttribute('id', String(countAddServices) + '_id_div')

    let newSelect = document.createElement('select');

    newSelect.setAttribute('class', 'add-select');
    newSelect.setAttribute('onchange', 'addServiceSelectDataTransfer()')
    newSelect.required = true
    newSelect.classList.add('add-select');

    let option = document.createElement('option');
    option.text = 'Доп. услуга';
    option.value = '';
    option.defaultSelected = true;
    option.disabled = true;
    option.selected = true;
    newSelect.add(option);

    sendRequest('GET', requestURL + 'get_additional_service/')
        .then(data => {
            for (let i in data) {
                let option = document.createElement('option');
                option.value = i;
                option.text = data[i];
                newSelect.add(option);
            }
        })
        .catch(error => console.log(error))

    let newButton = document.createElement('button');
    newButton.setAttribute('type', 'button');
    newButton.setAttribute('class', 'remove-service-button');
    newButton.setAttribute('id', String(countAddServices) + '_id_button');
    newButton.setAttribute('onclick', 'removeServiceSelect(this)')
    newButton.classList.add('remove-service-button');
    newButton.innerHTML = '<img class="img-button-remove-service" src="/media/sign_up/free-icon-font-square-minus.png">'



    newDiv.insertAdjacentElement('afterbegin', newSelect);
    newDiv.insertAdjacentElement('beforeend', newButton);
    hiddenRealAddService.insertAdjacentElement('beforebegin', newDiv);

    countAddServices ++
}

function addServiceSelectDataTransfer() {
    let selects = document.querySelectorAll('.add-select')
    let hiddenAddService = document.querySelector('#id_add_service');
    for (let option of hiddenAddService.options) {
        option.selected = false;
    }
    for (let select of selects) {
        if (select.selectedIndex > 0) {
            hiddenAddService.options[select.selectedIndex - 1].selected = true;
        }
    }
}

function removeServiceSelect (button) {
    document.getElementById(button.id[0] + '_id_div').remove();
    addServiceSelectDataTransfer()
}

let countAddServices = 0
document.querySelector('.button-add-service').addEventListener('click', addElementSelect);



