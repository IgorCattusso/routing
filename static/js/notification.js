// Sets an interval to check for new notifications every 5 seconds
setInterval(function () {
    notify();
}, 5000);

// Check for notifications permission and prompts the user for it if it's not allowed
// Checks if the user is logged in before calling the notification function
function notify() {
    const userId = document.getElementById('userId'); // Checks if the user id is present (logged in)
    const userStatus = document.getElementById('userStatus').innerHTML; // Checks if the user id is present (logged in)
    if (userId && userStatus === 'Online') { // If the user id is present, then calls the notification function
        if (!("Notification" in window)) { // Checks if the browser supports notifications
            alert("This browser does not support desktop notification");
        } else if (Notification.permission === "granted") { // Checks if the browser allows notifications
            notification(userId) // If allows notifications, then calls the notification function
        } else if (Notification.permission !== "denied") { // If it does not allow notifications
            console.log('Nofications are disabled!'); // Logs to the console
            Notification.requestPermission().then((permission) => { // Prompts for permission
                if (permission === "granted") { // If granted
                        notification(userId) // Calls the notification function
                }
            });
        }
    }
}


// Get the notification sound file
const newTicketNotificationSound = new Audio('/static/snd/new_ticket_notification.wav');

// Get a user's notifications, one at a time, then marks it as received.
// After that, displays the notification and flags it as received
function notification(userId) {
    $.ajax({
        type: 'GET', // Get notifications
        url: '/get-users-next-notification/' + userId.value,
        success: function (get_notification_response, xhr, textStatus) {
            // console.log('get-users-next-notification-status: ' + textStatus.status)
            if (textStatus.status === 200) { // If a notification was received
                var options = {
                    body: get_notification_response['content'],
                    icon: '/static/img/favicon.png',
                }

                    // Notifications.id,
                    // Notifications.type,
                    // Notifications.content,
                    // Notifications.url,

                    // Notifications.id,
                    // Notifications.content,
                    // Notifications.url,
                    // Notifications.read,

                $.ajax({
                    type: 'POST', // Set's the notification as received
                    url: '/flag-notification-as-sent/' + get_notification_response['id'],
                    success: function (flag_as_sent_response, xhr, textStatus) {
                        // console.log('flag-notification-as-sent-status: ' + textStatus.status)
                        if (textStatus.status === 200) {  // If a notification was successfully flagged as received
                            // Displays a notification
                            const notification = new Notification("Novo ticket atribuído!", options);



                            // Plays a sound. To play the sound is either necessary:
                            // 1. That the user interacts with the page, any interaction like changing the status or
                            //    loggin in. After reloading the page, it's necessary to perform an interaction again.
                            // 2. It's possible to get around the interaction thing by granting access to the page
                            //    to Sound instead of "automatic".
                            newTicketNotificationSound.play();
                            // Sets an onclick event to redirect the user to the ticket when clicking the notification
                            if (get_notification_response['url']) {
                                notification.onclick = function (event) {
                                    event.preventDefault();
                                    window.open(get_notification_response['url']);

                                }
                            }
                            // Sets the notification as received
                            $.ajax({
                                type: 'POST',
                                url: '/flag-notification-as-received/' + get_notification_response['id'],
                                success: function (flag_as_received_response, xhr, textStatus) {
                                    // console.log('flag-notification-as-received-status: ' + textStatus.status)
                                },
                                error: function (xhr, status, error) {
                                    console.log('Error flagging notification as received: ' + error);
                                }
                            });
                        }
                    },
                    error: function (xhr, status, error) {
                        console.log('Error flagging notification as sent: ' + error);
                    }
                });
            }
        },
        error: function (xhr, status, error) {
            console.log('Error getting new notifications: ' + error);
        }
    });
}

function flagNotificationAsRead(notification_id){

    const _notification_id = "notificationUnreadIcon-" + notification_id
    const isNotificationAlreadyRead = document.getElementById(_notification_id)

    if (isNotificationAlreadyRead) {
        $.ajax({
            type: 'POST',
            url: '/flag-notification-as-read/' + notification_id,
            success: function (flag_as_read_response, xhr, textStatus) {
                if (textStatus.status === 200) {
                    const unreadIcon = 'notificationUnreadIcon-' + notification_id;
                    const notification = document.getElementById(unreadIcon);
                    if (notification) {
                        notification.style.display = "none";
                    }
                }
            },
            error: function (xhr, status, error) {
                console.log('Error flagging notification as read: ' + error);
            }
        });

        updateNewNotificationCounter(1)

    }
}


function flagAllNotificationsAsRead(user_id){

    const unreadNotifications = document.getElementsByClassName("unread-notification-icon");
    let numberOfUnreadNotificationsElement = document.getElementById("newNotificationCounter");
    if (!numberOfUnreadNotificationsElement) {
        let numberOfUnreadNotificationsElement = document.getElementById("newNotificationCounterMoreThanTen")
    }

    const numberOfUnreadNotifications = numberOfUnreadNotificationsElement.textContent

    console.log('number: ' + numberOfUnreadNotifications)

    if (unreadNotifications) {
        $.ajax({
            type: 'POST',
            url: '/flag-all-notifications-as-read/' + user_id,
            success: function (flag_all_as_read_response, xhr, textStatus) {
                if (textStatus.status === 200) {
                    const unreadIcons = document.getElementsByClassName("unread-notification-icon");
                    for (let i = 0; i < unreadIcons.length; i++) {
                        unreadIcons[i].style.display = "none";
                    }
                }

                updateNewNotificationCounter(numberOfUnreadNotifications)

            },
            error: function (xhr, status, error) {
                console.log('Error flagging notification as read: ' + error);
            }
        });
    }
}

function updateNewNotificationCounter(numberOfReadNotifications){
    let newNotificationCounter = document.getElementById( "newNotificationCounter");
    let newNotificationCounterMoreThanTen = document.getElementById( "newNotificationCounterMoreThanTen");

    if (newNotificationCounter) {
        console.log(newNotificationCounter.textContent);
        newNotificationCounter.textContent = (newNotificationCounter.textContent - numberOfReadNotifications);
        console.log(newNotificationCounter.textContent);
    }

    if (newNotificationCounterMoreThanTen) {
        console.log(newNotificationCounterMoreThanTen.textContent);
        newNotificationCounterMoreThanTen.textContent = (newNotificationCounterMoreThanTen.textContent - numberOfReadNotifications);
        console.log(newNotificationCounterMoreThanTen.textContent);
        if (newNotificationCounterMoreThanTen.textContent <10 ) {
            newNotificationCounterMoreThanTen.classList.add("fix-alignment")
        }
    }
}


const notificationBell = document.getElementById('notificationBellContainer');
const notificationWrapper = document.getElementById('notificationPanelWrapper');
notificationBell.addEventListener('click', function() {
  const notificationWrapperStyle = window.getComputedStyle(notificationWrapper);
  if (notificationWrapperStyle.display === 'none') {
    notificationWrapper.style.display = 'flex';
  } else {
    notificationWrapper.style.display = 'none';
  }
});


document.addEventListener('click', function(event) {
  const isClickInside = notificationWrapper.contains(event.target) || notificationBell.contains(event.target);
  if (!isClickInside) {
    notificationWrapper.style.display = 'none';
  }
});


function addNewNotification(numberOfReadNotifications){
    let newNotificationCounter = document.getElementById( "newNotificationCounter");
    let newNotificationCounterMoreThanTen = document.getElementById( "newNotificationCounterMoreThanTen");

    if (newNotificationCounter) {
        console.log(newNotificationCounter.textContent);
        newNotificationCounter.textContent = (newNotificationCounter.textContent - numberOfReadNotifications);
        console.log(newNotificationCounter.textContent);
    }

    if (newNotificationCounterMoreThanTen) {
        console.log(newNotificationCounterMoreThanTen.textContent);
        newNotificationCounterMoreThanTen.textContent = (newNotificationCounterMoreThanTen.textContent - numberOfReadNotifications);
        console.log(newNotificationCounterMoreThanTen.textContent);
        if (newNotificationCounterMoreThanTen.textContent <10 ) {
            newNotificationCounterMoreThanTen.classList.add("fix-alignment")
        }
    }
}
