var expose;
var scroll;
var formkey;

function updateStatus(text) {
    var ut = $("#updateTitle");
    ut.html("阅读记录更新：<span style=\"color: #f00;\">"+text+"</span>");
}

function hideForm() {
    var divFrame = $("#addProgress");
    divFrame.css("display", "none");
}

function showForm(bkey) {
    formkey = bkey;
    var divFrame = $("#addProgress");
    $("#updateDay").attr("value", "");
    divFrame.css("display", "block");
    expose = divFrame.expose({api: true, maskId: "exposeMask"});
    expose.onBeforeClose(hideForm).load();

    var chart = $("#my_chart");
    if (chart != null) {
	chart.css("z-index", "-1");
    }
    var d = new Date();
    coverimg = $("#"+bkey+" div.cover img").attr("src");
    $("#updateCover img").attr("src", coverimg);
    $("#updateDay").attr("value", "" + d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate());
}

function updateRecord(date, page) {
    // alert("更新记录 Date="+date+" Page="+page+" Key="+formkey);
    updateStatus("更新数据中。。");
    $.ajax({
	url: "/updateRecord?key="+formkey+"&date="+date+"&page="+page,
	cache: false,
	timeout: 5000,
	error: function(html) {
	    updateStatus("连接错误");
	},
	success: function(html) {
	    updateStatus(html);
	    // if (html = "success")
	    // 	updateStatus("更新成功");
	    // else
	    // 	updateStatus("更新失败-"+html);
 	}
    });
    // setTimeOut('expose.close()', 1500);
}
function initHandlers() {
    // initialize scrollable
    scroll = $("div.scrollable").scrollable({
        api: true,
        size: 3,
        items: '#thumbs',
        hoverClass: 'hover'
    });

    $("div.cover").click(function() {
        bkey = $(this).parent().attr("id");
        showChart("/getOFCData?key=" + bkey);
    });

    $("div.progressBar").click(function() {
        bkey = $(this).parent().attr("id");
        showChart("/getOFCData?key=" + bkey);
    });

    $("div.update").click(function() {
	bkey = $(this).parent().parent().attr("id");
	showForm(bkey);
    });

    $("#updateSubmit").click(function() {
	var date = $("#updateDay").attr("value");
	var page = $("#updatePage").attr("value");
	updateRecord(date, page);
    });

}
