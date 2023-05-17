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

    const latamUser = document.getElementsByName("latam-user");
    const rockStarUser = document.getElementsByName("rock-star-user");
    const jnjContestationUser = document.getElementsByName("jnj-contestation-user");
    const jnjHomologationUser = document.getElementsByName("jnj-homologation-user");


    const CSRFToken = document.getElementById("CSRFToken");

    var userZendeskUserIdValue = ""
    for (let i = 0; i < userZendeskUserId.length; i++) {
        userZendeskUserIdValue = userZendeskUserId[i].id
    }

    if (userZendeskUserIdValue === "userZendeskUsersId") {
        userZendeskUserIdValue = null
    }

    let userZendeskScheduleIdValue = "";
    for (let i = 0; i < userZendeskScheduleId.length; i++) {
        userZendeskScheduleIdValue = userZendeskScheduleId[i].id
    }

    if (userZendeskScheduleIdValue === "userZendeskSchedulesId") {
        userZendeskScheduleIdValue = null
    }

    let latamUserValue
    for (let i = 0; i < latamUser.length; i++) {
        if (latamUser[i].checked) {
            let latamUserOption = latamUser[i].id
            if (latamUserOption === "latam-no") {
                latamUserValue = 0
            } else if (latamUserOption === "latam-yes") {
                latamUserValue = 1
            } else if (latamUserOption === "latam-both") {
                latamUserValue = 2
            }
        }
    }


    let rockStarUserValue
    for (let i = 0; i < rockStarUser.length; i++) {
        if (rockStarUser[i].checked) {
            let rockStarUserOption = rockStarUser[i].id
            if (rockStarUserOption === "rock-star-no") {
                rockStarUserValue = 0
            } else if (rockStarUserOption === "rock-star-yes") {
                rockStarUserValue = 1
            }
        }
    }


    let jnjContestationUserValue
    for (let i = 0; i < jnjContestationUser.length; i++) {
        if (jnjContestationUser[i].checked) {
            let jnjContestationUserOption = jnjContestationUser[i].id
            if (jnjContestationUserOption === "jnj-contestation-no") {
                jnjContestationUserValue = 0
            } else if (jnjContestationUserOption === "jnj-contestation-yes") {
                jnjContestationUserValue = 1
            }
        }
    }


    let jnjHomologationUserValue
    for (let i = 0; i < jnjHomologationUser.length; i++) {
        if (jnjHomologationUser[i].checked) {
            let jnjHomologationUserOption = jnjHomologationUser[i].id
            if (jnjHomologationUserOption === "jnj-homologation-no") {
                jnjHomologationUserValue = 0
            } else if (jnjHomologationUserOption === "jnj-homologation-yes") {
                jnjHomologationUserValue = 1
            }
        }
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
                zendesk_users_id: userZendeskUserIdValue,
                zendesk_schedules_id: userZendeskScheduleIdValue,
                latam_user: latamUserValue,
                rock_star_user: rockStarUserValue,
                jnj_contestation_user: jnjContestationUserValue,
                jnj_homologation_user: jnjHomologationUserValue,
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
                latam_user: latamUserValue,
                rock_star_user: rockStarUserValue,
                jnj_contestation_user: jnjContestationUserValue,
                jnj_homologation_user: jnjHomologationUserValue,
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
