$(function(){
    $('#submit-btn').on('click', function(e){
        e.preventDefault();
        let decision = confirm('정말로 이체하시겠습니까?');
        if (decision == true){
            // $('#transfer-form').submit();
            let send_string = $('#transfer-form').serialize()
            $.ajax({
                url: "/transfer",
                type: 'post',
                data: send_string,
                dataType: 'json',
                success: function(response){
                    alert('이체 성공했습니다!')
                    $('#form-area').attr('hidden', true);
                    $('#success-msg').text(`${response.amount} 코인 이체에 성공했습니다.`);
                    $('#after-transfer').attr('hidden', false);
                },
                error: function(response){
                    alert('이체에 실패했습니다 ㅠㅠ', error)
                }
            });
        }
    });
});