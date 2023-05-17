const ticketId = document.getElementById("ticketIdInput");
const userId = document.getElementById("userInput");
const initialDate = document.getElementById("createdAtInitial");
const finalDate = document.getElementById("createdAtFinal");
const searchButton = document.getElementById("search");

searchButton.addEventListener("click", async () => {

    const json = {
        zendesk_ticket_id: parseInt(ticketId.value),
        users_id: parseInt(userId.id),
        initial_date: initialDate.value,
        final_date: finalDate.value,
    };

    if (isNaN(json["zendesk_ticket_id"]) || json["zendesk_ticket_id"] === 0) {
        json["zendesk_ticket_id"] = null
    }
    if (isNaN(json["users_id"]) || json["users_id"] === 0) {
        json["users_id"] = null
    }
    if (json["initial_date"] === "") {
        json["initial_date"] = null
    }
    if (json["final_date"] === "") {
        json["final_date"] = null
    }

    $(".row-container").remove();

    fetch("/search-logs", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(json)
    })
        .then(response => response.json())
        .then(data => {
            for (let i = 0; i < data.length; i++) {

                const containerTable = document.getElementById("tbody");

                const tableRowContainer = document.createElement("div");
                tableRowContainer.setAttribute("class", "row-container");
                tableRowContainer.setAttribute("id", data[i]["log_id"]);

                containerTable.append(tableRowContainer);

                const tableRow = document.createElement("div");
                tableRow.setAttribute("class", "std-tr");
                tableRow.setAttribute("data-id", data[i]["log_id"]);
                tableRowContainer.append(tableRow);

                const tableColumnId = document.createElement("span");
                tableColumnId.setAttribute("class", "std-td std-td-id");
                tableColumnId.innerText = data[i]["log_id"];
                tableRow.append(tableColumnId);

                const tableColumnTicketId = document.createElement("span");
                tableColumnTicketId.setAttribute("class", "std-td std-td-ticket-id");
                tableColumnTicketId.innerText = data[i]["ticket_id"];
                tableRow.append(tableColumnTicketId);

                const tableColumnUserName = document.createElement("span");
                tableColumnUserName.setAttribute("class", "std-td std-td-users-name");
                tableColumnUserName.innerText = data[i]["user_name"];
                tableRow.append(tableColumnUserName);

                const tableColumnShortMessage = document.createElement("span");
                tableColumnShortMessage.setAttribute("class", "std-td std-td-short-message");
                tableColumnShortMessage.innerText = data[i]["short_message"];
                tableRow.append(tableColumnShortMessage);

                const tableColumnCreatedAt = document.createElement("span");
                tableColumnCreatedAt.setAttribute("class", "std-td std-td-created-at");
                tableColumnCreatedAt.innerText = data[i]["created_at"];
                tableRow.append(tableColumnCreatedAt);

                const tableColumnArrowSvg = document.createElement("object");
                tableColumnArrowSvg.setAttribute("class", "std-td std-td-arrow");
                tableColumnArrowSvg.setAttribute("data", "/static/svg/arrow-down.svg");
                tableColumnArrowSvg.setAttribute("type", "image/svg+xml");
                tableRow.append(tableColumnArrowSvg);

                const tableFullMessageContainer = document.createElement("div")
                tableFullMessageContainer.setAttribute("class", "full-message-container")

                tableRowContainer.append(tableFullMessageContainer)

                const tableColumnFullMessage = document.createElement("span");
                tableColumnFullMessage.setAttribute("class", "std-td std-td-json-row json-row");
                tableColumnFullMessage.style.display = "none";
                tableColumnFullMessage.innerText = data[i]["full_message"];

                tableFullMessageContainer.append(tableColumnFullMessage)
            }
        })
        .catch(error => {
            console.error("Error:", error);
        });
    await sleep(500);
    await logsSearchFormatJSON()
    await sleep(500);
});

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function logsSearchFormatJSON() {
    function formatJSON2() {
        const jsonRows2 = document.getElementsByClassName("json-row");
        Array.prototype.forEach.call(jsonRows2, function (jsonRow2) {
            const jsonString2 = jsonRow2.innerHTML.trim();
            const jsonObject2 = JSON.parse(jsonString2.replace(/"/g, "\""));
            const formattedJsonString2 = JSON.stringify(jsonObject2, null, 4);
            jsonRow2.innerHTML = "<pre>" + formattedJsonString2 + "</pre>";
        });
    }

    await sleep(50);
    formatJSON2();
    await sleep(50);

    let rowContainers2 = document.querySelectorAll(".row-container");
// Add an event listener to each "row-container" element
    rowContainers2.forEach(rowContainer2 => {
        rowContainer2.addEventListener("click", () => {
            // Get the corresponding "std-td-json-row" element for the clicked "row-container"
            const jsonRow2 = rowContainer2.querySelector(".std-td-json-row");

            jsonRow2.classList.toggle("show");

            // Toggle the display value of the "std-td-json-row" element
            const jsonRowComputedStyle = window.getComputedStyle(jsonRow2);
            if (jsonRowComputedStyle.display === "none") {
                jsonRow2.style.display = "block";
                jsonRow2.style.height = "100%";
            } else {
                jsonRow2.style.display = "none";
            }
        });
    });
    await sleep(50);
}


const clearFiltersButton = document.getElementById("clearFilters");
clearFiltersButton.addEventListener("click", () => {
    ticketId.value = null
    ticketId.innerText = null

    userId.id = "userInput"
    userId.innerText = null
    userId.value = null

    initialDate.value = null
    initialDate.innerText = null

    finalDate.value = null
    finalDate.innerText = null
})

// Remove the content of the ID field when the users erases the field manually
userId.addEventListener("input", function () {
    if (this.value === "") {
        this.removeAttribute("id");
    }
});
