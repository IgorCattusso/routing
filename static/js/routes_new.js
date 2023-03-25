const userList = document.getElementById("usersListContainer");
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





// Get the checkbox and the container
const localesCheckbox = document.querySelector('#tickets-locales');
const localesContainer = document.querySelector('#localesListContainer');
// Add an event listener to the checkbox
localesCheckbox.addEventListener('change', function() {
  // If the checkbox is checked, show the container; otherwise, hide it
  if (localesCheckbox.checked) {
    localesContainer.removeAttribute('hidden');
  } else {
    localesContainer.setAttribute('hidden', 'hidden');
  }
});




// Get the checkbox and the container
const groupsCheckbox = document.querySelector('#tickets-groups');
const groupsContainer = document.querySelector('#ticketsGroupsListContainer');
// Add an event listener to the checkbox
groupsCheckbox.addEventListener('change', function() {
  // If the checkbox is checked, show the container; otherwise, hide it
  if (groupsCheckbox.checked) {
    groupsContainer.removeAttribute('hidden');
  } else {
    groupsContainer.setAttribute('hidden', 'hidden');
  }
});





$(document).ready(function() {
    $('#status').hide();
    var slider = $('<label class="switch"><input class="form-item-field-status" id="status-slider" name="status-slider" type="checkbox" value="y"><span class="slider"></span></label>');
    $('#status').after(slider);
});





const optionContainers = document.querySelectorAll('.option-container');
optionContainers.forEach((optionContainer) => {
  optionContainer.addEventListener('click', () => {
    optionContainer.classList.toggle('selected');
  });
});





// Deselect GROUPS when USER is selected as the recipient and deselect USERS when GROUP is selected as recipient.
$(document).ready(function() {
  $('#recipient-users').click(function() {
    $('.js-group-option-container').removeClass('selected');
  });

  $('#recipient-groups').click(function() {
    $('.js-user-option-container').removeClass('selected');
  });

  $('#tickets-locales').click(function() {
    $('.js-locale-option-container').removeClass('selected');
  });

  $('#tickets-groups').click(function() {
    $('.js-group-option-container').removeClass('selected');
  });

});
