document.addEventListener('DOMContentLoaded', () => {
    const itemButton = document.getElementById('item');
    const orderButton = document.getElementById('order');
    const inputElement = document.getElementById('input-id');

    function redirectIfValid(basePath) {
        const value = inputElement.value.trim();

        if (!value) {
            alert('id товара или заказа не может быть пустым');
            return;
        }

        const url = basePath + '/' + value;
        window.location.href = url;
    }

    itemButton.addEventListener('click', () => {
        redirectIfValid('/item');
    });

    orderButton.addEventListener('click', () => {
        redirectIfValid('/order');
    });
});
