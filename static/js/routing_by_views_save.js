// Get the border of the routeName from being red, because it was blank on submit,
// back to normal when something is filled and to transparent when the field is out of focus
const routingViewName = document.getElementById("viewName");
routingViewName.addEventListener("input", function () {
    routingViewName.style.border = "2px solid #4693f8";
});
routingViewName.addEventListener("blur", function () {
    routingViewName.style.border = "2px solid transparent";
});
routingViewName.addEventListener("click", function () {
    routingViewName.style.border = "2px solid #4693f8";
});

// Get the #save button
// Add a click event listener to the #save button
const saveButton = document.querySelector("#save");
saveButton.addEventListener("click", () => {
    // Setting variables
    const routingViewId = document.getElementById("routingViewId");
    const routingViewName = document.getElementById("viewName");
    const selectedUsers = document.querySelectorAll(".js-user-option-container.selected");
    const selectedGroups = document.querySelectorAll(".js-group-option-container.selected");
    const zendeskViewId = document.getElementsByClassName("zendesk-views-id-chosen-value");
    const zendeskScheduleId = document.getElementsByClassName("zendesk-schedules-id-chosen-value");

    let zendeskViewIdValue = "";
    for (let i = 0; i < zendeskViewId.length; i++) {
        zendeskViewIdValue = zendeskViewId[i].id
    }

    if (zendeskViewIdValue === "zendeskViews") {
        zendeskViewIdValue = null
    }

    let zendeskScheduleIdValue = "";
    for (let i = 0; i < zendeskScheduleId.length; i++) {
        zendeskScheduleIdValue = zendeskScheduleId[i].id
    }

    if (zendeskScheduleIdValue === "zendeskSchedules") {
        zendeskScheduleIdValue = null
    }

    const CSRFToken = document.getElementById("CSRFToken");

    // If there are no selected option containers, do nothing
    if (selectedUsers.length === 0 && selectedGroups.length === 0) {
        alert("Selecione usuários ou grupos como destinatários da visualização");
        return;
    }

    // Alert that the routeName field is mandatory
    if (routingViewName.value === "") {
        routingViewName.placeholder = "Este campo é obrigatório";
        routingViewName.style.borderColor = "red";
        routingViewName.focus();
        return;
    }

    // Get the value of the View status, true or false
    const viewStatusValue = $("#viewStatus").prop("checked");

    // Initialize an array to hold the selected recipient users
    const selectedUsersValues = [];
    // Loop through each selected option container and extract the value of its selected option
    selectedUsers.forEach((selectedOptionContainer) => {
        const selectedOption = selectedOptionContainer.querySelector(".recipient-user-option");
        if (selectedOption.value !== null) {
            const selectedValue = selectedOption.value;
            selectedUsersValues.push(selectedValue);
        }
    });

    // Initialize an array to hold the selected recipient groups
    const selectedGroupsValues = [];
    // Loop through each selected option container and extract the value of its selected option
    selectedGroups.forEach((selectedOptionContainer) => {
        const selectedOption = selectedOptionContainer.querySelector(".recipient-group-option");
        if (selectedOption.value !== null) {
            const selectedValue = selectedOption.value;
            selectedGroupsValues.push(selectedValue);
        }
    });

    // If the ID of the route is empty, that means we"re on the NEW page, if it has a value, that means we"re on the EDIT page
    if (routingViewId.value === "") {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        // Send the selected values to your Flask app using an AJAX request
        $.ajax({
            type: "POST",
            url: "/routing-views/insert",
            data: JSON.stringify({
                routing_view_status: viewStatusValue,
                routing_view_name: routingViewName.value,
                recipient_users: selectedUsersValues,
                recipient_groups: selectedGroupsValues,
                zendesk_view_id: zendeskViewIdValue,
                zendesk_schedule_id: zendeskScheduleIdValue,
            }),
            contentType: "application/json",

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                console.log(this.data)
                alert("Cadastro realizado com sucesso!");
                window.location.href = "/routing-views";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                console.log(this.data);
                alert("Ocorreu um erro ao realizar o cadastro: " + error);
            }
        });
    }

    if (routingViewId.value !== "") {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "PUT",
            url: "/routing-views/update/" + routingViewId.value,
            data: JSON.stringify({
                routing_view_status: viewStatusValue,
                routing_view_name: routingViewName.value,
                recipient_users: selectedUsersValues,
                recipient_groups: selectedGroupsValues,
                zendesk_view_id: zendeskViewIdValue,
                zendesk_schedule_id: zendeskScheduleIdValue,
            }),
            contentType: "application/json",

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                console.log(this.data)
                alert("Cadastro alterado com sucesso!");
                window.location.href = "/routing-views";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                console.log(this.data);
                alert("Ocorreu um erro ao alterar o cadastro: " + error);
            }
        });
    }
});
