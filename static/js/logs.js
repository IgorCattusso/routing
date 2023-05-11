function formatJSON() {
    const jsonRows = document.getElementsByClassName("json-row");
    Array.prototype.forEach.call(jsonRows, function (jsonRow) {
      const jsonString = jsonRow.innerHTML.trim();
      const jsonObject = JSON.parse(jsonString.replace(/'/g, "\""));
      const formattedJsonString = JSON.stringify(jsonObject, null, 4);
      jsonRow.innerHTML = "<pre>" + formattedJsonString + "</pre>";
    });
}

formatJSON();

// Get all elements with the class name 'row-container'
let rowContainers = document.querySelectorAll('.row-container');

// Add an event listener to each 'row-container' element
rowContainers.forEach(rowContainer => {
  rowContainer.addEventListener('click', () => {
    // Get the corresponding 'std-td-json-row' element for the clicked 'row-container'
    const jsonRow = rowContainer.querySelector('.std-td-json-row');

    jsonRow.classList.toggle('show');

    // Toggle the display value of the 'std-td-json-row' element
    if (jsonRow.style.display === 'none') {
      jsonRow.style.display = 'block';
    } else {
      jsonRow.style.display = 'none';
    }
  });
});

const userInputField = document.querySelector('.chosen-form-value');
const userDropdown = document.querySelector('.users-values-list');
const userDropdownArray = [...document.getElementsByClassName('user-dropdown-list-option')];
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
        userInputField.id = item.id

        userDropdownArray.forEach(dropdown => {
            dropdown.classList.add('closed');
        });

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