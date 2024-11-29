$(function () {
    var modal = document.getElementById('myModal');
    var project_modal = document.getElementById('project');
    var new_project_btn = document.getElementById("new_project");
    var project_close_span = document.getElementById("project_close");

    $('.noti_dropdown').on('click', function (event) {
        if ($(this).hasClass('is_active') === false)
            $('.noti_dropdown').removeClass('is_active');
        $(this).toggleClass('is_active');
        event.stopPropagation();
    });

    $(document).click(function () {
        $('.noti_dropdown').removeClass('is_active');
    });

   // GetNotificationData();
    //CheckJobStatus();
   // setInterval("GetNotificationData()", 10000);
});

function isReadStatus() {
    var counts = $("#notcount").text();

    $.ajax({
        type: "get",
        url: "/api/WebAPI/UpdateStatsRead",
        contentType: "application/json",
        async: false,
        success: function (response) {
            //成功
            if (response == true) {
                $("#notcount").text('')
                $("#notcount").css('display', 'none');
            }
        },
        error: function (response) {
            //alert(savecolerror);
        }
    });
}


function GetNotificationData() {
    var notcount = "";
    var natdata = $("#notcount").text();
    //alert("nat :"+natdata);
    if (natdata != "") {
        //alert('nodata');
        isReadStatus();
    }
    $.ajax({
        type: "get",
        //    url: "/api/WebAPI/CheckSparkJobStatus",
        url: "/api/WebAPI/GetStatusAppNotificationData",
        contentType: "application/json",
        async: false,
        success: function (response) {
            //alert(response);
            notcount = response;
            //setInterval("isReadStatus()", 9000);
        },
        error: function (response) {

        }

    });
    if (notcount != "") {
        if (notcount != "0") {

            var notarr = notcount.split('*');
            //alert(colqiarr.length);
            if (notarr[0] == 0) {

            }
            else {
                $("#notcount").removeAttr("style");
                $("#notcount").text(notarr[0]);
                // location.reload();
            }

            //alert(notarr[1])
            $("#notdrop").html(notarr[1]);
        }

    }
    else {
        //   alert('111');
        //$("#notcount").text(String(notcount));
    }
}

function changlan(c) {
    // alert(c);
    $.ajax({
        type: "get",

        url: "/api/WebAPI/ChangeLang",
        contentType: "application/json",
        async: false,
        data: {
            lan: c
        },
        success: function (response) {
            location.reload();
        },
        error: function (response) {

        }

    });
}