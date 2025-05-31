// let allIndicators = [];
// let filterCount = 0;
// let activeInput = null;

// // Fetch indicators on page load
// fetch("/screener/api/indicators/")
//   .then((resp) => resp.json())
//   .then((data) => {
//     allIndicators = [
//       { value: "open", label: "Open" },
//       { value: "high", label: "High" },
//       { value: "low", label: "Low" },
//       { value: "close", label: "Close" },
//       { value: "volume", label: "Volume" },
//       ...data.indicators,
//     ];
//     renderIndicators("");
//   });

// function renderIndicators(filter = "") {
//   const list = document.getElementById("indicatorList");
//   list.innerHTML = "";
//   // Add a value entry option (for right side)
//   if (activeInput && activeInput.classList.contains("right-indicator")) {
//     const valueLi = document.createElement("li");
//     valueLi.className = "list-group-item list-group-item-action";
//     valueLi.style.cursor = "pointer";
//     valueLi.textContent = "Enter Value…";
//     valueLi.onclick = () => selectValueEntry();
//     list.appendChild(valueLi);
//   }
//   allIndicators
//     .filter((i) => i.label.toLowerCase().includes(filter.toLowerCase()))
//     .forEach((indicator) => {
//       const li = document.createElement("li");
//       li.className = "list-group-item list-group-item-action";
//       li.style.cursor = "pointer";
//       li.textContent = indicator.label;
//       li.onclick = () => selectIndicator(indicator.value);
//       list.appendChild(li);
//     });
// }

// // Add a modal for indicator parameters
// function showIndicatorParamsModal(indicatorValue, onSubmit) {
//   fetch(`/screener/api/indicator_params/?fn=${indicatorValue}`)
//     .then((resp) => resp.json())
//     .then((data) => {
//       let formHtml = "";
//       if (data.params && data.params.length) {
//         data.params.forEach((param) => {
//           if (param.type === "series") {
//             formHtml += `<label>${param.name}</label>
//               <select class="form-select mb-2" name="${param.name}">
//                 <option value="close">Close</option>
//                 <option value="open">Open</option>
//                 <option value="high">High</option>
//                 <option value="low">Low</option>
//                 <option value="volume">Volume</option>
//               </select>`;
//           } else {
//             formHtml += `<label>${param.name}</label>
//               <input class="form-control mb-2" name="${
//                 param.name
//               }" type="number" value="${
//               param.default !== null ? param.default : ""
//             }" />`;
//           }
//         });
//       }
//       const paramModal = document.createElement("div");
//       paramModal.className = "modal fade";
//       paramModal.id = "indicatorParamsModal";
//       paramModal.tabIndex = -1;
//       paramModal.innerHTML = `
//         <div class="modal-dialog">
//           <div class="modal-content">
//             <div class="modal-header">
//               <h5 class="modal-title">Indicator Parameters</h5>
//               <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
//             </div>
//             <form id="paramForm">
//               <div class="modal-body">
//                 ${formHtml}
//               </div>
//               <div class="modal-footer">
//                 <button type="submit" class="btn btn-primary">OK</button>
//               </div>
//             </form>
//           </div>
//         </div>
//       `;
//       document.body.appendChild(paramModal);
//       const bsModal = new bootstrap.Modal(paramModal);
//       bsModal.show();

//       paramModal.querySelector("#paramForm").onsubmit = function (e) {
//         e.preventDefault();
//         const formData = new FormData(this);
//         const paramStr = Array.from(formData.entries())
//           .map(([k, v]) => v)
//           .join(", ");
//         onSubmit(`${indicatorValue}(${paramStr})`);
//         bsModal.hide();
//         setTimeout(() => paramModal.remove(), 500);
//       };
//       paramModal.querySelector(".btn-close").onclick = function () {
//         bsModal.hide();
//         setTimeout(() => paramModal.remove(), 500);
//       };
//     });
// }

// // ==== Filter row template with identifiable classes ====
// function newConditionRow(idx = 0) {
//   return `
// <div class="filter-card px-3 py-2 mb-2 d-flex align-items-center flex-wrap rounded shadow-sm bg-white gap-2 condition-row">
//   <span class="filter-index badge bg-light text-secondary" style="font-size:1em;">[${idx}]</span>
//   <input type="text" class="form-control indicator-select left-indicator" style="width:130px;cursor:pointer" placeholder="Indicator" readonly>
//   <select class="form-select mx-2" style="width:80px">
//     <option value=">">&gt;</option>
//     <option value="<">&lt;</option>
//     <option value=">=">&ge;</option>
//     <option value="<=">&le;</option>
//     <option value="==">=</option>
//   </select>
//   <input type="text" class="form-control indicator-select right-indicator" style="width:130px;cursor:pointer" placeholder="Indicator/Value" readonly>
//   <input type="text" class="form-control ms-1" style="width:90px" placeholder="Constant">
//   <select class="form-select mx-2" style="width:80px">
//     <option value="AND">AND</option>
//     <option value="OR">OR</option>
//   </select>
//   <button class="icon-btn remove-condition" type="button" title="Remove"><span>❌</span></button>
//   <button class="icon-btn" type="button" title="Copy"><span>📋</span></button>
//   <button class="icon-btn" type="button" title="Explain"><span>❓</span></button>
// </div>
// `;
// }

// function refreshIndices() {
//   document.querySelectorAll("#conditions .filter-card").forEach((row, i) => {
//     row.querySelector(".filter-index").textContent = `[${i}]`;
//   });
// }
// function addConditionRow() {
//   let container = document.getElementById("conditions");
//   container.insertAdjacentHTML("beforeend", newConditionRow(filterCount));
//   filterCount++;
//   refreshIndices();
//   bindFilterEvents();
// }
// function bindFilterEvents() {
//   document.querySelectorAll(".remove-condition").forEach((btn) => {
//     btn.onclick = function () {
//       this.closest(".condition-row").remove();
//       refreshIndices();
//       filterCount = document.querySelectorAll(
//         "#conditions .filter-card"
//       ).length;
//     };
//   });
//   document.querySelectorAll(".indicator-select").forEach((el) => {
//     el.onclick = function () {
//       activeInput = this;
//       renderIndicators("");
//       let modal = new bootstrap.Modal(
//         document.getElementById("indicatorModal")
//       );
//       modal.show();
//     };
//   });
// }
// document.getElementById("addFilter").onclick = addConditionRow;
// addConditionRow(); // One filter row on load

// // ==== INDICATOR PICKER MODAL ====
// document
//   .getElementById("indicatorSearch")
//   .addEventListener("input", function () {
//     renderIndicators(this.value);
//   });

// function selectIndicator(indicatorValue) {
//   // Find the label for display
//   const indicatorObj = allIndicators.find((i) => i.value === indicatorValue);
//   fetch(`/screener/api/indicator_params/?fn=${indicatorValue}`)
//     .then((resp) => resp.json())
//     .then((data) => {
//       if (data.params && data.params.length) {
//         showIndicatorParamsModal(indicatorValue, (label) => {
//           if (activeInput) activeInput.value = label;
//         });
//       } else {
//         if (activeInput)
//           activeInput.value = indicatorObj
//             ? indicatorObj.label
//             : indicatorValue;
//       }
//       let modal = bootstrap.Modal.getInstance(
//         document.getElementById("indicatorModal")
//       );
//       modal.hide();
//     });
// }
// function selectValueEntry() {
//   if (activeInput) {
//     // Turn this input into a number input temporarily
//     const val = prompt("Enter value (e.g. 60):");
//     activeInput.value = val || "";
//   }
//   let modal = bootstrap.Modal.getInstance(
//     document.getElementById("indicatorModal")
//   );
//   modal.hide();
// }
// renderIndicators("");
// Chartink-style Filter Builder for #filter-list and #add-filter

let INDICATOR_GROUPS = {};
let INDICATORS = [];
const FIELDS = ["Open", "High", "Low", "Close", "Volume"];
const TIMEFRAMES = ["Daily", "Weekly", "15min"];
const OPERATORS = [">", "<", ">=", "<=", "crosses above", "crosses below"];
const RIGHT_TYPES = [
  { value: "number", label: "Number" },
  { value: "indicator", label: "Indicator" },
];

let filters = [];
let filterId = 0;

function fetchIndicatorsAndRender() {
  fetch("/screener/api/indicators/")
    .then((res) => res.json())
    .then((data) => {
      INDICATOR_GROUPS = data.groups;
      INDICATORS = Object.values(INDICATOR_GROUPS).flat();
      renderFilters();
    });
}
fetchIndicatorsAndRender();

function renderIndicatorDropdown(selected) {
  let html = "";
  for (const [group, items] of Object.entries(INDICATOR_GROUPS)) {
    html += `<optgroup label="${group}">`;
    for (const ind of items) {
      html += `<option value="${ind.value}" ${
        selected === ind.value ? "selected" : ""
      }>${ind.label}</option>`;
    }
    html += `</optgroup>`;
  }
  return html;
}

function renderFilters() {
  const filterList = document.getElementById("filter-list");
  filterList.innerHTML = "";
  filters.forEach((f, idx) => {
    filterList.appendChild(renderFilterRow(f, idx));
  });
}

function renderFilterRow(f, idx) {
  const row = document.createElement("div");
  row.className = "row align-items-center mb-2 filter-row";
  row.dataset.idx = idx;
  row.innerHTML += `
    <div class="col-auto">
      <select class="form-select form-select-sm timeframe-select">
        ${TIMEFRAMES.map(
          (tf) =>
            `<option ${f.timeframe === tf ? "selected" : ""}>${tf}</option>`
        ).join("")}
      </select>
    </div>
    <div class="col-auto">
      <select class="form-select form-select-sm indicator-select">
        <option value="">Indicator</option>
        ${renderIndicatorDropdown(f.indicator)}
      </select>
    </div>
    <div class="col-auto">
      <span>(</span>
      <select class="form-select form-select-sm timeframe2-select d-inline w-auto">
        ${TIMEFRAMES.map(
          (tf) =>
            `<option ${f.timeframe2 === tf ? "selected" : ""}>${tf}</option>`
        ).join("")}
      </select>
      <select class="form-select form-select-sm field-select d-inline w-auto">
        ${FIELDS.map(
          (field) =>
            `<option ${f.field === field ? "selected" : ""}>${field}</option>`
        ).join("")}
      </select>
      <input type="number" class="form-control form-control-sm period-input d-inline w-auto" value="${
        f.period
      }" style="width:60px;display:inline;" min="1">
      <span>)</span>
    </div>
    <div class="col-auto">
      <select class="form-select form-select-sm main-op-select d-inline w-auto">
        ${OPERATORS.map(
          (op) => `<option ${f.mainOp === op ? "selected" : ""}>${op}</option>`
        ).join("")}
      </select>
    </div>
    <div class="col-auto">
      <select class="form-select form-select-sm right-type-select d-inline w-auto">
        ${RIGHT_TYPES.map(
          (rt) =>
            `<option value="${rt.value}" ${
              f.rightType === rt.value ? "selected" : ""
            }>${rt.label}</option>`
        ).join("")}
      </select>
    </div>
    <div class="col-auto right-side">
      ${
        f.rightType === "number"
          ? `
        <input type="number" class="form-control form-control-sm right-number-input d-inline w-auto" value="${f.rightValue}" style="width:80px;">
      `
          : `
        <select class="form-select form-select-sm right-indicator-select d-inline w-auto">
          <option value="">Indicator</option>
          ${renderIndicatorDropdown(f.rightIndicator)}
        </select>
        <input type="number" class="form-control form-control-sm right-period-input d-inline w-auto" value="${
          f.rightPeriod || 14
        }" style="width:60px;">
      `
      }
    </div>
    <div class="col-auto">
      <button class="btn btn-outline-danger btn-sm remove-filter-btn">✕</button>
    </div>
  `;
  setTimeout(() => {
    row.querySelector(".timeframe-select").onchange = (e) =>
      updateFilter(idx, { timeframe: e.target.value });
    row.querySelector(".indicator-select").onchange = (e) =>
      updateFilter(idx, { indicator: e.target.value });
    row.querySelector(".timeframe2-select").onchange = (e) =>
      updateFilter(idx, { timeframe2: e.target.value });
    row.querySelector(".field-select").onchange = (e) =>
      updateFilter(idx, { field: e.target.value });
    row.querySelector(".period-input").oninput = (e) =>
      updateFilter(idx, { period: e.target.value });
    row.querySelector(".main-op-select").onchange = (e) =>
      updateFilter(idx, { mainOp: e.target.value });
    row.querySelector(".right-type-select").onchange = (e) =>
      updateFilter(idx, { rightType: e.target.value });
    if (f.rightType === "number") {
      row.querySelector(".right-number-input").oninput = (e) =>
        updateFilter(idx, { rightValue: e.target.value });
    } else {
      row.querySelector(".right-indicator-select").onchange = (e) =>
        updateFilter(idx, { rightIndicator: e.target.value });
      row.querySelector(".right-period-input").oninput = (e) =>
        updateFilter(idx, { rightPeriod: e.target.value });
    }
    row.querySelector(".remove-filter-btn").onclick = () => removeFilter(idx);
  }, 0);

  return row;
}

function updateFilter(idx, patch) {
  filters[idx] = { ...filters[idx], ...patch };
  renderFilters();
}

function removeFilter(idx) {
  filters.splice(idx, 1);
  renderFilters();
}

// Add filter button event
document.getElementById("add-filter").onclick = function () {
  filters.push({
    id: ++filterId,
    timeframe: "Daily",
    indicator: "",
    timeframe2: "Daily",
    field: "Close",
    period: 20,
    mainOp: ">=",
    rightType: "number",
    rightValue: 20,
    rightIndicator: "",
    rightPeriod: 14,
  });
  renderFilters();
};

// Run Scan button event
document.getElementById("runScan").onclick = function (e) {
  e.preventDefault();
  fetch("/screener/api/run_screener/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filters }),
  })
    .then((res) => res.json())
    .then((data) => renderResultsTable(data.matches));
};

function renderResultsTable(matches) {
  let html = "";
  if (!matches || matches.length === 0) {
    html = `<tr><td colspan="7" class="text-center py-4 text-muted">No results yet.</td></tr>`;
  } else {
    matches.forEach((row, i) => {
      html += `<tr>
        <td>${i + 1}</td>
        <td>${row.symbol || row}</td>
        <td>${row.last_price !== undefined ? row.last_price : ""}</td>
        <td>${row.change_pct !== undefined ? row.change_pct : ""}</td>
        <td>${row.volume !== undefined ? row.volume : ""}</td>
        <td>✔️</td>
        <td></td>
      </tr>`;
    });
  }
  document.getElementById("resultsBody").innerHTML = html;
}

// Initial render (no filter rows until user adds)
renderFilters();
