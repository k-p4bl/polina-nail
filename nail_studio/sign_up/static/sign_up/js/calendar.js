let ten = document.querySelector('#id_time_0');
let thirteen = document.querySelector('#id_time_1');
let sixteen = document.querySelector('#id_time_2');
ten.disabled = true;
thirteen.disabled = true;
sixteen.disabled = true;

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

document.addEventListener('DOMContentLoaded', () => {
    const calendar = new VanillaCalendar('#calendar',
    {
        settings: {
            lang: 'ru-RU',
            range: {
                disablePast: true,
                disableWeekday: [1],
                disabled: dis,
            },
            visibility: {
                theme: 'light',
            },
        },
        actions: {
            clickDay(event, self) {
                let date = document.querySelector('#date');
                let errorDate = document.querySelector('#error-date');
                let errorTime = document.querySelector('#error-time');
                date.value = self.selectedDates
                errorDate.style = 'display: none';
                errorTime.style = 'display: none';

                sendRequest('POST', validateDate, self.selectedDates)
                    .then(data => {
                        ten.disabled = data['10'];
                        if (ten.disabled) {
                            ten.checked = false
                        }
                        thirteen.disabled = data['13'];
                        if (thirteen.disabled) {
                            thirteen.checked = false
                        }
                        sixteen.disabled = data['16'];
                        if (sixteen.disabled) {
                            sixteen.checked = false
                        }
                    })
                    .catch(err => console.log(err))
            },
        },
    }
    );
    calendar.init();
});
if (ten.disabled) {
    ten.checked = false
}
if (thirteen.disabled) {
    thirteen.checked = false
}
if (sixteen.disabled) {
    sixteen.checked = false
}