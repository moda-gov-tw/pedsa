
//新增人員
var member_modal = document.getElementById('member');
var new_member_btn = document.getElementById("new_member");
var member_close_span = document.getElementById("member_close");

new_member_btn.onclick = function() {
    member_modal.style.display = "block";
}

member_close_span.onclick = function() {
    member_modal.style.display = "none";
}

//新增專案


//nda
$(".btn_data_download , .nda_popup .close").click(function() {
    $(".mask, .nda_popup").toggle("fade", 350);
});


