const button = document.getElementById("seeUser");
button.addEventListener("click", function() {
  // get selected row IDs
  const table = document.getElementById("groupsTable");
  const rows = table.getElementsByTagName("tr");
  const selectedRowIDs = [];
  for (let i = 0; i < rows.length; i++) {
    if (rows[i].classList.contains("selected")) {
      selectedRowIDs.push(rows[i].getAttribute("data-id"));
    }
  }
  // redirect to new page with row IDs in URL if only one row is selected
  if (selectedRowIDs.length === 1) {
    window.location.href = `/users-in-group/${selectedRowIDs[0]}`;
  } else {
    // disable button if more than one row is selected
    button.setAttribute("disabled", true);
  }
});

const table = document.getElementById("groupsTable");
const rows = table.getElementsByTagName("tr");
for (let i = 0; i < rows.length; i++) {
  rows[i].addEventListener("click", function() {
    // toggle "selected" class on clicked row
    this.classList.toggle("selected");
    // enable/disable button based on selected rows
    const selectedRows = table.querySelectorAll(".selected");
    if (selectedRows.length === 1) {
      button.removeAttribute("disabled");
    } else {
      button.setAttribute("disabled", true);
    }
  });
}
