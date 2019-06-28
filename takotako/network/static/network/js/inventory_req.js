////////////////////////////////////////////////////////////////
// DOM selecotrs declaration                                  //
////////////////////////////////////////////////////////////////
var openButton = document.getElementById('openButton');
var myForm = document.getElementById('myForm');
var progressBar = document.getElementById('progressBar')
var uploadButton = document.getElementById('uploadButton')
var reloadButton = document.getElementById("reloadButton");


////////////////////////////////////////////////////////////////
// Event listeners to submit user input upon clicking submit  //
// button                                                     //
////////////////////////////////////////////////////////////////

openButton && openButton.addEventListener("click", function () {
    myForm.style.display = "block";
    openButton.style.display = "none"
});

uploadButton && uploadButton.addEventListener("click", function () {
    myForm.style.display = "none";
    progressBar.style.display = "block"
});

reloadButton && reloadButton.addEventListener("click", function () {
    myForm.style.display = "block";
});



