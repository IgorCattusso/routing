notify();

// Sets an interval to check for new notifications every 5 seconds
setInterval(function () {
    notify();
}, 5000);

// Check for notifications permission and prompts the users for it if it"s not allowed
// Checks if the users is logged in before calling the notification function
function notify() {
    const userId = document.getElementById("userId"); // Checks if the users id is present (logged in)
    const userStatus = document.getElementById("userStatus"); // Checks if the users id is present (logged in)
    if (userId && userStatus.innerHTML === "Online") { // If the users id is present, then calls the notification function
        if (!("Notification" in window)) { // Checks if the browser supports notifications
            alert("This browser does not support desktop notification");
        } else if (Notification.permission === "granted") { // Checks if the browser allows notifications
            notification(userId) // If allows notifications, then calls the notification function
        } else if (Notification.permission !== "denied") { // If it does not allow notifications
            console.log("Nofications are disabled!"); // Logs to the console
            Notification.requestPermission().then((permission) => { // Prompts for permission
                if (permission === "granted") { // If granted
                    notification(userId) // Calls the notification function
                }
            });
        }
    }
}


// Get the notification sound file
const newTicketNotificationSound = new Audio("/static/snd/new_ticket_notification.wav");
const CSRFToken = document.getElementById("CSRFToken");

// Get a users"s notifications, one at a time, then marks it as received.
// After that, displays the notification and flags it as received
function notification(userId) {
    $.ajax({
        type: "GET", // Get notifications
        url: "/get-users-next-notification/" + userId.value,
        success: function (get_notification_response, xhr, textStatus) {
            if (textStatus.status === 200) { // If a notification was received
                let options = {
                    body: get_notification_response["content"],
                    icon: "/static/img/favicon.png",
                }

                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                        }
                    }
                });
                $.ajax({
                    type: "POST", // Sets the notification as received
                    url: "/flag-notification-as-sent/" + get_notification_response["id"],
                    success: function (flag_as_sent_response, xhr, textStatus) {
                        if (textStatus.status === 200) {  // If a notification was successfully flagged as received
                            // Displays a notification
                            if (get_notification_response["type"] === 0) {
                                new Notification("Novo ticket atribuído!", options);
                                addNewNotificationToList(
                                    get_notification_response["id"],
                                    get_notification_response["content"],
                                    get_notification_response["url"],
                                )
                            } else {
                                new Notification("Operação concluída!", options);
                                addNewNotificationToList(
                                    get_notification_response["id"],
                                    get_notification_response["content"],
                                )
                            }

                            // Plays a sound. To play the sound is either necessary:
                            // 1. That the users interacts with the page, any interaction like changing the status or
                            //    loggin in. After reloading the page, it"s necessary to perform an interaction again.
                            // 2. It"s possible to get around the interaction thing by granting access to the page
                            //    to Sound instead of "automatic".
                            newTicketNotificationSound.play();
                            // Sets an onclick event to redirect the users to the ticket when clicking the notification
                            if (get_notification_response["url"]) {
                                notification.onclick = function (event) {
                                    event.preventDefault();
                                    window.open(get_notification_response["url"]);
                                }
                            }
                            // Sets the notification as received
                            $.ajaxSetup({
                                beforeSend: function(xhr, settings) {
                                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                                        xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                                    }
                                }
                            });
                            $.ajax({
                                type: "POST",
                                url: "/flag-notification-as-received/" + get_notification_response["id"],
                                success: function (flag_as_received_response, xhr, textStatus) {
                                    // console.log("flag-notification-as-received-status: " + textStatus.status)
                                },
                                error: function (xhr, status, error) {
                                    console.log("Error flagging notification as received: " + error);
                                }
                            });
                        }
                    },
                    error: function (xhr, status, error) {
                        console.log("Error flagging notification as sent: " + error);
                    }
                });
            }
        },
        error: function (xhr, status, error) {
            console.log("Error getting new notifications: " + error);
        }
    });
}

function flagNotificationAsRead(notification_id) {

    let _notification_id = "notificationUnreadIcon-" + notification_id
    let isNotificationAlreadyRead = document.getElementById(_notification_id)

    if (isNotificationAlreadyRead) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "POST",
            url: "/flag-notification-as-read/" + notification_id,
            success: function (flag_as_read_response, xhr, textStatus) {
                if (textStatus.status === 200) {
                    const unreadIcon = "notificationUnreadIcon-" + notification_id;
                    const notification = document.getElementById(unreadIcon);
                    if (notification) {
                        notification.style.display = "none";
                    }
                }
            },
            error: function (xhr, status, error) {
                console.log("Error flagging notification as read: " + error);
            }
        });
        updateUnreadNotificationCounter("subtract", 1)
    }
}


function flagAllNotificationsAsRead(user_id) {

    const unreadNotifications = document.getElementsByClassName("unread-notification-icon");
    let numberOfUnreadNotificationsElement = document.getElementById("newNotificationCounter");
    if (!numberOfUnreadNotificationsElement) {
        numberOfUnreadNotificationsElement = document.getElementById("newNotificationCounterMoreThanTen")
    }

    const numberOfUnreadNotifications = numberOfUnreadNotificationsElement.textContent

    if (unreadNotifications) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", CSRFToken.value);
                }
            }
        });
        $.ajax({
            type: "POST",
            url: "/flag-all-notifications-as-read/" + user_id,
            success: function (flag_all_as_read_response, xhr, textStatus) {
                if (textStatus.status === 200) {
                    const unreadIcons = document.getElementsByClassName("unread-notification-icon");
                    for (let i = 0; i < unreadIcons.length; i++) {
                        unreadIcons[i].style.display = "none";
                    }
                }
                updateUnreadNotificationCounter("subtract", numberOfUnreadNotifications)
            },
            error: function (xhr, status, error) {
                console.log("Error flagging notification as read: " + error);
            }
        });
    }
}

function updateUnreadNotificationCounter(operation, numberOfReadNotifications) {
    let newNotificationCounter = document.getElementById("newNotificationCounter");
    let newNotificationCounterMoreThanTen = document.getElementById("newNotificationCounterMoreThanTen");

    if (newNotificationCounter) {
        if (operation === "subtract" && parseInt(newNotificationCounter.textContent) > 0) {
            newNotificationCounter.textContent = parseInt(newNotificationCounter.textContent) - numberOfReadNotifications;
            if (newNotificationCounter.textContent < 10) {
                newNotificationCounter.classList.add("fix-alignment-less-than-ten")
                newNotificationCounter.classList.remove("fix-alignment-more-than-ten")
            }
        } else if (operation === "add") {
            newNotificationCounter.textContent = parseInt(newNotificationCounter.textContent) + numberOfReadNotifications;
            if (newNotificationCounter.textContent >= 10) {
                newNotificationCounter.classList.add("fix-alignment-more-than-ten")
                newNotificationCounter.classList.remove("fix-alignment-less-than-ten")
            }
        }
    }

    if (newNotificationCounterMoreThanTen) {
        if (operation === "subtract" && parseInt(newNotificationCounterMoreThanTen.textContent) > 0) {
            newNotificationCounterMoreThanTen.textContent = (parseInt(newNotificationCounterMoreThanTen.textContent) - numberOfReadNotifications);
            if (newNotificationCounterMoreThanTen.textContent < 10) {
                newNotificationCounterMoreThanTen.classList.add("fix-alignment-less-than-ten")
                newNotificationCounterMoreThanTen.classList.remove("fix-alignment-more-than-ten")
            }
        } else if (operation === "add") {
            newNotificationCounterMoreThanTen.textContent = (parseInt(newNotificationCounterMoreThanTen.textContent) + numberOfReadNotifications);
            if (newNotificationCounterMoreThanTen.textContent >= 10) {
                newNotificationCounterMoreThanTen.classList.add("fix-alignment-more-than-ten")
                newNotificationCounterMoreThanTen.classList.remove("fix-alignment-less-than-ten")
            }
        }
    }

}

const notificationBell = document.getElementById("notificationBell");
const notificationWrapper = document.getElementById("notificationPanelWrapper");
if (notificationBell) {
    notificationBell.addEventListener("click", function () {
        const notificationWrapperStyle = window.getComputedStyle(notificationWrapper);
        if (notificationWrapperStyle.display === "none") {
            notificationWrapper.style.display = "flex";
        } else {
            notificationWrapper.style.display = "none";
        }
    });

    document.addEventListener("click", function (event) {
    const isClickInside = notificationWrapper.contains(event.target) || notificationBell.contains(event.target);
    if (!isClickInside) {
            notificationWrapper.style.display = "none";
        }
    });

}



function addNewNotificationToList(notificationId, notificationContent, notificationURL = null) {

    const notificationsPanelContainer = document.getElementById("notificationsPanelContainer");

    const notificationContainer = document.createElement("div");
    notificationContainer.setAttribute("class", "notification-container");
    notificationContainer.setAttribute("onClick", "flagNotificationAsRead(" + notificationId + ")");
    notificationContainer.setAttribute("onAuxClick", "flagNotificationAsRead(" + notificationId + ")");

    const notificationText = document.createElement("span");
    notificationText.setAttribute("id", "notification-" + notificationId);
    notificationText.setAttribute("class", "notification-text-" + notificationId);
    notificationText.setAttribute("onClick", "flagNotificationAsRead(" + notificationId + ")");
    notificationText.setAttribute("onAuxClick", "flagNotificationAsRead(" + notificationId + ")");
    notificationText.style.fontSize = "13px";
    notificationText.innerText = notificationContent;
    notificationContainer.append(notificationText);

    const notificationIconsWrapper = document.createElement("div");
    notificationIconsWrapper.setAttribute("class", "notification-icons-wrapper");
    notificationContainer.append(notificationIconsWrapper);

    if (notificationURL) {

        const notificationLink = document.createElement("a");
        notificationLink.setAttribute("id", "notification-" + notificationId);
        notificationLink.setAttribute("href", notificationURL);
        notificationLink.setAttribute("target", "_blank");
        notificationLink.setAttribute("class", "notification-link");
        notificationsPanelContainer.prepend(notificationLink);

        notificationLink.append(notificationContainer);

        const notificationUrlSvg = document.createElement("object");
        notificationUrlSvg.setAttribute("id", "notificationOpenLinkIcon-" + notificationId);
        notificationUrlSvg.setAttribute("class", "open-link-svg");
        notificationUrlSvg.setAttribute("data", "/static/svg/open-link.svg");
        notificationUrlSvg.setAttribute("type", "image/svg+xml");
        notificationIconsWrapper.prepend(notificationUrlSvg);
    } else {
        notificationsPanelContainer.prepend(notificationContainer);
    }

    const unreadNotificationSvg = document.createElement("object");
    unreadNotificationSvg.setAttribute("id", "notificationUnreadIcon-" + notificationId);
    unreadNotificationSvg.setAttribute("class", "open-link-svg");
    unreadNotificationSvg.setAttribute("data", "/static/svg/unread-notification-icon.svg");
    unreadNotificationSvg.setAttribute("type", "image/svg+xml");
    unreadNotificationSvg.style.width = "10px";
    unreadNotificationSvg.style.height = "10px";
    notificationIconsWrapper.append(unreadNotificationSvg);

    updateUnreadNotificationCounter("add", 1)

}
