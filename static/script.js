function filterTag(tag, btn) {

    let rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {

        let select = row.querySelector(".tag-select");
        let value = select ? select.value.trim() : "";

        if (tag === "ALL") {
            row.style.display = "";
        }
        else if (tag === "EMPTY") {
            row.style.display = (value === "") ? "" : "none";
        }
        else {
            row.style.display = (value === tag) ? "" : "none";
        }
    });

    document.querySelectorAll(".tag-bar button").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
}


// BO SAVE
document.querySelectorAll(".bo-input").forEach(input => {
    input.addEventListener("change", function () {

        fetch("/update", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                symbol: this.dataset.symbol,
                bo_level: this.value
            })
        });
    });
});


// TAG SAVE
document.querySelectorAll(".tag-select").forEach(select => {
    select.addEventListener("change", function () {

        fetch("/update", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                symbol: this.dataset.symbol,
                tag: this.value
            })
        });
    });
});

// 🔍 SEARCH FUNCTION
document.getElementById("searchBox").addEventListener("keyup", function () {

    let value = this.value.toUpperCase();
    let rows = document.querySelectorAll("tbody tr");

    rows.forEach(row => {
        let symbol = row.children[1].innerText.toUpperCase();

        if (symbol.includes(value)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
});

let sortDirection = {};

function sortTable(colIndex) {

    let table = document.querySelector("table tbody");
    let rows = Array.from(table.rows);

    let asc = !sortDirection[colIndex];
    sortDirection[colIndex] = asc;

    // 🔥 RESET ALL ICONS
    document.querySelectorAll(".sort-icon").forEach(icon => {
        icon.innerText = "⬍";
    });

    rows.sort((a, b) => {

        let A = a.cells[colIndex].innerText.replace('%','');
        let B = b.cells[colIndex].innerText.replace('%','');

        let numA = parseFloat(A);
        let numB = parseFloat(B);

        if (!isNaN(numA) && !isNaN(numB)) {
            return asc ? numA - numB : numB - numA;
        }

        return asc ? A.localeCompare(B) : B.localeCompare(A);
    });

    rows.forEach(row => table.appendChild(row));

    // 🔥 UPDATE CURRENT COLUMN ICON
    let header = document.querySelectorAll("thead th")[colIndex];
    let icon = header.querySelector(".sort-icon");

    if (icon) {
        icon.innerText = asc ? "🔼" : "🔽";
    }
}