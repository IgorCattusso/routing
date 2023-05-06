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
const rowContainers = document.querySelectorAll('.row-container');

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
