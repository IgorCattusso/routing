const table = document.getElementById("std-table");
const rows = document.getElementsByClassName("std-tr");
const deleteButton = document.getElementById("delete");
const editButton = document.getElementById("edit");

for (let i = 0; i < rows.length; i++) {
    rows[i].addEventListener("click", function () {
        // toggle "selected" class on clicked row
        this.classList.toggle("selected");
        // enable/disable button based on selected rows
        const selectedRows = table.querySelectorAll(".selected");
        if (selectedRows.length === 1) {
            deleteButton.removeAttribute("disabled");
            editButton.removeAttribute("disabled");
        } else {
            deleteButton.setAttribute("disabled", true);
            editButton.setAttribute("disabled", true);
        }
    });
}


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
        window.location.href = `/user/edit/${selectedRowIDs[0]}`;
    } else {
        editButton.setAttribute("disabled", true);
    }
});


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
        const user = document.querySelector(".std-tr.selected");
        const userId = user.getAttribute("data-id");
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
            url: "/users/delete/" + userId,

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                alert("Usuário excluído com sucesso!");
                window.location.href = "/users";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                alert("Ocorreu um erro ao excluir o usuário: " + error);
            }
        });
    } else {
        deleteButton.setAttribute("disabled", true);
    }
});

const changeUserStatus = document.getElementById("changeUserStatus");
changeUserStatus.addEventListener("click", function () {
    const table = document.getElementById("std-table");
    const rows = table.getElementsByClassName("std-tr");
    const selectedRowIDs = [];
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].classList.contains("selected")) {
            selectedRowIDs.push(rows[i].getAttribute("data-id"));
        }
    }

    if (selectedRowIDs.length === 1) {
        const user = document.querySelector(".std-tr.selected");
        const userId = user.getAttribute("data-id");
        const CSRFToken = document.getElementById("CSRFToken");
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "PATCH",
            url: "/users/change-user-status/" + userId,

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                alert("Status alterado com sucesso!");
                window.location.href = "/users";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                alert("Ocorreu um erro ao alterar o status do usuário: " + error);
            }
        });
    } else if (selectedRowIDs.length === 0) {
        alert("Por favor, selecione algum usuário");
    } else {
        alert("Por favor, selecione apenas um usuário");
    }
});
