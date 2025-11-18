document.addEventListener('DOMContentLoaded', function() {
    var itemButton = document.getElementById('item');
    var orderButton = document.getElementById('order');

    itemButton.addEventListener('click', function() {
        const inputElement = document.getElementById('input-id');
        const inputValue = inputElement.value;
        if (inputValue === '') {
            alert('id товара или заказа не может быть пустым')
        } else {
            url = "item/" + inputValue
            fetch(url, {
                    method: 'GET'
                })
                .then(response => {
                    window.location.href = response.url
                })
        }
    })

    orderButton.addEventListener('click', function() {
        const inputElement = document.getElementById('input-id');
        const inputValue = inputElement.value;
        if (inputValue === '') {
            alert('id товара или заказа не может быть пустым')
        } else {
            url = "order/" + inputValue
            fetch(url, {
                    method: 'GET'
                })
                .then(response => {
                    window.location.href = response.url
                })
        }
    })
})