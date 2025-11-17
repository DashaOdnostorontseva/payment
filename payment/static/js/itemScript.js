document.addEventListener('DOMContentLoaded', function() {
    var buyButton = document.getElementById('buy-button');
    var itemId = buyButton.getAttribute('item-id')
    var url = "/buy/" + itemId
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