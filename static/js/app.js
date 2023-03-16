const button = document.getElementById("edit");
button.addEventListener("click", function() {
  // get selected row IDs
  const table = document.getElementById("std-table");
  const rows = table.getElementsByClassName("std-tr");
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


const table = document.getElementById("std-table");
const header = document.getElementById("thead");
const rows = document.getElementsByClassName("std-tr");
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


function toggleOptions() {
  var options = document.getElementById("options-list");
  if (options.style.display === "none") {
    options.style.display = "block";
  } else {
    options.style.display = "none";
  }
}


$(function() {
  var Accordion = function(el, multiple) {
    this.el = el || {};
    // more then one submenu open?
    this.multiple = multiple || false;

    var dropdownlink = this.el.find('.dropdown-link');
    dropdownlink.on('click',
                    { el: this.el, multiple: this.multiple },
                    this.dropdown);
  };

  Accordion.prototype.dropdown = function(e) {
    var $el = e.data.el,
        $this = $(this),
        //this is the ul.submenuItems
        $next = $this.next();

    $next.slideToggle();
    $this.parent().toggleClass('open');

    if(!e.data.multiple) {
      //show only one menu at the same time
      $el.find('.submenu-Items').not($next).slideUp().parent().removeClass('open');
    }
  }
  var accordion = new Accordion($('.accordion-menu'), false);
})


// Store the original rows in an array
var originalRows = $('#tbody .std-tr').toArray();

// Bind a click event handler to all .std-th elements
$('.std-th').on('click', function() {
  var column = $(this).index();
  var $tbody = $('#tbody');
  var $rows = originalRows.slice(0); // Make a copy of the original rows

  // Sort the rows based on the clicked column
  $rows.sort(function(a, b) {
    var aVal = $(a).find('.std-td').eq(column).text();
    var bVal = $(b).find('.std-td').eq(column).text();
    if (column === -1 || column === 3) {
      return parseInt(aVal) - parseInt(bVal);
    } else {
      return aVal.localeCompare(bVal);
    }
  });

  // Reverse the order of the rows if the column was already sorted in ascending order
  if ($(this).hasClass('asc')) {
    $rows.reverse();
    $(this).removeClass('asc').addClass('desc');
  } else {
    $(this).removeClass('desc').addClass('asc');
  }

  // Replace the contents of the tbody with the sorted rows
  $tbody.empty().append($rows);
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
