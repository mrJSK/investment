// // let INDICATORS = [];
// // const OPERATORS = [
// //   { value: "==", label: "Equals", icon: "＝" },
// //   { value: "!=", label: "Not equals", icon: "≠" },
// //   { value: ">", label: "Greater than", icon: "＞" },
// //   { value: ">=", label: "Greater than equal to", icon: "≥" },
// //   { value: "<", label: "Less than", icon: "＜" },
// //   { value: "<=", label: "Less than equal to", icon: "≤" },
// //   { value: "crosses above", label: "Crossed above", icon: "⤴️" },
// //   { value: "crosses below", label: "Crossed below", icon: "⤵️" },
// // ];
// // const TIMEFRAMES = ["Daily", "Weekly", "15min"];
// // const FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// // let filters = [];
// // let filterId = 0;
// // let MODAL_ROW_IDX = null;
// // let MODAL_TARGET = null;
// // let MODAL_INDICATOR = null;
// // let MODAL_FOCUS_FIELD = null;

// // function fetchIndicatorsAndRender() {
// //   fetch("/screener/api/indicators/")
// //     .then((res) => res.json())
// //     .then((data) => {
// //       INDICATORS = data.indicators || [];
// //       renderFilters();
// //     });
// // }
// // fetchIndicatorsAndRender();

// // document.getElementById("add-filter").onclick = function () {
// //   filters.push({ id: ++filterId, step: 1, left: null, op: null, right: null });
// //   renderFilters();
// //   openIndicatorModal(filters.length - 1, "left");
// // };

// // function renderFilterRow(f, idx) {
// //   const row = document.createElement("div");
// //   row.className = "filter-row";
// //   let html = "";

// //   // Step-by-step builder logic
// //   if (f.step === 1) {
// //     html += `<button class="builder-token token-indicator" onclick="openIndicatorModal(${idx}, 'left')" title="Pick indicator/number">
// //       <span style="font-size:1.1em;">📊</span> Select Indicator/Number
// //     </button>`;
// //   } else if (f.step === 2) {
// //     html +=
// //       showIndicatorOrNumber(f.left, "left", idx) +
// //       `<button class="token-mini token-op" onclick="openOperatorModal(${idx})" title="Pick operator" style="margin-left:8px;">
// //         <span style="font-size:1.1em;">${getOperatorIcon(f.op)}</span>
// //         ${f.op ? getOperatorLabel(f.op) : "?"}
// //       </button>`;
// //   } else if (f.step === 3) {
// //     html +=
// //       showIndicatorOrNumber(f.left, "left", idx) +
// //       `<button class="token-mini token-op" onclick="openOperatorModal(${idx})" title="Edit operator" style="margin-left:6px;margin-right:6px;">
// //         <span style="font-size:1.1em;">${getOperatorIcon(f.op)}</span>
// //         ${getOperatorLabel(f.op)}
// //       </button>` +
// //       showIndicatorOrNumber(f.right, "right", idx, true);
// //   } else if (f.step === 4) {
// //     html +=
// //       showIndicatorOrNumber(f.left, "left", idx) +
// //       `<button class="token-mini token-op" onclick="openOperatorModal(${idx})" title="Edit operator" style="margin-left:6px;margin-right:6px;">
// //         <span style="font-size:1.1em;">${getOperatorIcon(f.op)}</span>
// //         ${getOperatorLabel(f.op)}
// //       </button>` +
// //       showIndicatorOrNumber(f.right, "right", idx, true) +
// //       `<button class="icon-btn" style="margin-left:12px;" title="Copy filter">&#128203;</button>
// //        <button class="icon-btn" title="Enable/Disable">&#128994;</button>`;
// //   }
// //   html += `<button class="remove-filter-btn icon-btn" title="Delete Filter" style="margin-left:8px;" onclick="removeFilter(${idx})">🗑️</button>`;
// //   row.innerHTML = html;
// //   return row;
// // }

// // function showIndicatorOrNumber(val, side, idx, allowEmpty = false) {
// //   if (!val && !allowEmpty) return "";
// //   if (val && val.type === "indicator") {
// //     // Formula tokens: each part clickable
// //     return `
// //       <span class="token-ind-formula">
// //         <button class="token-mini token-tf" onclick="editToken('${side}','timeframe',${idx})">${val.timeframe}</button>
// //         <button class="token-mini token-ind" onclick="editToken('${side}','indicator',${idx})">${val.value}</button>
// //         (<button class="token-mini token-field" onclick="editToken('${side}','field',${idx})">${val.field}</button>
// //         , <button class="token-mini token-per" onclick="editToken('${side}','period',${idx})">${val.period}</button>)
// //       </span>
// //     `;
// //   } else if (val && val.type === "number") {
// //     return `<span class="token-number">
// //       <button class="token-mini token-num" onclick="editToken('${side}','number',${idx})">${val.value}</button>
// //     </span>`;
// //   } else if (allowEmpty) {
// //     // Allow for right-side to show "Select Indicator/Number" if empty
// //     return `<button class="builder-token token-indicator" onclick="openIndicatorModal(${idx}, '${side}')" title="Pick indicator/number">
// //       <span style="font-size:1.1em;">📊</span> Select Indicator/Number
// //     </button>`;
// //   }
// //   return "";
// // }
// // function getOperatorLabel(op) {
// //   let x = OPERATORS.find((o) => o.value === op);
// //   return x ? x.label : op;
// // }
// // function getOperatorIcon(op) {
// //   let x = OPERATORS.find((o) => o.value === op);
// //   return x ? x.icon : "";
// // }
// // function removeFilter(idx) {
// //   filters.splice(idx, 1);
// //   renderFilters();
// // }

// // window.openIndicatorModal = openIndicatorModal;
// // function openIndicatorModal(idx, target) {
// //   MODAL_ROW_IDX = idx;
// //   MODAL_TARGET = target;
// //   document.getElementById("indicatorSearch").value = "";
// //   renderIndicatorModal();
// //   let modal = new bootstrap.Modal(document.getElementById("indicatorModal"));
// //   modal.show();
// // }
// // function renderIndicatorModal() {
// //   const searchInput = document.getElementById("indicatorSearch");
// //   const list = document.getElementById("indicatorList");
// //   let val = (searchInput.value || "").toLowerCase();
// //   list.innerHTML = "";

// //   // NUMBER/CONSTANT always first
// //   let liNum = document.createElement("li");
// //   liNum.className = "list-group-item list-group-item-action text-primary";
// //   liNum.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant)</b>`;
// //   liNum.onclick = () => {
// //     let numVal = prompt("Enter number value:", "20");
// //     if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
// //       setIndicatorConfigOnRow(MODAL_ROW_IDX, MODAL_TARGET, {
// //         type: "number",
// //         value: numVal,
// //       });
// //       bootstrap.Modal.getInstance(
// //         document.getElementById("indicatorModal")
// //       ).hide();
// //     }
// //   };
// //   list.appendChild(liNum);

// //   // All indicators (use short name in value)
// //   INDICATORS.filter(
// //     (ind) =>
// //       ind.label.toLowerCase().includes(val) ||
// //       ind.value.toLowerCase().includes(val)
// //   ).forEach((ind) => {
// //     let li = document.createElement("li");
// //     li.className = "list-group-item list-group-item-action";
// //     li.innerHTML = `<span style="font-size:1.1em;">📊</span> <b>${ind.value}</b> <span style="font-size:0.95em;color:#555;">(${ind.label})</span>`;
// //     li.onclick = () => {
// //       MODAL_INDICATOR = ind;
// //       openIndicatorConfigModal(MODAL_ROW_IDX, MODAL_TARGET, ind);
// //       bootstrap.Modal.getInstance(
// //         document.getElementById("indicatorModal")
// //       ).hide();
// //     };
// //     list.appendChild(li);
// //   });
// // }
// // document.getElementById("indicatorSearch").oninput = renderIndicatorModal;

// // // ---- Indicator Config Modal ----

// // function openIndicatorConfigModal(idx, target, indicator, focusField = null) {
// //   MODAL_FOCUS_FIELD = focusField;
// //   document.getElementById(
// //     "indicatorConfigModalLabel"
// //   ).innerText = `Configure ${indicator.value}`;
// //   document.getElementById("indicatorConfigTimeframe").value = "Daily";
// //   document.getElementById("indicatorConfigField").value = "Close";
// //   let hasPeriod = !["VWAP", "OBV", "AD"].includes(indicator.value); // Tweak per-indicator if needed
// //   document.getElementById("indicatorConfigPeriodGroup").style.display =
// //     hasPeriod ? "block" : "none";
// //   document.getElementById("indicatorConfigPeriod").value = "20";
// //   setTimeout(() => {
// //     if (focusField === "timeframe")
// //       document.getElementById("indicatorConfigTimeframe").focus();
// //     if (focusField === "field")
// //       document.getElementById("indicatorConfigField").focus();
// //     if (focusField === "period")
// //       document.getElementById("indicatorConfigPeriod").focus();
// //   }, 350);

// //   document.getElementById("indicatorConfigDone").onclick = function () {
// //     let config = {
// //       type: "indicator",
// //       value: indicator.value,
// //       label: indicator.label,
// //       timeframe: document.getElementById("indicatorConfigTimeframe").value,
// //       field: document.getElementById("indicatorConfigField").value,
// //       period: hasPeriod
// //         ? document.getElementById("indicatorConfigPeriod").value
// //         : "",
// //     };
// //     setIndicatorConfigOnRow(idx, target, config);
// //     bootstrap.Modal.getInstance(
// //       document.getElementById("indicatorConfigModal")
// //     ).hide();
// //   };
// //   let modal = new bootstrap.Modal(
// //     document.getElementById("indicatorConfigModal")
// //   );
// //   modal.show();
// // }

// // // Used for edits
// // function openPartialIndicatorConfigModal(idx, side, focusField) {
// //   let indicator = filters[idx][side];
// //   // Populate modal with existing values
// //   document.getElementById(
// //     "indicatorConfigModalLabel"
// //   ).innerText = `Edit ${indicator.value}`;
// //   document.getElementById("indicatorConfigTimeframe").value =
// //     indicator.timeframe;
// //   document.getElementById("indicatorConfigField").value = indicator.field;
// //   document.getElementById("indicatorConfigPeriod").value = indicator.period;
// //   document.getElementById("indicatorConfigPeriodGroup").style.display = "block";
// //   setTimeout(() => {
// //     if (focusField === "timeframe")
// //       document.getElementById("indicatorConfigTimeframe").focus();
// //     if (focusField === "field")
// //       document.getElementById("indicatorConfigField").focus();
// //     if (focusField === "period")
// //       document.getElementById("indicatorConfigPeriod").focus();
// //   }, 350);

// //   document.getElementById("indicatorConfigDone").onclick = function () {
// //     indicator.timeframe = document.getElementById(
// //       "indicatorConfigTimeframe"
// //     ).value;
// //     indicator.field = document.getElementById("indicatorConfigField").value;
// //     indicator.period = document.getElementById("indicatorConfigPeriod").value;
// //     // DO NOT reset filters[idx] or step here!
// //     renderFilters();
// //     bootstrap.Modal.getInstance(
// //       document.getElementById("indicatorConfigModal")
// //     ).hide();
// //   };
// //   let modal = new bootstrap.Modal(
// //     document.getElementById("indicatorConfigModal")
// //   );
// //   modal.show();
// // }

// // function setIndicatorConfigOnRow(idx, target, config) {
// //   if (target === "left") {
// //     filters[idx].left = config;
// //     filters[idx].step = 2;
// //   } else {
// //     filters[idx].right = config;
// //     filters[idx].step = 4;
// //   }
// //   renderFilters();
// //   if (filters[idx].step === 2) openOperatorModal(idx);
// // }

// // // ---- Operator Modal ----

// // window.openOperatorModal = openOperatorModal;
// // function openOperatorModal(idx) {
// //   MODAL_ROW_IDX = idx;
// //   renderOperatorModal();
// //   let modal = new bootstrap.Modal(document.getElementById("operatorModal"));
// //   modal.show();
// // }
// // function renderOperatorModal() {
// //   const list = document.getElementById("operatorList");
// //   list.innerHTML = "";
// //   OPERATORS.forEach((op) => {
// //     let li = document.createElement("li");
// //     li.className = "list-group-item list-group-item-action";
// //     li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b>`;
// //     li.onclick = () => {
// //       setOperatorOnRow(MODAL_ROW_IDX, op.value);
// //       bootstrap.Modal.getInstance(
// //         document.getElementById("operatorModal")
// //       ).hide();
// //     };
// //     list.appendChild(li);
// //   });
// // }
// // function setOperatorOnRow(idx, op) {
// //   filters[idx].op = op;
// //   filters[idx].step = 3;
// //   renderFilters();
// //   openIndicatorModal(idx, "right");
// // }

// // // ---- Editable Token Logic ----

// // window.editToken = function (side, tokenType, idx) {
// //   let f = filters[idx];
// //   let val = f[side];
// //   if (!val) return;

// //   if (tokenType === "indicator") {
// //     openIndicatorModal(idx, side); // Will set new indicator and update in place
// //   } else if (
// //     tokenType === "timeframe" ||
// //     tokenType === "field" ||
// //     tokenType === "period"
// //   ) {
// //     // Open config modal with *existing* indicator config, don't delete or reset!
// //     openPartialIndicatorConfigModal(idx, side, tokenType);
// //   } else if (tokenType === "number") {
// //     let numVal = prompt("Edit number:", val.value);
// //     if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
// //       filters[idx][side].value = numVal;
// //       renderFilters();
// //     }
// //   }
// // };

// // function renderFilters() {
// //   const filterList = document.getElementById("filter-list");
// //   filterList.innerHTML = "";
// //   filters.forEach((f, idx) => {
// //     filterList.appendChild(renderFilterRow(f, idx));
// //   });
// // }
// // window.removeFilter = removeFilter;
// // renderFilters();
// let INDICATORS = [];
// const OPERATORS = [
//   { value: "==", label: "Equals", icon: "＝" },
//   { value: "!=", label: "Not equals", icon: "≠" },
//   { value: ">", label: "Greater than", icon: "＞" },
//   { value: ">=", label: "Greater than equal to", icon: "≥" },
//   { value: "<", label: "Less than", icon: "＜" },
//   { value: "<=", label: "Less than equal to", icon: "≤" },
//   { value: "crosses above", label: "Crossed above", icon: "⤴️" },
//   { value: "crosses below", label: "Crossed below", icon: "⤵️" },
// ];
// const TIMEFRAMES = ["Daily", "Weekly", "15min"];
// const FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// let filters = [];
// let filterId = 0;
// let MODAL_ROW_IDX = null;
// let MODAL_TARGET = null;
// let MODAL_INDICATOR = null;
// let MODAL_FOCUS_FIELD = null;

// // Utility to safely attach events
// function attachEvent(element, event, handler) {
//   element.addEventListener(event, handler);
// }

// // Fetch indicators from backend and render builder
// function fetchIndicatorsAndRender() {
//   fetch("/screener/api/indicators/")
//     .then((res) => res.json())
//     .then((data) => {
//       INDICATORS = data.indicators || [];
//       renderFilters();
//     });
// }
// fetchIndicatorsAndRender();

// document.getElementById("add-filter").onclick = function () {
//   filters.push({ id: ++filterId, step: 1, left: null, op: null, right: null });
//   renderFilters();
//   openIndicatorModal(filters.length - 1, "left");
// };

// function renderFilterRow(f, idx) {
//   const row = document.createElement("div");
//   row.className = "filter-row";

//   // LEFT SIDE
//   if (f.left && f.left.type === "indicator") {
//     let span = document.createElement("span");
//     span.className = "token-ind-formula";
//     // Timeframe
//     let btnTf = document.createElement("button");
//     btnTf.className = "token-mini token-tf";
//     btnTf.textContent = f.left.timeframe;
//     btnTf.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openPartialIndicatorConfigModal(idx, "left", "timeframe");
//     });
//     // Indicator
//     let btnInd = document.createElement("button");
//     btnInd.className = "token-mini token-ind";
//     btnInd.textContent = f.left.value;
//     btnInd.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openIndicatorModal(idx, "left");
//     });
//     // (
//     let txtOpen = document.createTextNode("(");
//     // Field
//     let btnField = document.createElement("button");
//     btnField.className = "token-mini token-field";
//     btnField.textContent = f.left.field;
//     btnField.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openPartialIndicatorConfigModal(idx, "left", "field");
//     });
//     // ,
//     let txtComma = document.createTextNode(", ");
//     // Period
//     let btnPeriod = document.createElement("button");
//     btnPeriod.className = "token-mini token-per";
//     btnPeriod.textContent = f.left.period;
//     btnPeriod.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openPartialIndicatorConfigModal(idx, "left", "period");
//     });
//     // )
//     let txtClose = document.createTextNode(")");
//     // Assemble
//     span.append(
//       btnTf,
//       btnInd,
//       txtOpen,
//       btnField,
//       txtComma,
//       btnPeriod,
//       txtClose
//     );
//     row.appendChild(span);
//   } else if (f.left && f.left.type === "number") {
//     let span = document.createElement("span");
//     span.className = "token-number";
//     let btnNum = document.createElement("button");
//     btnNum.className = "token-mini token-num";
//     btnNum.textContent = f.left.value;
//     btnNum.addEventListener("click", (e) => {
//       e.stopPropagation();
//       editToken("left", "number", idx);
//     });
//     span.appendChild(btnNum);
//     row.appendChild(span);
//   } else {
//     let btn = document.createElement("button");
//     btn.className = "builder-token token-indicator";
//     btn.innerHTML = `<span style="font-size:1.1em;">📊</span> Select Indicator/Number`;
//     btn.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openIndicatorModal(idx, "left");
//     });
//     row.appendChild(btn);
//   }

//   // OPERATOR
//   let btnOp = document.createElement("button");
//   btnOp.className = "token-mini token-op";
//   btnOp.textContent = f.op ? getOperatorLabel(f.op) : "?";
//   btnOp.addEventListener("click", (e) => {
//     e.stopPropagation();
//     openOperatorModal(idx);
//   });
//   row.appendChild(btnOp);

//   // RIGHT SIDE
//   if (f.right && f.right.type === "indicator") {
//     let span = document.createElement("span");
//     span.className = "token-ind-formula";
//     // Timeframe
//     let btnTf = document.createElement("button");
//     btnTf.className = "token-mini token-tf";
//     btnTf.textContent = f.right.timeframe;
//     btnTf.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openPartialIndicatorConfigModal(idx, "right", "timeframe");
//     });
//     // Indicator
//     let btnInd = document.createElement("button");
//     btnInd.className = "token-mini token-ind";
//     btnInd.textContent = f.right.value;
//     btnInd.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openIndicatorModal(idx, "right");
//     });
//     // (
//     let txtOpen = document.createTextNode("(");
//     // Field
//     let btnField = document.createElement("button");
//     btnField.className = "token-mini token-field";
//     btnField.textContent = f.right.field;
//     btnField.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openPartialIndicatorConfigModal(idx, "right", "field");
//     });
//     // ,
//     let txtComma = document.createTextNode(", ");
//     // Period
//     let btnPeriod = document.createElement("button");
//     btnPeriod.className = "token-mini token-per";
//     btnPeriod.textContent = f.right.period;
//     btnPeriod.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openPartialIndicatorConfigModal(idx, "right", "period");
//     });
//     // )
//     let txtClose = document.createTextNode(")");
//     // Assemble
//     span.append(
//       btnTf,
//       btnInd,
//       txtOpen,
//       btnField,
//       txtComma,
//       btnPeriod,
//       txtClose
//     );
//     row.appendChild(span);
//   } else if (f.right && f.right.type === "number") {
//     let span = document.createElement("span");
//     span.className = "token-number";
//     let btnNum = document.createElement("button");
//     btnNum.className = "token-mini token-num";
//     btnNum.textContent = f.right.value;
//     btnNum.addEventListener("click", (e) => {
//       e.stopPropagation();
//       editToken("right", "number", idx);
//     });
//     span.appendChild(btnNum);
//     row.appendChild(span);
//   } else if (f.step >= 3) {
//     let btn = document.createElement("button");
//     btn.className = "builder-token token-indicator";
//     btn.innerHTML = `<span style="font-size:1.1em;">📊</span> Select Indicator/Number`;
//     btn.addEventListener("click", (e) => {
//       e.stopPropagation();
//       openIndicatorModal(idx, "right");
//     });
//     row.appendChild(btn);
//   }

//   // ACTIONS: Delete
//   let delBtn = document.createElement("button");
//   delBtn.className = "remove-filter-btn icon-btn";
//   delBtn.title = "Delete Filter";
//   delBtn.style.marginLeft = "8px";
//   delBtn.innerHTML = "🗑️";
//   delBtn.addEventListener("click", (e) => {
//     e.stopPropagation();
//     removeFilter(idx);
//   });
//   row.appendChild(delBtn);

//   // (Optional: Copy/Toggle buttons can be added similarly here.)

//   return row;
// }

// function showIndicatorOrNumber(val, side, idx, allowEmpty = false) {
//   if (!val && !allowEmpty) return "";
//   if (val && val.type === "indicator") {
//     // Use span and button for each token, no inline handlers
//     return `
//       <span class="token-ind-formula">
//         <button class="token-mini token-tf">${val.timeframe}</button>
//         <button class="token-mini token-ind">${val.value}</button>
//         (<button class="token-mini token-field">${val.field}</button>
//         , <button class="token-mini token-per">${val.period}</button>)
//       </span>
//     `;
//   } else if (val && val.type === "number") {
//     return `<span class="token-number">
//       <button class="token-mini token-num">${val.value}</button>
//     </span>`;
//   } else if (allowEmpty) {
//     return `<button class="builder-token token-indicator" title="Pick indicator/number">
//       <span style="font-size:1.1em;">📊</span> Select Indicator/Number
//     </button>`;
//   }
//   return "";
// }
// function getOperatorLabel(op) {
//   let x = OPERATORS.find((o) => o.value === op);
//   return x ? x.label : op;
// }
// function getOperatorIcon(op) {
//   let x = OPERATORS.find((o) => o.value === op);
//   return x ? x.icon : "";
// }
// function removeFilter(idx) {
//   filters.splice(idx, 1);
//   renderFilters();
// }

// window.openIndicatorModal = openIndicatorModal;
// function openIndicatorModal(idx, target) {
//   MODAL_ROW_IDX = idx;
//   MODAL_TARGET = target;
//   document.getElementById("indicatorSearch").value = "";
//   renderIndicatorModal();
//   let modal = new bootstrap.Modal(document.getElementById("indicatorModal"));
//   modal.show();
// }
// function renderIndicatorModal() {
//   const searchInput = document.getElementById("indicatorSearch");
//   const list = document.getElementById("indicatorList");
//   let val = (searchInput.value || "").toLowerCase();
//   list.innerHTML = "";

//   // NUMBER/CONSTANT always first
//   let liNum = document.createElement("li");
//   liNum.className = "list-group-item list-group-item-action text-primary";
//   liNum.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant)</b>`;
//   liNum.onclick = () => {
//     let numVal = prompt("Enter number value:", "20");
//     if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
//       setIndicatorConfigOnRow(MODAL_ROW_IDX, MODAL_TARGET, {
//         type: "number",
//         value: numVal,
//       });
//       bootstrap.Modal.getInstance(
//         document.getElementById("indicatorModal")
//       ).hide();
//     }
//   };
//   list.appendChild(liNum);

//   // All indicators (use short name in value)
//   INDICATORS.filter(
//     (ind) =>
//       ind.label.toLowerCase().includes(val) ||
//       ind.value.toLowerCase().includes(val)
//   ).forEach((ind) => {
//     let li = document.createElement("li");
//     li.className = "list-group-item list-group-item-action";
//     li.innerHTML = `<span style="font-size:1.1em;">📊</span> <b>${ind.value}</b> <span style="font-size:0.95em;color:#555;">(${ind.label})</span>`;
//     li.onclick = () => {
//       MODAL_INDICATOR = ind;
//       openIndicatorConfigModal(MODAL_ROW_IDX, MODAL_TARGET, ind);
//       bootstrap.Modal.getInstance(
//         document.getElementById("indicatorModal")
//       ).hide();
//     };
//     list.appendChild(li);
//   });
// }
// document.getElementById("indicatorSearch").oninput = renderIndicatorModal;

// // ---- Indicator Config Modal ----

// function openIndicatorConfigModal(idx, target, indicator, focusField = null) {
//   MODAL_FOCUS_FIELD = focusField;
//   document.getElementById(
//     "indicatorConfigModalLabel"
//   ).innerText = `Configure ${indicator.value}`;
//   document.getElementById("indicatorConfigTimeframe").value = "Daily";
//   document.getElementById("indicatorConfigField").value = "Close";
//   let hasPeriod = !["VWAP", "OBV", "AD"].includes(indicator.value); // Tweak per-indicator if needed
//   document.getElementById("indicatorConfigPeriodGroup").style.display =
//     hasPeriod ? "block" : "none";
//   document.getElementById("indicatorConfigPeriod").value = "20";
//   setTimeout(() => {
//     if (focusField === "timeframe")
//       document.getElementById("indicatorConfigTimeframe").focus();
//     if (focusField === "field")
//       document.getElementById("indicatorConfigField").focus();
//     if (focusField === "period")
//       document.getElementById("indicatorConfigPeriod").focus();
//   }, 350);

//   document.getElementById("indicatorConfigDone").onclick = function () {
//     let config = {
//       type: "indicator",
//       value: indicator.value,
//       label: indicator.label,
//       timeframe: document.getElementById("indicatorConfigTimeframe").value,
//       field: document.getElementById("indicatorConfigField").value,
//       period: hasPeriod
//         ? document.getElementById("indicatorConfigPeriod").value
//         : "",
//     };
//     setIndicatorConfigOnRow(idx, target, config);
//     bootstrap.Modal.getInstance(
//       document.getElementById("indicatorConfigModal")
//     ).hide();
//   };
//   let modal = new bootstrap.Modal(
//     document.getElementById("indicatorConfigModal")
//   );
//   modal.show();
// }

// // Used for edits
// function openPartialIndicatorConfigModal(idx, side, focusField) {
//   let indicator = filters[idx][side];
//   document.getElementById(
//     "indicatorConfigModalLabel"
//   ).innerText = `Edit ${indicator.value}`;
//   document.getElementById("indicatorConfigTimeframe").value =
//     indicator.timeframe;
//   document.getElementById("indicatorConfigField").value = indicator.field;
//   document.getElementById("indicatorConfigPeriod").value = indicator.period;
//   document.getElementById("indicatorConfigPeriodGroup").style.display = "block";
//   setTimeout(() => {
//     if (focusField === "timeframe")
//       document.getElementById("indicatorConfigTimeframe").focus();
//     if (focusField === "field")
//       document.getElementById("indicatorConfigField").focus();
//     if (focusField === "period")
//       document.getElementById("indicatorConfigPeriod").focus();
//   }, 350);

//   document.getElementById("indicatorConfigDone").onclick = function () {
//     indicator.timeframe = document.getElementById(
//       "indicatorConfigTimeframe"
//     ).value;
//     indicator.field = document.getElementById("indicatorConfigField").value;
//     indicator.period = document.getElementById("indicatorConfigPeriod").value;
//     renderFilters();
//     bootstrap.Modal.getInstance(
//       document.getElementById("indicatorConfigModal")
//     ).hide();
//   };
//   let modal = new bootstrap.Modal(
//     document.getElementById("indicatorConfigModal")
//   );
//   modal.show();
// }

// function setIndicatorConfigOnRow(idx, target, config) {
//   if (target === "left") {
//     filters[idx].left = config;
//     filters[idx].step = 2;
//   } else {
//     filters[idx].right = config;
//     filters[idx].step = 4;
//   }
//   renderFilters();
//   if (filters[idx].step === 2) openOperatorModal(idx);
// }

// // ---- Operator Modal ----

// window.openOperatorModal = openOperatorModal;
// function openOperatorModal(idx) {
//   MODAL_ROW_IDX = idx;
//   renderOperatorModal();
//   let modal = new bootstrap.Modal(document.getElementById("operatorModal"));
//   modal.show();
// }
// function renderOperatorModal() {
//   const list = document.getElementById("operatorList");
//   list.innerHTML = "";
//   OPERATORS.forEach((op) => {
//     let li = document.createElement("li");
//     li.className = "list-group-item list-group-item-action";
//     li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b>`;
//     li.onclick = () => {
//       setOperatorOnRow(MODAL_ROW_IDX, op.value);
//       bootstrap.Modal.getInstance(
//         document.getElementById("operatorModal")
//       ).hide();
//     };
//     list.appendChild(li);
//   });
// }
// function setOperatorOnRow(idx, op) {
//   filters[idx].op = op;
//   filters[idx].step = 3;
//   renderFilters();
//   openIndicatorModal(idx, "right");
// }

// // ---- Editable Token Logic ----

// window.editToken = function (side, tokenType, idx) {
//   let f = filters[idx];
//   let val = f[side];
//   if (!val) return;

//   if (tokenType === "indicator") {
//     openIndicatorModal(idx, side);
//   } else if (
//     tokenType === "timeframe" ||
//     tokenType === "field" ||
//     tokenType === "period"
//   ) {
//     openPartialIndicatorConfigModal(idx, side, tokenType);
//   } else if (tokenType === "number") {
//     let numVal = prompt("Edit number:", val.value);
//     if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
//       filters[idx][side].value = numVal;
//       renderFilters();
//     }
//   }
// };

// function renderFilters() {
//   const filterList = document.getElementById("filter-list");
//   filterList.innerHTML = "";
//   filters.forEach((f, idx) => {
//     filterList.appendChild(renderFilterRow(f, idx));
//   });
// }
// window.removeFilter = removeFilter;
// renderFilters();
let INDICATORS = [];
const OPERATORS = [
  { value: "==", label: "Equals", icon: "＝" },
  { value: "!=", label: "Not equals", icon: "≠" },
  { value: ">", label: "Greater than", icon: "＞" },
  { value: ">=", label: "Greater than equal to", icon: "≥" },
  { value: "<", label: "Less than", icon: "＜" },
  { value: "<=", label: "Less than equal to", icon: "≤" },
  { value: "crosses above", label: "Crossed above", icon: "⤴️" },
  { value: "crosses below", label: "Crossed below", icon: "⤵️" },
];
const TIMEFRAMES = ["Daily", "Weekly", "15min"];
const FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// Make filters global so dashboard.js can access it
window.filters = [];
let filterId = 0;
let MODAL_ROW_IDX = null;
let MODAL_TARGET = null;
let MODAL_INDICATOR = null;
let MODAL_FOCUS_FIELD = null;

// Utility to safely attach events (not strictly used here, but good to keep)
function attachEvent(element, event, handler) {
  element.addEventListener(event, handler);
}

// Fetch indicators from backend and render builder
function fetchIndicatorsAndRender() {
  fetch("/screener/api/indicators/")
    .then((res) => res.json())
    .then((data) => {
      INDICATORS = data.indicators || [];
      renderFilters();
    });
}
fetchIndicatorsAndRender();

document.getElementById("add-filter").onclick = function () {
  window.filters.push({
    id: ++filterId,
    step: 1,
    left: null,
    op: null,
    right: null,
  });
  renderFilters();
  openIndicatorModal(window.filters.length - 1, "left");
};

function renderFilterRow(f, idx) {
  const row = document.createElement("div");
  row.className = "filter-row";

  // LEFT SIDE
  if (f.left && f.left.type === "indicator") {
    let span = document.createElement("span");
    span.className = "token-ind-formula";
    // Timeframe
    let btnTf = document.createElement("button");
    btnTf.className = "token-mini token-tf";
    btnTf.textContent = f.left.timeframe;
    btnTf.addEventListener("click", (e) => {
      e.stopPropagation();
      openPartialIndicatorConfigModal(idx, "left", "timeframe");
    });
    // Indicator
    let btnInd = document.createElement("button");
    btnInd.className = "token-mini token-ind";
    btnInd.textContent = f.left.value;
    btnInd.addEventListener("click", (e) => {
      e.stopPropagation();
      openIndicatorModal(idx, "left");
    });
    // (
    let txtOpen = document.createTextNode("(");
    // Field
    let btnField = document.createElement("button");
    btnField.className = "token-mini token-field";
    btnField.textContent = f.left.field;
    btnField.addEventListener("click", (e) => {
      e.stopPropagation();
      openPartialIndicatorConfigModal(idx, "left", "field");
    });
    // ,
    let txtComma = document.createTextNode(", ");
    // Period
    let btnPeriod = document.createElement("button");
    btnPeriod.className = "token-mini token-per";
    btnPeriod.textContent = f.left.period;
    btnPeriod.addEventListener("click", (e) => {
      e.stopPropagation();
      openPartialIndicatorConfigModal(idx, "left", "period");
    });
    // )
    let txtClose = document.createTextNode(")");
    // Assemble
    span.append(
      btnTf,
      btnInd,
      txtOpen,
      btnField,
      txtComma,
      btnPeriod,
      txtClose
    );
    row.appendChild(span);
  } else if (f.left && f.left.type === "number") {
    let span = document.createElement("span");
    span.className = "token-number";
    let btnNum = document.createElement("button");
    btnNum.className = "token-mini token-num";
    btnNum.textContent = f.left.value;
    btnNum.addEventListener("click", (e) => {
      e.stopPropagation();
      editToken("left", "number", idx);
    });
    span.appendChild(btnNum);
    row.appendChild(span);
  } else {
    let btn = document.createElement("button");
    btn.className = "builder-token token-indicator";
    btn.innerHTML = `<span style="font-size:1.1em;">📊</span> Select Indicator/Number`;
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openIndicatorModal(idx, "left");
    });
    row.appendChild(btn);
  }

  // OPERATOR
  let btnOp = document.createElement("button");
  btnOp.className = "token-mini token-op";
  btnOp.textContent = f.op ? getOperatorLabel(f.op) : "?";
  btnOp.addEventListener("click", (e) => {
    e.stopPropagation();
    openOperatorModal(idx);
  });
  row.appendChild(btnOp);

  // RIGHT SIDE
  if (f.right && f.right.type === "indicator") {
    let span = document.createElement("span");
    span.className = "token-ind-formula";
    // Timeframe
    let btnTf = document.createElement("button");
    btnTf.className = "token-mini token-tf";
    btnTf.textContent = f.right.timeframe;
    btnTf.addEventListener("click", (e) => {
      e.stopPropagation();
      openPartialIndicatorConfigModal(idx, "right", "timeframe");
    });
    // Indicator
    let btnInd = document.createElement("button");
    btnInd.className = "token-mini token-ind";
    btnInd.textContent = f.right.value;
    btnInd.addEventListener("click", (e) => {
      e.stopPropagation();
      openIndicatorModal(idx, "right");
    });
    // (
    let txtOpen = document.createTextNode("(");
    // Field
    let btnField = document.createElement("button");
    btnField.className = "token-mini token-field";
    btnField.textContent = f.right.field;
    btnField.addEventListener("click", (e) => {
      e.stopPropagation();
      openPartialIndicatorConfigModal(idx, "right", "field");
    });
    // ,
    let txtComma = document.createTextNode(", ");
    // Period
    let btnPeriod = document.createElement("button");
    btnPeriod.className = "token-mini token-per";
    btnPeriod.textContent = f.right.period;
    btnPeriod.addEventListener("click", (e) => {
      e.stopPropagation();
      openPartialIndicatorConfigModal(idx, "right", "period");
    });
    // )
    let txtClose = document.createTextNode(")");
    // Assemble
    span.append(
      btnTf,
      btnInd,
      txtOpen,
      btnField,
      txtComma,
      btnPeriod,
      txtClose
    );
    row.appendChild(span);
  } else if (f.right && f.right.type === "number") {
    let span = document.createElement("span");
    span.className = "token-number";
    let btnNum = document.createElement("button");
    btnNum.className = "token-mini token-num";
    btnNum.textContent = f.right.value;
    btnNum.addEventListener("click", (e) => {
      e.stopPropagation();
      editToken("right", "number", idx);
    });
    span.appendChild(btnNum);
    row.appendChild(span);
  } else if (f.step >= 3) {
    let btn = document.createElement("button");
    btn.className = "builder-token token-indicator";
    btn.innerHTML = `<span style="font-size:1.1em;">📊</span> Select Indicator/Number`;
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      openIndicatorModal(idx, "right");
    });
    row.appendChild(btn);
  }

  // ACTIONS: Delete
  let delBtn = document.createElement("button");
  delBtn.className = "remove-filter-btn icon-btn";
  delBtn.title = "Delete Filter";
  delBtn.style.marginLeft = "8px";
  delBtn.innerHTML = "🗑️";
  delBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    removeFilter(idx);
  });
  row.appendChild(delBtn);

  return row;
}

function showIndicatorOrNumber(val, side, idx, allowEmpty = false) {
  if (!val && !allowEmpty) return "";
  if (val && val.type === "indicator") {
    return `
      <span class="token-ind-formula">
        <button class="token-mini token-tf">${val.timeframe}</button>
        <button class="token-mini token-ind">${val.value}</button>
        (<button class="token-mini token-field">${val.field}</button>
        , <button class="token-mini token-per">${val.period}</button>)
      </span>
    `;
  } else if (val && val.type === "number") {
    return `<span class="token-number">
      <button class="token-mini token-num">${val.value}</button>
    </span>`;
  } else if (allowEmpty) {
    return `<button class="builder-token token-indicator" title="Pick indicator/number">
      <span style="font-size:1.1em;">📊</span> Select Indicator/Number
    </button>`;
  }
  return "";
}
function getOperatorLabel(op) {
  let x = OPERATORS.find((o) => o.value === op);
  return x ? x.label : op;
}
function getOperatorIcon(op) {
  let x = OPERATORS.find((o) => o.value === op);
  return x ? x.icon : "";
}
function removeFilter(idx) {
  window.filters.splice(idx, 1);
  renderFilters();
}

window.openIndicatorModal = openIndicatorModal;
function openIndicatorModal(idx, target) {
  MODAL_ROW_IDX = idx;
  MODAL_TARGET = target;
  document.getElementById("indicatorSearch").value = "";
  renderIndicatorModal();
  let modal = new bootstrap.Modal(document.getElementById("indicatorModal"));
  modal.show();
}
function renderIndicatorModal() {
  const searchInput = document.getElementById("indicatorSearch");
  const list = document.getElementById("indicatorList");
  let val = (searchInput.value || "").toLowerCase();
  list.innerHTML = "";

  // NUMBER/CONSTANT always first
  let liNum = document.createElement("li");
  liNum.className = "list-group-item list-group-item-action text-primary";
  liNum.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant)</b>`;
  liNum.onclick = () => {
    let numVal = prompt("Enter number value:", "20");
    if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
      setIndicatorConfigOnRow(MODAL_ROW_IDX, MODAL_TARGET, {
        type: "number",
        value: numVal,
      });
      bootstrap.Modal.getInstance(
        document.getElementById("indicatorModal")
      ).hide();
    }
  };
  list.appendChild(liNum);

  // All indicators (use short name in value)
  INDICATORS.filter(
    (ind) =>
      ind.label.toLowerCase().includes(val) ||
      ind.value.toLowerCase().includes(val)
  ).forEach((ind) => {
    let li = document.createElement("li");
    li.className = "list-group-item list-group-item-action";
    li.innerHTML = `<span style="font-size:1.1em;">📊</span> <b>${ind.value}</b> <span style="font-size:0.95em;color:#555;">(${ind.label})</span>`;
    li.onclick = () => {
      MODAL_INDICATOR = ind;
      openIndicatorConfigModal(MODAL_ROW_IDX, MODAL_TARGET, ind);
      bootstrap.Modal.getInstance(
        document.getElementById("indicatorModal")
      ).hide();
    };
    list.appendChild(li);
  });
}
document.getElementById("indicatorSearch").oninput = renderIndicatorModal;

// ---- Indicator Config Modal ----

function openIndicatorConfigModal(idx, target, indicator, focusField = null) {
  MODAL_FOCUS_FIELD = focusField;
  document.getElementById(
    "indicatorConfigModalLabel"
  ).innerText = `Configure ${indicator.value}`;
  document.getElementById("indicatorConfigTimeframe").value = "Daily";
  document.getElementById("indicatorConfigField").value = "Close";
  let hasPeriod = !["VWAP", "OBV", "AD"].includes(indicator.value); // Tweak per-indicator if needed
  document.getElementById("indicatorConfigPeriodGroup").style.display =
    hasPeriod ? "block" : "none";
  document.getElementById("indicatorConfigPeriod").value = "20";
  setTimeout(() => {
    if (focusField === "timeframe")
      document.getElementById("indicatorConfigTimeframe").focus();
    if (focusField === "field")
      document.getElementById("indicatorConfigField").focus();
    if (focusField === "period")
      document.getElementById("indicatorConfigPeriod").focus();
  }, 350);

  document.getElementById("indicatorConfigDone").onclick = function () {
    let config = {
      type: "indicator",
      value: indicator.value,
      label: indicator.label,
      timeframe: document.getElementById("indicatorConfigTimeframe").value,
      field: document.getElementById("indicatorConfigField").value,
      period: hasPeriod
        ? document.getElementById("indicatorConfigPeriod").value
        : "",
    };
    setIndicatorConfigOnRow(idx, target, config);
    bootstrap.Modal.getInstance(
      document.getElementById("indicatorConfigModal")
    ).hide();
  };
  let modal = new bootstrap.Modal(
    document.getElementById("indicatorConfigModal")
  );
  modal.show();
}

// Used for edits
function openPartialIndicatorConfigModal(idx, side, focusField) {
  let indicator = window.filters[idx][side];
  document.getElementById(
    "indicatorConfigModalLabel"
  ).innerText = `Edit ${indicator.value}`;
  document.getElementById("indicatorConfigTimeframe").value =
    indicator.timeframe;
  document.getElementById("indicatorConfigField").value = indicator.field;
  document.getElementById("indicatorConfigPeriod").value = indicator.period;
  document.getElementById("indicatorConfigPeriodGroup").style.display = "block";
  setTimeout(() => {
    if (focusField === "timeframe")
      document.getElementById("indicatorConfigTimeframe").focus();
    if (focusField === "field")
      document.getElementById("indicatorConfigField").focus();
    if (focusField === "period")
      document.getElementById("indicatorConfigPeriod").focus();
  }, 350);

  document.getElementById("indicatorConfigDone").onclick = function () {
    indicator.timeframe = document.getElementById(
      "indicatorConfigTimeframe"
    ).value;
    indicator.field = document.getElementById("indicatorConfigField").value;
    indicator.period = document.getElementById("indicatorConfigPeriod").value;
    renderFilters();
    bootstrap.Modal.getInstance(
      document.getElementById("indicatorConfigModal")
    ).hide();
  };
  let modal = new bootstrap.Modal(
    document.getElementById("indicatorConfigModal")
  );
  modal.show();
}

function setIndicatorConfigOnRow(idx, target, config) {
  if (target === "left") {
    window.filters[idx].left = config;
    window.filters[idx].step = 2;
  } else {
    window.filters[idx].right = config;
    window.filters[idx].step = 4;
  }
  renderFilters();
  if (window.filters[idx].step === 2) openOperatorModal(idx);
}

// ---- Operator Modal ----

window.openOperatorModal = openOperatorModal;
function openOperatorModal(idx) {
  MODAL_ROW_IDX = idx;
  renderOperatorModal();
  let modal = new bootstrap.Modal(document.getElementById("operatorModal"));
  modal.show();
}
function renderOperatorModal() {
  const list = document.getElementById("operatorList");
  list.innerHTML = "";
  OPERATORS.forEach((op) => {
    let li = document.createElement("li");
    li.className = "list-group-item list-group-item-action";
    li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b>`;
    li.onclick = () => {
      setOperatorOnRow(MODAL_ROW_IDX, op.value);
      bootstrap.Modal.getInstance(
        document.getElementById("operatorModal")
      ).hide();
    };
    list.appendChild(li);
  });
}
function setOperatorOnRow(idx, op) {
  window.filters[idx].op = op;
  window.filters[idx].step = 3;
  renderFilters();
  openIndicatorModal(idx, "right");
}

// ---- Editable Token Logic ----

window.editToken = function (side, tokenType, idx) {
  let f = window.filters[idx];
  let val = f[side];
  if (!val) return;

  if (tokenType === "indicator") {
    openIndicatorModal(idx, side);
  } else if (
    tokenType === "timeframe" ||
    tokenType === "field" ||
    tokenType === "period"
  ) {
    openPartialIndicatorConfigModal(idx, side, tokenType);
  } else if (tokenType === "number") {
    let numVal = prompt("Edit number:", val.value);
    if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
      window.filters[idx][side].value = numVal;
      renderFilters();
    }
  }
};

function renderFilters() {
  const filterList = document.getElementById("filter-list");
  filterList.innerHTML = "";
  window.filters.forEach((f, idx) => {
    filterList.appendChild(renderFilterRow(f, idx));
  });
}
window.removeFilter = removeFilter;
renderFilters();

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

// Function to render scan results (made global for access from dashboard.js)
window.renderResultsTable = function (matches) {
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
};
