//---------------------------------//
// See users in the selected group //
//---------------------------------//
const table = document.getElementById("std-table");
const rows = document.getElementsByClassName("std-tr");
for (let i = 0; i < rows.length; i++) {
    rows[i].addEventListener("click", function () {
        // toggle "selected" class on clicked row
        this.classList.toggle("selected");
        // enable/disable button based on selected rows
        const selectedRows = table.querySelectorAll(".selected");
        if (selectedRows.length === 1) {
            button.removeAttribute("disabled");
        } else {
            button.setAttribute("disabled", true);
        }
    });
}


const button = document.getElementById("seeFormStructure");
button.addEventListener("click", function () {
    const table = document.getElementById("std-table");
    const rows = table.getElementsByClassName("std-tr");
    const selectedRowIDs = [];
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("selected")) {
            selectedRowIDs.push(rows[i].getAttribute("data-id"));
        }
    }
    if (selectedRowIDs.length === 1) {
        window.location.href = `/ticket-forms-structure/${selectedRowIDs[0]}`;
    } else {
        button.setAttribute("disabled", true);
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const updateGroups = document.getElementById("updateForms");
    updateGroups.addEventListener("click", function () {
        window.location.href = "/get-ticket-forms";
    });
});