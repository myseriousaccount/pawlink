$(document).ready(function() {
    $('#shelter-form').on('submit', function(event){
        event.preventDefault();

        const form = this;
        const formData = new FormData(form)

        const button = $('button[type="submit"]', form);

        if (button.prop('disabled')) return;

        button.prop('disabled', true);

        $('#shelter-form-message').text('');
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
                if (xhr.responseJSON?.redirect_url) {
                    window.location.href = xhr.responseJSON.redirect_url;
                    return;
                }

                const errors = xhr.responseJSON?.errors;

                $('#shelter-form-message').text(
                    errors ? '' : (xhr.responseJSON?.message || 'Не вдалося виконати запит. Спробуйте ще раз.')
                );

                if (errors) {
                    for (const field in errors) {
                        const message = errors[field][0].message;

                        if (field === '__all__') {
                            $('#shelter-form-message').text(message);
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
