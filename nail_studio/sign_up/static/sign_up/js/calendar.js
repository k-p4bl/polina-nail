const times = document.querySelectorAll("input[data-time-input]")

for (let i = 0; i < times.length; i++) {
    times[i].disabled = true
}

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
                        for (timeId in data) {
                            let timeDisabled = data[timeId]
                            let timeInput = document.querySelector("#id_time_" + timeId)
                            timeInput.disabled = timeDisabled
                        }
                    })
                    .catch(err => console.log(err))
            },
        },
    }
    );
    calendar.init();
});
for (let i = 0; i < times.length; i++) {
    if (times[i].disabled) {
        times[i].checked = false
    }
}