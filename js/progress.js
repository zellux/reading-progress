var expose;

function hideForm() {
    var divFrame = $("#addProgress");
    divFrame.css("display", "none");
}

function showForm(bkey) {
    var divFrame = $("#addProgress");
    divFrame.css("display", "block");
    expose = divFrame.expose({api: true,});
    expose.onBeforeClose(hideForm).load();
    var d = new Date();
    $("#updateDay").attr("value", "" + d.getFullYear() + "-" + d.getMonth() + "-" + d.getDate());
}

function updateRecord(date, page) {
    alert("更新记录" + date + ":" + page);
    expose.close();
}
function initHandlers() {
    // initialize scrollable
    var api = $("div.scrollable").scrollable({
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
	bkey = $(this).parent().attr("id");
	showForm(bkey);
    });

    $("#updateSubmit").click(function() {
	var date = $("#updateDay").attr("value");
	var page = $("#updatePage").attr("value");
	updateRecord(date, page);
    });
}
