$(document).ready(function () {
    $(".report-link").on("click", function() {
        var clipId = $(this).attr("data-clip-id");
        $("#report-clip-id").attr("value", clipId);
    });
});