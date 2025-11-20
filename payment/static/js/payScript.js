document.addEventListener('DOMContentLoaded', function () {
    const buyButton = document.getElementById('buy-button');
    const id = buyButton.dataset.id;
    const payType = buyButton.dataset.payType;

    let basePath;
    let errorText;
    if (payType === 'item') {
        basePath = '/pay_item/';
        errorText = 'Не удалось получить ссылку на оплату товара';
    } else if (payType === 'order') {
        basePath = '/pay_order/';
        errorText = 'Не удалось получить ссылку на оплату заказа';
    } else {
        return;
    }

    buyButton.addEventListener('click', function () {
        const url = basePath + id;

        fetch(url, { method: 'GET' })
        .then(response => {
            if (!response.ok) {
                return response.json().catch(() => ({}));
            }
            return response.json();
        })
        .then(data => {
            if (!data || !data.sessionUrl) {
                alert(errorText);
                return;
            }
            window.location.href = data.sessionUrl;
        })
        .catch(error => {
            alert('Произошла ошибка при обращении к сервису оплаты', error);
        });
    });
});
