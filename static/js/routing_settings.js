// Get the #save button
// Add a click event listener to the #save button
const saveButton = document.querySelector("#save");
saveButton.addEventListener("click", () => {
    // Setting variables

    const useRoutesInput = document.getElementById("routesYes");
    const dontUseRoutesInput = document.getElementById("routesNo");

    const leastActiveInput = document.getElementById("leastActive");
    const roundRobinInput = document.getElementById("roundRobin");

    const ticketLimit = document.getElementById("ticketLimit");
    const dailyLimit = document.getElementById("dailyLimit");
    const hourlyLimit = document.getElementById("hourlyLimit");

    const userZendeskScheduleId = document.getElementsByClassName("zendesk-schedules-id-chosen-value");

    const CSRFToken = document.getElementById("CSRFToken");

    let useRoutes;
    if (useRoutesInput.checked === true && dontUseRoutesInput.checked === false) {
        useRoutes = true; // assign the value inside the if statement
    } else if (useRoutesInput.checked === false && dontUseRoutesInput.checked === true) {
        useRoutes = false; // assign the value inside the else if statement
    }

    let routing_model;
    if (leastActiveInput.checked === true && roundRobinInput.checked === false) {
        routing_model = 0; // assign the value inside the if statement
    } else if (leastActiveInput.checked === false && roundRobinInput.checked === true) {
        routing_model = 1; // assign the value inside the else if statement
    }

    if (ticketLimit.value === 0) {
        ticketLimit.value = ""
    }
    if (dailyLimit.value === 0) {
        dailyLimit.value = ""
    }
    if (hourlyLimit.value === 0) {
        hourlyLimit.value = ""
    }

    let userZendeskScheduleIdValue = "";
    for (let i = 0; i < userZendeskScheduleId.length; i++) {
        userZendeskScheduleIdValue = userZendeskScheduleId[i].id
    }

    if (userZendeskScheduleIdValue === "userZendeskSchedulesId") {
        userZendeskScheduleIdValue = null
    }

    // If the ID of the route is empty, that means we"re on the NEW page, if it has a value, that means we"re on the EDIT page
    // Send the selected values to your Flask app using an AJAX request
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
            }
        }
    });

    $.ajax({
        type: "PUT",
        url: "/routing-settings",
        data: JSON.stringify({
            use_routes: useRoutes,
            routing_model: routing_model,
            backlog_limit: ticketLimit.value,
            daily_assignment_limit: dailyLimit.value,
            hourly_assignment_limit: hourlyLimit.value,
            zendesk_schedules_id: userZendeskScheduleIdValue,
        }),
        contentType: "application/json",

        success: function (response) {
            // Provide feedback to the users that the data was processed successfully
            alert("Configurações alteradas com sucesso!");
            window.location.href = "/routing-settings";
        },
        error: function (xhr, status, error) {
            // Provide feedback to the users that an error occurred during the processing of the data
            alert("Ocorreu um erro ao realizar o cadastro: " + error);
        }
    });

});


const scheduleInputField = document.querySelector(".zendesk-schedules-id-chosen-value");
const scheduleDropdown = document.querySelector(".schedule-values-list");
const scheduleDropdownArray = [...document.getElementsByClassName("schedule-dropdown-menu-option")];
const zendeskschedulesFieldsWrapper = document.getElementById("zendeskSchedulesWrapper")

let scheduleValueArray = [];
scheduleDropdownArray.forEach(item => {
    scheduleValueArray.push(item.textContent);
});


scheduleInputField.addEventListener("input", () => {
    scheduleDropdown.classList.add("open");
    let inputValue = scheduleInputField.value.toLowerCase();
    if (inputValue.length > 0) {
        for (let j = 0; j < scheduleValueArray.length; j++) {
            if (!(inputValue.substring(0, inputValue.length) === scheduleValueArray[j].substring(0, inputValue.length).toLowerCase())) {
                scheduleDropdownArray[j].classList.add("closed");
            } else {
                scheduleDropdownArray[j].classList.remove("closed");
            }
        }
    } else {
        for (let j = 0; j < scheduleDropdownArray.length; j++) {
            scheduleDropdownArray[j].classList.remove("closed");
        }
    }
});

scheduleDropdownArray.forEach(item => {
    item.addEventListener("click", (evt) => {
        scheduleInputField.value = item.textContent;
        scheduleInputField.id = item.value
        scheduleDropdownArray.forEach(dropdown => {
            dropdown.classList.add("closed");
        });
        zendeskschedulesFieldsWrapper.style.display = "flex";
    });
})

scheduleInputField.addEventListener("focus", () => {
    scheduleInputField.placeholder = "Selecione";
    scheduleDropdown.classList.add("open");
    scheduleDropdownArray.forEach(dropdown => {
        dropdown.classList.remove("closed");
    });
});

scheduleInputField.addEventListener("blur", () => {
    scheduleInputField.placeholder = "Selecione";
    scheduleDropdown.classList.remove("open");
});

document.addEventListener("click", (evt) => {
    const isDropdown = scheduleDropdown.contains(evt.target);
    const isInput = scheduleInputField.contains(evt.target);
    if (!isDropdown && !isInput) {
        scheduleDropdown.classList.remove("open");
    }
});