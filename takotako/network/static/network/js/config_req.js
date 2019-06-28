
var configForm = document.getElementById('configForm')

////////////////////////////////
// configFor submission       //
////////////////////////////////

configForm.addEventListener('submit', function (e) {
    console.log('im in')
    e.preventDefault()
    order = 'config'
    var elements = configForm.getElementsByClassName('validate')
    var configs = {}
    for (i = 0; i < elements.length; i++) {
        if (elements[i].value !== '') {
            var crit_key = elements[i].id;
            var crit_value = elements[i].value;
            configs[crit_key] = crit_value;
        }
    }
    console.log(configs)
    configSend(order, configs)
});


////////////////////////////////////////////////////////////////
// Post function sending user input and recovering server     //
// Calling back function to handle response                   //
////////////////////////////////////////////////////////////////


function configSend(order, configs) {
    //Json sent to the django server
    var data2send = {
        order: order,
        configs: configs,
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
            }
        }
    });
};
