// Get the border of the routeName from being red, because it was blank on submit,
// back to normal when something is filled and to transparent when the field is out of focus
const userName = document.getElementById("userName");
userName.addEventListener("input", function () {
    userName.style.border = "2px solid #4693f8";
});
userName.addEventListener("blur", function () {
    userName.style.border = "2px solid transparent";
});
userName.addEventListener("click", function () {
    userName.style.border = "2px solid #4693f8";
});

const userEmail = document.getElementById("userName");
userEmail.addEventListener("input", function () {
    userEmail.style.border = "2px solid #4693f8";
});
userEmail.addEventListener("blur", function () {
    userEmail.style.border = "2px solid transparent";
});
userEmail.addEventListener("click", function () {
    userEmail.style.border = "2px solid #4693f8";
});


// Get the #save button
// Add a click event listener to the #save button
const saveButton = document.querySelector("#save");
saveButton.addEventListener("click", () => {
    // Setting variables
    const userId = document.getElementById("editUserId");
    const userName = document.getElementById("userName");
    const userEmail = document.getElementById("userEmail");
    const userZendeskUserId = document.getElementsByClassName("zendesk-users-id-chosen-value");
    const userZendeskScheduleId = document.getElementsByClassName("zendesk-schedules-id-chosen-value");

    const backlogLimit = document.getElementById("ticketLimit");
    const dailyLimit = document.getElementById("dailyLimit");
    const hourlyLimit = document.getElementById("hourlyLimit");

    const CSRFToken = document.getElementById("CSRFToken");

    let userZendeskUserIdValue = ""
    for (let i = 0; i < userZendeskUserId.length; i++) {
        userZendeskUserIdValue = userZendeskUserId[i].id
    }

    let userZendeskScheduleIdValue = "";
    for (let i = 0; i < userZendeskScheduleId.length; i++) {
        userZendeskScheduleIdValue = userZendeskScheduleId[i].id
    }

    if (userZendeskUserIdValue === "ZendeskUsers" || userZendeskUserIdValue === "None") {
        userZendeskUserIdValue = null
    }

    if (userZendeskScheduleIdValue === "zendeskUserSchedules" || userZendeskScheduleIdValue === "None") {
        userZendeskScheduleIdValue = null
    }



    if (backlogLimit.value === 0) {
        backlogLimit.value = null
    }
    if (dailyLimit.value === 0) {
        dailyLimit.value = null
    }
    if (hourlyLimit.value === 0) {
        hourlyLimit.value = null
    }


    if (userName.value === "") {
        userName.placeholder = "Este campo é obrigatório";
        userName.style.borderColor = "red";
        userName.focus();
        return;
    }

    if (userEmail.value === "") {
        userEmail.placeholder = "Este campo é obrigatório";
        userEmail.style.borderColor = "red";
        userEmail.focus();
        return;
    }

    const userStatusValue = $("#editUserStatus").prop("checked");

    // If the ID of the route is empty, that means we"re on the NEW page, if it has a value, that means we"re on the EDIT page
    if (userId.value === "") {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "POST",
            url: "/users/new",
            data: JSON.stringify({
                user_status: userStatusValue,
                user_name: userName.value,
                user_email: userEmail.value,
                zendesk_users_id: parseInt(userZendeskUserIdValue),
                zendesk_schedules_id: parseInt(userZendeskScheduleIdValue),
                backlog_limit: backlogLimit.value,
                hourly_ticket_assignment_limit: hourlyLimit.value,
                daily_ticket_assignment_limit: dailyLimit.value,
            }),
            contentType: "application/json",

            success: function (response) {
                alert("Cadastro realizado com sucesso!");
                window.location.href = "/users";
            },
            error: function (xhr, status, error) {
                alert("Ocorreu um erro ao realizar o cadastro: " + error);
            }
        });
    }

    if (userId.value !== "") {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });

        $.ajax({
            type: "PUT",
            url: "/user/edit/" + userId.value,
            data: JSON.stringify({
                user_id: userId.value,
                user_status: userStatusValue,
                user_name: userName.value,
                user_email: userEmail.value,
                zendesk_users_id: userZendeskUserIdValue,
                zendesk_schedules_id: userZendeskScheduleIdValue,
                backlog_limit: backlogLimit.value,
                hourly_ticket_assignment_limit: hourlyLimit.value,
                daily_ticket_assignment_limit: dailyLimit.value,
            }),
            contentType: "application/json",

            success: function (response) {
                alert("Cadastro alterado com sucesso!");
                window.location.href = "/users";
            },
            error: function (xhr, status, error) {
                alert("Ocorreu um erro ao alterar o cadastro: " + error);
            }
        });
    }
});
