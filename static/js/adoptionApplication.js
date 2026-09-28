$(document).ready(function() {
    $('#adoption-form').on('submit', function(event){
        event.preventDefault();

        const form = this;
        const formData = new FormData(form)

        // блокування кнопки якщо користувач вже відправив форму
        const button = $('button[type="submit"]', form);
        button.prop('disabled', true);

        $('#application-message', form).text('');
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
                    $('#application-message', form).text(
                        xhr.responseJSON?.message || 'Не вдалося завершити запит.'
                    );
                }

                if (errors) {
                    for (const field in errors) {
                        const message = errors[field][0].message;

                        if (field === '__all__') {
                            $('#application-message', form).text(message);
                        } else {
                            const elementId = '#' + field + '-error';
                            $(elementId).text(message);
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