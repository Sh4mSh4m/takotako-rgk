////////////////////////////////////////////////////////////////
// DOM selecotrs declaration                                  //
////////////////////////////////////////////////////////////////
var shootForm = document.getElementById("shoot");
var browseReady = document.getElementById("browseReady")

////////////////////////////////////////////////////////////////
// Event listeners to submit user input upon clicking submit  //
// button                                                     //
////////////////////////////////////////////////////////////////


shootForm.addEventListener("submit", function (e) {
    e.preventDefault();
    order = 'shoot';
    var box_list = document.getElementsByClassName("box")
    var values = [];
    for (i = 0; i < box_list.length; i++) {
        if (box_list[i].checked) {
            values.push(box_list[i].value);
        }
    }
    console.log(values)
    orderSend(order, values)
});


////////////////////////////////////////////////////////////////
// Post function sending user input and recovering server     //
// Calling back function to handle response                   //
////////////////////////////////////////////////////////////////
function orderSend(order, values) {
    //Json sent to the django server
    var data2send = {
        order: order,
        values: values,
        other_field: 'for future use'
    }
    $.ajax({
        "url": window.location.href,
        "type": "POST",
        "contentType": "application/json; #charset=utf-8",
        "dataType": "json",
        "data": JSON.stringify(data2send),
        "success": function (result) {
            console.log(result.celery_job_id)
            poll_state(result.celery_job_id)
        }
    });
};


function poll_state(celery_job_id) {
    var data2send = {
        celery_job_id: celery_job_id,
        other_field: 'for future use'
    }
    $.ajax({
        "url": poll_state_url,
        "type": "POST",
        "contentType": "application/json; #charset=utf-8",
        "dataType": "json",
        "data": JSON.stringify(data2send),
        "success": function (response) {
            if (response.status === 'FAILURE') {
                console.log('FAILED')
            }
            else if (response.status !== 'SUCCESS') {
                console.log(response.status)
                setTimeout(poll_state.bind(null, celery_job_id), 5000)
            }
            else {
                console.log('HURRAY WE ARE DONE')
                browseReady.style.display = 'block'
            }
        }
    });
};
