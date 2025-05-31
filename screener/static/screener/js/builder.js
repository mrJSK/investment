// // // let INDICATORS = [];
// // // const OPERATORS = [
// // //   { value: "==", label: "Equals", icon: "＝" },
// // //   { value: "!=", label: "Not equals", icon: "≠" },
// // //   { value: ">", label: "Greater than", icon: "＞" },
// // //   { value: ">=", label: "Greater than equal to", icon: "≥" },
// // //   { value: "<", label: "Less than", icon: "＜" },
// // //   { value: "<=", label: "Less than equal to", icon: "≤" },
// // //   { value: "crosses above", label: "Crossed above", icon: "⤴️" },
// // //   { value: "crosses below", label: "Crossed below", icon: "⤵️" },
// // // ];
// // // const TIMEFRAMES = ["Daily", "Weekly", "15min"];
// // // const FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// // // let filters = [];
// // // let filterId = 0;
// // // let MODAL_ROW_IDX = null;
// // // let MODAL_TARGET = null;
// // // let MODAL_INDICATOR = null;
// // // let MODAL_FOCUS_FIELD = null;

// // // function fetchIndicatorsAndRender() {
// // //   fetch("/screener/api/indicators/")
// // //     .then((res) => res.json())
// // //     .then((data) => {
// // //       INDICATORS = data.indicators || [];
// // //       renderFilters();
// // //     });
// // // }
// // // fetchIndicatorsAndRender();

// // // document.getElementById("add-filter").onclick = function () {
// // //   filters.push({ id: ++filterId, step: 1, left: null, op: null, right: null });
// // //   renderFilters();
// // //   openIndicatorModal(filters.length - 1, "left");
// // // };

// // // function renderFilterRow(f, idx) {
// // //   const row = document.createElement("div");
// // //   row.className = "filter-row";
// // //   let html = "";

// // //   // Step-by-step builder logic
// // //   if (f.step === 1) {
// // //     html += `<button class="builder-token token-indicator" onclick="openIndicatorModal(${idx}, 'left')" title="Pick indicator/number">
// // //       <span style="font-size:1.1em;">📊</span> Select Indicator/Number
// // //     </button>`;
// // //   } else if (f.step === 2) {
// // //     html +=
// // //       showIndicatorOrNumber(f.left, "left", idx) +
// // //       `<button class="token-mini token-op" onclick="openOperatorModal(${idx})" title="Pick operator" style="margin-left:8px;">
// // //         <span style="font-size:1.1em;">${getOperatorIcon(f.op)}</span>
// // //         ${f.op ? getOperatorLabel(f.op) : "?"}
// // //       </button>`;
// // //   } else if (f.step === 3) {
// // //     html +=
// // //       showIndicatorOrNumber(f.left, "left", idx) +
// // //       `<button class="token-mini token-op" onclick="openOperatorModal(${idx})" title="Edit operator" style="margin-left:6px;margin-right:6px;">
// // //         <span style="font-size:1.1em;">${getOperatorIcon(f.op)}</span>
// // //         ${getOperatorLabel(f.op)}
// // //       </button>` +
// // //       showIndicatorOrNumber(f.right, "right", idx, true);
// // //   } else if (f.step === 4) {
// // //     html +=
// // //       showIndicatorOrNumber(f.left, "left", idx) +
// // //       `<button class="token-mini token-op" onclick="openOperatorModal(${idx})" title="Edit operator" style="margin-left:6px;margin-right:6px;">
// // //         <span style="font-size:1.1em;">${getOperatorIcon(f.op)}</span>
// // //         ${getOperatorLabel(f.op)}
// // //       </button>` +
// // //       showIndicatorOrNumber(f.right, "right", idx, true) +
// // //       `<button class="icon-btn" style="margin-left:12px;" title="Copy filter">&#128203;</button>
// // //        <button class="icon-btn" title="Enable/Disable">&#128994;</button>`;
// // //   }
// // //   html += `<button class="remove-filter-btn icon-btn" title="Delete Filter" style="margin-left:8px;" onclick="removeFilter(${idx})">🗑️</button>`;
// // //   row.innerHTML = html;
// // //   return row;
// // // }

// // // function showIndicatorOrNumber(val, side, idx, allowEmpty = false) {
// // //   if (!val && !allowEmpty) return "";
// // //   if (val && val.type === "indicator") {
// // //     // Formula tokens: each part clickable
// // //     return `
// // //       <span class="token-ind-formula">
// // //         <button class="token-mini token-tf" onclick="editToken('${side}','timeframe',${idx})">${val.timeframe}</button>
// // //         <button class="token-mini token-ind" onclick="editToken('${side}','indicator',${idx})">${val.value}</button>
// // //         (<button class="token-mini token-field" onclick="editToken('${side}','field',${idx})">${val.field}</button>
// // //         , <button class="token-mini token-per" onclick="editToken('${side}','period',${idx})">${val.period}</button>)
// // //       </span>
// // //     `;
// // //   } else if (val && val.type === "number") {
// // //     return `<span class="token-number">
// // //       <button class="token-mini token-num" onclick="editToken('${side}','number',${idx})">${val.value}</button>
// // //     </span>`;
// // //   } else if (allowEmpty) {
// // //     // Allow for right-side to show "Select Indicator/Number" if empty
// // //     return `<button class="builder-token token-indicator" onclick="openIndicatorModal(${idx}, '${side}')" title="Pick indicator/number">
// // //       <span style="font-size:1.1em;">📊</span> Select Indicator/Number
// // //     </button>`;
// // //   }
// // //   return "";
// // // }
// // // function getOperatorLabel(op) {
// // //   let x = OPERATORS.find((o) => o.value === op);
// // //   return x ? x.label : op;
// // // }
// // // function getOperatorIcon(op) {
// // //   let x = OPERATORS.find((o) => o.value === op);
// // //   return x ? x.icon : "";
// // // }
// // // function removeFilter(idx) {
// // //   filters.splice(idx, 1);
// // //   renderFilters();
// // // }

// // // window.openIndicatorModal = openIndicatorModal;
// // // function openIndicatorModal(idx, target) {
// // //   MODAL_ROW_IDX = idx;
// // //   MODAL_TARGET = target;
// // //   document.getElementById("indicatorSearch").value = "";
// // //   renderIndicatorModal();
// // //   let modal = new bootstrap.Modal(document.getElementById("indicatorModal"));
// // //   modal.show();
// // // }
// // // function renderIndicatorModal() {
// // //   const searchInput = document.getElementById("indicatorSearch");
// // //   const list = document.getElementById("indicatorList");
// // //   let val = (searchInput.value || "").toLowerCase();
// // //   list.innerHTML = "";

// // //   // NUMBER/CONSTANT always first
// // //   let liNum = document.createElement("li");
// // //   liNum.className = "list-group-item list-group-item-action text-primary";
// // //   liNum.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant)</b>`;
// // //   liNum.onclick = () => {
// // //     let numVal = prompt("Enter number value:", "20");
// // //     if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
// // //       setIndicatorConfigOnRow(MODAL_ROW_IDX, MODAL_TARGET, {
// // //         type: "number",
// // //         value: numVal,
// // //       });
// // //       bootstrap.Modal.getInstance(
// // //         document.getElementById("indicatorModal")
// // //       ).hide();
// // //     }
// // //   };
// // //   list.appendChild(liNum);

// // //   // All indicators (use short name in value)
// // //   INDICATORS.filter(
// // //     (ind) =>
// // //       ind.label.toLowerCase().includes(val) ||
// // //       ind.value.toLowerCase().includes(val)
// // //   ).forEach((ind) => {
// // //     let li = document.createElement("li");
// // //     li.className = "list-group-item list-group-item-action";
// // //     li.innerHTML = `<span style="font-size:1.1em;">📊</span> <b>${ind.value}</b> <span style="font-size:0.95em;color:#555;">(${ind.label})</span>`;
// // //     li.onclick = () => {
// // //       MODAL_INDICATOR = ind;
// // //       openIndicatorConfigModal(MODAL_ROW_IDX, MODAL_TARGET, ind);
// // //       bootstrap.Modal.getInstance(
// // //         document.getElementById("indicatorModal")
// // //       ).hide();
// // //     };
// // //     list.appendChild(li);
// // //   });
// // // }
// // // document.getElementById("indicatorSearch").oninput = renderIndicatorModal;

// // // // ---- Indicator Config Modal ----

// // // function openIndicatorConfigModal(idx, target, indicator, focusField = null) {
// // //   MODAL_FOCUS_FIELD = focusField;
// // //   document.getElementById(
// // //     "indicatorConfigModalLabel"
// // //   ).innerText = `Configure ${indicator.value}`;
// // //   document.getElementById("indicatorConfigTimeframe").value = "Daily";
// // //   document.getElementById("indicatorConfigField").value = "Close";
// // //   let hasPeriod = !["VWAP", "OBV", "AD"].includes(indicator.value); // Tweak per-indicator if needed
// // //   document.getElementById("indicatorConfigPeriodGroup").style.display =
// // //     hasPeriod ? "block" : "none";
// // //   document.getElementById("indicatorConfigPeriod").value = "20";
// // //   setTimeout(() => {
// // //     if (focusField === "timeframe")
// // //       document.getElementById("indicatorConfigTimeframe").focus();
// // //     if (focusField === "field")
// // //       document.getElementById("indicatorConfigField").focus();
// // //     if (focusField === "period")
// // //       document.getElementById("indicatorConfigPeriod").focus();
// // //   }, 350);

// // //   document.getElementById("indicatorConfigDone").onclick = function () {
// // //     let config = {
// // //       type: "indicator",
// // //       value: indicator.value,
// // //       label: indicator.label,
// // //       timeframe: document.getElementById("indicatorConfigTimeframe").value,
// // //       field: document.getElementById("indicatorConfigField").value,
// // //       period: hasPeriod
// // //         ? document.getElementById("indicatorConfigPeriod").value
// // //         : "",
// // //     };
// // //     setIndicatorConfigOnRow(idx, target, config);
// // //     bootstrap.Modal.getInstance(
// // //       document.getElementById("indicatorConfigModal")
// // //     ).hide();
// // //   };
// // //   let modal = new bootstrap.Modal(
// // //     document.getElementById("indicatorConfigModal")
// // //   );
// // //   modal.show();
// // // }

// // // // Used for edits
// // // function openPartialIndicatorConfigModal(idx, side, focusField) {
// // //   let indicator = filters[idx][side];
// // //   // Populate modal with existing values
// // //   document.getElementById(
// // //     "indicatorConfigModalLabel"
// // //   ).innerText = `Edit ${indicator.value}`;
// // //   document.getElementById("indicatorConfigTimeframe").value =
// // //     indicator.timeframe;
// // //   document.getElementById("indicatorConfigField").value = indicator.field;
// // //   document.getElementById("indicatorConfigPeriod").value = indicator.period;
// // //   document.getElementById("indicatorConfigPeriodGroup").style.display = "block";
// // //   setTimeout(() => {
// // //     if (focusField === "timeframe")
// // //       document.getElementById("indicatorConfigTimeframe").focus();
// // //     if (focusField === "field")
// // //       document.getElementById("indicatorConfigField").focus();
// // //     if (focusField === "period")
// // //       document.getElementById("indicatorConfigPeriod").focus();
// // //   }, 350);

// // //   document.getElementById("indicatorConfigDone").onclick = function () {
// // //     indicator.timeframe = document.getElementById(
// // //       "indicatorConfigTimeframe"
// // //     ).value;
// // //     indicator.field = document.getElementById("indicatorConfigField").value;
// // //     indicator.period = document.getElementById("indicatorConfigPeriod").value;
// // //     // DO NOT reset filters[idx] or step here!
// // //     renderFilters();
// // //     bootstrap.Modal.getInstance(
// // //       document.getElementById("indicatorConfigModal")
// // //     ).hide();
// // //   };
// // //   let modal = new bootstrap.Modal(
// // //     document.getElementById("indicatorConfigModal")
// // //   );
// // //   modal.show();
// // // }

// // // function setIndicatorConfigOnRow(idx, target, config) {
// // //   if (target === "left") {
// // //     filters[idx].left = config;
// // //     filters[idx].step = 2;
// // //   } else {
// // //     filters[idx].right = config;
// // //     filters[idx].step = 4;
// // //   }
// // //   renderFilters();
// // //   if (filters[idx].step === 2) openOperatorModal(idx);
// // // }

// // // // ---- Operator Modal ----

// // // window.openOperatorModal = openOperatorModal;
// // // function openOperatorModal(idx) {
// // //   MODAL_ROW_IDX = idx;
// // //   renderOperatorModal();
// // //   let modal = new bootstrap.Modal(document.getElementById("operatorModal"));
// // //   modal.show();
// // // }
// // // function renderOperatorModal() {
// // //   const list = document.getElementById("operatorList");
// // //   list.innerHTML = "";
// // //   OPERATORS.forEach((op) => {
// // //     let li = document.createElement("li");
// // //     li.className = "list-group-item list-group-item-action";
// // //     li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b>`;
// // //     li.onclick = () => {
// // //       setOperatorOnRow(MODAL_ROW_IDX, op.value);
// // //       bootstrap.Modal.getInstance(
// // //         document.getElementById("operatorModal")
// // //       ).hide();
// // //     };
// // //     list.appendChild(li);
// // //   });
// // // }
// // // function setOperatorOnRow(idx, op) {
// // //   filters[idx].op = op;
// // //   filters[idx].step = 3;
// // //   renderFilters();
// // //   openIndicatorModal(idx, "right");
// // // }

// // // // ---- Editable Token Logic ----

// // // window.editToken = function (side, tokenType, idx) {
// // //   let f = filters[idx];
// // //   let val = f[side];
// // //   if (!val) return;

// // //   if (tokenType === "indicator") {
// // //     openIndicatorModal(idx, side); // Will set new indicator and update in place
// // //   } else if (
// // //     tokenType === "timeframe" ||
// // //     tokenType === "field" ||
// // //     tokenType === "period"
// // //   ) {
// // //     // Open config modal with *existing* indicator config, don't delete or reset!
// // //     openPartialIndicatorConfigModal(idx, side, tokenType);
// // //   } else if (tokenType === "number") {
// // //     let numVal = prompt("Edit number:", val.value);
// // //     if (numVal !== null && numVal !== "" && !isNaN(numVal)) {
// // //       filters[idx][side].value = numVal;
// // //       renderFilters();
// // //     }
// // //   }
// // // };

// // // function renderFilters() {
// // //   const filterList = document.getElementById("filter-list");
// // //   filterList.innerHTML = "";
// // //   filters.forEach((f, idx) => {
// // //     filterList.appendChild(renderFilterRow(f, idx));
// // //   });
// // // }
// // // window.removeFilter = removeFilter;
// // // renderFilters();
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

// // // Utility to safely attach events
// // function attachEvent(element, event, handler) {
// //   element.addEventListener(event, handler);
// // }

// // // Fetch indicators from backend and render builder
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

// //   // LEFT SIDE
// //   if (f.left && f.left.type === "indicator") {
// //     let span = document.createElement("span");
// //     span.className = "token-ind-formula";
// //     // Timeframe
// //     let btnTf = document.createElement("button");
// //     btnTf.className = "token-mini token-tf";
// //     btnTf.textContent = f.left.timeframe;
// //     btnTf.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openPartialIndicatorConfigModal(idx, "left", "timeframe");
// //     });
// //     // Indicator
// //     let btnInd = document.createElement("button");
// //     btnInd.className = "token-mini token-ind";
// //     btnInd.textContent = f.left.value;
// //     btnInd.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openIndicatorModal(idx, "left");
// //     });
// //     // (
// //     let txtOpen = document.createTextNode("(");
// //     // Field
// //     let btnField = document.createElement("button");
// //     btnField.className = "token-mini token-field";
// //     btnField.textContent = f.left.field;
// //     btnField.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openPartialIndicatorConfigModal(idx, "left", "field");
// //     });
// //     // ,
// //     let txtComma = document.createTextNode(", ");
// //     // Period
// //     let btnPeriod = document.createElement("button");
// //     btnPeriod.className = "token-mini token-per";
// //     btnPeriod.textContent = f.left.period;
// //     btnPeriod.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openPartialIndicatorConfigModal(idx, "left", "period");
// //     });
// //     // )
// //     let txtClose = document.createTextNode(")");
// //     // Assemble
// //     span.append(
// //       btnTf,
// //       btnInd,
// //       txtOpen,
// //       btnField,
// //       txtComma,
// //       btnPeriod,
// //       txtClose
// //     );
// //     row.appendChild(span);
// //   } else if (f.left && f.left.type === "number") {
// //     let span = document.createElement("span");
// //     span.className = "token-number";
// //     let btnNum = document.createElement("button");
// //     btnNum.className = "token-mini token-num";
// //     btnNum.textContent = f.left.value;
// //     btnNum.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       editToken("left", "number", idx);
// //     });
// //     span.appendChild(btnNum);
// //     row.appendChild(span);
// //   } else {
// //     let btn = document.createElement("button");
// //     btn.className = "builder-token token-indicator";
// //     btn.innerHTML = `<span style="font-size:1.1em;">📊</span> Select Indicator/Number`;
// //     btn.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openIndicatorModal(idx, "left");
// //     });
// //     row.appendChild(btn);
// //   }

// //   // OPERATOR
// //   let btnOp = document.createElement("button");
// //   btnOp.className = "token-mini token-op";
// //   btnOp.textContent = f.op ? getOperatorLabel(f.op) : "?";
// //   btnOp.addEventListener("click", (e) => {
// //     e.stopPropagation();
// //     openOperatorModal(idx);
// //   });
// //   row.appendChild(btnOp);

// //   // RIGHT SIDE
// //   if (f.right && f.right.type === "indicator") {
// //     let span = document.createElement("span");
// //     span.className = "token-ind-formula";
// //     // Timeframe
// //     let btnTf = document.createElement("button");
// //     btnTf.className = "token-mini token-tf";
// //     btnTf.textContent = f.right.timeframe;
// //     btnTf.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openPartialIndicatorConfigModal(idx, "right", "timeframe");
// //     });
// //     // Indicator
// //     let btnInd = document.createElement("button");
// //     btnInd.className = "token-mini token-ind";
// //     btnInd.textContent = f.right.value;
// //     btnInd.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openIndicatorModal(idx, "right");
// //     });
// //     // (
// //     let txtOpen = document.createTextNode("(");
// //     // Field
// //     let btnField = document.createElement("button");
// //     btnField.className = "token-mini token-field";
// //     btnField.textContent = f.right.field;
// //     btnField.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openPartialIndicatorConfigModal(idx, "right", "field");
// //     });
// //     // ,
// //     let txtComma = document.createTextNode(", ");
// //     // Period
// //     let btnPeriod = document.createElement("button");
// //     btnPeriod.className = "token-mini token-per";
// //     btnPeriod.textContent = f.right.period;
// //     btnPeriod.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openPartialIndicatorConfigModal(idx, "right", "period");
// //     });
// //     // )
// //     let txtClose = document.createTextNode(")");
// //     // Assemble
// //     span.append(
// //       btnTf,
// //       btnInd,
// //       txtOpen,
// //       btnField,
// //       txtComma,
// //       btnPeriod,
// //       txtClose
// //     );
// //     row.appendChild(span);
// //   } else if (f.right && f.right.type === "number") {
// //     let span = document.createElement("span");
// //     span.className = "token-number";
// //     let btnNum = document.createElement("button");
// //     btnNum.className = "token-mini token-num";
// //     btnNum.textContent = f.right.value;
// //     btnNum.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       editToken("right", "number", idx);
// //     });
// //     span.appendChild(btnNum);
// //     row.appendChild(span);
// //   } else if (f.step >= 3) {
// //     let btn = document.createElement("button");
// //     btn.className = "builder-token token-indicator";
// //     btn.innerHTML = `<span style="font-size:1.1em;">📊</span> Select Indicator/Number`;
// //     btn.addEventListener("click", (e) => {
// //       e.stopPropagation();
// //       openIndicatorModal(idx, "right");
// //     });
// //     row.appendChild(btn);
// //   }

// //   // ACTIONS: Delete
// //   let delBtn = document.createElement("button");
// //   delBtn.className = "remove-filter-btn icon-btn";
// //   delBtn.title = "Delete Filter";
// //   delBtn.style.marginLeft = "8px";
// //   delBtn.innerHTML = "🗑️";
// //   delBtn.addEventListener("click", (e) => {
// //     e.stopPropagation();
// //     removeFilter(idx);
// //   });
// //   row.appendChild(delBtn);

// //   // (Optional: Copy/Toggle buttons can be added similarly here.)

// //   return row;
// // }

// // function showIndicatorOrNumber(val, side, idx, allowEmpty = false) {
// //   if (!val && !allowEmpty) return "";
// //   if (val && val.type === "indicator") {
// //     // Use span and button for each token, no inline handlers
// //     return `
// //       <span class="token-ind-formula">
// //         <button class="token-mini token-tf">${val.timeframe}</button>
// //         <button class="token-mini token-ind">${val.value}</button>
// //         (<button class="token-mini token-field">${val.field}</button>
// //         , <button class="token-mini token-per">${val.period}</button>)
// //       </span>
// //     `;
// //   } else if (val && val.type === "number") {
// //     return `<span class="token-number">
// //       <button class="token-mini token-num">${val.value}</button>
// //     </span>`;
// //   } else if (allowEmpty) {
// //     return `<button class="builder-token token-indicator" title="Pick indicator/number">
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
// //     openIndicatorModal(idx, side);
// //   } else if (
// //     tokenType === "timeframe" ||
// //     tokenType === "field" ||
// //     tokenType === "period"
// //   ) {
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

// // Make filters global so dashboard.js can access it
// window.filters = [];
// let filterId = 0;
// let MODAL_ROW_IDX = null;
// let MODAL_TARGET = null;
// let MODAL_INDICATOR = null;
// let MODAL_FOCUS_FIELD = null;

// // Utility to safely attach events (not strictly used here, but good to keep)
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
//   window.filters.push({
//     id: ++filterId,
//     step: 1,
//     left: null,
//     op: null,
//     right: null,
//   });
//   renderFilters();
//   openIndicatorModal(window.filters.length - 1, "left");
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

//   return row;
// }

// function showIndicatorOrNumber(val, side, idx, allowEmpty = false) {
//   if (!val && !allowEmpty) return "";
//   if (val && val.type === "indicator") {
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
//   window.filters.splice(idx, 1);
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
//   let indicator = window.filters[idx][side];
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
//     window.filters[idx].left = config;
//     window.filters[idx].step = 2;
//   } else {
//     window.filters[idx].right = config;
//     window.filters[idx].step = 4;
//   }
//   renderFilters();
//   if (window.filters[idx].step === 2) openOperatorModal(idx);
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
//   window.filters[idx].op = op;
//   window.filters[idx].step = 3;
//   renderFilters();
//   openIndicatorModal(idx, "right");
// }

// // ---- Editable Token Logic ----

// window.editToken = function (side, tokenType, idx) {
//   let f = window.filters[idx];
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
//       window.filters[idx][side].value = numVal;
//       renderFilters();
//     }
//   }
// };

// function renderFilters() {
//   const filterList = document.getElementById("filter-list");
//   filterList.innerHTML = "";
//   window.filters.forEach((f, idx) => {
//     filterList.appendChild(renderFilterRow(f, idx));
//   });
// }
// window.removeFilter = removeFilter;
// renderFilters();

// // CSRF utility, add if not already present:
// function getCookie(name) {
//   let cookieValue = null;
//   if (document.cookie && document.cookie !== "") {
//     const cookies = document.cookie.split(";");
//     for (let i = 0; i < cookies.length; i++) {
//       const cookie = cookies[i].trim();
//       if (cookie.substring(0, name.length + 1) === name + "=") {
//         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//         break;
//       }
//     }
//   }
//   return cookieValue;
// }

// // Function to render scan results (made global for access from dashboard.js)
// window.renderResultsTable = function (matches) {
//   let html = "";
//   if (!matches || matches.length === 0) {
//     html = `<tr><td colspan="7" class="text-center py-4 text-muted">No results yet.</td></tr>`;
//   } else {
//     matches.forEach((row, i) => {
//       html += `<tr>
//         <td>${i + 1}</td>
//         <td>${row.symbol || row}</td>
//         <td>${row.last_price !== undefined ? row.last_price : ""}</td>
//         <td>${row.change_pct !== undefined ? row.change_pct : ""}</td>
//         <td>${row.volume !== undefined ? row.volume : ""}</td>
//         <td>✔️</td>
//         <td></td>
//       </tr>`;
//     });
//   }
//   document.getElementById("resultsBody").innerHTML = html;
// };
// --- Constants ---
let INDICATORS = [
  // Mock data - replace with actual API call if needed
  { value: "CLOSE", label: "Close Price", params: ["timeframe"] },
  { value: "OPEN", label: "Open Price", params: ["timeframe"] },
  { value: "HIGH", label: "High Price", params: ["timeframe"] },
  { value: "LOW", label: "Low Price", params: ["timeframe"] },
  { value: "VOLUME", label: "Volume", params: ["timeframe"] },
  {
    value: "SMA",
    label: "Simple Moving Average",
    params: ["timeframe", "field", "period"],
  },
  {
    value: "EMA",
    label: "Exponential Moving Average",
    params: ["timeframe", "field", "period"],
  },
  {
    value: "RSI",
    label: "Relative Strength Index",
    params: ["timeframe", "field", "period"],
  }, // Typically field is Close for RSI
  {
    value: "MACD_LINE",
    label: "MACD Line",
    params: [
      "timeframe",
      "field",
      "fast_period",
      "slow_period",
      "signal_period",
    ],
  }, // Simplified display
  {
    value: "MACD_SIGNAL",
    label: "MACD Signal Line",
    params: [
      "timeframe",
      "field",
      "fast_period",
      "slow_period",
      "signal_period",
    ],
  },
  {
    value: "VWAP",
    label: "Volume Weighted Average Price",
    params: ["timeframe"],
  },
  {
    value: "SUPERTREND",
    label: "Supertrend",
    params: ["timeframe", "period", "multiplier"],
  },
  // Add more indicators with their typical parameters
];

const OPERATORS = [
  { value: ">", label: "Greater than", icon: "＞" },
  { value: ">=", label: "Greater than or equal to", icon: "≥" },
  { value: "<", label: "Less than", icon: "＜" },
  { value: "<=", label: "Less than or equal to", icon: "≤" },
  { value: "==", label: "Equals", icon: "＝" },
  { value: "!=", label: "Not equals", icon: "≠" },
  { value: "crosses_above", label: "Crosses above", icon: "⤴️" },
  { value: "crosses_below", label: "Crosses below", icon: "⤵️" },
];

const TIMEFRAMES = [
  "Daily",
  "Weekly",
  "Monthly",
  "1hour",
  "30min",
  "15min",
  "5min",
  "1min",
];
const FIELDS = ["Open", "High", "Low", "Close", "Volume"]; // For indicators that use a field

// --- Global State ---
window.filters = []; // Array to hold filter condition objects
let filterIdCounter = 0; // To give unique IDs to filters if needed for complex logic

// Modal-related state
let CURRENT_MODAL_FILTER_INDEX = null;
let CURRENT_MODAL_TARGET_SIDE = null; // 'left' or 'right'
let CURRENT_MODAL_INDICATOR_DEF = null; // The definition from INDICATORS array

// Bootstrap Modal Instances (initialize after DOM is ready)
let indicatorModalInstance, indicatorConfigModalInstance, operatorModalInstance;

// --- DOM Elements ---
const filterListContainer = document.getElementById("filter-list");
const addFilterButton = document.getElementById("add-filter");

// Indicator Modal Elements
const indicatorSearchInput = document.getElementById("indicatorSearch");
const indicatorListUl = document.getElementById("indicatorList");

// Indicator Config Modal Elements
const indicatorConfigModalLabel = document.getElementById(
  "indicatorConfigModalLabelText"
);
const indicatorConfigTimeframeSelect = document.getElementById(
  "indicatorConfigTimeframe"
);
const indicatorConfigFieldSelect = document.getElementById(
  "indicatorConfigField"
);
const indicatorConfigPeriodGroup = document.getElementById(
  "indicatorConfigPeriodGroup"
);
const indicatorConfigPeriodInput = document.getElementById(
  "indicatorConfigPeriod"
);
const indicatorConfigDoneButton = document.getElementById(
  "indicatorConfigDone"
);
// Add more config fields here if indicators have more diverse params like fast_period, slow_period, multiplier

// Operator Modal Elements
const operatorListUl = document.getElementById("operatorList");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  // Initialize Bootstrap Modals
  indicatorModalInstance = new bootstrap.Modal(
    document.getElementById("indicatorModal")
  );
  indicatorConfigModalInstance = new bootstrap.Modal(
    document.getElementById("indicatorConfigModal")
  );
  operatorModalInstance = new bootstrap.Modal(
    document.getElementById("operatorModal")
  );

  // Populate static dropdowns in config modal
  TIMEFRAMES.forEach((tf) => {
    indicatorConfigTimeframeSelect.options.add(new Option(tf, tf));
  });
  FIELDS.forEach((f) => {
    indicatorConfigFieldSelect.options.add(new Option(f, f));
  });

  // Attach event listeners
  addFilterButton.addEventListener("click", handleAddFilter);
  indicatorSearchInput.addEventListener("input", renderIndicatorModalList);
  indicatorConfigDoneButton.addEventListener(
    "click",
    handleIndicatorConfigDone
  );

  // Initial render (e.g., load saved filters or start fresh)
  renderFilters();
  // fetchIndicatorsAndRender(); // If you have a backend for indicators
});

// --- Core Filter Management ---
function handleAddFilter() {
  window.filters.push({
    id: ++filterIdCounter,
    step: 1, // To guide initial selection: 1 for left, 2 for op, 3 for right
    left: null, // { type: 'indicator'/'number', value: ..., params: {...} }
    op: null, // operator value string
    right: null, // { type: 'indicator'/'number', value: ..., params: {...} }
  });
  renderFilters();
  // Directly open modal to select the left operand for the new filter
  openIndicatorPickerModal(window.filters.length - 1, "left");
}

function removeFilter(filterIndex) {
  window.filters.splice(filterIndex, 1);
  renderFilters();
}

function renderFilters() {
  filterListContainer.innerHTML = ""; // Clear existing filters
  window.filters.forEach((filter, index) => {
    filterListContainer.appendChild(createFilterRowElement(filter, index));
  });
}

// --- Filter Row Element Creation (Tokenized Display) ---
function createFilterRowElement(filter, filterIndex) {
  const rowDiv = document.createElement("div");
  rowDiv.className = "filter-row-tokenized";

  // 1. Left Operand
  if (filter.left) {
    rowDiv.appendChild(createOperandToken(filter.left, "left", filterIndex));
  } else {
    const addLeftBtn = createButtonToken(
      "📊 Select Indicator/Number",
      "builder-token",
      () => openIndicatorPickerModal(filterIndex, "left")
    );
    rowDiv.appendChild(addLeftBtn);
  }

  // 2. Operator
  if (filter.op) {
    const opLabel =
      OPERATORS.find((o) => o.value === filter.op)?.label || filter.op;
    const opIcon = OPERATORS.find((o) => o.value === filter.op)?.icon || "";
    rowDiv.appendChild(
      createButtonToken(`${opIcon} ${opLabel}`, "token-op", () =>
        openOperatorPickerModal(filterIndex)
      )
    );
  } else if (filter.left) {
    // Show operator picker only if left is selected
    rowDiv.appendChild(
      createButtonToken("? Operator", "token-op", () =>
        openOperatorPickerModal(filterIndex)
      )
    );
  }

  // 3. Right Operand
  if (filter.right) {
    rowDiv.appendChild(createOperandToken(filter.right, "right", filterIndex));
  } else if (filter.op) {
    // Show right operand picker only if operator is selected
    const addRightBtn = createButtonToken(
      "📊 Select Indicator/Number",
      "builder-token",
      () => openIndicatorPickerModal(filterIndex, "right")
    );
    rowDiv.appendChild(addRightBtn);
  }

  // Delete button
  const deleteBtn = document.createElement("button");
  deleteBtn.className = "icon-btn remove-filter-btn ms-auto"; // ms-auto for Tailwind-like margin-left: auto
  deleteBtn.innerHTML = `<i class="fas fa-trash-alt"></i>`;
  deleteBtn.title = "Delete Filter";
  deleteBtn.addEventListener("click", () => removeFilter(filterIndex));
  rowDiv.appendChild(deleteBtn);

  return rowDiv;
}

function createOperandToken(operand, side, filterIndex) {
  const wrapperSpan = document.createElement("span");
  wrapperSpan.className = `token-operand-group ${
    operand.type === "indicator" ? "token-ind-formula" : "token-number"
  }`;
  wrapperSpan.classList.add(
    "d-inline-flex",
    "flex-wrap",
    "gap-1",
    "align-items-center"
  );

  if (operand.type === "indicator") {
    const indicatorDef = INDICATORS.find((ind) => ind.value === operand.value);
    // Timeframe (always for indicators conceptually, even if not used by all)
    wrapperSpan.appendChild(
      createButtonToken(
        operand.params.timeframe || "Daily",
        "token-mini token-tf",
        () => openIndicatorConfigEditor(filterIndex, side, "timeframe")
      )
    );

    // Indicator Name
    wrapperSpan.appendChild(
      createButtonToken(operand.value, "token-mini token-ind", () =>
        openIndicatorPickerModal(filterIndex, side)
      )
    ); // Click to change indicator

    if (indicatorDef && indicatorDef.params && indicatorDef.params.length > 0) {
      const requiresParams =
        indicatorDef.params.includes("field") ||
        indicatorDef.params.includes("period") ||
        indicatorDef.params.includes("fast_period"); // etc.
      if (requiresParams) {
        wrapperSpan.appendChild(document.createTextNode("("));
        let firstParam = true;
        if (indicatorDef.params.includes("field")) {
          wrapperSpan.appendChild(
            createButtonToken(
              operand.params.field || "Close",
              "token-mini token-field",
              () => openIndicatorConfigEditor(filterIndex, side, "field")
            )
          );
          firstParam = false;
        }
        if (indicatorDef.params.includes("period")) {
          if (!firstParam)
            wrapperSpan.appendChild(document.createTextNode(","));
          wrapperSpan.appendChild(
            createButtonToken(
              String(operand.params.period || 20),
              "token-mini token-per",
              () => openIndicatorConfigEditor(filterIndex, side, "period")
            )
          );
          firstParam = false;
        }
        // Add other params like fast_period, slow_period, signal_period, multiplier similarly
        // Example for MACD (simplified for brevity)
        if (indicatorDef.params.includes("fast_period")) {
          if (!firstParam)
            wrapperSpan.appendChild(document.createTextNode(","));
          wrapperSpan.appendChild(
            createButtonToken(
              String(operand.params.fast_period || 12),
              "token-mini token-per", // using token-per style for now
              () => openIndicatorConfigEditor(filterIndex, side, "fast_period")
            )
          );
          firstParam = false;
        }
        if (indicatorDef.params.includes("slow_period")) {
          if (!firstParam)
            wrapperSpan.appendChild(document.createTextNode(","));
          wrapperSpan.appendChild(
            createButtonToken(
              String(operand.params.slow_period || 26),
              "token-mini token-per",
              () => openIndicatorConfigEditor(filterIndex, side, "slow_period")
            )
          );
          firstParam = false;
        }
        // Note: Signal period for MACD often isn't edited per-token for simplicity, but could be.

        wrapperSpan.appendChild(document.createTextNode(")"));
      }
    }
  } else if (operand.type === "number") {
    wrapperSpan.appendChild(
      createButtonToken(String(operand.value), "token-mini token-num", () =>
        editNumberToken(filterIndex, side)
      )
    );
  }
  return wrapperSpan;
}

function createButtonToken(text, baseClass, onClickHandler) {
  const button = document.createElement("button");
  button.className = baseClass; // e.g., "token-mini token-tf" or "builder-token"
  button.textContent = text;
  button.addEventListener("click", onClickHandler);
  return button;
}

// --- Modal Opening Functions ---
function openIndicatorPickerModal(filterIndex, targetSide) {
  CURRENT_MODAL_FILTER_INDEX = filterIndex;
  CURRENT_MODAL_TARGET_SIDE = targetSide;
  indicatorSearchInput.value = "";
  renderIndicatorModalList();
  indicatorModalInstance.show();
}

function openOperatorPickerModal(filterIndex) {
  CURRENT_MODAL_FILTER_INDEX = filterIndex;
  renderOperatorModalList();
  operatorModalInstance.show();
}

function openIndicatorConfigEditor(filterIndex, targetSide, focusField = null) {
  // This function is called when clicking an existing indicator's parameter token.
  // It should pre-fill the config modal with current values.
  CURRENT_MODAL_FILTER_INDEX = filterIndex;
  CURRENT_MODAL_TARGET_SIDE = targetSide;

  const currentOperand = window.filters[filterIndex][targetSide];
  if (!currentOperand || currentOperand.type !== "indicator") return;

  CURRENT_MODAL_INDICATOR_DEF = INDICATORS.find(
    (ind) => ind.value === currentOperand.value
  );
  if (!CURRENT_MODAL_INDICATOR_DEF) return; // Should not happen if data is consistent

  indicatorConfigModalLabel.textContent = `Configure ${CURRENT_MODAL_INDICATOR_DEF.label}`;

  // Pre-fill basic fields
  indicatorConfigTimeframeSelect.value =
    currentOperand.params.timeframe || "Daily";
  indicatorConfigFieldSelect.value = currentOperand.params.field || "Close";
  indicatorConfigPeriodInput.value = currentOperand.params.period || "20";
  // Show/hide fields based on CURRENT_MODAL_INDICATOR_DEF.params
  indicatorConfigFieldSelect.closest(".mb-3").style.display =
    CURRENT_MODAL_INDICATOR_DEF.params.includes("field") ? "block" : "none";
  indicatorConfigPeriodGroup.style.display =
    CURRENT_MODAL_INDICATOR_DEF.params.includes("period") ? "block" : "none";
  // Add logic for other params (fast, slow, signal, multiplier) if they exist

  indicatorConfigModalInstance.show();

  // Optional: focus the specific field being edited
  if (focusField === "timeframe") indicatorConfigTimeframeSelect.focus();
  else if (focusField === "field") indicatorConfigFieldSelect.focus();
  else if (focusField === "period") indicatorConfigPeriodInput.focus();
}

function editNumberToken(filterIndex, side) {
  const currentOperand = window.filters[filterIndex][side];
  let newValue = prompt("Enter number:", currentOperand.value);
  if (newValue !== null && !isNaN(parseFloat(newValue))) {
    window.filters[filterIndex][side].value = parseFloat(newValue);
    renderFilters();
  }
}

// --- Modal List Rendering ---
function renderIndicatorModalList() {
  const searchTerm = indicatorSearchInput.value.toLowerCase();
  indicatorListUl.innerHTML = ""; // Clear list

  // Option for "Number (constant)"
  const numLi = document.createElement("li");
  numLi.className = "list-group-item list-group-item-action text-primary"; // Bootstrap classes
  numLi.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant)</b>`;
  numLi.addEventListener("click", () => {
    let numVal = prompt("Enter number value:", "0");
    if (numVal !== null && !isNaN(parseFloat(numVal))) {
      applyOperandSelection({ type: "number", value: parseFloat(numVal) });
      indicatorModalInstance.hide();
    }
  });
  indicatorListUl.appendChild(numLi);

  // Filtered indicators
  INDICATORS.filter(
    (ind) =>
      ind.label.toLowerCase().includes(searchTerm) ||
      ind.value.toLowerCase().includes(searchTerm)
  ).forEach((indicatorDef) => {
    const li = document.createElement("li");
    li.className = "list-group-item list-group-item-action";
    li.innerHTML = `<span style="font-size:1.1em;">📊</span> <b>${indicatorDef.value}</b> <small class="text-muted">(${indicatorDef.label})</small>`;
    li.addEventListener("click", () => {
      CURRENT_MODAL_INDICATOR_DEF = indicatorDef; // Store the selected indicator definition
      indicatorModalInstance.hide();
      // Open config modal for the NEWLY selected indicator
      indicatorConfigModalLabel.textContent = `Configure ${indicatorDef.label}`;
      // Reset/default config modal fields for a new indicator
      indicatorConfigTimeframeSelect.value = "Daily"; // Default
      indicatorConfigFieldSelect.value = "Close"; // Default
      indicatorConfigPeriodInput.value = "20"; // Default

      // Show/hide fields based on CURRENT_MODAL_INDICATOR_DEF.params
      indicatorConfigFieldSelect.closest(".mb-3").style.display =
        CURRENT_MODAL_INDICATOR_DEF.params.includes("field") ? "block" : "none";
      indicatorConfigPeriodGroup.style.display =
        CURRENT_MODAL_INDICATOR_DEF.params.includes("period")
          ? "block"
          : "none";
      // Add logic for other params...

      indicatorConfigModalInstance.show();
    });
    indicatorListUl.appendChild(li);
  });
}

function renderOperatorModalList() {
  operatorListUl.innerHTML = ""; // Clear list
  OPERATORS.forEach((op) => {
    const li = document.createElement("li");
    li.className = "list-group-item list-group-item-action";
    li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b>`;
    li.addEventListener("click", () => {
      applyOperatorSelection(op.value);
      operatorModalInstance.hide();
    });
    operatorListUl.appendChild(li);
  });
}

// --- Modal Submission/Application Logic ---
function handleIndicatorConfigDone() {
  if (
    CURRENT_MODAL_FILTER_INDEX === null ||
    CURRENT_MODAL_TARGET_SIDE === null ||
    CURRENT_MODAL_INDICATOR_DEF === null
  ) {
    console.error("State error in handleIndicatorConfigDone");
    indicatorConfigModalInstance.hide();
    return;
  }

  const params = {
    timeframe: indicatorConfigTimeframeSelect.value,
    // Conditionally add other params based on CURRENT_MODAL_INDICATOR_DEF
  };

  if (CURRENT_MODAL_INDICATOR_DEF.params.includes("field")) {
    params.field = indicatorConfigFieldSelect.value;
  }
  if (CURRENT_MODAL_INDICATOR_DEF.params.includes("period")) {
    params.period = parseInt(indicatorConfigPeriodInput.value, 10) || 20;
  }
  // Add other params like fast_period, slow_period, multiplier from their respective inputs

  const operand = {
    type: "indicator",
    value: CURRENT_MODAL_INDICATOR_DEF.value, // The short name like "SMA"
    label: CURRENT_MODAL_INDICATOR_DEF.label, // Full label
    params: params,
  };

  applyOperandSelection(operand);
  indicatorConfigModalInstance.hide();
}

function applyOperandSelection(operandConfig) {
  // operandConfig is { type: 'indicator'/'number', value: ..., params: (if indicator) }
  const filter = window.filters[CURRENT_MODAL_FILTER_INDEX];
  if (!filter) return;

  filter[CURRENT_MODAL_TARGET_SIDE] = operandConfig;

  // Progress step logic
  if (CURRENT_MODAL_TARGET_SIDE === "left") {
    filter.step = 2; // Move to operator selection
    renderFilters();
    openOperatorPickerModal(CURRENT_MODAL_FILTER_INDEX); // Auto-open operator picker
  } else if (CURRENT_MODAL_TARGET_SIDE === "right") {
    filter.step = 4; // Filter completed (or ready for more actions)
    renderFilters();
  } else {
    renderFilters(); // For edits that don't change step
  }
}

function applyOperatorSelection(operatorValue) {
  const filter = window.filters[CURRENT_MODAL_FILTER_INDEX];
  if (!filter) return;

  filter.op = operatorValue;
  filter.step = 3; // Move to right operand selection
  renderFilters();
  openIndicatorPickerModal(CURRENT_MODAL_FILTER_INDEX, "right"); // Auto-open right operand picker
}

// --- Run Scan (Placeholder) ---
document.getElementById("runScan")?.addEventListener("click", () => {
  console.log(
    "Running scan with filters:",
    JSON.stringify(window.filters, null, 2)
  );
  // Here you would typically send window.filters to your backend
  // and then populate the results table.
  alert("Scan would run now! Check console for filter data.");
  // Example: updateResultsTable([{symbol: "TEST", ltp: 100, change_pct: "1%", volume: "1M"}]);
});

// Placeholder for updating results table
function updateResultsTable(results) {
  const tbody = document.getElementById("resultsTableBody");
  const noResultsRow = document.getElementById("noResultsRow");
  tbody.innerHTML = ""; // Clear old results

  if (!results || results.length === 0) {
    noResultsRow.classList.remove("d-none");
    tbody.appendChild(noResultsRow);
    document.getElementById("stockCount").textContent = "Matching Stocks: 0";
    return;
  }

  noResultsRow.classList.add("d-none");
  document.getElementById(
    "stockCount"
  ).textContent = `Matching Stocks: ${results.length}`;

  results.forEach((stock, index) => {
    const tr = tbody.insertRow();
    tr.innerHTML = `
            <td>${index + 1}</td>
            <td class="fw-medium" style="color:#a78bfa;">${stock.symbol}</td>
            <td>${stock.ltp || "N/A"}</td>
            <td style="color:${
              (stock.change_pct && parseFloat(stock.change_pct)) > 0
                ? "#34d399"
                : "#f87171"
            };">${stock.change_pct || "N/A"}</td>
            <td>${stock.volume || "N/A"}</td>
            <td>
                <button class="icon-btn text-info" title="View Chart"><i class="fas fa-chart-line"></i></button>
                <button class="icon-btn text-primary" title="Add to Watchlist"><i class="fas fa-plus-square"></i></button>
            </td>
        `;
  });
}

// --- End of builder.js ---
