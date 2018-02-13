$(document).ready(function () {
    $(".delete-link").on("click", function() {
        var clipId = $(this).attr("data-clip-id");
        $("#delete-clip-id").attr("value", clipId);
    });
});