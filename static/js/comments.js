function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function toggleReplyForm(commentId) {
    var replyForm = document.getElementById('reply-form-' + commentId);
    replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
}

$(document).ready(function() {
    // Yorum formu gönderildiğinde
    $('.comment-form form').on('submit', function(e) {
        e.preventDefault(); // Formun normal gönderimini engelle

        var form = $(this);
        var url = form.attr('action');
        var formData = form.serialize(); // Form verilerini al

        $.ajax({
            type: 'POST',
            url: url,
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Yorum başarıyla eklendiğinde
                    var newComment = $(response.comment_html).hide().fadeIn(1000); // Yeni yorumu ekle
                    $('.comment-list').append(newComment); // Yorum listesine ekle
                    form.trigger('reset'); // Formu temizle
                } else {
                    alert('Hata: ' + response.errors);
                }
            },
            error: function() {
                alert('Bir hata oluştu. Lütfen tekrar deneyin.');
            }
        });
    });

    // Yanıt formu gönderildiğinde
    $('.reply-form form').on('submit', function(e) {
        e.preventDefault(); // Formun normal gönderimini engelle

        var form = $(this);
        var url = form.attr('action');
        var formData = form.serialize(); // Form verilerini al

        $.ajax({
            type: 'POST',
            url: url,
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            data: formData,
            success: function(response) {
                if (response.success) {
                    // Yanıt başarıyla eklendiğinde
                    var newReply = $(response.comment_html).hide().fadeIn(1000); // Yeni yanıtı ekle
                    form.closest('.comment-item').find('.reply-item').last().after(newReply); // Yanıt listesine ekle
                    form.trigger('reset'); // Formu temizle
                    form.closest('.reply-form').hide(); // Yanıt formunu gizle
                } else {
                    alert('Hata: ' + response.errors);
                }
            },
            error: function() {
                alert('Bir hata oluştu. Lütfen tekrar deneyin.');
            }
        });
    });
});