$(document).ready(function () {
    var modal = document.getElementById('myModal');
    var btn = document.getElementById("login");
    var span = document.getElementsByClassName("close")[0];
    btn.onclick = function () {
        modal.style.display = "block";
    }
    span.onclick = function () {
        modal.style.display = "none";
    }

    var len = 100; // 超過50個字以"..."取代
    $(".prodesc").each(function (i) {
        if ($(this).text().length > len) {
            $(this).attr("title", $(this).text());
            var text = $(this).text().substring(0, len - 1) + "...";
            $(this).text(text);
        }
    });

    var project_modal = document.getElementById('project');
    var new_project_btn = document.getElementById("new_project");
    var project_close_span = document.getElementById("project_close");

    new_project_btn.onclick = function () {
        project_modal.style.display = "block";
    }

    project_close_span.onclick = function () {
        project_modal.style.display = "none";
    }

    setInterval("GetRefresh()", 12000);
});

function checkVal(str) {
    var regExp = /^[\d|a-zA-Z]+$/;
    var regEn = /[`~!@@#$%^&*()+<>?:"{},.\/;'[\]]/;
    var regEnNew = /\W/;
    var pattern = new RegExp("[`~!@@#$^&*()=|{}':;',\\[\\].<>《》/?~！@@#￥……&*（）——|{}【】‘；：”“'。，、？]");

    if (regEn.test(str)) {
        // alert('有底線');
        return false;
    } else {
        return true;
    }
}

function InsertNewProject() {
    var pname = $("#p_name").val();
    var p_dsname = $("#p_dataset_name").val();
    var pdes = $("#p_des").val();
    var memberAcc = $('#memberAcc').text();
    var memberId = $('#memberId').text();

    // var pinput = $("#p_input").val();
    //var poutput = $("#p_output").val();
    var powner = $("#p_owner option:selected").val();
    if (pname == "") {
        alert('請輸入專案名稱');
        return false;
    } else {

        if (!checkVal(pname)) {
            alert('專案名稱必須要英文或數字組成!');
            return false;
        }
    }
    //  alert(pdes);
    if (pdes == "") {
        alert('請輸入專案描述!');
        return false;
    }

    if (p_dsname == "") {
        alert('請輸入專案資料集名稱!');
        return false;
    }

    if (pname != p_dsname) {
        alert('專案名稱與專案資料集名稱需相同!');
        return false;
    }

    if (powner == 0) {
        alert('請選擇專案管理人!');
        return false;

    }

    $.ajax({
        type: "get",
        url: "/api/WebAPI/InsertProject",
        contentType: "application/json",
        data: {
            pname: pname,
            prodesc: pdes,
            pinput: "data/input",
            poutput: "data/output",
            powner: powner,
            p_dsname: p_dsname,
            memberacc: memberAcc,
            memberid: memberId
        },
        success: function (data, status) {
            // alert('project load success');
            //alert(data);
            //    $("#projectlist").html(data);
            if (data == "-2") {
                alert('專案名稱重複!');
                return false;
            }

            if (data == "-4") {
                alert('專案狀態錯誤!') return false;
            }

            if (data == "0") {
                alert("系統寫入出現錯誤");
            }
            var project_modal = document.getElementById('project');
            project_modal.style.display = "none";
            location.reload();
        },
        error: function (data, status) {
            if (data == "-2") {
                alert('專案名稱重複!');
                return false;
            }

            if (data == "-4") {
                alert('專案狀態錯誤!') return false;
            }

            if (data == "0") {
                alert("系統寫入出現錯誤");
            }
        }
    });
    return false;
}

function delproject(pid, pname) {
    var delconfirm = $('#delconfirm').text();
    var deleted = $('#deleted').text();
    var delerror = $('#delerror').text();
    var memberAcc = $('#memberAcc').text();
    var memberId = $('#memberId').text();
    if (confirm(delconfirm)) {
        //      alert('11');
        $.ajax({
            type: "get",
            url: "/api/WebAPI/DeleteProject",
            contentType: "application/json",
            data: {
                project_id: pid,
                pname: pname,
                project_status: 2,
                memberid: memberId,
                memberacc: memberAcc
            },
            success: function (data, status) {
                //document.location.href = "@Url.Action("Step2", "ProjectStep")";
                alert(deleted);
                location.reload();
            },
            error: function (data, status) {
                alert(deleted);
                location.reload();

            }

        });
        // alert('取消!')
    } else {
        //   alert('XX')
        return;

    }
}


function getcancel(pid, pname, pstatus) {
    //alert('1111');
    var resetconfirm = $('#resetconfirm').text();
    var resetfin = $('#resetfin').text();
    var reseterr = $('#reseterr').text();
    var memberAcc = $('#memberAcc').text();
    var memberId = $('#memberId').text();
    if (parseInt(pstatus) <= 1) {
        alert('專案尚未匯入資料');
        return false;
    } else if (parseInt(pstatus) <= 2 && parseInt(pstatus) > 1) {
        alert('專案狀態階段尚未進行概化，可以不用重設專案!');
        return false;
    }
    if (confirm(resetconfirm)) {
        //      alert('11');
        $.ajax({
            type: "get",
            url: "/api/WebAPI/CancelProjectStatus",
            contentType: "application/json",
            data: {
                project_id: pid,
                pname: pname,
                project_status: 3,
                memberid: memberId,
                memberacc: memberAcc
            },
            success: function (data, status) {
                //document.location.href = "@Url.Action("Step2", "ProjectStep")";
                alert(resetfin);
                location.reload();
            },
            error: function (data, status) {
                alert(reseterr);
            }

        });
        // alert('取消!')
    } else {
        //   alert('XX')
        return;

    }
}

function GetRefresh() {
    var notcount = "";
    //alert('111');
    $.ajax({
        type: "get",
        //    url: "/api/WebAPI/CheckSparkJobStatus",
        url: "/api/WebAPI/GetStatusAppNotificationData",
        contentType: "application/json",
        async: false,
        success: function (response) {
            //alert(response);
            notcount = response;
        },
        error: function (response) {

        }

    });
    if (notcount != "") {
        if (notcount != "0") {

            var notarr = notcount.split('*');
            //alert(colqiarr.length);
            if (notarr[0] > 0) {
                location.reload();
            }

        }

    } else {
        //   alert('111');
        //$("#notcount").text(String(notcount));
    }
}