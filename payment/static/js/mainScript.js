document.addEventListener('DOMContentLoaded', function() {
    var itemButton = document.getElementById('item');
    var orderButton = document.getElementById('order');

    itemButton.addEventListener('click', function() {
        const inputElement = document.getElementById('input-id');
        const inputValue = inputElement.value;
        if (inputValue === '') {
            alert('id товара или заказа не может быть пустым')
        } else {
            window.location.href = "/item/" + inputValue;
        }
    })

    orderButton.addEventListener('click', function() {
        const inputElement = document.getElementById('input-id');
        const inputValue = inputElement.value;
        if (inputValue === '') {
            alert('id товара или заказа не может быть пустым')
        } else {
            window.location.href = "/order/" + inputValue;
        }
    })
})