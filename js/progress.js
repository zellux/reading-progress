var expose;
var scroll;
var formkey;

function showChart(url) {
    swfobject.embedSWF(
	"swf/OFC.swf", "my_chart",
	"631", "300", "9.0.0", "swf/expressInstall.swf",
	{"data-file":url, "loading":"图表生成中..."});
}

function updateStatus(text) {
    var ut = $("#updateTitle");
    ut.html("阅读记录更新：<span style=\"color: #f00;\">"+text+"</span>");
}

function setBar(bar, cur, total) {
    var v1 = parseInt(total * 0.3);
    var v2 = parseInt(total * 0.7);

    var barImageObj = {};
    barImageObj[0] = '/img/pbar/progressbg_red.gif';
    barImageObj[v1] = '/img/pbar/progressbg_orange.gif';
    barImageObj[v2] = '/img/pbar/progressbg_green.gif';

    bar.progressBar(cur, {
	max: total,
	textFormat: 'fraction',
	boxImage: '/img/pbar/progressbar.gif',
	barImage: barImageObj
    });
}

function refreshBar() {
    var bar = $("#"+formkey+" .progressBar");
    $.ajax({
	url: "/ajaxGetPage?key="+formkey,
	cache: false,
	timeout: 2000,
	success: function(html) {
	    setBar(bar, html, bar.attr("total"));
 	}
    });
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
	    refreshBar();
 	}
    });
    // setTimeOut('expose.close()', 1500);
}
function initHandlers() {
    // initialize scrollable
    scroll = $("div.scrollable").scrollable({
        api: true,
        size: 4,
        items: '#thumbs',
        hoverClass: 'hover'
    });

    $("div.cover").click(function() {
        bkey = $(this).parent().attr("id");
        showChart("/getOFCData?key=" + bkey);
    });

    $("div.title").click(function() {
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
