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
// On Tickets, when deselecting the groups of rules (locales, groups, organizations, etc.), this will deselect the options selected in that group
$(document).ready(function () {
    $("#recipient-users").click(function () {
        $(".js-group-option-container").removeClass("selected");
    });
    $("#recipient-groups").click(function () {
        $(".js-users-option-container").removeClass("selected");
    });

    $("#tickets-locales").click(function () {
        $(".js-locale-option-container").removeClass("selected");
    });
    $("#tickets-groups").click(function () {
        $(".js-group-option-container").removeClass("selected");
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
    const checkbox = document.getElementById("routeStatus");
    checkbox.checked = checkbox.checked !== true;
}


// This functions will show or hide the recipients acording to wich one was selected
const routeInfoAndRecipientsButton = document.getElementById("routeInfoAndRecipients")
const routeTicketLocalesButton = document.getElementById("routeTicketLocales")
const routeTicketGroupsButton = document.getElementById("routeTicketGroups")
const routeTicketFieldsButton = document.getElementById("routeTicketFields")
const routeTicketTagsButton = document.getElementById("routeTicketTags")


const routeInfoAndRecipientsContainer = document.getElementById("routeInfoAndRecipientsContainer");
const routeTicketsContainer = document.getElementById("routeTicketsContainer");


const routeTicketsLocales = document.getElementById("ticketLocalesListContainer");
const routeTicketsGroups = document.getElementById("ticketGroupsListContainer");
const routeTicketsFields = document.getElementById("ticketFormsAndFieldsContainer");
const routeTicketsTags = document.getElementById("ticketTagsListContainer");

routeInfoAndRecipientsButton.addEventListener("click", () => {
    routeInfoAndRecipientsContainer.removeAttribute("hidden");
    routeInfoAndRecipientsButton.classList.add("selected");

    routeTicketLocalesButton.classList.remove("selected");
    routeTicketGroupsButton.classList.remove("selected");
    routeTicketFieldsButton.classList.remove("selected");
    routeTicketTagsButton.classList.remove("selected");

    routeTicketsContainer.setAttribute("hidden", "hidden");
});


routeTicketLocalesButton.addEventListener("click", () => {
    routeTicketLocalesButton.classList.add("selected");
    routeInfoAndRecipientsButton.classList.remove("selected");
    routeTicketGroupsButton.classList.remove("selected");
    routeTicketFieldsButton.classList.remove("selected");
    routeTicketTagsButton.classList.remove("selected");

    routeInfoAndRecipientsContainer.setAttribute("hidden", "hidden");
    routeTicketsGroups.setAttribute("hidden", "hidden");
    routeTicketsFields.setAttribute("hidden", "hidden");
    routeTicketsTags.setAttribute("hidden", "hidden");

    routeTicketsContainer.removeAttribute("hidden");
    routeTicketsLocales.removeAttribute("hidden");
});


routeTicketGroupsButton.addEventListener("click", () => {
    routeTicketGroupsButton.classList.add("selected");
    routeInfoAndRecipientsButton.classList.remove("selected");
    routeTicketLocalesButton.classList.remove("selected");
    routeTicketFieldsButton.classList.remove("selected");
    routeTicketTagsButton.classList.remove("selected");

    routeInfoAndRecipientsContainer.setAttribute("hidden", "hidden");
    routeTicketsLocales.setAttribute("hidden", "hidden");
    routeTicketsFields.setAttribute("hidden", "hidden");
    routeTicketsTags.setAttribute("hidden", "hidden");

    routeTicketsContainer.removeAttribute("hidden");
    routeTicketsGroups.removeAttribute("hidden");
});


routeTicketTagsButton.addEventListener("click", () => {
    routeTicketTagsButton.classList.add("selected");
    routeInfoAndRecipientsButton.classList.remove("selected");
    routeTicketLocalesButton.classList.remove("selected");
    routeTicketGroupsButton.classList.remove("selected");
    routeTicketFieldsButton.classList.remove("selected");

    routeInfoAndRecipientsContainer.setAttribute("hidden", "hidden");
    routeTicketsLocales.setAttribute("hidden", "hidden");
    routeTicketsGroups.setAttribute("hidden", "hidden");
    routeTicketsFields.setAttribute("hidden", "hidden");

    routeTicketsContainer.removeAttribute("hidden");
    routeTicketsTags.removeAttribute("hidden");
});


routeTicketFieldsButton.addEventListener("click", () => {
    routeTicketFieldsButton.classList.add("selected");
    routeInfoAndRecipientsButton.classList.remove("selected");
    routeTicketLocalesButton.classList.remove("selected");
    routeTicketGroupsButton.classList.remove("selected");
    routeTicketTagsButton.classList.remove("selected");

    routeInfoAndRecipientsContainer.setAttribute("hidden", "hidden");
    routeTicketsLocales.setAttribute("hidden", "hidden");
    routeTicketsGroups.setAttribute("hidden", "hidden");
    routeTicketsTags.setAttribute("hidden", "hidden");

    routeTicketsContainer.removeAttribute("hidden");
    routeTicketsFields.removeAttribute("hidden");
});


var searchInput = document.getElementById("tagSearchInput");
var timeout;

searchInput.addEventListener("input", function () {
    clearTimeout(timeout);
    if (searchInput.value === "") {
        search("");
    } else {
        timeout = setTimeout(function () {
            search(searchInput.value);
        }, 500); // Wait 500ms before calling search
    }
});

function search() {
    var searchText = searchInput.value;
    var elements = document.getElementsByClassName("ticket-tag-option");
    for (let i = 0; i < elements.length; i++) {
        let element = elements[i];
        var parent = element.parentElement;
        if (searchText === "") {
            for (let i = 0; i < elements.length; i++) {
                parent.classList.remove("matched");
                parent.classList.remove("not-in-filter");
            }
        } else {
            if (element.innerText.toLowerCase().indexOf(searchText.toLowerCase()) > -1) {
                while (parent && !parent.classList.contains("js-tag-option-container")) {
                    parent = parent.parentElement;
                }
                if (parent) {
                    parent.classList.add("matched");
                    parent.classList.remove("not-in-filter");
                }
            } else {
                parent.classList.remove("matched");
                parent.classList.add("not-in-filter");
            }
        }
    }
}


const formInputField = document.querySelector(".chosen-form-value");
const formDropdown = document.querySelector(".form-values-list");
const formDropdownArray = [...document.getElementsByClassName("form-dropdown-menu-option")];
const ticketFieldsWrapper = document.getElementById("ticketFieldsWrapper")
formDropdown.classList.add("open");
let formValueArray = [];
formDropdownArray.forEach(item => {
    formValueArray.push(item.textContent);
});


formInputField.addEventListener("input", () => {
    formDropdown.classList.add("open");
    let inputValue = formInputField.value.toLowerCase();
    if (inputValue.length > 0) {
        for (let j = 0; j < formValueArray.length; j++) {

            if (!(inputValue.substring(0, inputValue.length) === formValueArray[j].substring(0, inputValue.length).toLowerCase())) {
                formDropdownArray[j].classList.add("closed");
            } else {
                formDropdownArray[j].classList.remove("closed");
            }
        }
    } else {
        for (let j = 0; j < formDropdownArray.length; j++) {
            formDropdownArray[j].classList.remove("closed");
        }
    }
});

formDropdownArray.forEach(item => {
    item.addEventListener("click", (evt) => {
        formInputField.value = item.textContent;
        formInputField.id = item.value
        // console.log(formInputField.id)
        const selectedFormInputField = formInputField.id
        // Get the fields of the selected form
        fetch("../forms/get-form-fields/" + selectedFormInputField)
            .then(response => response.json())
            .then(data => {
                // Removing the existing fields before displaying the fetched ones
                const parentElementRemove = document.getElementById("formFields");
                const elementsToRemove = document.getElementsByClassName("ticket-field-options");
                // Loop backwards to remove every field as it"s an HTMLCollection, therefore it"s length changes with
                // every removal, messing up the loop when it"s made from first to last
                for (let j = elementsToRemove.length - 1; j >= 0; j--) {
                    parentElementRemove.removeChild(elementsToRemove[j]);
                }

                // Iterate through the fields
                for (let i = 0; i < data.fields.length; i++) {
                    // TicketAssignmentLog the id and title properties of each field to the console
                    // console.log("ID: " + data.fields[i].id + ", Title: " + data.fields[i].title);
                    var parentElement = document.getElementById("formFields")
                    var newElement = document.createElement("li");
                    newElement.className = "field-dropdown-menu-option ticket-field-options dropdown-menu-option"
                    var textNode = document.createTextNode(data.fields[i].title);
                    newElement.appendChild(textNode);
                    parentElement.appendChild(newElement);
                }

            })
            .catch(error => {
                console.error(error);
            });
        formDropdownArray.forEach(dropdown => {
            dropdown.classList.add("closed");
        });

        ticketFieldsWrapper.style.display = "flex";

        let script = document.createElement("script");
        script.src = "/static/js/routing_by_routes_fields.js";
        document.body.appendChild(script); // or document.body.appendChild(script);

    });
})

formInputField.addEventListener("focus", () => {
    formInputField.placeholder = "Selecione";
    formDropdown.classList.add("open");
    formDropdownArray.forEach(dropdown => {
        dropdown.classList.remove("closed");
    });
});

formInputField.addEventListener("blur", () => {
    formInputField.placeholder = "Selecione";
    formDropdown.classList.remove("open");
});

document.addEventListener("click", (evt) => {
    const isDropdown = formDropdown.contains(evt.target);
    const isInput = formInputField.contains(evt.target);
    if (!isDropdown && !isInput) {
        formDropdown.classList.remove("open");
    }
});
