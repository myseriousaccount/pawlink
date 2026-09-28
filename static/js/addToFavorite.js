$(document).ready(function () {

    $('#add-fav-form').on('submit', function (event) {

        event.preventDefault();

        const form = this;
        const formData = new FormData(form);
        const button = $('button[type="submit"]', form);

        if (button.prop('disabled')) {
            return;
        }

        button.prop('disabled', true)
        $('#favorite-message').text('');

        $.ajax({
            url: form.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            dataType: 'json',

            success: function (response) {
                if (response.is_favorite) {
                    button.text('Прибрати з обраного');
                } else {
                    button.text('Додати в обране');
                }
            },

            error: function (xhr) {
                if (xhr.status === 401) {
                    window.location.href = xhr.responseJSON.redirect_url;
                    return;
                }

                const message = 'Не вдалося змінити обране. Оновіть сторінку та спробуйте ще раз.'
                $('#favorite-message').text(message);

            },

            complete: function () {
                button.prop('disabled', false);
            }

        })



    });

});