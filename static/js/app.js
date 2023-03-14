const button = document.getElementById("edit");
button.addEventListener("click", function() {
  // get selected row IDs
  const table = document.getElementById("contentTable");
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


const table = document.getElementById("contentTable");
const header = table.querySelector("thead");
const rows = table.querySelectorAll("tbody tr");
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


// Add click event listener to each table header
header.querySelectorAll("th").forEach((th, i) => {
  th.addEventListener("click", () => {
    // Sort table rows based on the clicked header
    const sortedRows = Array.from(rows);
    const order = (th.dataset.order || "asc") === "asc" ? "desc" : "asc";
    const sortFunction = getSortFunction(i, order);
    sortedRows.sort(sortFunction);

    // Reorder the table rows
    const tbody = table.querySelector("tbody");
    tbody.innerHTML = "";
    sortedRows.forEach((row) => {
      tbody.appendChild(row);
    });

    // Update the header to reflect the sort order
    header.querySelectorAll("th").forEach((th2) => {
      th2.dataset.order = "";
    });
    th.dataset.order = order;
  });
});


// Helper function to get the sort function for a specific column and order
function getSortFunction(column, order) {
  return (a, b) => {
    const aVal = a.querySelectorAll("td")[column].textContent.trim();
    const bVal = b.querySelectorAll("td")[column].textContent.trim();
    if (aVal === bVal) {
      return 0;
    }
    if (order === "asc") {
      return aVal < bVal ? -1 : 1;
    } else {
      return aVal > bVal ? -1 : 1;
    }
  };
}


function toggleOptions() {
  var options = document.getElementById("options");
  if (options.style.display === "none") {
    options.style.display = "block";
  } else {
    options.style.display = "none";
  }
}
