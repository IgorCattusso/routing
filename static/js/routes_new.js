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


// On Recipients, when selecting Users, this function it will deselect all Groups and vice-versa
// On Tickets, when deselecting the groups of rules (locales, groups, organizations, etc.), this will deselect the options selected in that group
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





// When selecting a type on Tickets, these functions will show that type options
const localesCheckbox = document.querySelector('#tickets-locales');
const localesContainer = document.querySelector('#localesListContainer');
localesCheckbox.addEventListener('change', function() {
  if (localesCheckbox.checked) {
    localesContainer.removeAttribute('hidden');
  } else {
    localesContainer.setAttribute('hidden', 'hidden');
  }
});

const groupsCheckbox = document.querySelector('#tickets-groups');
const groupsContainer = document.querySelector('#ticketsGroupsListContainer');
groupsCheckbox.addEventListener('change', function() {
  if (groupsCheckbox.checked) {
    groupsContainer.removeAttribute('hidden');
  } else {
    groupsContainer.setAttribute('hidden', 'hidden');
  }
});





// Select items on any list of options
const optionContainers = document.querySelectorAll('.option-container');
optionContainers.forEach((optionContainer) => {
  optionContainer.addEventListener('click', () => {
    optionContainer.classList.toggle('selected');
  });
});







function toggleCheckbox() {
  var checkbox = document.getElementById("routeStatus");
  checkbox.checked = checkbox.checked !== true;
}




