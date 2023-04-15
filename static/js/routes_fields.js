// This script begins with a timeout, because, god knows why, the fieldDropdownArray does not
// load the elements to the array if the script runs at once
setTimeout(function() {
    const fieldInputField = document.querySelector('.chosen-field-value');
    const fieldDropdown = document.querySelector('.field-values-list');
    const fieldDropdownArray = [...document.getElementsByClassName('field-dropdown-menu-option')];
    fieldDropdown.classList.add('open');
    let fieldValueArray = [];
    fieldDropdownArray.forEach(item => {
        fieldValueArray.push(item.textContent);
    });

    fieldInputField.addEventListener('input', () => {
        fieldDropdown.classList.add('open');
        let inputValue = fieldInputField.value.toLowerCase();
        if (inputValue.length > 0) {
            for (let i = 0; i < fieldValueArray.length; i++) {
                if (!(inputValue.substring(0, inputValue.length) === fieldValueArray[i].substring(0, inputValue.length).toLowerCase())) {
                    fieldDropdownArray[i].classList.add('closed');
                } else {
                    fieldDropdownArray[i].classList.remove('closed');
                }
            }
        } else {
            for (let j = 0; j < fieldDropdownArray.length; j++) {
                fieldDropdownArray[j].classList.remove('closed');
            }
        }
    });

    fieldDropdownArray.forEach(item => {
        item.addEventListener('click', (evt) => {
            fieldInputField.value = item.textContent;
            fieldInputField.id = item.value
            const selectedFormInputField = fieldInputField.id
            // Get the fields of the selected field
            fetch('../fields/get-form-fields/' + selectedFormInputField)
                .then(response => response.json())
                .then(data => {
                    // Removing the existing fields before displaying the fetched ones
                    const parentElementRemove = document.getElementById("fieldFields");
                    const elementsToRemove = document.getElementsByClassName("ticket-field-options");
                    // Loop backwards to remove every field as it's an HTMLCollection, therefore it's length changes with
                    // every removal, messing up the loop when it's made from first to last
                    for (let j = elementsToRemove.length - 1; j >= 0; j--) {
                        parentElementRemove.removeChild(elementsToRemove[j]);
                    }

                    // Iterate through the fields
                    for (let i = 0; i < data.fields.length; i++) {
                        var parentElement = document.getElementById('fieldFields')
                        var newElement = document.createElement("li");
                        newElement.className = "ticket-field-options"
                        var textNode = document.createTextNode(data.fields[i].title);
                        newElement.appendChild(textNode);
                        parentElement.appendChild(newElement);
                    }



                })
                .catch(error => {
                    console.error(error);
                });
            fieldDropdownArray.forEach(dropdown => {
                dropdown.classList.add('closed');
            });
        });
    })

    fieldInputField.addEventListener('focus', () => {
        fieldInputField.placeholder = 'Pesquisar';
        fieldDropdown.classList.add('open');
        fieldDropdownArray.forEach(dropdown => {
            dropdown.classList.remove('closed');
        });
    });

    fieldInputField.addEventListener('blur', () => {
        fieldInputField.placeholder = 'Selecione';
        fieldDropdown.classList.remove('open');
    });

    document.addEventListener('click', (evt) => {
        const isDropdown = fieldDropdown.contains(evt.target);
        const isInput = fieldInputField.contains(evt.target);
        if (!isDropdown && !isInput) {
            fieldDropdown.classList.remove('open');
        }
    });

}, 250);
