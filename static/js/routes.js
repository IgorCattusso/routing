const table = document.getElementById("std-table");
const rows = document.getElementsByClassName("std-tr");
for (let i = 0; i < rows.length; i++) {
    rows[i].addEventListener("click", function () {
        // toggle "selected" class on clicked row
        this.classList.toggle("selected");
        // enable/disable button based on selected rows
        const selectedRows = table.querySelectorAll(".selected");
        if (selectedRows.length === 1) {
            editButton.removeAttribute("disabled");
            deleteButton.removeAttribute("disabled");
            deactivateButton.removeAttribute("disabled");
        } else {
            editButton.setAttribute("disabled", true);
            deleteButton.setAttribute("disabled", true);
            deactivateButton.setAttribute("disabled", true);
        }
    });
}



const editButton = document.getElementById("edit");
editButton.addEventListener("click", function () {
    const table = document.getElementById("std-table");
    const rows = table.getElementsByClassName("std-tr");
    const selectedRowIDs = [];
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("selected")) {
            selectedRowIDs.push(rows[i].getAttribute("data-id"));
        }
    }
    if (selectedRowIDs.length === 1) {
        window.location.href = `/routes/edit/${selectedRowIDs[0]}`;
    } else {
        editButton.setAttribute("disabled", true);
    }
});



const deleteButton = document.getElementById("deactivate");
deleteButton.addEventListener("click", function () {
    const table = document.getElementById("std-table");
    const rows = table.getElementsByClassName("std-tr");
    const selectedRowIDs = [];
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("selected")) {
            selectedRowIDs.push(rows[i].getAttribute("data-id"));
        }
    }
    if (selectedRowIDs.length === 1) {
        window.location.href = `/routes/deactivate/${selectedRowIDs[0]}`;
    } else {
        deleteButton.setAttribute("disabled", true);
    }
});



const deactivateButton = document.getElementById("delete");
deactivateButton.addEventListener("click", function () {
    const table = document.getElementById("std-table");
    const rows = table.getElementsByClassName("std-tr");
    const selectedRowIDs = [];
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("selected")) {
            selectedRowIDs.push(rows[i].getAttribute("data-id"));
        }
    }
    if (selectedRowIDs.length === 1) {
        window.location.href = `/routes/delete/${selectedRowIDs[0]}`;
    } else {
        deactivateButton.setAttribute("disabled", true);
    }
});



