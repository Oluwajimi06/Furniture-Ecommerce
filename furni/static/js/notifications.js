// static/js/notifications.js
document.addEventListener('DOMContentLoaded', function () {
    // Function to show notification
    function showNotification(message) {
        var notification = document.getElementById('notification');
        notification.textContent = message;
        notification.classList.add('show');

        // Hide notification after 3 seconds
        setTimeout(function () {
            notification.classList.remove('show');
            notification.classList.add('hide');
        }, 3000);
    }

    // Handle form submissions
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default form submission
            var formData = new FormData(form);
            var actionUrl = form.action;

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Product added to cart successfully!');
                } else {
                    showNotification('Failed to add product to cart.');
                }
            })
            .catch(error => {
                showNotification('An error occurred.');
            });
        });
    });
});
