$(document).ready(function () {
    $('#register-form').on('submit', function (event) {
        event.preventDefault();

        // поточна форма
        const form = this;
        // збирання значень з усіх полів форми
        const formData = new FormData(form);

        // console.log('Форму перехоплено');

        // очищення старих повідолмень перед запитом
        $('#register-message').text('');
        $('.field-error', form).text('');

        // надсилання даних на сервер
        $.ajax({
            url: form.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,

            success: function (response) {
                // console.log('Відповідь сервера отримано');
                window.location.href = response.redirect_url;
            },

            error: function (xhr) {
                const errors = xhr.responseJSON?.errors;

                if (!errors) {
                    $('#register-message').text('Не вдалося завершити запит.');
                }

                if (errors) {
                    for (const field in errors) {
                        const message = errors[field][0].message;

                        if (field === '__all__') {
                            $('#register-message').text(message);
                        } else {
                            const elementId = '#' + field + '-error';
                            $(elementId).text(message);
                        }
                    }
                }

                // console.log('Статус помилки:', xhr.status);
            }
        });
    });
});
