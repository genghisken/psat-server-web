// 2018-08-15 KWS Added sessionStorage line so that we can refresh the page
//                and remember all our previous choices.
$(function() {

// select all radio buttons in the "E" column (.E class)
$('#select_all_e').click(function(){
    $("input[class=E]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"E");
    });
    $("label[value=E]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "C" column (.C class)
$('#select_all_c').click(function(){
    $("input[class=C]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"C");
    });
    $("label[value=C]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "U" column (.U class)
$('#select_all_u').click(function(){
    $("input[class=U]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"U");
    });
    $("label[value=U]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "G" column (.G class)
$('#select_all_g').click(function(){
    $("input[class=G]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"G");
    });
    $("label[value=G]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "P" column (.P class)
$('#select_all_p').click(function(){
    $("input[class=P]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"P");
    });
    $("label[value=P]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "S" column (.S class)
$('#select_all_s').click(function(){
    $("input[class=S]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"S");
    });
    $("label[value=S]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "A" column (.A class)
$('#select_all_a').click(function(){
    $("input[class=A]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"A");
    });
    $("label[value=A]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});

// select all radio buttons in the "T" column (.T class)
$('#select_all_t').click(function(){
    $("input[class=T]").each(function(){
        $(this).prop("checked", true);
        sessionStorage.setItem($( this ).attr('name'),"T");
    });
    $("label[value=T]").each(function(){
        $(this).addClass('active').siblings().removeClass('active');
    });
});


});
