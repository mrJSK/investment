// // // --- Constants ---
// // let INDICATORS = []; // Populated by fetchIndicatorsAndRender

// // const OPERATORS = [
// //   { value: ">", label: "Greater than", icon: "＞" },
// //   { value: ">=", label: "Greater than or equal to", icon: "≥" },
// //   { value: "<", label: "Less than", icon: "＜" },
// //   { value: "<=", label: "Less than or equal to", icon: "≤" },
// //   { value: "==", label: "Equals", icon: "＝" },
// //   { value: "!=", label: "Not equals", icon: "≠" },
// //   { value: "crosses_above", label: "Crosses above", icon: "⤴️" },
// //   { value: "crosses_below", label: "Crosses below", icon: "⤵️" },
// // ];

// // const DEFAULT_TIMEFRAMES = [
// //   "Daily",
// //   "Weekly",
// //   "Monthly",
// //   "1hour",
// //   "30min",
// //   "15min",
// //   "5min",
// //   "1min",
// // ];
// // const DEFAULT_FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// // // --- Global State ---
// // window.filters = [];
// // let filterIdCounter = 0;
// // let CURRENT_MODAL_FILTER_INDEX = null;
// // let CURRENT_MODAL_TARGET_SIDE = null;
// // let CURRENT_MODAL_INDICATOR_DEF = null; // Stores the definition of the indicator being configured

// // // --- Modal Instances (Bootstrap) ---
// // let indicatorModalInstance, indicatorConfigModalInstance, operatorModalInstance;

// // // --- DOM Elements ---
// // const filterListContainer = document.getElementById("filter-list");
// // const addFilterButton = document.getElementById("add-filter");
// // const runScanButton = document.getElementById("runScan");
// // const clearFiltersButton = document.getElementById("clearFiltersButton");

// // const indicatorSearchInput = document.getElementById("indicatorSearch");
// // const indicatorListUl = document.getElementById("indicatorList");

// // const indicatorConfigModalLabel = document.getElementById(
// //   "indicatorConfigModalLabelText"
// // );
// // const indicatorConfigTimeframeSelect = document.getElementById(
// //   "indicatorConfigTimeframe"
// // );
// // const indicatorConfigFieldSelect = document.getElementById(
// //   "indicatorConfigField"
// // );
// // const indicatorConfigFieldGroup = document.getElementById(
// //   "indicatorConfigFieldGroup"
// // ); // To show/hide
// // const indicatorConfigPeriodGroup = document.getElementById(
// //   "indicatorConfigPeriodGroup"
// // );
// // const indicatorConfigPeriodInput = document.getElementById(
// //   "indicatorConfigPeriod"
// // );
// // const indicatorConfigFastPeriodGroup = document.getElementById(
// //   "indicatorConfigFastPeriodGroup"
// // );
// // const indicatorConfigFastPeriodInput = document.getElementById(
// //   "indicatorConfigFastPeriod"
// // );
// // const indicatorConfigSlowPeriodGroup = document.getElementById(
// //   "indicatorConfigSlowPeriodGroup"
// // );
// // const indicatorConfigSlowPeriodInput = document.getElementById(
// //   "indicatorConfigSlowPeriod"
// // );
// // const indicatorConfigSignalPeriodGroup = document.getElementById(
// //   "indicatorConfigSignalPeriodGroup"
// // );
// // const indicatorConfigSignalPeriodInput = document.getElementById(
// //   "indicatorConfigSignalPeriod"
// // );
// // const indicatorConfigMultiplierGroup = document.getElementById(
// //   "indicatorConfigMultiplierGroup"
// // );
// // const indicatorConfigMultiplierInput = document.getElementById(
// //   "indicatorConfigMultiplier"
// // );
// // const indicatorConfigDoneButton = document.getElementById(
// //   "indicatorConfigDone"
// // );

// // const operatorListUl = document.getElementById("operatorList");
// // const resultsTableBody = document.getElementById("resultsTableBody");
// // const stockCountSpan = document.getElementById("stockCount");

// // // --- Initialization ---
// // document.addEventListener("DOMContentLoaded", () => {
// //   indicatorModalInstance = new bootstrap.Modal(
// //     document.getElementById("indicatorModal")
// //   );
// //   indicatorConfigModalInstance = new bootstrap.Modal(
// //     document.getElementById("indicatorConfigModal")
// //   );
// //   operatorModalInstance = new bootstrap.Modal(
// //     document.getElementById("operatorModal")
// //   );

// //   DEFAULT_TIMEFRAMES.forEach((tf) =>
// //     indicatorConfigTimeframeSelect.options.add(new Option(tf, tf))
// //   );
// //   DEFAULT_FIELDS.forEach((f) =>
// //     indicatorConfigFieldSelect.options.add(new Option(f, f))
// //   );

// //   if (addFilterButton)
// //     addFilterButton.addEventListener("click", handleAddFilter);
// //   if (indicatorSearchInput)
// //     indicatorSearchInput.addEventListener("input", renderIndicatorModalList);
// //   if (indicatorConfigDoneButton)
// //     indicatorConfigDoneButton.addEventListener(
// //       "click",
// //       handleIndicatorConfigDone
// //     );
// //   if (runScanButton) runScanButton.addEventListener("click", handleRunScan);
// //   if (clearFiltersButton)
// //     clearFiltersButton.addEventListener("click", () => {
// //       window.filters = [];
// //       renderFilters();
// //       resultsTableBody.innerHTML =
// //         '<tr id="initialMessageRow"><td colspan="9" class="text-center py-5" style="color:#6b7280;">No results yet. Add filters and click "Run Scan".</td></tr>';
// //       stockCountSpan.textContent = "Matching Stocks: 0";
// //     });

// //   fetchIndicatorsAndRender(); // Fetch indicators and then render
// // });

// // let INDICATOR_GROUPS = {};

// // function fetchIndicatorsAndRender() {
// //   fetch("/screener/api/indicators/") // Make sure this matches your grouped endpoint!
// //     .then((response) => response.json())
// //     .then((data) => {
// //       if (data && data.groups && typeof data.groups === "object") {
// //         INDICATOR_GROUPS = data.groups;
// //       } else {
// //         INDICATOR_GROUPS = {}; // fallback
// //       }
// //     })
// //     .catch((error) => {
// //       INDICATOR_GROUPS = {};
// //     })
// //     .finally(() => {
// //       renderFilters();
// //       renderIndicatorModalList();
// //     });
// // }

// // function setDefaultIndicators() {
// //   // Fallback if API fails
// //   INDICATORS = [
// //     { value: "CLOSE", label: "Close Price", params: ["timeframe"] },
// //     {
// //       value: "SMA",
// //       label: "Simple Moving Average",
// //       params: ["timeframe", "field", "period"],
// //     },
// //     {
// //       value: "RSI",
// //       label: "Relative Strength Index",
// //       params: ["timeframe", "field", "period"],
// //     },
// //     { value: "VOLUME", label: "Volume", params: ["timeframe"] },
// //   ];
// // }

// // function handleAddFilter() {
// //   window.filters.push({
// //     id: ++filterIdCounter,
// //     step: 1,
// //     left: null,
// //     op: null,
// //     right: null,
// //   });
// //   renderFilters();
// //   openIndicatorPickerModal(window.filters.length - 1, "left");
// // }

// // function removeFilter(filterIndex) {
// //   window.filters.splice(filterIndex, 1);
// //   renderFilters();
// // }

// // function renderFilters() {
// //   filterListContainer.innerHTML = "";
// //   if (window.filters.length === 0) {
// //     // filterListContainer.innerHTML = '<p class="text-secondary text-sm">No filters added. Click "Add Filter".</p>';
// //   } else {
// //     window.filters.forEach((filter, index) => {
// //       filterListContainer.appendChild(createFilterRowElement(filter, index));
// //     });
// //   }
// // }

// // function createFilterRowElement(filter, filterIndex) {
// //   const rowDiv = document.createElement("div");
// //   rowDiv.className = "filter-row-tokenized";

// //   if (filter.left)
// //     rowDiv.appendChild(createOperandToken(filter.left, "left", filterIndex));
// //   else
// //     rowDiv.appendChild(
// //       createButtonToken("📊 Select Left", "builder-token", (e) => {
// //         e.stopPropagation();
// //         openIndicatorPickerModal(filterIndex, "left");
// //       })
// //     );

// //   if (filter.op) {
// //     const opMeta = OPERATORS.find((o) => o.value === filter.op) || {
// //       icon: "",
// //       label: filter.op,
// //     };
// //     rowDiv.appendChild(
// //       createButtonToken(
// //         `${opMeta.icon} ${opMeta.label}`,
// //         "token-mini token-op",
// //         (e) => {
// //           e.stopPropagation();
// //           openOperatorPickerModal(filterIndex);
// //         }
// //       )
// //     );
// //   } else if (filter.left) {
// //     rowDiv.appendChild(
// //       createButtonToken("? Operator", "builder-token token-op", (e) => {
// //         e.stopPropagation();
// //         openOperatorPickerModal(filterIndex);
// //       })
// //     );
// //   }

// //   if (filter.right)
// //     rowDiv.appendChild(createOperandToken(filter.right, "right", filterIndex));
// //   else if (filter.op)
// //     rowDiv.appendChild(
// //       createButtonToken("📊 Select Right", "builder-token", (e) => {
// //         e.stopPropagation();
// //         openIndicatorPickerModal(filterIndex, "right");
// //       })
// //     );

// //   const deleteBtn = document.createElement("button");
// //   deleteBtn.className = "icon-btn remove-filter-btn ms-auto";
// //   deleteBtn.innerHTML = `<i class="fas fa-trash-alt"></i>`;
// //   deleteBtn.title = "Delete Filter";
// //   deleteBtn.addEventListener("click", (e) => {
// //     e.stopPropagation();
// //     removeFilter(filterIndex);
// //   });
// //   rowDiv.appendChild(deleteBtn);
// //   return rowDiv;
// // }

// // // function createOperandToken(operand, side, filterIndex) {
// // //   const wrapperSpan = document.createElement("span");
// // //   wrapperSpan.className = `token-operand-group ${
// // //     operand.type === "indicator" ? "token-ind-formula" : "token-number"
// // //   }`;
// // //   wrapperSpan.classList.add(
// // //     "d-inline-flex",
// // //     "flex-wrap",
// // //     "gap-1",
// // //     "align-items-center"
// // //   );

// // //   if (operand.type === "indicator") {
// // //     const indDef = INDICATORS.find((i) => i.value === operand.value);
// // //     const displayParams = operand.params || {}; // Ensure params object exists

// // //     wrapperSpan.appendChild(
// // //       createButtonToken(
// // //         displayParams.timeframe || "Daily",
// // //         "token-mini token-tf",
// // //         (e) => {
// // //           e.stopPropagation();
// // //           openIndicatorConfigEditor(filterIndex, side, "timeframe");
// // //         }
// // //       )
// // //     );
// // //     wrapperSpan.appendChild(
// // //       createButtonToken(operand.value, "token-mini token-ind", (e) => {
// // //         e.stopPropagation();
// // //         openIndicatorPickerModal(filterIndex, side);
// // //       })
// // //     );

// // //     const actualParamsFromDef = indDef
// // //       ? indDef.params
// // //       : getImplicitParams(operand.value); // Use getImplicitParams as a fallback
// // //     const hasConfigurableParams = actualParamsFromDef.some((p) =>
// // //       [
// // //         "field",
// // //         "period",
// // //         "fast_period",
// // //         "slow_period",
// // //         "signal_period",
// // //         "multiplier",
// // //         "fastk_period",
// // //         "slowk_period",
// // //         "slowd_period",
// // //         "nbdev",
// // //       ].includes(p)
// // //     );

// // //     if (hasConfigurableParams) {
// // //       wrapperSpan.appendChild(document.createTextNode("("));
// // //       let firstParamRendered = true;
// // //       const addComma = () => {
// // //         if (!firstParamRendered)
// // //           wrapperSpan.appendChild(document.createTextNode(", "));
// // //         firstParamRendered = false;
// // //       };

// // //       if (actualParamsFromDef.includes("field")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             displayParams.field || "Close",
// // //             "token-mini token-field",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "field");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.period || 20),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "period");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("fast_period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.fast_period || 12),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "fast_period");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("slow_period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.slow_period || 26),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "slow_period");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("signal_period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.signal_period || 9),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "signal_period");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("nbdev")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.nbdev || 2),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "nbdev");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("multiplier")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.multiplier || 2),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "multiplier");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       // STOCH specific params (map from TA-Lib like fastk_period to our 'fast_period' if desired, or use as is)
// // //       if (actualParamsFromDef.includes("fastk_period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.fastk_period || 14),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "fastk_period");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("slowk_period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.slowk_period || 3),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "slowk_period");
// // //             }
// // //           )
// // //         );
// // //       }
// // //       if (actualParamsFromDef.includes("slowd_period")) {
// // //         addComma();
// // //         wrapperSpan.appendChild(
// // //           createButtonToken(
// // //             String(displayParams.slowd_period || 3),
// // //             "token-mini token-per",
// // //             (e) => {
// // //               e.stopPropagation();
// // //               openIndicatorConfigEditor(filterIndex, side, "slowd_period");
// // //             }
// // //           )
// // //         );
// // //       }

// // //       wrapperSpan.appendChild(document.createTextNode(")"));
// // //     }
// // //   } else if (operand.type === "number") {
// // //     wrapperSpan.appendChild(
// // //       createButtonToken(String(operand.value), "token-mini token-num", (e) => {
// // //         e.stopPropagation();
// // //         editNumberToken(filterIndex, side);
// // //       })
// // //     );
// // //   }
// // //   return wrapperSpan;
// // // }

// // function createOperandToken(operand, side, filterIndex) {
// //   const wrapperSpan = document.createElement("span");
// //   wrapperSpan.className = `token-operand-group ${
// //     operand.type === "indicator" ? "token-ind-formula" : "token-number"
// //   }`;
// //   wrapperSpan.classList.add(
// //     "d-inline-flex",
// //     "flex-wrap",
// //     "gap-1",
// //     "align-items-center"
// //   );

// //   if (operand.type === "indicator") {
// //     // Find indicator definition for label
// //     let indDef = INDICATORS.find((i) => i.value === operand.value);
// //     if (!indDef && typeof INDICATOR_GROUPS === "object") {
// //       // Flatten all groups
// //       for (const groupIndicators of Object.values(INDICATOR_GROUPS)) {
// //         const found = groupIndicators.find((i) => i.value === operand.value);
// //         if (found) {
// //           indDef = found;
// //           break;
// //         }
// //       }
// //     }
// //     const displayParams = operand.params || {};
// //     const displayLabel =
// //       operand.label || (indDef ? indDef.label : operand.value);
// //     const actualParamsFromDef = indDef
// //       ? indDef.params
// //       : getImplicitParams(operand.value);

// //     // Check if it has any "configurable" parameters except timeframe
// //     const hasConfigurableParams = actualParamsFromDef.some((p) =>
// //       [
// //         "field",
// //         "period",
// //         "fast_period",
// //         "slow_period",
// //         "signal_period",
// //         "multiplier",
// //         "fastk_period",
// //         "slowk_period",
// //         "slowd_period",
// //         "nbdev",
// //       ].includes(p)
// //     );

// //     // --- If NO extra params, just show [TF] + Pretty Name
// //     wrapperSpan.appendChild(
// //       createButtonToken(
// //         displayParams.timeframe || "Daily",
// //         "token-mini token-tf",
// //         (e) => {
// //           e.stopPropagation();
// //           openIndicatorConfigEditor(filterIndex, side, "timeframe");
// //         }
// //       )
// //     );
// //     wrapperSpan.appendChild(
// //       createButtonToken(displayLabel, "token-mini token-ind", (e) => {
// //         e.stopPropagation();
// //         openIndicatorPickerModal(filterIndex, side);
// //       })
// //     );

// //     // --- Only add param chips if any configurable params exist
// //     if (hasConfigurableParams) {
// //       wrapperSpan.appendChild(document.createTextNode("("));
// //       let firstParamRendered = true;
// //       const addComma = () => {
// //         if (!firstParamRendered)
// //           wrapperSpan.appendChild(document.createTextNode(", "));
// //         firstParamRendered = false;
// //       };

// //       if (actualParamsFromDef.includes("field")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             displayParams.field || "Close",
// //             "token-mini token-field",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "field");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.period || 20),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "period");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("fast_period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.fast_period || 12),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "fast_period");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("slow_period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.slow_period || 26),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "slow_period");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("signal_period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.signal_period || 9),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "signal_period");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("nbdev")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.nbdev || 2),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "nbdev");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("multiplier")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.multiplier || 2),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "multiplier");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("fastk_period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.fastk_period || 14),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "fastk_period");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("slowk_period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.slowk_period || 3),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "slowk_period");
// //             }
// //           )
// //         );
// //       }
// //       if (actualParamsFromDef.includes("slowd_period")) {
// //         addComma();
// //         wrapperSpan.appendChild(
// //           createButtonToken(
// //             String(displayParams.slowd_period || 3),
// //             "token-mini token-per",
// //             (e) => {
// //               e.stopPropagation();
// //               openIndicatorConfigEditor(filterIndex, side, "slowd_period");
// //             }
// //           )
// //         );
// //       }
// //       wrapperSpan.appendChild(document.createTextNode(")"));
// //     }
// //   } else if (operand.type === "number") {
// //     wrapperSpan.appendChild(
// //       createButtonToken(String(operand.value), "token-mini token-num", (e) => {
// //         e.stopPropagation();
// //         editNumberToken(filterIndex, side);
// //       })
// //     );
// //   }
// //   return wrapperSpan;
// // }

// // function createButtonToken(text, className, onClickHandler) {
// //   const button = document.createElement("button");
// //   button.className = className;
// //   button.innerHTML = text;
// //   button.type = "button"; // Important for buttons not in a form
// //   button.addEventListener("click", onClickHandler);
// //   return button;
// // }

// // function openIndicatorPickerModal(filterIndex, targetSide) {
// //   CURRENT_MODAL_FILTER_INDEX = filterIndex;
// //   CURRENT_MODAL_TARGET_SIDE = targetSide;
// //   indicatorSearchInput.value = "";
// //   renderIndicatorModalList(); // Ensure list is populated with current INDICATORS
// //   indicatorModalInstance.show();
// // }

// // function openOperatorPickerModal(filterIndex) {
// //   CURRENT_MODAL_FILTER_INDEX = filterIndex;
// //   renderOperatorModalList();
// //   operatorModalInstance.show();
// // }

// // function openIndicatorConfigEditor(filterIndex, targetSide, focusField = null) {
// //   CURRENT_MODAL_FILTER_INDEX = filterIndex;
// //   CURRENT_MODAL_TARGET_SIDE = targetSide;
// //   const currentOperand = window.filters[filterIndex][targetSide];

// //   if (!currentOperand || currentOperand.type !== "indicator") {
// //     console.error("Cannot configure non-indicator operand:", currentOperand);
// //     return;
// //   }

// //   CURRENT_MODAL_INDICATOR_DEF = INDICATORS.find(
// //     (ind) => ind.value === currentOperand.value
// //   ) || {
// //     label: currentOperand.value,
// //     value: currentOperand.value,
// //     params: getImplicitParams(currentOperand.value),
// //   };

// //   indicatorConfigModalLabel.textContent = `Configure ${CURRENT_MODAL_INDICATOR_DEF.label}`;

// //   const currentParams = currentOperand.params || {};
// //   indicatorConfigTimeframeSelect.value = currentParams.timeframe || "Daily";

// //   const showHideAndFill = (
// //     paramName,
// //     groupElem,
// //     inputElem,
// //     defaultValue,
// //     inputType = "value"
// //   ) => {
// //     if (CURRENT_MODAL_INDICATOR_DEF.params.includes(paramName)) {
// //       groupElem.style.display = "block";
// //       inputElem.value =
// //         currentParams[paramName] !== undefined
// //           ? currentParams[paramName]
// //           : defaultValue;
// //     } else {
// //       groupElem.style.display = "none";
// //     }
// //   };

// //   showHideAndFill(
// //     "field",
// //     indicatorConfigFieldGroup,
// //     indicatorConfigFieldSelect,
// //     "Close"
// //   );
// //   showHideAndFill(
// //     "period",
// //     indicatorConfigPeriodGroup,
// //     indicatorConfigPeriodInput,
// //     "20"
// //   );
// //   showHideAndFill(
// //     "fast_period",
// //     indicatorConfigFastPeriodGroup,
// //     indicatorConfigFastPeriodInput,
// //     "12"
// //   );
// //   showHideAndFill(
// //     "slow_period",
// //     indicatorConfigSlowPeriodGroup,
// //     indicatorConfigSlowPeriodInput,
// //     "26"
// //   );
// //   showHideAndFill(
// //     "signal_period",
// //     indicatorConfigSignalPeriodGroup,
// //     indicatorConfigSignalPeriodInput,
// //     "9"
// //   );
// //   showHideAndFill(
// //     "multiplier",
// //     indicatorConfigMultiplierGroup,
// //     indicatorConfigMultiplierInput,
// //     "2"
// //   );
// //   showHideAndFill(
// //     "nbdev",
// //     indicatorConfigPeriodGroup,
// //     indicatorConfigPeriodInput,
// //     "2"
// //   ); // Re-use period for nbdev for BBANDS for simplicity
// //   showHideAndFill(
// //     "fastk_period",
// //     indicatorConfigFastPeriodGroup,
// //     indicatorConfigFastPeriodInput,
// //     "14"
// //   ); // STOCH
// //   showHideAndFill(
// //     "slowk_period",
// //     indicatorConfigSlowPeriodGroup,
// //     indicatorConfigSlowPeriodInput,
// //     "3"
// //   ); // STOCH
// //   showHideAndFill(
// //     "slowd_period",
// //     indicatorConfigSignalPeriodGroup,
// //     indicatorConfigSignalPeriodInput,
// //     "3"
// //   ); // STOCH (re-using signal group for slowd)

// //   indicatorConfigModalInstance.show();
// // }

// // function editNumberToken(filterIndex, side) {
// //   const currentOperand = window.filters[filterIndex][side];
// //   let newValue = prompt("Enter number:", currentOperand.value);
// //   if (newValue !== null && !isNaN(parseFloat(newValue))) {
// //     currentOperand.value = parseFloat(newValue);
// //     renderFilters();
// //   }
// // }

// // function renderIndicatorModalList() {
// //   const searchTerm = indicatorSearchInput.value.toLowerCase();
// //   indicatorListUl.innerHTML = "";

// //   // Number first
// //   const numLi = document.createElement("li");
// //   numLi.className = "list-group-item list-group-item-action text-primary";
// //   numLi.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant)</b>`;
// //   numLi.addEventListener("click", () => {
// //     let numVal = prompt("Enter number value:", "0");
// //     if (numVal !== null && !isNaN(parseFloat(numVal))) {
// //       applyOperandSelection({ type: "number", value: parseFloat(numVal) });
// //       indicatorModalInstance.hide();
// //     }
// //   });
// //   indicatorListUl.appendChild(numLi);

// //   // Render categories
// //   Object.entries(INDICATOR_GROUPS).forEach(([group, indicators]) => {
// //     // Group header
// //     const groupLi = document.createElement("li");
// //     groupLi.className = "list-group-item";
// //     groupLi.innerHTML = `<strong style="color:#5eead4;font-size:1em">${group}</strong>`;
// //     groupLi.style.background = "#232b3b";
// //     indicatorListUl.appendChild(groupLi);

// //     indicators
// //       .filter(
// //         (ind) =>
// //           ind.label.toLowerCase().includes(searchTerm) ||
// //           ind.value.toLowerCase().includes(searchTerm)
// //       )
// //       .forEach((indicatorDef) => {
// //         const li = document.createElement("li");
// //         li.className = "list-group-item list-group-item-action";
// //         li.innerHTML = `<span style="font-size:1.1em;">📊</span> <b>${indicatorDef.value}</b> <small class="text-muted">(${indicatorDef.label})</small>`;
// //         li.addEventListener("click", () => {
// //           CURRENT_MODAL_INDICATOR_DEF = indicatorDef;
// //           indicatorModalInstance.hide();
// //           // Continue to config modal etc...
// //           // (Your existing logic here)
// //         });
// //         indicatorListUl.appendChild(li);
// //       });
// //   });
// // }

// // function renderOperatorModalList() {
// //   operatorListUl.innerHTML = "";
// //   OPERATORS.forEach((op) => {
// //     const li = document.createElement("li");
// //     li.className = "list-group-item list-group-item-action";
// //     li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b>`;
// //     li.addEventListener("click", () => {
// //       applyOperatorSelection(op.value);
// //       operatorModalInstance.hide();
// //     });
// //     operatorListUl.appendChild(li);
// //   });
// // }

// // function handleIndicatorConfigDone() {
// //   if (!CURRENT_MODAL_INDICATOR_DEF) return;
// //   const params = { timeframe: indicatorConfigTimeframeSelect.value };

// //   const addParamIfVisible = (
// //     paramName,
// //     groupElem,
// //     inputElem,
// //     isNumeric = true,
// //     isFloat = false
// //   ) => {
// //     if (
// //       groupElem.style.display !== "none" &&
// //       CURRENT_MODAL_INDICATOR_DEF.params.includes(paramName)
// //     ) {
// //       let val = inputElem.value;
// //       if (isNumeric) val = isFloat ? parseFloat(val) : parseInt(val, 10);
// //       params[paramName] = val;
// //     }
// //   };

// //   addParamIfVisible(
// //     "field",
// //     indicatorConfigFieldGroup,
// //     indicatorConfigFieldSelect,
// //     false
// //   );
// //   addParamIfVisible(
// //     "period",
// //     indicatorConfigPeriodGroup,
// //     indicatorConfigPeriodInput
// //   );
// //   addParamIfVisible(
// //     "fast_period",
// //     indicatorConfigFastPeriodGroup,
// //     indicatorConfigFastPeriodInput
// //   );
// //   addParamIfVisible(
// //     "slow_period",
// //     indicatorConfigSlowPeriodGroup,
// //     indicatorConfigSlowPeriodInput
// //   );
// //   addParamIfVisible(
// //     "signal_period",
// //     indicatorConfigSignalPeriodGroup,
// //     indicatorConfigSignalPeriodInput
// //   );
// //   addParamIfVisible(
// //     "multiplier",
// //     indicatorConfigMultiplierGroup,
// //     indicatorConfigMultiplierInput,
// //     true,
// //     true
// //   );
// //   addParamIfVisible(
// //     "nbdev",
// //     indicatorConfigPeriodGroup,
// //     indicatorConfigPeriodInput
// //   ); // Assuming nbdev uses period input
// //   addParamIfVisible(
// //     "fastk_period",
// //     indicatorConfigFastPeriodGroup,
// //     indicatorConfigFastPeriodInput
// //   );
// //   addParamIfVisible(
// //     "slowk_period",
// //     indicatorConfigSlowPeriodGroup,
// //     indicatorConfigSlowPeriodInput
// //   );
// //   addParamIfVisible(
// //     "slowd_period",
// //     indicatorConfigSignalPeriodGroup,
// //     indicatorConfigSignalPeriodInput
// //   );

// //   applyOperandSelection({
// //     type: "indicator",
// //     value: CURRENT_MODAL_INDICATOR_DEF.value,
// //     label: CURRENT_MODAL_INDICATOR_DEF.label,
// //     params: params,
// //   });
// //   indicatorConfigModalInstance.hide();
// // }

// // function applyOperandSelection(operandConfig) {
// //   const filter = window.filters[CURRENT_MODAL_FILTER_INDEX];
// //   if (!filter) return;
// //   filter[CURRENT_MODAL_TARGET_SIDE] = operandConfig;
// //   if (CURRENT_MODAL_TARGET_SIDE === "left") {
// //     filter.step = 2;
// //     renderFilters();
// //     openOperatorPickerModal(CURRENT_MODAL_FILTER_INDEX);
// //   } else {
// //     filter.step = 4;
// //     renderFilters();
// //   }
// // }

// // function applyOperatorSelection(operatorValue) {
// //   const filter = window.filters[CURRENT_MODAL_FILTER_INDEX];
// //   if (!filter) return;
// //   filter.op = operatorValue;
// //   filter.step = 3;
// //   renderFilters();
// //   openIndicatorPickerModal(CURRENT_MODAL_FILTER_INDEX, "right");
// // }

// // function getCookie(name) {
// //   let cookieValue = null;
// //   if (document.cookie && document.cookie !== "") {
// //     const cookies = document.cookie.split(";");
// //     for (let i = 0; i < cookies.length; i++) {
// //       const cookie = cookies[i].trim();
// //       if (cookie.substring(0, name.length + 1) === name + "=") {
// //         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
// //         break;
// //       }
// //     }
// //   }
// //   return cookieValue;
// // }

// // function handleRunScan() {
// //   resultsTableBody.innerHTML =
// //     '<tr><td colspan="9" class="text-center py-5" style="color:#6b7280;"><i class="fas fa-spinner fa-spin fa-2x me-2"></i>Running scan, please wait...</td></tr>';
// //   stockCountSpan.textContent = "Matching Stocks: -";

// //   const transformedFilters = window.filters.map((f) => {
// //     let transformed = {};
// //     // Transform left operand
// //     if (f.left) {
// //       transformed.indicator = f.left.value;
// //       transformed.timeframe = f.left.params.timeframe;
// //       // Add other parameters from f.left.params based on what evaluate_filter_row expects
// //       if (f.left.params.field) transformed.field = f.left.params.field;
// //       if (f.left.params.period) transformed.period = f.left.params.period;
// //       if (f.left.params.fast_period)
// //         transformed.fastperiod = f.left.params.fast_period; // Match TA-Lib param name
// //       if (f.left.params.slow_period)
// //         transformed.slowperiod = f.left.params.slow_period; // Match TA-Lib param name
// //       if (f.left.params.signal_period)
// //         transformed.signalperiod = f.left.params.signal_period; // Match TA-Lib param name
// //       if (f.left.params.fastk_period)
// //         transformed.fastk_period = f.left.params.fastk_period;
// //       if (f.left.params.slowk_period)
// //         transformed.slowk_period = f.left.params.slowk_period;
// //       if (f.left.params.slowd_period)
// //         transformed.slowd_period = f.left.params.slowd_period;
// //       if (f.left.params.nbdev) transformed.nbdev = f.left.params.nbdev; // For BBANDS
// //       if (f.left.params.multiplier)
// //         transformed.multiplier = f.left.params.multiplier; // For Supertrend
// //     }
// //     transformed.mainOp = f.op; // Ensure this matches operators in evaluate_operation

// //     // Transform right operand
// //     if (f.right) {
// //       if (f.right.type === "number") {
// //         transformed.rightType = "number";
// //         transformed.rightValue = f.right.value;
// //       } else if (f.right.type === "indicator") {
// //         transformed.rightType = "indicator";
// //         transformed.rightIndicator = f.right.value;
// //         transformed.rightTimeframe = f.right.params.timeframe; // Important: timeframe for right indicator
// //         if (f.right.params.field) transformed.rightField = f.right.params.field;
// //         if (f.right.params.period)
// //           transformed.rightPeriod = f.right.params.period;
// //         // Add other specific params for right indicator
// //         if (f.right.params.fast_period)
// //           transformed.rightFastperiod = f.right.params.fast_period;
// //         if (f.right.params.slow_period)
// //           transformed.rightSlowperiod = f.right.params.slow_period;
// //         if (f.right.params.signal_period)
// //           transformed.rightSignalperiod = f.right.params.signal_period;
// //       }
// //     }
// //     return transformed;
// //   });

// //   fetch("/api/run_screener/", {
// //     // Main API endpoint
// //     method: "POST",
// //     headers: {
// //       "Content-Type": "application/json",
// //       "X-CSRFToken": getCookie("csrftoken"),
// //     },
// //     body: JSON.stringify({
// //       filters: transformedFilters,
// //       segment: document.getElementById("segmentDropdown")?.value || "Nifty 500",
// //     }),
// //   })
// //     .then((response) => {
// //       if (!response.ok) {
// //         return response.json().then((err) => {
// //           throw err.error || err;
// //         });
// //       } // Throw error object or string
// //       return response.json();
// //     })
// //     .then((data) => {
// //       if (data.results) {
// //         updateResultsTable(data.results);
// //       } else {
// //         updateResultsTable([]); // Show "no match" or error from data.error
// //         if (data.error) console.error("Backend scan error:", data.error);
// //       }
// //     })
// //     .catch((error) => {
// //       console.error("Error running scan:", error);
// //       let errorMsg =
// //         typeof error === "string"
// //           ? error
// //           : error.message || "Failed to fetch results.";
// //       if (typeof error === "object" && error.error) errorMsg = error.error; // If backend sends {error: "message"}

// //       resultsTableBody.innerHTML = `<tr><td colspan="9" class="text-center py-5" style="color:#f87171;">Error: ${errorMsg}</td></tr>`;
// //       stockCountSpan.textContent = "Matching Stocks: 0";
// //     });
// // }

// // function updateResultsTable(results) {
// //   tbody = document.getElementById("resultsTableBody"); // ensure tbody is defined here
// //   stockCountSpan = document.getElementById("stockCount"); // ensure stockCountSpan is defined here
// //   tbody.innerHTML = "";

// //   if (!results || results.length === 0) {
// //     tbody.innerHTML =
// //       '<tr><td colspan="9" class="text-center py-5" style="color:#6b7280;">No stocks match your criteria.</td></tr>';
// //     stockCountSpan.textContent = "Matching Stocks: 0";
// //     return;
// //   }

// //   stockCountSpan.textContent = `Matching Stocks: ${results.length}`;
// //   results.forEach((stock, index) => {
// //     const tr = tbody.insertRow();
// //     let changePctStyle = "";
// //     if (stock.change_pct && typeof stock.change_pct === "string") {
// //       const numericChange = parseFloat(stock.change_pct.replace("%", ""));
// //       if (!isNaN(numericChange)) {
// //         changePctStyle =
// //           numericChange > 0 ? "color:#34d399;" : "color:#f87171;";
// //       }
// //     }
// //     tr.innerHTML = `
// //             <td>${index + 1}</td>
// //             <td class="fw-medium" style="color:#a78bfa;">${
// //               stock.symbol || "N/A"
// //             }</td>
// //             <td>${stock.timestamp || "N/A"}</td>
// //             <td>${stock.open || "N/A"}</td>
// //             <td>${stock.high || "N/A"}</td>
// //             <td>${stock.low || "N/A"}</td>
// //             <td>${stock.close || "N/A"}</td>
// //             <td style="${changePctStyle}">${stock.change_pct || "N/A"}</td>
// //             <td>${stock.volume || "N/A"}</td>
// //             <td>
// //                 <button type="button" class="icon-btn text-info" title="View Chart"><i class="fas fa-chart-line"></i></button>
// //                 <button type="button" class="icon-btn text-primary" title="Add to Watchlist"><i class="fas fa-plus-square"></i></button>
// //             </td>`;
// //   });
// // }

// // {% static 'screener/js/builder.js' %}

// // --- Constants ---
// let INDICATORS = []; // Populated by fetchIndicatorsAndRender from INDICATOR_GROUPS
// let INDICATOR_GROUPS = {}; // Populated by fetchIndicatorsAndRender

// const LOGICAL_OPERATORS = [
//   { value: "AND", label: "AND" },
//   { value: "OR", label: "OR" },
// ];

// const OPERATORS = [
//   { value: ">", label: "Greater than", icon: "＞" },
//   { value: ">=", label: "Greater than or equal to", icon: "≥" },
//   { value: "<", label: "Less than", icon: "＜" },
//   { value: "<=", label: "Less than or equal to", icon: "≤" },
//   { value: "==", label: "Equals", icon: "＝" },
//   // { value: "!=", label: "Not equals", icon: "≠" }, // Backend might not support this easily
//   { value: "crosses_above", label: "Crosses above", icon: "⤴️" },
//   { value: "crosses_below", label: "Crosses below", icon: "⤵️" },
// ];

// const DEFAULT_TIMEFRAMES = [
//   "Daily",
//   "Weekly",
//   "Monthly",
//   "1hour",
//   "30min",
//   "15min",
//   "5min",
//   "1min",
// ];
// const DEFAULT_FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// // --- Global State ---
// let nodeIdCounter = 0; // For unique IDs for groups and conditions
// window.filterTree = createGroupNode("root"); // Initialize with a root group

// let CURRENT_MODAL_NODE_ID = null; // ID of the condition node being configured
// let CURRENT_MODAL_TARGET_SIDE = null; // 'left' or 'right'
// let CURRENT_MODAL_INDICATOR_DEF = null;

// // --- Modal Instances (Bootstrap) ---
// let indicatorModalInstance, indicatorConfigModalInstance, operatorModalInstance;

// // --- DOM Elements ---
// const filterTreeContainer = document.getElementById("filter-list"); // Renamed for clarity
// const addRootFilterButton = document.getElementById("add-filter"); // This button adds to the root
// const runScanButton = document.getElementById("runScan");
// const clearFiltersButton = document.getElementById("clearFiltersButton");

// const indicatorSearchInput = document.getElementById("indicatorSearch");
// const indicatorListUl = document.getElementById("indicatorList");

// // Indicator Config Modal Elements (ensure all are correctly identified from your HTML)
// const indicatorConfigModalLabel = document.getElementById(
//   "indicatorConfigModalLabelText"
// );
// const indicatorConfigTimeframeSelect = document.getElementById(
//   "indicatorConfigTimeframe"
// );
// const indicatorConfigFieldSelect = document.getElementById(
//   "indicatorConfigField"
// );
// const indicatorConfigFieldGroup = document.getElementById(
//   "indicatorConfigFieldGroup"
// );
// const indicatorConfigPeriodGroup = document.getElementById(
//   "indicatorConfigPeriodGroup"
// );
// const indicatorConfigPeriodInput = document.getElementById(
//   "indicatorConfigPeriod"
// );
// const indicatorConfigFastPeriodGroup = document.getElementById(
//   "indicatorConfigFastPeriodGroup"
// );
// const indicatorConfigFastPeriodInput = document.getElementById(
//   "indicatorConfigFastPeriod"
// );
// const indicatorConfigSlowPeriodGroup = document.getElementById(
//   "indicatorConfigSlowPeriodGroup"
// );
// const indicatorConfigSlowPeriodInput = document.getElementById(
//   "indicatorConfigSlowPeriod"
// );
// const indicatorConfigSignalPeriodGroup = document.getElementById(
//   "indicatorConfigSignalPeriodGroup"
// );
// const indicatorConfigSignalPeriodInput = document.getElementById(
//   "indicatorConfigSignalPeriod"
// );
// const indicatorConfigMultiplierGroup = document.getElementById(
//   "indicatorConfigMultiplierGroup"
// );
// const indicatorConfigMultiplierInput = document.getElementById(
//   "indicatorConfigMultiplier"
// );
// const indicatorConfigNbdevGroup = document.getElementById(
//   "indicatorConfigNbdevGroup"
// );
// const indicatorConfigNbdevInput = document.getElementById(
//   "indicatorConfigNbdev"
// );
// const indicatorConfigFastKPeriodGroup = document.getElementById(
//   "indicatorConfigFastKPeriodGroup"
// );
// const indicatorConfigFastKPeriodInput = document.getElementById(
//   "indicatorConfigFastKPeriod"
// );
// const indicatorConfigSlowKPeriodGroup = document.getElementById(
//   "indicatorConfigSlowKPeriodGroup"
// );
// const indicatorConfigSlowKPeriodInput = document.getElementById(
//   "indicatorConfigSlowKPeriod"
// );
// const indicatorConfigSlowDPeriodGroup = document.getElementById(
//   "indicatorConfigSlowDPeriodGroup"
// );
// const indicatorConfigSlowDPeriodInput = document.getElementById(
//   "indicatorConfigSlowDPeriod"
// );
// const indicatorConfigDoneButton = document.getElementById(
//   "indicatorConfigDone"
// );

// const operatorListUl = document.getElementById("operatorList");
// const resultsTableBody = document.getElementById("resultsTableBody");
// const stockCountSpan = document.getElementById("stockCount");

// // --- Initialization ---
// document.addEventListener("DOMContentLoaded", () => {
//   indicatorModalInstance = new bootstrap.Modal(
//     document.getElementById("indicatorModal")
//   );
//   indicatorConfigModalInstance = new bootstrap.Modal(
//     document.getElementById("indicatorConfigModal")
//   );
//   operatorModalInstance = new bootstrap.Modal(
//     document.getElementById("operatorModal")
//   );

//   DEFAULT_TIMEFRAMES.forEach((tf) =>
//     indicatorConfigTimeframeSelect.options.add(new Option(tf, tf.toLowerCase()))
//   );
//   DEFAULT_FIELDS.forEach((f) =>
//     indicatorConfigFieldSelect.options.add(new Option(f, f.toLowerCase()))
//   );

//   if (addRootFilterButton)
//     addRootFilterButton.addEventListener("click", handleAddRootCondition);
//   if (indicatorSearchInput)
//     indicatorSearchInput.addEventListener("input", renderIndicatorModalList);
//   if (indicatorConfigDoneButton)
//     indicatorConfigDoneButton.addEventListener(
//       "click",
//       handleIndicatorConfigDone
//     );
//   if (runScanButton) runScanButton.addEventListener("click", handleRunScan);
//   if (clearFiltersButton) {
//     clearFiltersButton.addEventListener("click", () => {
//       window.filterTree = createGroupNode("root"); // Reset to a new root group
//       nodeIdCounter = 0; // Reset counter
//       renderFilterTree();
//       resultsTableBody.innerHTML =
//         '<tr id="initialMessageRow"><td colspan="10" class="text-center py-5" style="color:#6b7280;">No results yet. Add filters and click "Run Scan".</td></tr>';
//       stockCountSpan.textContent = "Matching Stocks: 0";
//     });
//   }
//   fetchIndicatorsAndRender();
// });

// // --- Tree Node Creation ---
// function createGroupNode(parentId = null, logicalOperator = "AND") {
//   nodeIdCounter++;
//   return {
//     id: `g${nodeIdCounter}`,
//     type: "group",
//     logicalOperator: logicalOperator,
//     parentId: parentId, // Keep track of parent for easier deletion/traversal if needed
//     children: [],
//   };
// }

// function createConditionNode(parentId) {
//   nodeIdCounter++;
//   return {
//     id: `c${nodeIdCounter}`,
//     type: "condition",
//     parentId: parentId,
//     left: null,
//     op: null,
//     right: null,
//     step: 1, // For sequential selection: 1=left, 2=op, 3=right, 4=done
//   };
// }

// // --- Find Node in Tree (Recursive) ---
// function findNodeById(nodeId, currentNode = window.filterTree) {
//   if (currentNode.id === nodeId) {
//     return currentNode;
//   }
//   if (currentNode.type === "group" && currentNode.children) {
//     for (const child of currentNode.children) {
//       const found = findNodeById(nodeId, child);
//       if (found) return found;
//     }
//   }
//   return null;
// }
// // --- Remove Node from Tree (Recursive) ---
// function removeNodeFromTree(nodeIdToRemove, currentNode = window.filterTree) {
//   if (currentNode.type === "group" && currentNode.children) {
//     const childIndex = currentNode.children.findIndex(
//       (child) => child.id === nodeIdToRemove
//     );
//     if (childIndex !== -1) {
//       currentNode.children.splice(childIndex, 1);
//       return true; // Node found and removed
//     }
//     // If not found in direct children, search in grandchildren
//     for (const child of currentNode.children) {
//       if (removeNodeFromTree(nodeIdToRemove, child)) {
//         return true; // Node found and removed in a deeper level
//       }
//     }
//   }
//   return false; // Node not found at this level or its children
// }

// // --- Indicator Fetching & Fallback ---
// function setDefaultIndicatorsFallback() {
//   INDICATOR_GROUPS = {
//     /* ... same as previous ... */
//   };
//   INDICATORS = []; /* ... same as previous ... */
//   console.warn("Using fallback indicator definitions.");
// }

// function fetchIndicatorsAndRender() {
//   fetch("/screener/api/indicators/")
//     .then((response) =>
//       response.ok
//         ? response.json()
//         : Promise.reject(`HTTP error! status: ${response.status}`)
//     )
//     .then((data) => {
//       if (
//         data &&
//         data.groups &&
//         typeof data.groups === "object" &&
//         Object.keys(data.groups).length > 0
//       ) {
//         INDICATOR_GROUPS = data.groups;
//         INDICATORS = [];
//         for (const groupName in INDICATOR_GROUPS) {
//           if (Array.isArray(INDICATOR_GROUPS[groupName])) {
//             INDICATOR_GROUPS[groupName].forEach((ind) => {
//               ind.params = ind.params || getImplicitParams(ind.value);
//             });
//             INDICATORS = INDICATORS.concat(INDICATOR_GROUPS[groupName]);
//           }
//         }
//         if (INDICATORS.length === 0) setDefaultIndicatorsFallback();
//         else
//           console.log(
//             "Indicators loaded from API:",
//             INDICATORS.length,
//             "total"
//           );
//       } else {
//         console.error("Invalid or empty data.groups from API:", data);
//         setDefaultIndicatorsFallback();
//       }
//     })
//     .catch((error) => {
//       console.error("Error fetching indicators:", error);
//       setDefaultIndicatorsFallback();
//     })
//     .finally(() => {
//       renderFilterTree(); // Initial render of the (empty) tree
//       renderIndicatorModalList(); // Prepare indicator picker
//     });
// }

// // --- Filter Tree Rendering ---
// function renderFilterTree(
//   parentNode = window.filterTree,
//   containerElement = filterTreeContainer,
//   level = 0
// ) {
//   if (level === 0) {
//     // Clear container only for the root level call
//     containerElement.innerHTML = "";
//   }

//   const groupDiv = document.createElement("div");
//   groupDiv.className = "filter-group p-3 border rounded mb-3";
//   groupDiv.style.marginLeft = `${level * 20}px`; // Indentation for nesting
//   groupDiv.style.borderColor = "#374151"; // Darker border for groups
//   groupDiv.style.backgroundColor = level === 0 ? "#1f2937" : "#2d3748"; // Slightly different for nested

//   // Group Header: Logical Operator Selector & Action Buttons
//   const groupHeaderDiv = document.createElement("div");
//   groupHeaderDiv.className =
//     "d-flex justify-content-between align-items-center mb-2 pb-2 border-bottom";
//   groupHeaderDiv.style.borderColor = "#4a5568";

//   if (parentNode.id !== "root" || parentNode.children.length > 0) {
//     // Show operator for non-empty or non-root groups
//     const logicalOpSelect = document.createElement("select");
//     logicalOpSelect.className = "form-select form-select-sm w-auto me-2";
//     LOGICAL_OPERATORS.forEach((op) => {
//       const option = new Option(op.label, op.value);
//       logicalOpSelect.add(option);
//     });
//     logicalOpSelect.value = parentNode.logicalOperator;
//     logicalOpSelect.addEventListener("change", (e) => {
//       parentNode.logicalOperator = e.target.value;
//       // No need to re-render full tree, just update data. If visual change needed, selective update.
//     });
//     groupHeaderDiv.appendChild(logicalOpSelect);
//   } else if (parentNode.id === "root" && parentNode.children.length === 0) {
//     const placeholderText = document.createElement("span");
//     placeholderText.className = "text-secondary fst-italic";
//     placeholderText.textContent =
//       'No conditions added. Click "Add Filter Condition Row" to start.';
//     groupHeaderDiv.appendChild(placeholderText);
//   }

//   const groupButtonsDiv = document.createElement("div");
//   groupButtonsDiv.className = "btn-group btn-group-sm";

//   const addConditionBtn = createButtonTokenFlex(
//     `<i class="fas fa-plus-circle me-1"></i> Add Condition`,
//     "btn btn-outline-primary btn-sm",
//     () => {
//       const newCond = createConditionNode(parentNode.id);
//       parentNode.children.push(newCond);
//       renderFilterTree(); // Re-render the whole tree for now, can be optimized
//       openIndicatorPickerModal(newCond.id, "left");
//     }
//   );
//   groupButtonsDiv.appendChild(addConditionBtn);

//   const addGroupBtn = createButtonTokenFlex(
//     `<i class="fas fa-object-group me-1"></i> Add Group`,
//     "btn btn-outline-secondary btn-sm",
//     () => {
//       const newSubGroup = createGroupNode(parentNode.id);
//       parentNode.children.push(newSubGroup);
//       renderFilterTree();
//     }
//   );
//   groupButtonsDiv.appendChild(addGroupBtn);

//   if (parentNode.id !== "root") {
//     // Root group cannot be deleted this way
//     const deleteGroupBtn = createButtonTokenFlex(
//       `<i class="fas fa-trash"></i>`,
//       "btn btn-outline-danger btn-sm",
//       () => {
//         if (confirm(`Delete this group and all its conditions/sub-groups?`)) {
//           removeNodeFromTree(parentNode.id);
//           renderFilterTree();
//         }
//       }
//     );
//     deleteGroupBtn.title = "Delete this group";
//     groupButtonsDiv.appendChild(deleteGroupBtn);
//   }
//   groupHeaderDiv.appendChild(groupButtonsDiv);
//   groupDiv.appendChild(groupHeaderDiv);

//   // Children container
//   const childrenContainerDiv = document.createElement("div");
//   childrenContainerDiv.className = "filter-group-children mt-2";
//   groupDiv.appendChild(childrenContainerDiv);

//   parentNode.children.forEach((childNode) => {
//     if (childNode.type === "group") {
//       renderFilterTree(childNode, childrenContainerDiv, level + 1);
//     } else if (childNode.type === "condition") {
//       childrenContainerDiv.appendChild(
//         createConditionRowElement(childNode, level + 1)
//       );
//     }
//   });
//   containerElement.appendChild(groupDiv);
// }

// function createConditionRowElement(conditionNode, level) {
//   const rowDiv = document.createElement("div");
//   rowDiv.className = "filter-row-tokenized align-items-center"; // Bootstrap class for alignment
//   // rowDiv.style.marginLeft = `${level * 10}px`; // Indent conditions slightly less than groups

//   // Left Operand
//   if (conditionNode.left) {
//     rowDiv.appendChild(
//       createOperandToken(conditionNode.left, "left", conditionNode.id)
//     );
//   } else {
//     rowDiv.appendChild(
//       createButtonToken("📊 L Operand", "builder-token btn-sm", (e) => {
//         e.stopPropagation();
//         openIndicatorPickerModal(conditionNode.id, "left");
//       })
//     );
//   }

//   // Operator
//   if (conditionNode.op) {
//     const opMeta = OPERATORS.find((o) => o.value === conditionNode.op) || {
//       icon: "?",
//       label: conditionNode.op,
//     };
//     rowDiv.appendChild(
//       createButtonToken(
//         `${opMeta.icon} ${opMeta.label}`,
//         "token-mini token-op btn-sm",
//         (e) => {
//           e.stopPropagation();
//           openOperatorPickerModal(conditionNode.id);
//         }
//       )
//     );
//   } else if (conditionNode.left) {
//     rowDiv.appendChild(
//       createButtonToken("? Operator", "builder-token token-op btn-sm", (e) => {
//         e.stopPropagation();
//         openOperatorPickerModal(conditionNode.id);
//       })
//     );
//   }

//   // Right Operand
//   if (conditionNode.right) {
//     rowDiv.appendChild(
//       createOperandToken(conditionNode.right, "right", conditionNode.id)
//     );
//   } else if (conditionNode.op) {
//     rowDiv.appendChild(
//       createButtonToken("🔢 R Operand", "builder-token btn-sm", (e) => {
//         e.stopPropagation();
//         openIndicatorPickerModal(conditionNode.id, "right");
//       })
//     );
//   }

//   // Extend condition button (placeholder for future)
//   const extendBtn = createButtonTokenFlex(
//     '<i class="fas fa-ellipsis-h"></i>',
//     "icon-btn text-info btn-sm",
//     () => {
//       alert(
//         `Extend functionality for condition ${conditionNode.id} (e.g., add math operation) - TBD`
//       );
//     }
//   );
//   extendBtn.title = "Extend condition (e.g. Math operation)";
//   rowDiv.appendChild(extendBtn);

//   const deleteBtn = createButtonTokenFlex(
//     `<i class="fas fa-times"></i>`,
//     "icon-btn remove-filter-btn btn-sm ms-auto",
//     (e) => {
//       e.stopPropagation();
//       if (confirm("Delete this condition?")) {
//         removeNodeFromTree(conditionNode.id);
//         renderFilterTree();
//       }
//     }
//   );
//   deleteBtn.title = "Delete Condition";
//   rowDiv.appendChild(deleteBtn);

//   return rowDiv;
// }

// // Helper for buttons with icons, ensures flex display for proper icon alignment
// function createButtonTokenFlex(innerHTML, className, onClickHandler) {
//   const button = document.createElement("button");
//   button.className = className + " d-inline-flex align-items-center"; // Added flex classes
//   button.innerHTML = innerHTML;
//   button.type = "button";
//   button.addEventListener("click", onClickHandler);
//   return button;
// }

// // --- Event Handlers for Adding Nodes ---
// function handleAddRootCondition() {
//   const newCond = createConditionNode(window.filterTree.id); // Add to root group
//   window.filterTree.children.push(newCond);
//   renderFilterTree();
//   openIndicatorPickerModal(newCond.id, "left"); // Open picker for the new condition
// }

// // --- Operand Token Creation (Largely similar to previous, but uses nodeId) ---
// function createOperandToken(operand, side, nodeId) {
//   const wrapperSpan = document.createElement("span");
//   wrapperSpan.className = `token-operand-group ${
//     operand.type === "indicator" ? "token-ind-formula" : "token-number"
//   }`;
//   wrapperSpan.classList.add(
//     "d-inline-flex",
//     "flex-wrap",
//     "gap-1",
//     "align-items-center"
//   );

//   if (operand.type === "indicator") {
//     const indDef = INDICATORS.find((i) => i.value === operand.value);
//     const displayParams = operand.params || {};
//     const actualParamsFromDef = indDef
//       ? indDef.params || []
//       : getImplicitParams(operand.value);

//     wrapperSpan.appendChild(
//       createButtonToken(
//         displayParams.timeframe || "Daily",
//         "token-mini token-tf btn-sm",
//         (e) => {
//           e.stopPropagation();
//           openIndicatorConfigEditor(nodeId, side, "timeframe", indDef);
//         }
//       )
//     );
//     wrapperSpan.appendChild(
//       createButtonToken(operand.value, "token-mini token-ind btn-sm", (e) => {
//         // Short name
//         e.stopPropagation();
//         openIndicatorPickerModal(nodeId, side); // To change indicator type
//       })
//     );

//     const configurableParamsToShow = [];
//     // Simplified: check actualParamsFromDef and add if present in displayParams
//     actualParamsFromDef.forEach((paramKey) => {
//       if (paramKey === "timeframe") return; // Already handled
//       if (displayParams[paramKey] !== undefined) {
//         let paramClass = `token-${paramKey.replace("_", "")}`; // e.g. token-fastperiod
//         configurableParamsToShow.push({
//           key: paramKey,
//           label: String(displayParams[paramKey]),
//           class: paramClass,
//         });
//       } else if (
//         paramKey === "field" &&
//         actualParamsFromDef.includes("field")
//       ) {
//         // Default for field if not set
//         configurableParamsToShow.push({
//           key: "field",
//           label: "close",
//           class: "token-field",
//         });
//       }
//     });

//     if (configurableParamsToShow.length > 0) {
//       wrapperSpan.appendChild(document.createTextNode("("));
//       configurableParamsToShow.forEach((param, idx) => {
//         wrapperSpan.appendChild(
//           createButtonToken(
//             param.label,
//             `token-mini ${param.class} btn-sm`,
//             (e) => {
//               e.stopPropagation();
//               openIndicatorConfigEditor(nodeId, side, param.key, indDef);
//             }
//           )
//         );
//         if (idx < configurableParamsToShow.length - 1)
//           wrapperSpan.appendChild(document.createTextNode(", "));
//       });
//       wrapperSpan.appendChild(document.createTextNode(")"));
//     }
//   } else if (operand.type === "number") {
//     wrapperSpan.appendChild(
//       createButtonToken(
//         String(operand.value),
//         "token-mini token-num btn-sm",
//         (e) => {
//           e.stopPropagation();
//           editNumberToken(nodeId, side);
//         }
//       )
//     );
//   }
//   return wrapperSpan;
// }

// // --- Modal Interaction Logic (Updated for Node IDs) ---
// function openIndicatorPickerModal(nodeId, targetSide) {
//   CURRENT_MODAL_NODE_ID = nodeId;
//   CURRENT_MODAL_TARGET_SIDE = targetSide;
//   indicatorSearchInput.value = "";
//   renderIndicatorModalList();
//   indicatorModalInstance.show();
// }

// function openOperatorPickerModal(nodeId) {
//   CURRENT_MODAL_NODE_ID = nodeId;
//   renderOperatorModalList();
//   operatorModalInstance.show();
// }

// function openIndicatorConfigEditor(
//   nodeId,
//   targetSide,
//   focusedParamKey = null,
//   selectedIndicatorDef = null
// ) {
//   CURRENT_MODAL_NODE_ID = nodeId;
//   CURRENT_MODAL_TARGET_SIDE = targetSide;
//   const conditionNode = findNodeById(nodeId);

//   if (!conditionNode || conditionNode.type !== "condition") {
//     console.error(
//       "Invalid node ID or not a condition node for config editor:",
//       nodeId
//     );
//     return;
//   }

//   const existingOperand = conditionNode[targetSide];

//   if (selectedIndicatorDef) {
//     CURRENT_MODAL_INDICATOR_DEF = selectedIndicatorDef;
//   } else if (existingOperand && existingOperand.type === "indicator") {
//     CURRENT_MODAL_INDICATOR_DEF = INDICATORS.find(
//       (ind) => ind.value === existingOperand.value
//     ) || {
//       label: existingOperand.label || existingOperand.value,
//       value: existingOperand.value,
//       params: getImplicitParams(existingOperand.value),
//     };
//   } else {
//     console.error(
//       "Cannot configure: No indicator definition for node:",
//       nodeId,
//       "side:",
//       targetSide
//     );
//     indicatorConfigModalInstance.hide();
//     return;
//   }

//   indicatorConfigModalLabel.textContent = `Configure: ${CURRENT_MODAL_INDICATOR_DEF.label}`;
//   const currentParams =
//     existingOperand && existingOperand.params ? existingOperand.params : {};
//   const indicatorDefinedParams =
//     CURRENT_MODAL_INDICATOR_DEF.params ||
//     getImplicitParams(CURRENT_MODAL_INDICATOR_DEF.value);

//   indicatorConfigTimeframeSelect.value = (
//     currentParams.timeframe || "daily"
//   ).toLowerCase();

//   const setupField = (paramKey, groupEl, inputEl, defaultValue) => {
//     if (indicatorDefinedParams.includes(paramKey)) {
//       groupEl.style.display = "block";
//       inputEl.value =
//         currentParams[paramKey] !== undefined
//           ? currentParams[paramKey]
//           : defaultValue;
//     } else {
//       groupEl.style.display = "none";
//     }
//   };

//   setupField(
//     "field",
//     indicatorConfigFieldGroup,
//     indicatorConfigFieldSelect,
//     "close"
//   );
//   setupField(
//     "period",
//     indicatorConfigPeriodGroup,
//     indicatorConfigPeriodInput,
//     "14"
//   );
//   setupField(
//     "fast_period",
//     indicatorConfigFastPeriodGroup,
//     indicatorConfigFastPeriodInput,
//     "12"
//   );
//   setupField(
//     "slow_period",
//     indicatorConfigSlowPeriodGroup,
//     indicatorConfigSlowPeriodInput,
//     "26"
//   );
//   setupField(
//     "signal_period",
//     indicatorConfigSignalPeriodGroup,
//     indicatorConfigSignalPeriodInput,
//     "9"
//   );
//   setupField(
//     "nbdev",
//     indicatorConfigNbdevGroup,
//     indicatorConfigNbdevInput,
//     "2"
//   );
//   setupField(
//     "multiplier",
//     indicatorConfigMultiplierGroup,
//     indicatorConfigMultiplierInput,
//     "2.0"
//   );
//   setupField(
//     "fastk_period",
//     indicatorConfigFastKPeriodGroup,
//     indicatorConfigFastKPeriodInput,
//     "14"
//   );
//   setupField(
//     "slowk_period",
//     indicatorConfigSlowKPeriodGroup,
//     indicatorConfigSlowKPeriodInput,
//     "3"
//   );
//   setupField(
//     "slowd_period",
//     indicatorConfigSlowDPeriodGroup,
//     indicatorConfigSlowDPeriodInput,
//     "3"
//   );

//   indicatorConfigModalInstance.show();
// }

// function editNumberToken(nodeId, side) {
//   const conditionNode = findNodeById(nodeId);
//   if (!conditionNode || conditionNode.type !== "condition") return;
//   const currentOperand = conditionNode[side];
//   let newValue = prompt(
//     "Enter number:",
//     currentOperand ? currentOperand.value : "0"
//   );
//   if (newValue !== null && !isNaN(parseFloat(newValue))) {
//     conditionNode[side] = { type: "number", value: parseFloat(newValue) }; // Ensure it's set correctly
//     renderFilterTree();
//   }
// }

// function renderIndicatorModalList() {
//   // ... (largely same as previous, ensure event listener calls openIndicatorConfigEditor with indicatorDef)
//   const searchTerm = indicatorSearchInput.value.toLowerCase();
//   indicatorListUl.innerHTML = "";

//   const numLi = document.createElement("li");
//   numLi.className = "list-group-item list-group-item-action text-primary";
//   numLi.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant value)</b>`;
//   numLi.addEventListener("click", () => {
//     let numValStr = prompt("Enter number value:", "0");
//     if (numValStr !== null) {
//       const numVal = parseFloat(numValStr);
//       if (!isNaN(numVal)) {
//         applyOperandSelection({ type: "number", value: numVal });
//         indicatorModalInstance.hide();
//       } else {
//         alert("Invalid number entered.");
//       }
//     }
//   });
//   indicatorListUl.appendChild(numLi);

//   if (Object.keys(INDICATOR_GROUPS).length > 0) {
//     Object.entries(INDICATOR_GROUPS).forEach(
//       ([groupName, indicatorsInGroup]) => {
//         const filteredIndicators = indicatorsInGroup.filter(
//           (ind) =>
//             ind.label.toLowerCase().includes(searchTerm) ||
//             ind.value.toLowerCase().includes(searchTerm)
//         );
//         if (filteredIndicators.length > 0) {
//           const groupHeaderLi = document.createElement("li");
//           groupHeaderLi.className =
//             "list-group-item list-group-item-secondary fw-bold";
//           groupHeaderLi.textContent = groupName;
//           groupHeaderLi.style.background = "#232b3b";
//           groupHeaderLi.style.color = "#5eead4";
//           indicatorListUl.appendChild(groupHeaderLi);

//           filteredIndicators.forEach((indicatorDef) => {
//             const li = document.createElement("li");
//             li.className = "list-group-item list-group-item-action";
//             li.innerHTML = `<span style="font-size:1.1em;">📊</span> ${indicatorDef.label}`;
//             li.addEventListener("click", () => {
//               indicatorModalInstance.hide();
//               openIndicatorConfigEditor(
//                 CURRENT_MODAL_NODE_ID,
//                 CURRENT_MODAL_TARGET_SIDE,
//                 null,
//                 indicatorDef
//               );
//             });
//             indicatorListUl.appendChild(li);
//           });
//         }
//       }
//     );
//   } else {
//     indicatorListUl.innerHTML =
//       '<li class="list-group-item">No indicators loaded.</li>';
//   }
// }

// function renderOperatorModalList() {
//   // ... (same as previous)
//   operatorListUl.innerHTML = "";
//   OPERATORS.forEach((op) => {
//     const li = document.createElement("li");
//     li.className = "list-group-item list-group-item-action";
//     li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b> (${op.value})`;
//     li.addEventListener("click", () => {
//       applyOperatorSelection(op.value);
//       operatorModalInstance.hide();
//     });
//     operatorListUl.appendChild(li);
//   });
// }

// function handleIndicatorConfigDone() {
//   // ... (largely same as previous, reads from CURRENT_MODAL_INDICATOR_DEF.params)
//   if (!CURRENT_MODAL_INDICATOR_DEF) {
//     indicatorConfigModalInstance.hide();
//     return;
//   }
//   const params = { timeframe: indicatorConfigTimeframeSelect.value };
//   const indicatorDefinedParams =
//     CURRENT_MODAL_INDICATOR_DEF.params ||
//     getImplicitParams(CURRENT_MODAL_INDICATOR_DEF.value);

//   const readParamIfVisible = (
//     paramKey,
//     groupEl,
//     inputEl,
//     isNumeric = true,
//     isFloat = false
//   ) => {
//     if (
//       indicatorDefinedParams.includes(paramKey) &&
//       groupEl.style.display !== "none"
//     ) {
//       let val = inputEl.value;
//       if (inputEl.type === "select-one") val = val.toLowerCase();
//       else if (isNumeric) val = isFloat ? parseFloat(val) : parseInt(val, 10);
//       if (!(isNumeric && isNaN(val))) params[paramKey] = val; // Only assign if not NaN for numbers
//     }
//   };
//   readParamIfVisible(
//     "field",
//     indicatorConfigFieldGroup,
//     indicatorConfigFieldSelect,
//     false
//   );
//   readParamIfVisible(
//     "period",
//     indicatorConfigPeriodGroup,
//     indicatorConfigPeriodInput
//   );
//   readParamIfVisible(
//     "fast_period",
//     indicatorConfigFastPeriodGroup,
//     indicatorConfigFastPeriodInput
//   );
//   readParamIfVisible(
//     "slow_period",
//     indicatorConfigSlowPeriodGroup,
//     indicatorConfigSlowPeriodInput
//   );
//   readParamIfVisible(
//     "signal_period",
//     indicatorConfigSignalPeriodGroup,
//     indicatorConfigSignalPeriodInput
//   );
//   readParamIfVisible(
//     "nbdev",
//     indicatorConfigNbdevGroup,
//     indicatorConfigNbdevInput,
//     true,
//     true
//   );
//   readParamIfVisible(
//     "multiplier",
//     indicatorConfigMultiplierGroup,
//     indicatorConfigMultiplierInput,
//     true,
//     true
//   );
//   readParamIfVisible(
//     "fastk_period",
//     indicatorConfigFastKPeriodGroup,
//     indicatorConfigFastKPeriodInput
//   );
//   readParamIfVisible(
//     "slowk_period",
//     indicatorConfigSlowKPeriodGroup,
//     indicatorConfigSlowKPeriodInput
//   );
//   readParamIfVisible(
//     "slowd_period",
//     indicatorConfigSlowDPeriodGroup,
//     indicatorConfigSlowDPeriodInput
//   );

//   applyOperandSelection({
//     type: "indicator",
//     value: CURRENT_MODAL_INDICATOR_DEF.value,
//     label: CURRENT_MODAL_INDICATOR_DEF.label,
//     params: params,
//   });
//   indicatorConfigModalInstance.hide();
// }

// function applyOperandSelection(operandConfig) {
//   const conditionNode = findNodeById(CURRENT_MODAL_NODE_ID);
//   if (!conditionNode || conditionNode.type !== "condition") return;

//   conditionNode[CURRENT_MODAL_TARGET_SIDE] = operandConfig;

//   if (CURRENT_MODAL_TARGET_SIDE === "left") {
//     conditionNode.step = 2;
//     renderFilterTree();
//     openOperatorPickerModal(conditionNode.id);
//   } else {
//     conditionNode.step = 4;
//     renderFilterTree();
//   }
// }

// function applyOperatorSelection(operatorValue) {
//   const conditionNode = findNodeById(CURRENT_MODAL_NODE_ID);
//   if (!conditionNode || conditionNode.type !== "condition") return;
//   conditionNode.op = operatorValue;
//   conditionNode.step = 3;
//   renderFilterTree();
//   openIndicatorPickerModal(conditionNode.id, "right");
// }

// // --- Utility and Backend Communication ---
// function getCookie(name) {
//   /* ... same as previous ... */
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

// function getImplicitParams(indicatorValue) {
//   // Basic fallback if indicatorDef.params is missing
//   // console.warn(`Using implicit params for ${indicatorValue}`);
//   if (indicatorValue.toUpperCase().startsWith("CDL")) return ["timeframe"];
//   const noFieldParams = [
//     "VOLUME",
//     "OBV",
//     "AD",
//     "ADOSC",
//     "CLOSE",
//     "OPEN",
//     "HIGH",
//     "LOW",
//     "AVGPRICE",
//     "MEDPRICE",
//     "TYPPRICE",
//     "WCLPRICE",
//     "TRANGE",
//     "ATR",
//     "NATR",
//   ];
//   if (noFieldParams.includes(indicatorValue.toUpperCase()))
//     return ["timeframe", "period"];
//   return ["timeframe", "field", "period"];
// }

// function transformFilterTreeForBackend(node) {
//   if (node.type === "condition") {
//     if (!node.left || !node.op || !node.right) return null; // Incomplete condition

//     let transformed = {};
//     if (node.left.type === "indicator") {
//       transformed.indicator = node.left.value;
//       Object.assign(transformed, node.left.params);
//     } else {
//       return null; /* Left must be indicator for now */
//     }

//     transformed.mainOp = node.op;

//     if (node.right.type === "number") {
//       transformed.rightType = "number";
//       transformed.rightValue = node.right.value;
//     } else if (node.right.type === "indicator") {
//       transformed.rightType = "indicator";
//       transformed.rightIndicator = node.right.value;
//       if (node.right.params) {
//         for (const key in node.right.params) {
//           transformed[`right${key.charAt(0).toUpperCase() + key.slice(1)}`] =
//             node.right.params[key];
//         }
//       }
//     } else {
//       return null; /* Right operand missing or invalid type */
//     }
//     return transformed;
//   } else if (node.type === "group") {
//     const childrenConditions = node.children
//       .map((child) => transformFilterTreeForBackend(child))
//       .filter((child) => child !== null);

//     if (childrenConditions.length === 0) return null;

//     // If group has only one child and it's a condition, return it directly (no group needed)
//     // if (childrenConditions.length === 1 && !childrenConditions[0].conditions) return childrenConditions[0];

//     return {
//       logicalOperator: node.logicalOperator,
//       conditions: childrenConditions,
//     };
//   }
//   return null;
// }

// function handleRunScan() {
//   resultsTableBody.innerHTML =
//     '<tr><td colspan="10" class="text-center py-5" style="color:#6b7280;"><i class="fas fa-spinner fa-spin fa-2x me-2"></i>Running scan...</td></tr>';
//   stockCountSpan.textContent = "Matching Stocks: -";

//   const payloadFilters = transformFilterTreeForBackend(window.filterTree);

//   if (
//     !payloadFilters ||
//     (payloadFilters.conditions && payloadFilters.conditions.length === 0)
//   ) {
//     resultsTableBody.innerHTML =
//       '<tr><td colspan="10" class="text-center py-5" style="color:#6b7280;">No valid filters specified or all filters are incomplete.</td></tr>';
//     stockCountSpan.textContent = "Matching Stocks: 0";
//     return;
//   }

//   fetch("/screener/api/run_screener/", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//       "X-CSRFToken": getCookie("csrftoken"),
//     },
//     body: JSON.stringify({
//       filters: payloadFilters, // Send the transformed tree structure
//       segment: document.getElementById("segmentDropdown")?.value || "Nifty 500",
//     }),
//   })
//     .then((response) =>
//       response.ok
//         ? response.json()
//         : response
//             .json()
//             .then((err) =>
//               Promise.reject(err.error || `Server error: ${response.status}`)
//             )
//     )
//     .then((data) => {
//       if (data.error) {
//         console.error("Backend scan error:", data.error);
//         resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5" style="color:#f87171;">Error: ${data.error}</td></tr>`;
//         stockCountSpan.textContent = "Matching Stocks: 0";
//       } else if (data.results) {
//         updateResultsTable(data.results);
//       } else {
//         updateResultsTable([]);
//       }
//     })
//     .catch((error) => {
//       console.error("Error running scan:", error);
//       resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5" style="color:#f87171;">Error: ${
//         error.message || error
//       }</td></tr>`;
//       stockCountSpan.textContent = "Matching Stocks: 0";
//     });
// }

// function updateResultsTable(results) {
//   /* ... same as previous ... */
//   const tbody = document.getElementById("resultsTableBody");
//   const countSpan = document.getElementById("stockCount");
//   tbody.innerHTML = "";

//   if (!results || results.length === 0) {
//     tbody.innerHTML =
//       '<tr><td colspan="10" class="text-center py-5" style="color:#6b7280;">No stocks match your criteria.</td></tr>';
//     countSpan.textContent = "Matching Stocks: 0";
//     return;
//   }

//   countSpan.textContent = `Matching Stocks: ${results.length}`;
//   results.forEach((stock, index) => {
//     const tr = tbody.insertRow();
//     let changePctStyle = "";
//     let changePctText = stock.change_pct || "N/A";
//     if (stock.change_pct && typeof stock.change_pct === "string") {
//       const numericChange = parseFloat(stock.change_pct.replace("%", ""));
//       if (!isNaN(numericChange)) {
//         changePctStyle =
//           numericChange >= 0 ? "color:#34d399;" : "color:#f87171;";
//         changePctText = `${numericChange.toFixed(2)}%`;
//       }
//     }
//     const formatNum = (num, digits = 2) =>
//       typeof num === "number" ||
//       (typeof num === "string" && num !== "" && !isNaN(Number(num)))
//         ? Number(num).toFixed(digits)
//         : num || "N/A";

//     tr.innerHTML = `
//         <td>${index + 1}</td>
//         <td class="fw-medium" style="color:#a78bfa;">${
//           stock.symbol || "N/A"
//         }</td>
//         <td>${stock.timestamp || "N/A"}</td>
//         <td>${formatNum(stock.open)}</td>
//         <td>${formatNum(stock.high)}</td>
//         <td>${formatNum(stock.low)}</td>
//         <td>${formatNum(stock.close)}</td>
//         <td style="${changePctStyle}">${changePctText}</td>
//         <td>${formatNum(stock.volume, 0)}</td>
//         <td>
//             <button type="button" class="icon-btn text-info btn-sm" title="View Chart"><i class="fas fa-chart-line"></i></button>
//             <button type="button" class="icon-btn text-primary btn-sm" title="Add to Watchlist"><i class="fas fa-plus-square"></i></button>
//         </td>`;
//   });
// }

// // Helper to create generic button token
// function createButtonToken(text, className, onClickHandler) {
//   const button = document.createElement("button");
//   button.className = className;
//   button.innerHTML = text;
//   button.type = "button";
//   button.addEventListener("click", onClickHandler);
//   return button;
// }

// {% static 'screener/js/builder.js' %}

// --- Constants ---
// {% static 'screener/js/builder.js' %}

// --- Constants ---
let INDICATORS = []; // Populated by fetchIndicatorsAndRender from INDICATOR_GROUPS
let INDICATOR_GROUPS = {}; // Populated by fetchIndicatorsAndRender

const LOGICAL_OPERATORS = [
  { value: "AND", label: "AND" },
  { value: "OR", label: "OR" },
];

const OPERATORS = [
  { value: ">", label: "Greater than", icon: "＞" },
  { value: ">=", label: "Greater than or equal to", icon: "≥" },
  { value: "<", label: "Less than", icon: "＜" },
  { value: "<=", label: "Less than or equal to", icon: "≤" },
  { value: "==", label: "Equals", icon: "＝" },
  { value: "crosses_above", label: "Crosses above", icon: "⤴️" },
  { value: "crosses_below", label: "Crosses below", icon: "⤵️" },
];

const DEFAULT_TIMEFRAMES = [
  "Daily",
  "Weekly",
  "Monthly",
  "1hour",
  "30min",
  "15min",
  "5min",
  "1min",
];
const DEFAULT_FIELDS = ["Open", "High", "Low", "Close", "Volume"];

// --- Global State ---
let nodeIdCounter = 0;
window.filterTree = createGroupNode("root", "AND"); // Initialize with a root AND group

let CURRENT_MODAL_NODE_ID = null;
let CURRENT_MODAL_TARGET_SIDE = null;
let CURRENT_MODAL_INDICATOR_DEF = null;

// --- Modal Instances (Bootstrap) ---
let indicatorModalInstance, indicatorConfigModalInstance, operatorModalInstance;

// --- DOM Elements ---
const filterTreeContainer = document.getElementById("filter-list");
const addRootFilterButton = document.getElementById("add-filter");
const runScanButton = document.getElementById("runScan");
const clearFiltersButton = document.getElementById("clearFiltersButton");

const indicatorSearchInput = document.getElementById("indicatorSearch");
const indicatorListUl = document.getElementById("indicatorList");

const indicatorConfigModalLabel = document.getElementById(
  "indicatorConfigModalLabelText"
);
const indicatorConfigTimeframeSelect = document.getElementById(
  "indicatorConfigTimeframe"
);
const indicatorConfigFieldSelect = document.getElementById(
  "indicatorConfigField"
);
const indicatorConfigFieldGroup = document.getElementById(
  "indicatorConfigFieldGroup"
);
const indicatorConfigPeriodGroup = document.getElementById(
  "indicatorConfigPeriodGroup"
);
const indicatorConfigPeriodInput = document.getElementById(
  "indicatorConfigPeriod"
);
const indicatorConfigFastPeriodGroup = document.getElementById(
  "indicatorConfigFastPeriodGroup"
);
const indicatorConfigFastPeriodInput = document.getElementById(
  "indicatorConfigFastPeriod"
);
const indicatorConfigSlowPeriodGroup = document.getElementById(
  "indicatorConfigSlowPeriodGroup"
);
const indicatorConfigSlowPeriodInput = document.getElementById(
  "indicatorConfigSlowPeriod"
);
const indicatorConfigSignalPeriodGroup = document.getElementById(
  "indicatorConfigSignalPeriodGroup"
);
const indicatorConfigSignalPeriodInput = document.getElementById(
  "indicatorConfigSignalPeriod"
);
const indicatorConfigMultiplierGroup = document.getElementById(
  "indicatorConfigMultiplierGroup"
);
const indicatorConfigMultiplierInput = document.getElementById(
  "indicatorConfigMultiplier"
);
const indicatorConfigNbdevGroup = document.getElementById(
  "indicatorConfigNbdevGroup"
);
const indicatorConfigNbdevInput = document.getElementById(
  "indicatorConfigNbdev"
);
const indicatorConfigFastKPeriodGroup = document.getElementById(
  "indicatorConfigFastKPeriodGroup"
);
const indicatorConfigFastKPeriodInput = document.getElementById(
  "indicatorConfigFastKPeriod"
);
const indicatorConfigSlowKPeriodGroup = document.getElementById(
  "indicatorConfigSlowKPeriodGroup"
);
const indicatorConfigSlowKPeriodInput = document.getElementById(
  "indicatorConfigSlowKPeriod"
);
const indicatorConfigSlowDPeriodGroup = document.getElementById(
  "indicatorConfigSlowDPeriodGroup"
);
const indicatorConfigSlowDPeriodInput = document.getElementById(
  "indicatorConfigSlowDPeriod"
);
const indicatorConfigDoneButton = document.getElementById(
  "indicatorConfigDone"
);

const operatorListUl = document.getElementById("operatorList");
const resultsTableBody = document.getElementById("resultsTableBody");
const stockCountSpan = document.getElementById("stockCount");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  indicatorModalInstance = new bootstrap.Modal(
    document.getElementById("indicatorModal")
  );
  indicatorConfigModalInstance = new bootstrap.Modal(
    document.getElementById("indicatorConfigModal")
  );
  operatorModalInstance = new bootstrap.Modal(
    document.getElementById("operatorModal")
  );

  DEFAULT_TIMEFRAMES.forEach((tf) =>
    indicatorConfigTimeframeSelect.options.add(new Option(tf, tf.toLowerCase()))
  );
  DEFAULT_FIELDS.forEach((f) =>
    indicatorConfigFieldSelect.options.add(new Option(f, f.toLowerCase()))
  );

  if (addRootFilterButton) {
    addRootFilterButton.innerHTML =
      '<i class="fas fa-plus-circle me-2"></i>Add Initial Condition'; // Clarify button text
    addRootFilterButton.addEventListener("click", handleAddRootCondition);
  }
  if (indicatorSearchInput)
    indicatorSearchInput.addEventListener("input", renderIndicatorModalList);
  if (indicatorConfigDoneButton)
    indicatorConfigDoneButton.addEventListener(
      "click",
      handleIndicatorConfigDone
    );
  if (runScanButton) runScanButton.addEventListener("click", handleRunScan);
  if (clearFiltersButton) {
    clearFiltersButton.addEventListener("click", () => {
      window.filterTree = createGroupNode("root", "AND");
      nodeIdCounter = 0; // Reset counter for unique IDs
      renderFilterTree();
      resultsTableBody.innerHTML =
        '<tr id="initialMessageRow"><td colspan="10" class="text-center py-5" style="color:#6b7280;">No results yet. Add filters and click "Run Scan".</td></tr>';
      stockCountSpan.textContent = "Matching Stocks: 0";
    });
  }
  fetchIndicatorsAndRender();
});

// --- Tree Node Creation ---
function createGroupNode(parentId = null, logicalOperator = "AND") {
  nodeIdCounter++;
  return {
    id: `g${nodeIdCounter}`, // Use counter for unique group IDs
    type: "group",
    logicalOperator: logicalOperator,
    parentId: parentId,
    children: [],
  };
}

function createConditionNode(parentId) {
  nodeIdCounter++;
  return {
    id: `c${nodeIdCounter}`, // Use counter for unique condition IDs
    type: "condition",
    parentId: parentId,
    left: null,
    op: null,
    right: null,
    step: 1, // 1=left, 2=op, 3=right, 4=complete, 5=logical_op_chosen
  };
}

// --- Find/Remove Node in Tree (Recursive) ---
function findNodeById(nodeId, currentNode = window.filterTree) {
  if (!currentNode) return null;
  if (currentNode.id === nodeId) return currentNode;
  if (currentNode.type === "group" && currentNode.children) {
    for (const child of currentNode.children) {
      const found = findNodeById(nodeId, child);
      if (found) return found;
    }
  }
  return null;
}

function removeNodeFromTree(nodeIdToRemove, currentNode = window.filterTree) {
  if (!currentNode || !currentNode.children || currentNode.type !== "group")
    return false;

  const childIndex = currentNode.children.findIndex(
    (child) => child.id === nodeIdToRemove
  );
  if (childIndex !== -1) {
    currentNode.children.splice(childIndex, 1);
    return true;
  }
  // If not found in direct children, search in grandchildren
  for (const child of currentNode.children) {
    if (child.type === "group") {
      // Only recurse into groups
      if (removeNodeFromTree(nodeIdToRemove, child)) return true;
    }
  }
  return false;
}

// --- Indicator Fetching & Fallback ---
function setDefaultIndicatorsFallback() {
  INDICATOR_GROUPS = {
    Prices: [
      { value: "CLOSE", label: "Close Price (CLOSE)", params: ["timeframe"] },
    ],
    Overlays: [
      {
        value: "SMA",
        label: "Simple Moving Average (SMA)",
        params: ["timeframe", "field", "period"],
      },
      {
        value: "EMA",
        label: "Exponential Moving Average (EMA)",
        params: ["timeframe", "field", "period"],
      },
    ],
    Momentum: [
      {
        value: "RSI",
        label: "Relative Strength Index (RSI)",
        params: ["timeframe", "field", "period"],
      },
    ],
  };
  INDICATORS = [];
  for (const groupName in INDICATOR_GROUPS) {
    if (Array.isArray(INDICATOR_GROUPS[groupName])) {
      INDICATOR_GROUPS[groupName].forEach(
        (ind) => (ind.params = ind.params || getImplicitParams(ind.value))
      );
      INDICATORS = INDICATORS.concat(INDICATOR_GROUPS[groupName]);
    }
  }
  console.warn("Using fallback indicator definitions.");
}

function fetchIndicatorsAndRender() {
  fetch("/screener/api/indicators/")
    .then((response) =>
      response.ok
        ? response.json()
        : Promise.reject(`HTTP error! status: ${response.status}`)
    )
    .then((data) => {
      if (
        data &&
        data.groups &&
        typeof data.groups === "object" &&
        Object.keys(data.groups).length > 0
      ) {
        INDICATOR_GROUPS = data.groups;
        INDICATORS = [];
        for (const groupName in INDICATOR_GROUPS) {
          if (Array.isArray(INDICATOR_GROUPS[groupName])) {
            INDICATOR_GROUPS[groupName].forEach(
              (ind) => (ind.params = ind.params || getImplicitParams(ind.value))
            );
            INDICATORS = INDICATORS.concat(INDICATOR_GROUPS[groupName]);
          }
        }
        if (INDICATORS.length === 0) setDefaultIndicatorsFallback();
        else
          console.log(
            "Indicators loaded from API:",
            INDICATORS.length,
            "total"
          );
      } else {
        console.error("Invalid or empty data.groups from API:", data);
        setDefaultIndicatorsFallback();
      }
    })
    .catch((error) => {
      console.error("Error fetching indicators:", error);
      setDefaultIndicatorsFallback();
    })
    .finally(() => {
      renderFilterTree();
      renderIndicatorModalList();
    });
}

// --- Filter Tree Rendering ---
function renderFilterTree(
  parentNode = window.filterTree,
  containerElement = filterTreeContainer,
  level = 0
) {
  if (level === 0) containerElement.innerHTML = "";

  const groupDiv = document.createElement("div");
  groupDiv.className = "filter-group mb-3";
  groupDiv.style.marginLeft = `${level * 25}px`;

  const groupHeaderDiv = document.createElement("div");
  groupHeaderDiv.className =
    "filter-group-header d-flex align-items-center p-2 rounded-top mb-1";
  groupHeaderDiv.style.backgroundColor = level === 0 ? "#2d3748" : "#374151";
  groupHeaderDiv.style.border = `1px solid ${
    level === 0 ? "#4a5568" : "#5a6678"
  }`;
  groupHeaderDiv.style.borderBottom = "none";

  if (parentNode.id !== "root" || parentNode.children.length > 0 || level > 0) {
    // Show for non-empty root or any sub-group
    const logicalOpSelect = document.createElement("select");
    logicalOpSelect.className = "form-select form-select-sm me-2 shadow-sm";
    logicalOpSelect.style.width = "80px";
    LOGICAL_OPERATORS.forEach((op) =>
      logicalOpSelect.add(new Option(op.label, op.value))
    );
    logicalOpSelect.value = parentNode.logicalOperator;
    logicalOpSelect.addEventListener("change", (e) => {
      parentNode.logicalOperator = e.target.value;
    });
    groupHeaderDiv.appendChild(logicalOpSelect);
    const groupLabel = document.createElement("span");
    groupLabel.className = "fw-semibold me-auto";
    // groupLabel.textContent = "Group"; // Can be omitted for cleaner look
    groupHeaderDiv.appendChild(groupLabel);
  } else if (
    parentNode.id === "root" &&
    parentNode.children.length === 0 &&
    level === 0
  ) {
    const placeholderText = document.createElement("span");
    placeholderText.className = "text-secondary fst-italic p-2";
    placeholderText.textContent =
      'Click "Add Initial Condition" to build your query.';
    groupHeaderDiv.appendChild(placeholderText);
    groupHeaderDiv.style.border = `1px dashed #4a5568`;
  }

  const groupButtonsDiv = document.createElement("div");
  groupButtonsDiv.className = "btn-group btn-group-sm ms-auto";

  const addConditionBtn = createButtonTokenFlex(
    `<i class="fas fa-plus-circle"></i>`, // Icon only for less clutter
    "btn btn-outline-light btn-sm",
    () => {
      const newCond = createConditionNode(parentNode.id);
      parentNode.children.push(newCond);
      renderFilterTree();
      openIndicatorPickerModal(newCond.id, "left");
    }
  );
  addConditionBtn.title = "Add Condition to this Group";
  groupButtonsDiv.appendChild(addConditionBtn);

  const addGroupBtn = createButtonTokenFlex(
    `<i class="fas fa-object-group"></i>`, // Icon only
    "btn btn-outline-light btn-sm",
    () => {
      const newSubGroup = createGroupNode(parentNode.id, "AND");
      parentNode.children.push(newSubGroup);
      renderFilterTree();
    }
  );
  addGroupBtn.title = "Add Sub-Group";
  groupButtonsDiv.appendChild(addGroupBtn);

  if (parentNode.id !== "root") {
    const deleteGroupBtn = createButtonTokenFlex(
      `<i class="fas fa-trash-alt"></i>`, // Icon only
      "btn btn-outline-danger btn-sm",
      () => {
        if (confirm(`Delete this group and ALL its contents?`)) {
          removeNodeFromTree(parentNode.id);
          renderFilterTree();
        }
      }
    );
    deleteGroupBtn.title = "Delete this Group";
    groupButtonsDiv.appendChild(deleteGroupBtn);
  }
  groupHeaderDiv.appendChild(groupButtonsDiv);
  groupDiv.appendChild(groupHeaderDiv);

  const childrenContainerDiv = document.createElement("div");
  childrenContainerDiv.className = "filter-group-children p-2 rounded-bottom";
  childrenContainerDiv.style.backgroundColor =
    level === 0 ? "#1f2937" : "#2d3748";
  childrenContainerDiv.style.border = `1px solid ${
    level === 0 ? "#4a5568" : "#5a6678"
  }`;
  childrenContainerDiv.style.borderTop = "none";
  if (parentNode.children.length === 0 && parentNode.id !== "root") {
    childrenContainerDiv.innerHTML = `<p class="text-xs text-secondary fst-italic m-1">This group is empty. Add conditions or sub-groups.</p>`;
  }

  groupDiv.appendChild(childrenContainerDiv);

  parentNode.children.forEach((childNode) => {
    if (childNode.type === "group") {
      renderFilterTree(childNode, childrenContainerDiv, level + 1);
    } else if (childNode.type === "condition") {
      childrenContainerDiv.appendChild(
        createConditionRowElement(childNode, level + 1) // Pass level here as well for consistency if needed
      );
    }
  });
  containerElement.appendChild(groupDiv);
}

function createConditionRowElement(conditionNode, level) {
  // level parameter added
  const rowFlexContainer = document.createElement("div");
  rowFlexContainer.className =
    "d-flex align-items-center gap-2 mb-2 p-2 rounded";
  rowFlexContainer.style.backgroundColor = "#374151";

  const conditionContentDiv = document.createElement("div");
  conditionContentDiv.className = "filter-row-tokenized flex-grow-1";

  if (conditionNode.left)
    conditionContentDiv.appendChild(
      createOperandToken(conditionNode.left, "left", conditionNode.id)
    );
  else
    conditionContentDiv.appendChild(
      createButtonToken("📊 L Operand", "builder-token btn-sm", (e) => {
        e.stopPropagation();
        openIndicatorPickerModal(conditionNode.id, "left");
      })
    );

  if (conditionNode.op) {
    const opMeta = OPERATORS.find((o) => o.value === conditionNode.op) || {
      icon: "?",
      label: conditionNode.op,
    };
    conditionContentDiv.appendChild(
      createButtonToken(
        `${opMeta.icon} ${opMeta.label}`,
        "token-mini token-op btn-sm",
        (e) => {
          e.stopPropagation();
          openOperatorPickerModal(conditionNode.id);
        }
      )
    );
  } else if (conditionNode.left) {
    conditionContentDiv.appendChild(
      createButtonToken("? Operator", "builder-token token-op btn-sm", (e) => {
        e.stopPropagation();
        openOperatorPickerModal(conditionNode.id);
      })
    );
  }

  if (conditionNode.right)
    conditionContentDiv.appendChild(
      createOperandToken(conditionNode.right, "right", conditionNode.id)
    );
  else if (conditionNode.op)
    conditionContentDiv.appendChild(
      createButtonToken("🔢 R Operand", "builder-token btn-sm", (e) => {
        e.stopPropagation();
        openIndicatorPickerModal(conditionNode.id, "right");
      })
    );

  rowFlexContainer.appendChild(conditionContentDiv);

  const conditionActionsDiv = document.createElement("div");
  conditionActionsDiv.className = "d-flex align-items-center gap-1";

  const extendBtn = createButtonTokenFlex(
    '<i class="fas fa-ellipsis-h"></i>',
    "icon-btn text-info btn-sm",
    () => {
      alert(
        `Extend functionality for condition ${conditionNode.id} (e.g., add math operation) - To be implemented`
      );
    }
  );
  extendBtn.title = "Extend condition (e.g. Math operation)";
  conditionActionsDiv.appendChild(extendBtn);

  const deleteCondBtn = createButtonTokenFlex(
    `<i class="fas fa-times"></i>`,
    "icon-btn remove-filter-btn btn-sm",
    (e) => {
      e.stopPropagation();
      if (confirm("Delete this condition?")) {
        removeNodeFromTree(conditionNode.id);
        renderFilterTree();
      }
    }
  );
  deleteCondBtn.title = "Delete Condition";
  conditionActionsDiv.appendChild(deleteCondBtn);

  rowFlexContainer.appendChild(conditionActionsDiv);

  const continuationContainer = document.createElement("div");
  continuationContainer.className = "mt-1 d-flex justify-content-end gap-1";

  if (conditionNode.step === 4) {
    const andButton = createButtonTokenFlex(
      'AND <i class="fas fa-plus ms-1"></i>',
      "btn btn-outline-success btn-xs", // Using Bootstrap's extra small button class
      () => handleLogicalContinuation(conditionNode.id, "AND")
    );
    const orButton = createButtonTokenFlex(
      'OR <i class="fas fa-plus ms-1"></i>',
      "btn btn-outline-warning btn-xs", // Using Bootstrap's extra small button class
      () => handleLogicalContinuation(conditionNode.id, "OR")
    );
    continuationContainer.appendChild(andButton);
    continuationContainer.appendChild(orButton);
  }

  const conditionWrapperDiv = document.createElement("div");
  conditionWrapperDiv.appendChild(rowFlexContainer);
  conditionWrapperDiv.appendChild(continuationContainer);

  return conditionWrapperDiv;
}

function handleLogicalContinuation(currentConditionId, chosenLogicalOperator) {
  const currentConditionNode = findNodeById(currentConditionId);
  if (!currentConditionNode) return;

  const parentGroupNode = findNodeById(currentConditionNode.parentId);
  if (!parentGroupNode || parentGroupNode.type !== "group") return;

  parentGroupNode.logicalOperator = chosenLogicalOperator;
  currentConditionNode.step = 5;

  const newCond = createConditionNode(parentGroupNode.id);
  parentGroupNode.children.push(newCond);
  renderFilterTree();
  openIndicatorPickerModal(newCond.id, "left");
}

function createButtonTokenFlex(innerHTML, className, onClickHandler) {
  const button = document.createElement("button");
  button.className = `${className} d-inline-flex align-items-center justify-content-center`;
  button.innerHTML = innerHTML;
  button.type = "button";
  button.addEventListener("click", onClickHandler);
  return button;
}

function handleAddRootCondition() {
  const newCond = createConditionNode(window.filterTree.id);
  window.filterTree.children.push(newCond);
  renderFilterTree();
  openIndicatorPickerModal(newCond.id, "left");
}

function createOperandToken(operand, side, nodeId) {
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
    const indDef = INDICATORS.find((i) => i.value === operand.value);
    const displayParams = operand.params || {};
    const actualParamsFromDef = indDef
      ? indDef.params || []
      : getImplicitParams(operand.value);

    wrapperSpan.appendChild(
      createButtonToken(
        (displayParams.timeframe || "Daily").toUpperCase(),
        "token-mini token-tf btn-sm",
        (e) => {
          e.stopPropagation();
          openIndicatorConfigEditor(nodeId, side, "timeframe", indDef);
        }
      )
    );
    wrapperSpan.appendChild(
      createButtonToken(operand.value, "token-mini token-ind btn-sm", (e) => {
        e.stopPropagation();
        openIndicatorPickerModal(nodeId, side);
      })
    );

    const configurableParamsToShow = [];
    actualParamsFromDef.forEach((paramKey) => {
      if (paramKey === "timeframe") return;
      let label;
      let defaultVal = "";
      if (paramKey === "field") defaultVal = "close";
      else if (paramKey.includes("period")) defaultVal = "14";
      else if (paramKey === "nbdev" || paramKey === "multiplier")
        defaultVal = "2";

      label = String(
        displayParams[paramKey] !== undefined
          ? displayParams[paramKey]
          : defaultVal
      );

      if (
        displayParams[paramKey] !== undefined ||
        (paramKey === "field" && actualParamsFromDef.includes("field"))
      ) {
        // Show field by default if it's an expected param
        if (label !== "") {
          // Only show if there's a meaningful label (either set or a non-empty default)
          let paramClass = `token-${paramKey.replace("_", "")}`;
          configurableParamsToShow.push({
            key: paramKey,
            label: label,
            class: paramClass,
          });
        }
      }
    });

    if (configurableParamsToShow.length > 0) {
      wrapperSpan.appendChild(document.createTextNode("("));
      configurableParamsToShow.forEach((param, idx) => {
        wrapperSpan.appendChild(
          createButtonToken(
            param.label,
            `token-mini ${param.class} btn-sm`,
            (e) => {
              e.stopPropagation();
              openIndicatorConfigEditor(nodeId, side, param.key, indDef);
            }
          )
        );
        if (idx < configurableParamsToShow.length - 1)
          wrapperSpan.appendChild(document.createTextNode(", "));
      });
      wrapperSpan.appendChild(document.createTextNode(")"));
    }
  } else if (operand.type === "number") {
    wrapperSpan.appendChild(
      createButtonToken(
        String(operand.value),
        "token-mini token-num btn-sm",
        (e) => {
          e.stopPropagation();
          editNumberToken(nodeId, side);
        }
      )
    );
  }
  return wrapperSpan;
}

function openIndicatorPickerModal(nodeId, targetSide) {
  CURRENT_MODAL_NODE_ID = nodeId;
  CURRENT_MODAL_TARGET_SIDE = targetSide;
  indicatorSearchInput.value = "";
  renderIndicatorModalList();
  indicatorModalInstance.show();
}

function openOperatorPickerModal(nodeId) {
  CURRENT_MODAL_NODE_ID = nodeId;
  renderOperatorModalList();
  operatorModalInstance.show();
}

function openIndicatorConfigEditor(
  nodeId,
  targetSide,
  focusedParamKey = null,
  selectedIndicatorDef = null
) {
  CURRENT_MODAL_NODE_ID = nodeId;
  CURRENT_MODAL_TARGET_SIDE = targetSide;
  const conditionNode = findNodeById(nodeId);

  if (!conditionNode || conditionNode.type !== "condition") {
    console.error(
      "Config Editor: Invalid node ID or not a condition node:",
      nodeId
    );
    return;
  }
  const existingOperand = conditionNode[targetSide];
  if (selectedIndicatorDef) {
    CURRENT_MODAL_INDICATOR_DEF = selectedIndicatorDef;
  } else if (existingOperand && existingOperand.type === "indicator") {
    CURRENT_MODAL_INDICATOR_DEF = INDICATORS.find(
      (ind) => ind.value === existingOperand.value
    ) || {
      // Fallback if not found in master list (should be rare)
      label: existingOperand.label || existingOperand.value,
      value: existingOperand.value,
      params: getImplicitParams(existingOperand.value),
    };
  } else {
    console.error(
      "Config Editor: No indicator definition for node:",
      nodeId,
      "side:",
      targetSide,
      "operand:",
      existingOperand
    );
    indicatorConfigModalInstance.hide();
    return;
  }

  indicatorConfigModalLabel.textContent = `Configure: ${CURRENT_MODAL_INDICATOR_DEF.label}`;
  const currentParams =
    existingOperand && existingOperand.params ? existingOperand.params : {};
  const indicatorDefinedParams =
    CURRENT_MODAL_INDICATOR_DEF.params ||
    getImplicitParams(CURRENT_MODAL_INDICATOR_DEF.value);

  indicatorConfigTimeframeSelect.value = (
    currentParams.timeframe || "daily"
  ).toLowerCase();

  const setupField = (paramKey, groupEl, inputEl, defaultValue) => {
    if (indicatorDefinedParams.includes(paramKey)) {
      groupEl.style.display = "block";
      inputEl.value =
        currentParams[paramKey] !== undefined
          ? currentParams[paramKey]
          : defaultValue;
    } else {
      groupEl.style.display = "none";
    }
  };
  setupField(
    "field",
    indicatorConfigFieldGroup,
    indicatorConfigFieldSelect,
    "close"
  );
  setupField(
    "period",
    indicatorConfigPeriodGroup,
    indicatorConfigPeriodInput,
    "14"
  );
  setupField(
    "fast_period",
    indicatorConfigFastPeriodGroup,
    indicatorConfigFastPeriodInput,
    "12"
  );
  setupField(
    "slow_period",
    indicatorConfigSlowPeriodGroup,
    indicatorConfigSlowPeriodInput,
    "26"
  );
  setupField(
    "signal_period",
    indicatorConfigSignalPeriodGroup,
    indicatorConfigSignalPeriodInput,
    "9"
  );
  setupField(
    "nbdev",
    indicatorConfigNbdevGroup,
    indicatorConfigNbdevInput,
    "2"
  );
  setupField(
    "multiplier",
    indicatorConfigMultiplierGroup,
    indicatorConfigMultiplierInput,
    "2.0"
  );
  setupField(
    "fastk_period",
    indicatorConfigFastKPeriodGroup,
    indicatorConfigFastKPeriodInput,
    "14"
  );
  setupField(
    "slowk_period",
    indicatorConfigSlowKPeriodGroup,
    indicatorConfigSlowKPeriodInput,
    "3"
  );
  setupField(
    "slowd_period",
    indicatorConfigSlowDPeriodGroup,
    indicatorConfigSlowDPeriodInput,
    "3"
  );
  indicatorConfigModalInstance.show();
}

function editNumberToken(nodeId, side) {
  const conditionNode = findNodeById(nodeId);
  if (!conditionNode || conditionNode.type !== "condition") return;
  const currentOperand = conditionNode[side];
  let newValue = prompt(
    "Enter number:",
    currentOperand ? currentOperand.value : "0"
  );
  if (newValue !== null && !isNaN(parseFloat(newValue))) {
    conditionNode[side] = { type: "number", value: parseFloat(newValue) };
    renderFilterTree();
  }
}

function renderIndicatorModalList() {
  const searchTerm = indicatorSearchInput.value.toLowerCase();
  indicatorListUl.innerHTML = "";
  const numLi = document.createElement("li");
  numLi.className = "list-group-item list-group-item-action text-primary";
  numLi.innerHTML = `<span style="font-size:1.1em;">🔢</span> <b>Number (constant value)</b>`;
  numLi.addEventListener("click", () => {
    let numValStr = prompt("Enter number value:", "0");
    if (numValStr !== null) {
      const numVal = parseFloat(numValStr);
      if (!isNaN(numVal)) {
        applyOperandSelection({ type: "number", value: numVal });
        indicatorModalInstance.hide();
      } else {
        alert("Invalid number entered.");
      }
    }
  });
  indicatorListUl.appendChild(numLi);

  if (Object.keys(INDICATOR_GROUPS).length > 0) {
    Object.entries(INDICATOR_GROUPS).forEach(
      ([groupName, indicatorsInGroup]) => {
        const filteredIndicators = indicatorsInGroup.filter(
          (ind) =>
            ind.label.toLowerCase().includes(searchTerm) ||
            ind.value.toLowerCase().includes(searchTerm)
        );
        if (filteredIndicators.length > 0) {
          const groupHeaderLi = document.createElement("li");
          groupHeaderLi.className =
            "list-group-item list-group-item-secondary fw-bold";
          groupHeaderLi.textContent = groupName;
          groupHeaderLi.style.background = "#232b3b";
          groupHeaderLi.style.color = "#5eead4";
          indicatorListUl.appendChild(groupHeaderLi);
          filteredIndicators.forEach((indicatorDef) => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-action";
            li.innerHTML = `<span style="font-size:1.1em;">📊</span> ${indicatorDef.label}`;
            li.addEventListener("click", () => {
              indicatorModalInstance.hide();
              openIndicatorConfigEditor(
                CURRENT_MODAL_NODE_ID,
                CURRENT_MODAL_TARGET_SIDE,
                null,
                indicatorDef
              );
            });
            indicatorListUl.appendChild(li);
          });
        }
      }
    );
  } else {
    indicatorListUl.innerHTML =
      '<li class="list-group-item">No indicators loaded.</li>';
  }
}

function renderOperatorModalList() {
  operatorListUl.innerHTML = "";
  OPERATORS.forEach((op) => {
    const li = document.createElement("li");
    li.className = "list-group-item list-group-item-action";
    li.innerHTML = `<span style="font-size:1.15em;">${op.icon}</span> <b>${op.label}</b> (${op.value})`;
    li.addEventListener("click", () => {
      applyOperatorSelection(op.value);
      operatorModalInstance.hide();
    });
    operatorListUl.appendChild(li);
  });
}

function handleIndicatorConfigDone() {
  if (!CURRENT_MODAL_INDICATOR_DEF) {
    indicatorConfigModalInstance.hide();
    return;
  }
  const params = { timeframe: indicatorConfigTimeframeSelect.value }; // Ensure timeframe is always included
  const definedParams =
    CURRENT_MODAL_INDICATOR_DEF.params ||
    getImplicitParams(CURRENT_MODAL_INDICATOR_DEF.value);
  const readParam = (key, groupEl, inputEl, isNum = true, isFlt = false) => {
    if (definedParams.includes(key) && groupEl.style.display !== "none") {
      let val = inputEl.value;
      if (inputEl.type === "select-one" && key !== "timeframe")
        val = val.toLowerCase();
      // Lowercase for fields, etc. Timeframe is already handled.
      else if (isNum) val = isFlt ? parseFloat(val) : parseInt(val, 10);
      if (!(isNum && isNaN(val))) params[key] = val;
    }
  };
  readParam(
    "field",
    indicatorConfigFieldGroup,
    indicatorConfigFieldSelect,
    false
  );
  readParam("period", indicatorConfigPeriodGroup, indicatorConfigPeriodInput);
  readParam(
    "fast_period",
    indicatorConfigFastPeriodGroup,
    indicatorConfigFastPeriodInput
  );
  readParam(
    "slow_period",
    indicatorConfigSlowPeriodGroup,
    indicatorConfigSlowPeriodInput
  );
  readParam(
    "signal_period",
    indicatorConfigSignalPeriodGroup,
    indicatorConfigSignalPeriodInput
  );
  readParam(
    "nbdev",
    indicatorConfigNbdevGroup,
    indicatorConfigNbdevInput,
    true,
    true
  );
  readParam(
    "multiplier",
    indicatorConfigMultiplierGroup,
    indicatorConfigMultiplierInput,
    true,
    true
  );
  readParam(
    "fastk_period",
    indicatorConfigFastKPeriodGroup,
    indicatorConfigFastKPeriodInput
  );
  readParam(
    "slowk_period",
    indicatorConfigSlowKPeriodGroup,
    indicatorConfigSlowKPeriodInput
  );
  readParam(
    "slowd_period",
    indicatorConfigSlowDPeriodGroup,
    indicatorConfigSlowDPeriodInput
  );
  applyOperandSelection({
    type: "indicator",
    value: CURRENT_MODAL_INDICATOR_DEF.value,
    label: CURRENT_MODAL_INDICATOR_DEF.label,
    params: params,
  });
  indicatorConfigModalInstance.hide();
}

function applyOperandSelection(operandConfig) {
  const conditionNode = findNodeById(CURRENT_MODAL_NODE_ID);
  if (!conditionNode || conditionNode.type !== "condition") return;
  conditionNode[CURRENT_MODAL_TARGET_SIDE] = operandConfig;
  if (CURRENT_MODAL_TARGET_SIDE === "left") {
    conditionNode.step = 2;
    renderFilterTree();
    openOperatorPickerModal(conditionNode.id);
  } else {
    conditionNode.step = 4;
    renderFilterTree();
  }
}

function applyOperatorSelection(operatorValue) {
  const conditionNode = findNodeById(CURRENT_MODAL_NODE_ID);
  if (!conditionNode || conditionNode.type !== "condition") return;
  conditionNode.op = operatorValue;
  conditionNode.step = 3;
  renderFilterTree();
  openIndicatorPickerModal(conditionNode.id, "right");
}

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

function getImplicitParams(indicatorValue) {
  if (indicatorValue.toUpperCase().startsWith("CDL")) return ["timeframe"];
  const noField = [
    "VOLUME",
    "OBV",
    "AD",
    "ADOSC",
    "CLOSE",
    "OPEN",
    "HIGH",
    "LOW",
    "AVGPRICE",
    "MEDPRICE",
    "TYPPRICE",
    "WCLPRICE",
    "TRANGE",
    "ATR",
    "NATR",
  ];
  if (noField.includes(indicatorValue.toUpperCase()))
    return ["timeframe", "period"];
  return ["timeframe", "field", "period"];
}

function transformFilterTreeForBackend(node) {
  if (!node) return null;
  if (node.type === "condition") {
    if (!node.left || !node.op || !node.right) return null;
    let transformed = {};
    if (node.left.type === "indicator") {
      transformed.indicator = node.left.value;
      Object.assign(transformed, node.left.params);
    } else return null; // Left operand must be an indicator currently
    transformed.mainOp = node.op;
    if (node.right.type === "number") {
      transformed.rightType = "number";
      transformed.rightValue = node.right.value;
    } else if (node.right.type === "indicator") {
      transformed.rightType = "indicator";
      transformed.rightIndicator = node.right.value;
      if (node.right.params) {
        for (const key in node.right.params) {
          transformed[`right${key.charAt(0).toUpperCase() + key.slice(1)}`] =
            node.right.params[key];
        }
      }
    } else return null; // Right operand must be number or indicator
    return transformed;
  } else if (node.type === "group") {
    const childrenPayloads = node.children
      .map((child) => transformFilterTreeForBackend(child))
      .filter((child) => child !== null);
    if (childrenPayloads.length === 0 && node.id !== "root") return null; // Don't send empty non-root groups
    if (childrenPayloads.length === 0 && node.id === "root")
      return { logicalOperator: node.logicalOperator, conditions: [] }; // Send empty root group correctly

    return {
      logicalOperator: node.logicalOperator,
      conditions: childrenPayloads,
    };
  }
  return null;
}

function handleRunScan() {
  resultsTableBody.innerHTML =
    '<tr><td colspan="10" class="text-center py-5"><i class="fas fa-spinner fa-spin fa-2x me-2"></i>Running scan...</td></tr>';
  stockCountSpan.textContent = "Matching Stocks: -";
  const payloadFilters = transformFilterTreeForBackend(window.filterTree);

  if (
    !payloadFilters ||
    (payloadFilters.conditions &&
      payloadFilters.conditions.length === 0 &&
      payloadFilters.logicalOperator === "AND" &&
      window.filterTree.children.length === 0)
  ) {
    resultsTableBody.innerHTML =
      '<tr><td colspan="10" class="text-center py-5">No valid filters. Add conditions.</td></tr>';
    stockCountSpan.textContent = "Matching Stocks: 0";
    return;
  }

  fetch("/screener/api/run_screener/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      filters: payloadFilters,
      segment: document.getElementById("segmentDropdown")?.value || "Nifty 500",
    }),
  })
    .then((response) =>
      response.ok
        ? response.json()
        : response
            .json()
            .then((err) =>
              Promise.reject(err.error || `Server error: ${response.status}`)
            )
    )
    .then((data) => {
      if (data.error) {
        console.error("Backend scan error:", data.error);
        resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Error: ${data.error}</td></tr>`;
        stockCountSpan.textContent = "Matching Stocks: 0";
      } else if (data.results) updateResultsTable(data.results);
      else updateResultsTable([]);
    })
    .catch((error) => {
      console.error("Error running scan:", error);
      resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Error: ${
        error.message || error
      }</td></tr>`;
      stockCountSpan.textContent = "Matching Stocks: 0";
    });
}

function updateResultsTable(results) {
  const tbody = document.getElementById("resultsTableBody");
  const countSpan = document.getElementById("stockCount");
  tbody.innerHTML = "";
  if (!results || results.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="10" class="text-center py-5" style="color:#6b7280;">No stocks match your criteria.</td></tr>';
    countSpan.textContent = "Matching Stocks: 0";
    return;
  }
  countSpan.textContent = `Matching Stocks: ${results.length}`;
  results.forEach((stock, index) => {
    const tr = tbody.insertRow();
    let chgStyle = "",
      chgTxt = stock.change_pct || "N/A";
    if (stock.change_pct && typeof stock.change_pct === "string") {
      const numChg = parseFloat(stock.change_pct.replace("%", ""));
      if (!isNaN(numChg)) {
        chgStyle = numChg >= 0 ? "color:#34d399;" : "color:#f87171;";
        chgTxt = `${numChg.toFixed(2)}%`;
      }
    }
    const fmt = (n, d = 2) =>
      typeof n === "number" ||
      (typeof n === "string" && n !== "" && !isNaN(Number(n)))
        ? Number(n).toFixed(d)
        : n || "N/A";
    tr.innerHTML = `<td>${
      index + 1
    }</td><td class="fw-medium" style="color:#a78bfa;">${
      stock.symbol || "N/A"
    }</td><td>${stock.timestamp || "N/A"}</td><td>${fmt(
      stock.open
    )}</td><td>${fmt(stock.high)}</td><td>${fmt(stock.low)}</td><td>${fmt(
      stock.close
    )}</td><td style="${chgStyle}">${chgTxt}</td><td>${fmt(
      stock.volume,
      0
    )}</td><td><button type="button" class="icon-btn text-info btn-sm" title="View Chart"><i class="fas fa-chart-line"></i></button><button type="button" class="icon-btn text-primary btn-sm" title="Add to Watchlist"><i class="fas fa-plus-square"></i></button></td>`;
  });
}

function createButtonToken(text, className, onClickHandler) {
  const button = document.createElement("button");
  button.className = className;
  button.innerHTML = text;
  button.type = "button";
  button.addEventListener("click", onClickHandler);
  return button;
}

// NOTE: The duplicated function block that was previously at the end has been removed.
// Only the first, consistent set of definitions is retained.
