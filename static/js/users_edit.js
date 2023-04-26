function toggleCheckbox() {
    const checkbox = document.getElementById('userStatus');
    checkbox.checked = checkbox.checked !== true;
}




const userInputField = document.querySelector('.zendesk-users-id-chosen-value');
const userDropdown = document.querySelector('.user-values-list');
const userDropdownArray = [...document.getElementsByClassName('user-dropdown-menu-option')];
const zendeskUsersFieldsWrapper = document.getElementById('zendeskUsersWrapper')

let userValueArray = [];
userDropdownArray.forEach(item => {
    userValueArray.push(item.textContent);
});



userInputField.addEventListener('input', () => {
    userDropdown.classList.add('open');
    let inputValue = userInputField.value.toLowerCase();
    if (inputValue.length > 0) {
        for (let j = 0; j < userValueArray.length; j++) {

            if (!(inputValue.substring(0, inputValue.length) === userValueArray[j].substring(0, inputValue.length).toLowerCase())) {
                userDropdownArray[j].classList.add('closed');
            } else {
                userDropdownArray[j].classList.remove('closed');
            }
        }
    } else {
        for (let j = 0; j < userDropdownArray.length; j++) {
            userDropdownArray[j].classList.remove('closed');
        }
    }
});

userDropdownArray.forEach(item => {
    item.addEventListener('click', (evt) => {
        userInputField.value = item.textContent;
        userInputField.id = item.value
        userDropdownArray.forEach(dropdown => {
            dropdown.classList.add('closed');
        });

    zendeskUsersFieldsWrapper.style.display = "flex";

    });
})

userInputField.addEventListener('focus', () => {
    userInputField.placeholder = 'Selecione';
    userDropdown.classList.add('open');
    userDropdownArray.forEach(dropdown => {
        dropdown.classList.remove('closed');
    });
});

userInputField.addEventListener('blur', () => {
    userInputField.placeholder = 'Selecione';
    userDropdown.classList.remove('open');
});

document.addEventListener('click', (evt) => {
    const isDropdown = userDropdown.contains(evt.target);
    const isInput = userInputField.contains(evt.target);
    if (!isDropdown && !isInput) {
        userDropdown.classList.remove('open');
    }
});




const scheduleInputField = document.querySelector('.zendesk-schedules-id-chosen-value');
const scheduleDropdown = document.querySelector('.schedule-values-list');
const scheduleDropdownArray = [...document.getElementsByClassName('schedule-dropdown-menu-option')];
const zendeskschedulesFieldsWrapper = document.getElementById('zendeskSchedulesWrapper')

let scheduleValueArray = [];
scheduleDropdownArray.forEach(item => {
    scheduleValueArray.push(item.textContent);
});



scheduleInputField.addEventListener('input', () => {
    scheduleDropdown.classList.add('open');
    let inputValue = scheduleInputField.value.toLowerCase();
    if (inputValue.length > 0) {
        for (let j = 0; j < scheduleValueArray.length; j++) {

            if (!(inputValue.substring(0, inputValue.length) === scheduleValueArray[j].substring(0, inputValue.length).toLowerCase())) {
                scheduleDropdownArray[j].classList.add('closed');
            } else {
                scheduleDropdownArray[j].classList.remove('closed');
            }
        }
    } else {
        for (let j = 0; j < scheduleDropdownArray.length; j++) {
            scheduleDropdownArray[j].classList.remove('closed');
        }
    }
});

scheduleDropdownArray.forEach(item => {
    item.addEventListener('click', (evt) => {
        scheduleInputField.value = item.textContent;
        scheduleInputField.id = item.value
        scheduleDropdownArray.forEach(dropdown => {
            dropdown.classList.add('closed');
        });

    zendeskschedulesFieldsWrapper.style.display = "flex";

    });
})

scheduleInputField.addEventListener('focus', () => {
    scheduleInputField.placeholder = 'Selecione';
    scheduleDropdown.classList.add('open');
    scheduleDropdownArray.forEach(dropdown => {
        dropdown.classList.remove('closed');
    });
});

scheduleInputField.addEventListener('blur', () => {
    scheduleInputField.placeholder = 'Selecione';
    scheduleDropdown.classList.remove('open');
});

document.addEventListener('click', (evt) => {
    const isDropdown = scheduleDropdown.contains(evt.target);
    const isInput = scheduleInputField.contains(evt.target);
    if (!isDropdown && !isInput) {
        scheduleDropdown.classList.remove('open');
    }
});




