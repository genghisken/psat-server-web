// 2018-08-15 KWS Safari and Firefox allow page back on bootstrap quickview page
//                and show the previous "active" state of buttons, but do NOT
//                remember the previous "checked" state of radio choices! This
//                code fixes that, but doesn't work for Chrome, which also
//                doesn't remember the previous button active state.
function getInputValues()
{ 
  var dataArray = $( ":input" ).serializeArray(), len = dataArray.length;

  for (i=0; i<len; i++) {
     if (dataArray[i].name.includes("promote_demote"))
     {
       console.log(dataArray[i].name + ": " + dataArray[i].value);
     }
  }
};

// 2018-08-15 KWS OK - bind to pageshow now works for loading from sessionStorage in all cases!
$(function() {
  $(window).bind("pageshow", function() {
  //$( document ).ready(function() {
  //$( document ).onpageshow(function() {
      Object.keys(sessionStorage).map(k => sessionStorage.getItem(k));
      //Object.keys(sessionStorage).forEach(key => console.log(key + '=>' + sessionStorage[key]))
      Object.keys(sessionStorage).forEach(function(key) {
        var value = sessionStorage.getItem(key);

        // Now go and set the values
        $("input[name=" + key + "][value=" + value + "]").prop("checked", true);
        //$("input[name="+ key + "]").prop("value", sessionStorage.getItem(key));
        $("input[name=" + key + "][value=" + value + "]").parent().addClass('active').siblings().removeClass('active');
      });

      getInputValues();
  });
});

$(function() {
    $("#tbutton").click(function(){
       getInputValues();
    });
});

