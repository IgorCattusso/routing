//---------------------------------//
// See users in the selected group //
//---------------------------------//
const button = document.getElementById("seeUsers");
button.addEventListener("click", function() {
  const table = document.getElementById("std-table");
  const rows = table.getElementsByClassName("std-tr");
  const selectedRowIDs = [];
  for (let i = 0; i < rows.length; i++) {
    if (rows[i].classList.contains("selected")) {
      selectedRowIDs.push(rows[i].getAttribute("data-id"));
    }
  }
  if (selectedRowIDs.length === 1) {
    window.location.href = `/users-in-group/${selectedRowIDs[0]}`;
  } else {
    button.setAttribute("disabled", true);
  }
});


document.addEventListener('DOMContentLoaded', function() {
  const updateGroups = document.getElementById('updateGroups');
  updateGroups.addEventListener('click', function() {
    window.location.href = '/get-groups';
  });

  const updateGroupMemberships = document.getElementById('updateGroupMemberships');
  updateGroupMemberships.addEventListener('click', function() {
    window.location.href = '/get-group-memberships';
  });
});