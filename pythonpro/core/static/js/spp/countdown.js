function initCountDown(countDown) {
    const second = 1000,
        minute = second * 60,
        hour = minute * 60,
        day = hour * 24;
    x = setInterval(function () {

        let now = new Date().getTime(),
            distance = countDown - now;

        document.getElementsByClassName('days')[0].innerText = Math.floor(distance / (day));
        document.getElementsByClassName('hours')[0].innerText = Math.floor((distance % (day)) / (hour));
        document.getElementsByClassName('minutes')[0].innerText = Math.floor((distance % (hour)) / (minute));
        document.getElementsByClassName('seconds')[0].innerText = Math.floor((distance % (minute)) / second);

        if (distance < 0) {
            clearInterval(x);
            'Tempo esgotado!';
        }

    }, second)
}