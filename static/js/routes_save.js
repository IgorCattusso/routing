// Get the border of the routeName from being red, because it was blank on submit,
// back to normal when something is filled and to transparent when the field is out of focus
const routeName = document.getElementById("routeName");
routeName.addEventListener("input", function () {
    routeName.style.border = "2px solid #4693f8";
});
routeName.addEventListener("blur", function () {
    routeName.style.border = "2px solid transparent";
});
routeName.addEventListener("click", function () {
    routeName.style.border = "2px solid #4693f8";
});

// Get the #save button
// Add a click event listener to the #save button
const saveButton = document.querySelector("#save");
saveButton.addEventListener("click", () => {
    // Setting variables
    const routeId = document.getElementById("routeId");
    const routeName = document.getElementById("routeName");
    const selectedUsers = document.querySelectorAll(".js-users-option-container.selected");
    const selectedGroups = document.querySelectorAll(".js-group-option-container.selected");
    const selectedLocales = document.querySelectorAll(".js-locale-option-container.selected");
    const selectedTicketGroups = document.querySelectorAll(".js-ticket-group-option-container.selected");
    const selectedTags = document.querySelectorAll(".js-tag-option-container.selected");

    // If there are no selected option containers, do nothing
    if (selectedUsers.length === 0 && selectedGroups.length === 0) {
        alert("Selecione usuários ou grupos como Destinatários da rota");
        return;
    }

    // Alert that the routeName field is mandatory
    if (routeName.value === "") {
        routeName.placeholder = "Este campo é obrigatório";
        routeName.style.borderColor = "red";
        routeName.focus();
        return;
    }

    // Get the value of the Route status, true or false
    const routeStatusValue = $("#routeStatus").prop("checked");

    // Initialize an array to hold the selected recipient users
    const selectedUsersValues = [];
    // Loop through each selected option container and extract the value of its selected option
    selectedUsers.forEach((selectedOptionContainer) => {
        const selectedOption = selectedOptionContainer.querySelector(".recipient-users-option");
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

    // Initialize an array to hold the selected locales
    const selectedLocalesValues = [];
    // Loop through each selected option container and extract the value of its selected option
    selectedLocales.forEach((selectedOptionContainer) => {
        const selectedOption = selectedOptionContainer.querySelector(".ticket-locale-option");
        if (selectedOption.value !== null) {
            const selectedValue = selectedOption.value;
            selectedLocalesValues.push(selectedValue);
        }
    });

    // Initialize an array to hold the selected locales
    const selectedTicketGroupsValues = [];
    // Loop through each selected option container and extract the value of its selected option
    selectedTicketGroups.forEach((selectedOptionContainer) => {
        const selectedOption = selectedOptionContainer.querySelector(".ticket-group-option");
        if (selectedOption.value !== null) {
            const selectedValue = selectedOption.value;
            selectedTicketGroupsValues.push(selectedValue);
        }
    });

    // Initialize an array to hold the selected tags
    const selectedTagsValues = [];
    // Loop through each selected option container and extract the value of its selected option
    selectedTags.forEach((selectedOptionContainer) => {
        const selectedOption = selectedOptionContainer.querySelector(".ticket-tag-option");
        if (selectedOption.value !== null) {
            const selectedValue = selectedOption.value;
            selectedTagsValues.push(selectedValue);
        }
    });


    // If the ID of the route is empty, that means we"re on the NEW page, if it has a value, that means we"re on the EDIT page
    if (routeId.value === "") {
        // Send the selected values to your Flask app using an AJAX request
        $.ajax({
            type: "POST",
            url: "/routes/insert_new",
            data: JSON.stringify({
                route_status: routeStatusValue,
                route_name: routeName.value,
                recipient_users: selectedUsersValues,
                recipient_groups: selectedGroupsValues,
                ticket_locales: selectedLocalesValues,
                ticket_groups: selectedTicketGroupsValues,
                ticket_tags: selectedTagsValues,
            }),
            contentType: "application/json",

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                console.log(this.data)
                alert("Cadastro realizado com sucesso!");
                window.location.href = "/routes";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                console.log(this.data);
                alert("Ocorreu um erro ao realizar o cadastro: " + error);
            }
        });
    }

    if (routeId.value !== "") {
        $.ajax({
            type: "PUT",
            url: "/routes/update-existing-route/" + routeId.value,
            data: JSON.stringify({
                route_status: routeStatusValue,
                route_name: routeName.value,
                recipient_users: selectedUsersValues,
                recipient_groups: selectedGroupsValues,
                ticket_locales: selectedLocalesValues,
                ticket_groups: selectedTicketGroupsValues,
                ticket_tags: selectedTagsValues,
            }),
            contentType: "application/json",

            success: function (response) {
                // Provide feedback to the users that the data was processed successfully
                console.log(this.data)
                alert("Cadastro alterado com sucesso!");
                window.location.href = "/routes";
            },
            error: function (xhr, status, error) {
                // Provide feedback to the users that an error occurred during the processing of the data
                console.log(this.data);
                alert("Ocorreu um erro ao alterar o cadastro: " + error);
            }
        });
    }
});
