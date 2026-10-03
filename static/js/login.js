$(document).ready(function() {
    $('#login-form').on('submit', function(event){
        event.preventDefault();

        const form = this;
        const formData = new FormData(form)

        const button = $('button[type="submit"]', form);

        if (button.prop('disabled')) {
            return
        }

        button.prop('disabled', true);

        $('#login-message').text('');
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
                const errors = xhr.responseJSON?.errors;

                if (!errors) {
                    $('#login-message').text('Не вдалося завершити запит.');
                }

                if (errors) {
                    for (const field in errors) {
                        const message = errors[field][0].message;

                        if (field === '__all__') {
                            $('#login-message').text(message);
                        } else {
                            const elementId = '#' + field + '-error';
                            $(elementId).text(message);
                        }
                    }
                }

                button.prop('disabled', false);
            },
        })
    });
});
