$(document).ready(function() {
    var tags = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
            url: '/_get-tags',
            cache: false
        }
    });
    tags.initialize();

    $('.upload-tagsinput').tagsinput({
        confirmKeys: [13, 32, 44], // enter, space, comma
        typeaheadjs: {
            source: tags.ttAdapter()
        }
    });
});