$(document).ready(function() {
    $('.contribution-form').on('submit', function(event){
        event.preventDefault();

        const form = this;
        const formData = new FormData(form)


        // блокування кнопки якщо користувач вже відправив форму
        const button = $('button[type="submit"]', form);
        button.prop('disabled', true);

        $('.contribution-message', form).text('');
        $('.field-error', form).text('');

        $.ajax({
            url: form.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,

            success: function(response) {
                window.location.href = response.redirect_url;
            },

            error: function(xhr) {

                if (xhr.status === 401) {
                    window.location.href = xhr.responseJSON.redirect_url;
                    return;
                }

                const errors = xhr.responseJSON?.errors;

                if (!errors) {
                    $('.contribution-message', form).text(
                        xhr.responseJSON?.message || 'Не вдалося завершити запит.'
                    );
                }

                if (errors) {
                    for (const field in errors) {
                        const message = errors[field][0].message;

                        if (field === '__all__') {
                            $('.contribution-message', form).text(message);
                        } else {
                            $('[data-error-for="' + field + '"]', form).text(message);
                        }
                    }
                }
            },
            complete: function() {
                button.prop('disabled', false);
            }
        })
    });
});