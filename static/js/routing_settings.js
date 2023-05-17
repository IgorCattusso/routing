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
            agent_backlog_limit: ticketLimit.value,
            daily_assignment_limit: dailyLimit.value,
            hourly_assignment_limit: hourlyLimit.value,
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
