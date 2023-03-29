// This functions will show or hide the recipients acording to wich one was selected
const userList = document.getElementById('recipientsUsersListContainer');
const groupList = document.getElementById('recipientsGroupsListContainer');
const userRadio = document.getElementById('recipient-users');
const groupRadio = document.getElementById('recipient-groups');

userRadio.addEventListener('click', () => {
  userList.removeAttribute('hidden');
  userList.setAttribute('selected', 'selected');
  groupList.setAttribute('hidden', 'hidden');
  groupList.removeAttribute('selected');
});
groupRadio.addEventListener('click', () => {
  groupList.removeAttribute('hidden');
  groupList.setAttribute('selected', 'selected');
  userList.setAttribute('hidden', 'hidden');
  userList.removeAttribute('selected');
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



// Select items on any list of options
const optionContainers = document.querySelectorAll('.option-container');
optionContainers.forEach((optionContainer) => {
  optionContainer.addEventListener('click', () => {
    optionContainer.classList.toggle('selected');
  });
});


function toggleCheckbox() {
  const checkbox = document.getElementById('routeStatus');
  checkbox.checked = checkbox.checked !== true;
}





// This functions will show or hide the recipients acording to wich one was selected
const routeInfoAndRecipientsButton = document.getElementById('routeInfoAndRecipients')
const routeTicketLocalesButton = document.getElementById('routeTicketLocales')
const routeTicketGroupsButton = document.getElementById('routeTicketGroups')


const routeInfoAndRecipientsContainer = document.getElementById('routeInfoAndRecipientsContainer');
const routeTicketsContainer = document.getElementById('routeTicketsContainer');


const routeTicketsLocales = document.getElementById('ticketLocalesListContainer');
const routeTicketsGroups = document.getElementById('ticketGroupsListContainer');

routeInfoAndRecipientsButton.addEventListener('click', () => {
  routeInfoAndRecipientsContainer.removeAttribute('hidden');
  routeInfoAndRecipientsButton.classList.add('selected');

  routeTicketLocalesButton.classList.remove('selected');
  routeTicketGroupsButton.classList.remove('selected');

  routeTicketsContainer.setAttribute('hidden', 'hidden');
});


routeTicketLocalesButton.addEventListener('click', () => {
  routeTicketLocalesButton.classList.add('selected');
  routeInfoAndRecipientsButton.classList.remove('selected');
  routeTicketGroupsButton.classList.remove('selected');

  routeInfoAndRecipientsContainer.setAttribute('hidden', 'hidden');
  routeTicketsGroups.setAttribute('hidden', 'hidden');

  routeTicketsContainer.removeAttribute('hidden');
  routeTicketsLocales.removeAttribute('hidden');
});


routeTicketGroupsButton.addEventListener('click', () => {
  routeTicketGroupsButton.classList.add('selected');
  routeInfoAndRecipientsButton.classList.remove('selected');
  routeTicketLocalesButton.classList.remove('selected');

  routeInfoAndRecipientsContainer.setAttribute('hidden', 'hidden');
  routeTicketsLocales.setAttribute('hidden', 'hidden');

  routeTicketsContainer.removeAttribute('hidden');
  routeTicketsGroups.removeAttribute('hidden');
});