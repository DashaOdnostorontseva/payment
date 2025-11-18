document.addEventListener('DOMContentLoaded', function() {
    var buyButton = document.getElementById('buy-order-button');
    var orderId = buyButton.getAttribute('order-id')
    var url = "/pay_order/" + orderId
    console.log(url)
    buyButton.addEventListener('click', function() {
    fetch(url, {method: 'GET'})
    .then(response => {
        console.log('Raw response:', response);
        return response.json()
    })
    .then(data => {
        console.log('Parsed JSON:', data);
        window.location.href = data.sessionUrl
    })
    })
})