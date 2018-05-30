$(document).ready(function() {
    $("#addToMyBar").click(function (){
        var select = document.getElementById("add_ingredient");
        var ingredient = select.options[select.selectedIndex].value;
        $.ajax({
            type: "POST",
            url: "add_ingredient",
            data: {
                name: ingredient
            },
            success: function (data){
                $("body").html(data);
            }
        });
    });

    $("#calculateDrinks").click(function (){
        $.ajax({
            type: "GET",
            url: "calculate_possible_drinks",
            success: function (data){
                $("#calculationResults").html("<br><p>Results</p><hr>" + data);
            }
        });
    });



    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    }); 
});