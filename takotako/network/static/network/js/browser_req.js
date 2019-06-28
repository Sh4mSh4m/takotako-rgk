// var btn_description = document.getElementById('btn_description')
// var btn_statuses = document.getElementById('btn_status')
var head = document.getElementsByTagName('head')[0]
var btn_css = document.getElementById('btn_css')
var body = document.getElementById('global')
var btn_status = document.getElementById('btn_status')
var btn_description = document.getElementById('btn_description')
var btn_filter = document.getElementById('btn_filter')
var filterForm = document.getElementById('filterForm')
var filterFormClose = document.getElementById('filterFormClose')
var subFilter = document.getElementById('subFilter')
var userForm = document.getElementById('userForm')

////////////////////////////////////////////////////////////////
// Buttons actions for status or description based CSS        //
////////////////////////////////////////////////////////////////

btn_status.addEventListener('click', function () {
    var linkElement = document.createElement('link');
    linkElement.setAttribute('id', 'css_description');
    linkElement.setAttribute('rel', 'stylesheet');
    linkElement.setAttribute('href', '/static/network/css/browser_description.css');
    var linkChange = document.getElementById('css_status');
    head.replaceChild(linkElement, linkChange);
});

btn_description.addEventListener('click', function () {
    var linkElement = document.createElement('link');
    linkElement.setAttribute('id', 'css_status');
    linkElement.setAttribute('rel', 'stylesheet');
    linkElement.setAttribute('href', '/static/network/css/browser_status.css');
    var linkChange = document.getElementById('css_description');
    head.replaceChild(linkElement, linkChange);
});

btn_filter.addEventListener('click', function (e) {
    filterForm.style.display = 'block'
})

filterFormClose && filterFormClose.addEventListener('click', function () {
    filterForm.style.display = 'none'
})

userForm && userForm.addEventListener('submit', function (e) {
    e.preventDefault()
    order = 'filter'
    var elements = userForm.getElementsByClassName('validate')
    console.log(elements[3].type)
    console.log(elements[3].value)
    var filters = {}
    for (i = 0; i < elements.length; i++) {
        if (elements[i].value !== '') {
            var crit_key = elements[i].id;
            var crit_value = elements[i].value;
            filters[crit_key] = crit_value;
        }
    }
    console.log(filters)
    filterSend(order, filters)
});
////////////////////////////////////////////////////////////////
// Ports interactions for click or dbl click     //
////////////////////////////////////////////////////////////////
ports = document.querySelectorAll('.ports').forEach(function (elt) {
    elt.addEventListener('dblclick', function () {
        interface = elt.id;
        ajax_int_selection(interface)
    });
});

ports = document.querySelectorAll('.ports').forEach(function (elt) {
    elt.addEventListener('click', function () {
        interface = elt.id;
        ajax_int_sh_run(interface)
    });
});

////////////////////////////////////////////////////////////////
// Post function sending user input and recovering server     //
// Calling back function to handle response                   //
////////////////////////////////////////////////////////////////
function ajax_int_selection(interface) {
    //Json sent to the django server
    // Later on, might include user ID for instance
    // id recovered in the form as hidden parameter
    var data2send = {
        order: 'int_selection',
        host_interface: interface,
        other_field: 'for future use'
    }
    //#charset=utf-8
    $.ajax({
        "url": window.location.href,
        "type": "POST",
        "contentType": "application/json; #charset=utf-8",
        "dataType": "json",
        "data": JSON.stringify(data2send),
        "success": function (returned_int) {
            // modifes interface name class
            int_port_id = returned_int.host + '&&' + returned_int.interface
            int_name_id = returned_int.host + '&&' + returned_int.interface + '_name'
            var int_name = document.getElementById(int_name_id)
            var int_port = document.getElementById(int_port_id)
            if (returned_int.selected) {
                int_name.className = 'int_name_selected'
                // modifies port class
                if (returned_int.row === 'odd') {
                    int_port.firstElementChild.className = 'btooltip top_selected'
                }
                else {
                    int_port.firstElementChild.className = 'btooltip down_selected'
                }
            }
            else {
                int_name.className = 'int_name'
                if (returned_int.row === 'odd') {
                    int_port.firstElementChild.className = 'btooltip top'
                }
                else {
                    int_port.firstElementChild.className = 'btooltip down'
                };
            };
        }
    });
};


function ajax_int_sh_run(interface) {
    //Json sent to the django server
    // Later on, might include user ID for instance
    // id recovered in the form as hidden parameter
    var data2send = {
        order: 'int_sh_run',
        host_interface: interface,
        other_field: 'for future use'
    }
    //#charset=utf-8
    $.ajax({
        "url": window.location.href,
        "type": "POST",
        "contentType": "application/json; #charset=utf-8",
        "dataType": "json",
        "data": JSON.stringify(data2send),
        "success": function (returned_int) {
            pre_result_id = returned_int.host + '&&' + returned_int.module + '_result'
            var result = document.getElementById(pre_result_id)
            result.innerHTML = JSON.stringify(returned_int, undefined, 2)
        }
    });
};


function filterSend(order, filters) {
    //Json sent to the django server
    var data2send = {
        order: order,
        filters: filters,
        other_field: 'for future use'
    }
    $.ajax({
        "url": window.location.href,
        "type": "POST",
        "contentType": "application/json; #charset=utf-8",
        "dataType": "json",
        "data": JSON.stringify(data2send),
        "success": function (result) {
            //reload page on sucess
            location.reload()
        }
    });
};