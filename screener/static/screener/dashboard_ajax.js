document.getElementById("runScan").onclick = function (e) {
  e.preventDefault();
  // Use updated selectors for the new builder:
  let rows = document.querySelectorAll("#filter-list .filter-row");
  let filters = [];
  rows.forEach((row) => {
    let children = row.querySelectorAll("input,select");
    filters.push({
      left: children[0]?.value || "",
      op: children[1]?.value || "",
      right: children[2]?.value || "",
      constant: children[3]?.value || "",
      logic: children[4]?.value || "",
    });
  });
  let payload = {
    filters: filters,
    market_cap: document.getElementById("marketCap").value,
    sector: document.getElementById("sector").value,
    volume: document.getElementById("volumeSlider").value,
    segment: document.getElementById("segmentDropdown").value,
  };
  fetch("/screener/ajax-scan/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(payload),
  })
    .then((resp) => resp.json())
    .then((data) => {
      let tbody = document.getElementById("resultsBody");
      tbody.innerHTML = "";
      if (data.results && data.results.length) {
        data.results.forEach((row, idx) => {
          tbody.innerHTML += `<tr>
            <td>${idx + 1}</td>
            <td>${row.symbol}</td>
            <td>${row.price}</td>
            <td>${row.change}</td>
            <td>${row.volume}</td>
            <td>${row.matched}</td>
            <td>${
              row.signal
                ? `<span class="badge bg-success">${row.signal}</span>`
                : ""
            }</td>
          </tr>`;
        });
      } else {
        tbody.innerHTML =
          '<tr><td colspan="7" class="text-center py-4 text-muted">No results.</td></tr>';
      }
    });
};

// CSRF utility, add if not already present:
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
