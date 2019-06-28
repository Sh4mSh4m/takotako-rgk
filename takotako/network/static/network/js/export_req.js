
var exportTask = document.getElementById('exportTask')

////////////////////////////////
// configFor submission       //
////////////////////////////////

exportTask.addEventListener('submit', function (e) {
    console.log('im in')
    e.preventDefault()
    order = 'export'
    var tag = document.getElementById('file_name')
    file_name = tag.value
    console.log(name)
    exportSend(order, file_name)
});


////////////////////////////////////////////////////////////////
// Post function sending user input and recovering server     //
// Calling back function to handle response                   //
////////////////////////////////////////////////////////////////


function exportSend(order, file_name) {
    //Json sent to the django server
    var data2send = {
        order: order,
        file_name: file_name,
        other_field: 'for future use'
    }
    $.ajax({
        "url": window.location.href,
        "type": "POST",
        "contentType": "application/json; #charset=utf-8",
        "dataType": "json",
        "data": JSON.stringify(data2send),
        "success": function (result) {
            console.log('ok i did export')
            var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, undefined, 2));
            var downloadAnchorNode = document.createElement('a');
            downloadAnchorNode.setAttribute("href", dataStr);
            downloadAnchorNode.setAttribute("download", file_name + ".tki");
            document.body.appendChild(downloadAnchorNode); // required for firefox
            downloadAnchorNode.click();
            downloadAnchorNode.remove();
        }
    });
};
