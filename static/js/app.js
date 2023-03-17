//-----------------------//
// Select rows of tables //
//-----------------------//
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


//-------------------------//
// Pop-up the Options menu //
//-------------------------//
function toggleOptions() {
  var options = document.getElementById("options-list");
  if (options.style.display === "none") {
    options.style.display = "block";
  } else {
    options.style.display = "none";
  }
}


//--------------------------//
// Accordion menu navigator //
//------------------------- //
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
      $el.find('.submenu-Items').not($next).slideUp().parent().removeClass('open');
    }
  }
  var accordion = new Accordion($('.accordion-menu'), false);
})


//--------------------//
// Sort table content //
//--------------------//
var originalRows = $('#tbody .std-tr').toArray();
$('.std-th').on('click', function() {
  var column = $(this).index();
  var $tbody = $('#tbody');
  var $rows = originalRows.slice(0);
  $rows.sort(function(a, b) {
    var aVal = $(a).find('.std-td').eq(column).text();
    var bVal = $(b).find('.std-td').eq(column).text();
    if (column === -1 || column === 3) {
      return parseInt(aVal) - parseInt(bVal);
    } else {
      return aVal.localeCompare(bVal);
    }
  });
  if ($(this).hasClass('asc')) {
    $rows.reverse();
    $(this).removeClass('asc').addClass('desc');
  } else {
    $(this).removeClass('desc').addClass('asc');
  }
  $tbody.empty().append($rows);
});

