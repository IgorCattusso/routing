// This functions will show or hide the recipients acording to wich one was selected
const userList = document.getElementById("recipientsUsersListContainer");
const groupList = document.getElementById("recipientsGroupsListContainer");
const userRadio = document.getElementById("recipient-users");
const groupRadio = document.getElementById("recipient-groups");

userRadio.addEventListener("click", () => {
    userList.removeAttribute("hidden");
    userList.setAttribute("selected", "selected");
    groupList.setAttribute("hidden", "hidden");
    groupList.removeAttribute("selected");
});
groupRadio.addEventListener("click", () => {
    groupList.removeAttribute("hidden");
    groupList.setAttribute("selected", "selected");
    userList.setAttribute("hidden", "hidden");
    userList.removeAttribute("selected");
});


// On Recipients, when selecting User, this function it will deselect all Groups and vice-versa
$(document).ready(function () {
    $("#recipient-users").click(function () {
        $(".js-group-option-container").removeClass("selected");
    });
    $("#recipient-groups").click(function () {
        $(".js-user-option-container").removeClass("selected");
    });
});




// Select items on any list of options
const optionContainers = document.querySelectorAll(".option-container");
optionContainers.forEach((optionContainer) => {
    optionContainer.addEventListener("click", () => {
        optionContainer.classList.toggle("selected");
    });
});

function toggleCheckbox() {
    const checkbox = document.getElementById("viewStatus");
    checkbox.checked = checkbox.checked !== true;
}





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



const viewInputField = document.querySelector(".zendesk-views-id-chosen-value");
const viewDropdown = document.querySelector(".view-values-list");
const viewDropdownArray = [...document.getElementsByClassName("view-dropdown-menu-option")];
const viewFieldsWrapper = document.getElementById("zendeskViewsWrapper")

let viewValueArray = [];
viewDropdownArray.forEach(item => {
    viewValueArray.push(item.textContent);
});


viewInputField.addEventListener("input", () => {
    viewDropdown.classList.add("open");
    let inputValue = viewInputField.value.toLowerCase();
    if (inputValue.length > 0) {
        for (let j = 0; j < viewValueArray.length; j++) {
            if (!(inputValue.substring(0, inputValue.length) === viewValueArray[j].substring(0, inputValue.length).toLowerCase())) {
                viewDropdownArray[j].classList.add("closed");
            } else {
                viewDropdownArray[j].classList.remove("closed");
            }
        }
    } else {
        for (let j = 0; j < viewDropdownArray.length; j++) {
            viewDropdownArray[j].classList.remove("closed");
        }
    }
});

viewDropdownArray.forEach(item => {
    item.addEventListener("click", (evt) => {
        viewInputField.value = item.textContent;
        viewInputField.id = item.value
        viewDropdownArray.forEach(dropdown => {
            dropdown.classList.add("closed");
        });
        viewFieldsWrapper.style.display = "flex";
    });
})

viewInputField.addEventListener("focus", () => {
    viewInputField.placeholder = "Selecione";
    viewDropdown.classList.add("open");
    viewDropdownArray.forEach(dropdown => {
        dropdown.classList.remove("closed");
    });
});

viewInputField.addEventListener("blur", () => {
    viewInputField.placeholder = "Selecione";
    viewDropdown.classList.remove("open");
});

document.addEventListener("click", (evt) => {
    const isDropdown = viewDropdown.contains(evt.target);
    const isInput = viewInputField.contains(evt.target);
    if (!isDropdown && !isInput) {
        viewDropdown.classList.remove("open");
    }
});