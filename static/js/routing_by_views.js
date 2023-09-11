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
            runViewButton.removeAttribute("disabled");
        } else {
            editButton.setAttribute("disabled", true);
            deleteButton.setAttribute("disabled", true);
            deactivateButton.setAttribute("disabled", true);
            runViewButton.setAttribute("disabled", true);
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
        window.location.href = `/routing-views/edit/${selectedRowIDs[0]}`;
    } else {
        editButton.setAttribute("disabled", true);
    }
});


const deleteButton = document.getElementById("delete");
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
        const route = document.querySelector(".std-tr.selected");
        const viewId = route.getAttribute("data-id");
        const CSRFToken = document.getElementById("CSRFToken");
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "DELETE",
            url: "/routing-views/delete/" + viewId,

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                alert("Visualização excluída com sucesso!");
                window.location.href = "/routing-views";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                alert("Ocorreu um erro ao excluir a Visualização: " + error);
            }
        });
    } else {
        deleteButton.setAttribute("disabled", true);
    }
});


const deactivateButton = document.getElementById("deactivate");
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
        const route = document.querySelector(".std-tr.selected");
        const routeId = route.getAttribute("data-id");
        const CSRFToken = document.getElementById("CSRFToken");
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "PUT",
            url: "/routing-views/deactivate/" + routeId,

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                alert("Visualização inativada com sucesso!");
                window.location.href = "/routing-views";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                alert("Ocorreu um erro ao excluir a rota: " + error);
            }
        });
    } else {
        deactivateButton.setAttribute("disabled", true);
    }
});


const runViewButton = document.getElementById("runView");
runViewButton.addEventListener("click", function () {
    const table = document.getElementById("std-table");
    const rows = table.getElementsByClassName("std-tr");
    const selectedRowIDs = [];
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("selected")) {
            selectedRowIDs.push(rows[i].getAttribute("data-id"));
        }
    }
    if (selectedRowIDs.length === 1) {
        const view = document.querySelector(".std-tr.selected");
        const viewId = view.getAttribute("data-id");
        const CSRFToken = document.getElementById("CSRFToken");
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "POST",
            url: "/routing-views/run-view/" + viewId,

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                console.log(this.url)
                alert("Visualização executada com sucesso!");
                window.location.href = "/routing-views";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                alert("Ocorreu um erro ao executar a visualização: " + error);
            }
        });
    } else {
        runViewButton.setAttribute("disabled", true);
    }
});
