$(document).ready(function () {

    $('#add-fav-form').on('submit', function (event) {

        event.preventDefault();

        const form = this;
        const formData = new FormData(form);

        const button = $('button[type="submit"]', form);

        if (button.prop('disabled')) {
            return;
        }

        button.prop('disabled', true);

        $('#favorite-message').text('');

        $.ajax({
            url: form.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            dataType: 'json',

            success: function (response) {
                const isFavorite = response.is_favorite === true;
                const label = isFavorite ? 'Прибрати з обраного' : 'Додати в обране';

                button.attr('aria-pressed', String(isFavorite));
                button.attr('aria-label', label);
                button.attr('title', label);
                button.find('svg').attr('fill', isFavorite ? 'currentColor' : 'none');
            },

            error: function (xhr) {

                if (xhr.status === 401 && xhr.responseJSON?.redirect_url) {
                    window.location.href = xhr.responseJSON.redirect_url;
                    return;
                }

                const message = xhr.responseJSON?.message
                    || 'Не вдалося змінити обране. Оновіть сторінку та спробуйте ще раз.';

                $('#favorite-message').text(message);

            },

            complete: function () {
                button.prop('disabled', false);
            }

        })



    });

});
