function initCountDown(countDown) {
    const second = 1000,
        minute = second * 60,
        hour = minute * 60,
        day = hour * 24;
    x = setInterval(function () {
        let now = new Date().getTime(),
            distance = countDown - now;

        let data = {
            'days': distance / (day),
            'hours': (distance % (day)) / (hour),
            'minutes': (distance % (hour)) / (minute),
            'seconds': (distance % (minute)) / second
        };
        for (let prop in data) {
            for (let element of document.getElementsByClassName(prop)) {
                element.innerText = Math.floor(data[prop]);
            }
        }

        if (distance < 0) {
            clearInterval(x);
            'Tempo esgotado!';
        }
    }, second)
}

initCountDown(new Date('Aug 10, 2020 23:59:59').getTime());