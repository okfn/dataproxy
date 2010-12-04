// List all packages example

$('#examples').append('<li id="list"><a href="#">List all packages</a></li>');
$('#list').click(function(e) {
    e.preventDefault();
    $.ajax({
        url: 'http://catalogue.data.gov.uk/api/rest/package',
        type: 'GET',
        success: function(data){
            render_results(data);
        },
        error: function() {
            alert('Failed to get the list of packages.')
        },
        dataType: 'jsonp',
        jsonpCallback: 'jsonpcallback'
    });
});


var render_data = function(link, data) {
    var content = '<table>';
    for (var i=0; i<data.response.length; i++) { 
        content += '<tr>';
        for (var j=0; j<data.response[i].length; j++) { 
             content += '<td>'+data.response[i][j]+'</td>';
        }
        content += '</tr>';
    }
    content += '</table>'
    link.after(content)
}


// Render a list of packages to the results <div>

var render_results = function(packages) {
    $('#result').html('<ul id="packages"></ul>');
    for (var i=0; i<packages.length; i++) {
        var elem = $('<li><a href="#">'+packages[i]+'</a></li>')
        elem.click(function(e){
            e.preventDefault();
            var url = 'http://catalogue.data.gov.uk/api/2/rest/package/';
            url += $(this).find('a').html();
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data){
                    var output = '<p>'
                    for (name in data) {
                        if (data.hasOwnProperty(name)) {
                            if ( name == 'resources' ){
                                var urls = '';
                                for (var j=0; j<data[name].length; j++) {
                                    urls += '<a href="'+data[name][j]['url']+'">';
                                    urls += data[name][j]['url']+'</a> ';
                                }
                                output += name+': '+urls+'<br />';
                            } else {
                                output += name+': '+data[name]+'<br />';
                            }
                        }
                    }
                    output += '</p>'
                    $('#result').html(output);
                    $('#result a').each(function(){
                        var link = $(this);
                        link.click(function(e){
                            e.preventDefault();
                            $.ajax({
                                url: 'http://1.latest.jsonpdataproxy.appspot.com/',
                                type: 'GET',
                                data: {'url': link.attr('href')},
                                success: function(data){
                                    if (data['error'] !== undefined){
                                        alert(data.error.title);
                                    } else {
                                        render_data(link, data);
                                    }
                                },
                                error: function() {
                                    alert('Failed to get spreadsheet data.')
                                },
                                dataType: 'jsonp',
                                jsonpCallback: 'callback'
                            });
                        })
                    })
                },
                error: function() {
                    alert('Failed to search the packages.');
                },
                dataType: 'jsonp',
                jsonpCallback: 'jsonpcallback'
            });
        });
        $('#packages').append(elem);
    };
};


// Search packages example

$('#examples').append('<li id="search"><a href="#">Search package metadata</a></li>');
$('#search').click(function(e) {
    e.preventDefault();
    var search_form = '';
    search_form += '<form id="search_form">';
    search_form += 'Search: <input type="test" id="terms" name="q" />';
    search_form += '<input type="submit" value="Go" />';
    search_form += '</form>';
    $('#result').html(search_form);
    $('#search_form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: 'http://catalogue.data.gov.uk/api/2/search/package',
            type: 'GET',
            data: {'q': $('#terms').val(), 'all_fields': '1'},
            success: function(data){
                alert('Found '+data['count']+' result(s)')
                packages = []
                for (var i=0; i<data['results'].length; i++){
                    packages.push(data['results'][i]['name']);
                }
                render_results(packages);
            },
            error: function() {
                alert('Failed to search the packages.');
            },
            dataType: 'jsonp',
            jsonpCallback: 'jsonpcallback'
        });
    });
})


