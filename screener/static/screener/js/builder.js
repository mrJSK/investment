/**
 * builder.js
 *
 * This script manages the entire frontend logic for the screener application, including:
 * - Handling user input and query parsing.
 * - Autocomplete suggestions for indicators.
 * - Dynamic modals for configuring indicators and saving/loading scans.
 * - Executing scans by making API calls to the Django backend.
 * - Dynamically rendering scan results in a table, including columns for each indicator in the query.
 * - UI hooks for the backtesting engine.
 */

// ---------------------------
// Utility: Get CSRF token for Django POST requests
// ---------------------------
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

// ---------------------------
// Constants & Global State
// ---------------------------
let ALL_INDICATORS = [];
let INDICATOR_GROUPS = {};
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
const DEFAULT_FIELDS = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"];
let KEYWORDS = {};

const TOKEN_TYPES = {
  NUMBER: "NUMBER",
  IDENTIFIER: "IDENTIFIER",
  INDICATOR_NAME: "INDICATOR_NAME",
  TIME_FRAME: "TIME_FRAME",
  FIELD: "FIELD",
  OPERATOR_COMPARISON: "OPERATOR_COMPARISON",
  OPERATOR_LOGICAL: "OPERATOR_LOGICAL",
  BRACKET_OPEN: "BRACKET_OPEN",
  BRACKET_CLOSE: "BRACKET_CLOSE",
  COMMA: "COMMA",
  EOF: "EOF",
  ERROR: "ERROR",
};

// State variables for various UI interactions
let activeIndicatorForConfig = null;
let lastCursorPosition = 0;
let currentWordForAutocomplete = "";
let wordStartIndex = 0;
let parsedQueryForSave = null;
let segmentValueForSave = "";
// Changed equityChartInstance to store the LightweightCharts chart object
let equityChartInstance = null;
let equitySeries = null; // To store the line series for updating data

// ---------------------------
// Initialization on DOMContentLoaded
// ---------------------------
document.addEventListener("DOMContentLoaded", () => {
  setupAllModals();
  attachPrimaryEventListeners();
  fetchIndicatorsAndRender();
});

/**
 * Attaches event listeners to all primary interactive elements on the page.
 */
function attachPrimaryEventListeners() {
  const queryInput = document.getElementById("queryInput");
  const runScanBtn = document.getElementById("runScan");
  const saveScanBtn = document.getElementById("saveScanButton");
  const clearQueryBtn = document.getElementById("clearFiltersButton");
  const loadScanBtn = document.getElementById("loadScanButton");
  const runBacktestBtn = document.getElementById("runBacktestButton");

  const suggestionBox = createSuggestionBox();
  if (queryInput && queryInput.parentNode) {
    queryInput.parentNode.insertBefore(suggestionBox, queryInput.nextSibling);
    queryInput.addEventListener("input", (e) =>
      handleQueryInputChange(e, suggestionBox)
    );
    queryInput.addEventListener("keyup", (e) =>
      handleQueryInputKeyup(e, suggestionBox)
    );
    queryInput.addEventListener("blur", () =>
      setTimeout(() => {
        if (suggestionBox) suggestionBox.style.display = "none";
      }, 200)
    );
  }

  if (runScanBtn) runScanBtn.addEventListener("click", handleRunScan);
  if (saveScanBtn)
    saveScanBtn.addEventListener("click", handleSaveScanInitiate);
  if (clearQueryBtn) {
    clearQueryBtn.addEventListener("click", () => {
      if (queryInput) queryInput.value = "";
      updateResultsTable([], [], "empty-query");
    });
  }
  if (loadScanBtn) {
    const loadScanModalEl = document.getElementById("loadScanModal");
    loadScanBtn.addEventListener("click", () => {
      renderLoadableScansList();
      if (loadScanModalEl) {
        loadScanModalEl.classList.remove("hidden");
        loadScanModalEl.classList.add("flex");
      }
    });
  }
  if (runBacktestBtn)
    runBacktestBtn.addEventListener("click", handleRunBacktest);
}

/**
 * Sets up all modals (close buttons, action buttons).
 */
function setupAllModals() {
  document.querySelectorAll(".modal").forEach((modal) => {
    modal.querySelectorAll(".btn-close").forEach((button) => {
      button.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      });
    });
    const backdrop = modal.querySelector(".modal-backdrop");
    if (backdrop) {
      backdrop.addEventListener("click", () => {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
      });
    }
  });

  // Populate static dropdowns
  const timeframeSelect = document.getElementById("indicatorConfigTimeframe");
  const fieldSelect = document.getElementById("indicatorConfigField");
  if (timeframeSelect)
    DEFAULT_TIMEFRAMES.forEach((tf) =>
      timeframeSelect.add(new Option(tf, tf.toLowerCase()))
    );
  if (fieldSelect)
    DEFAULT_FIELDS.forEach((f) =>
      fieldSelect.add(new Option(f, f.toLowerCase()))
    );

  // Attach listeners to modal action buttons
  document
    .getElementById("indicatorConfigDone")
    ?.addEventListener("click", handleIndicatorConfigDone);
  document
    .getElementById("confirmSaveScanButton")
    ?.addEventListener("click", handleSaveScanConfirm);
  document
    .getElementById("loadScanSearch")
    ?.addEventListener("input", renderLoadableScansList);
}

/**
 * Creates the autocomplete suggestion box element.
 * @returns {HTMLUListElement} The suggestion box element.
 */
function createSuggestionBox() {
  const box = document.createElement("ul");
  box.id = "autocompleteSuggestionBox";
  box.className =
    "absolute z-50 bg-gray-700 border border-gray-600 rounded-md shadow-lg text-white list-none p-0";
  box.style.display = "none";
  return box;
}

// =================================================================
// SECTION: API Calls (Indicators, Scans)
// =================================================================

function fetchIndicatorsAndRender() {
  fetch("/screener/api/indicators/")
    .then((resp) =>
      resp.ok
        ? resp.json()
        : Promise.reject(new Error("Failed to fetch indicators."))
    )
    .then((data) => {
      INDICATOR_GROUPS = data.groups;
      ALL_INDICATORS = [];
      Object.values(INDICATOR_GROUPS).forEach((group) => {
        if (Array.isArray(group)) {
          group.forEach((ind) => {
            ind.params = ind.params || [];
            ALL_INDICATORS.push(ind);
          });
        }
      });
      // Populate keywords for the parser.
      // **CRITICAL**: This ensures OHLCV are treated as indicators by the parser.
      KEYWORDS = {};
      DEFAULT_TIMEFRAMES.forEach(
        (tf) => (KEYWORDS[tf.toUpperCase()] = TOKEN_TYPES.TIME_FRAME)
      );
      ALL_INDICATORS.forEach(
        (ind) =>
          (KEYWORDS[ind.value.toUpperCase()] = TOKEN_TYPES.INDICATOR_NAME)
      );
      KEYWORDS["AND"] = TOKEN_TYPES.OPERATOR_LOGICAL;
      KEYWORDS["OR"] = TOKEN_TYPES.OPERATOR_LOGICAL;
    })
    .catch((err) => console.error(err));
}

function handleRunScan() {
  updateResultsTable([], [], "loading");
  const queryInput = document.getElementById("queryInput");
  const rawQuery = queryInput.value.trim();

  if (!rawQuery) {
    updateResultsTable([], [], "empty-query");
    return;
  }

  const backendPayload = transformQueryStringToBackendStructure(rawQuery);
  if (!backendPayload || backendPayload.type === "PARSE_ERROR") {
    updateResultsTable(
      [],
      [],
      "parse-error",
      backendPayload?.error || "Invalid query syntax."
    );
    return;
  }

  fetch("/screener/api/run_screener/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      filters: backendPayload,
      segment: document.getElementById("segmentDropdown")?.value || "Nifty 500",
    }),
  })
    .then((resp) =>
      resp.ok ? resp.json() : resp.json().then((err) => Promise.reject(err))
    )
    .then((data) => {
      if (data.error) throw new Error(data.error);
      updateResultsTable(data.results || [], data.query_indicators || []);
    })
    .catch((err) => {
      updateResultsTable(
        [],
        [],
        "fetch-error",
        err.error || err.message || "Unknown server error."
      );
    });
}

// =================================================================
// SECTION: UI Rendering (Modals, Tables)
// =================================================================

function renderLoadableScansList() {
  const listContainer = document.getElementById("loadableScansList");
  const searchInput = document.getElementById("loadScanSearch");
  if (!listContainer || !searchInput) return;

  fetch("/screener/api/saved_scans/")
    .then((resp) => (resp.ok ? resp.json() : Promise.reject(resp)))
    .then((data) => {
      const scans = data.saved_scans || [];
      const searchTerm = searchInput.value.toLowerCase();
      const filteredScans = scans.filter((s) =>
        s.name.toLowerCase().includes(searchTerm)
      );
      listContainer.innerHTML = "";
      if (filteredScans.length === 0) {
        listContainer.innerHTML = `<li class="p-4 text-center text-gray-500">No matching scans found.</li>`;
        return;
      }
      filteredScans.forEach((scan) => {
        const li = document.createElement("li");
        li.className =
          "px-4 py-2 cursor-pointer hover:bg-gray-600 text-sm rounded-md";
        li.textContent = scan.name;
        li.addEventListener("click", () => {
          const queryInput = document.getElementById("queryInput");
          const segmentDropdown = document.getElementById("segmentDropdown");
          const loadScanModalEl = document.getElementById("loadScanModal");
          const queryString = transformBackendStructureToQueryString(
            scan.filters
          );
          queryInput.value = queryString;
          if (segmentDropdown && scan.segment)
            segmentDropdown.value = scan.segment;
          if (loadScanModalEl) {
            loadScanModalEl.classList.add("hidden");
            loadScanModalEl.classList.remove("flex");
          }
        });
        listContainer.appendChild(li);
      });
    })
    .catch((err) => {
      console.error("Error fetching scans for modal:", err);
      listContainer.innerHTML = `<li class="p-4 text-center text-red-400">Failed to load scans.</li>`;
    });
}

function handleSaveScanInitiate() {
  const queryInput = document.getElementById("queryInput");
  const scanNameModalEl = document.getElementById("scanNameModal");
  const scanNameInput = document.getElementById("scanNameInput");

  const rawQuery = queryInput.value.trim();
  if (!rawQuery) {
    console.warn("Cannot save an empty query.");
    return;
  }

  const parsed = transformQueryStringToBackendStructure(rawQuery);
  if (!parsed || parsed.type === "PARSE_ERROR") {
    console.error(
      "Cannot save, invalid query:",
      parsed?.error || "Unknown parsing error."
    );
    return;
  }

  parsedQueryForSave = parsed;
  const segmentDropdown = document.getElementById("segmentDropdown");
  segmentValueForSave = segmentDropdown ? segmentDropdown.value : "";
  if (scanNameInput) scanNameInput.value = "";
  if (scanNameModalEl) {
    scanNameModalEl.classList.remove("hidden");
    scanNameModalEl.classList.add("flex");
  }
}

function showSaveSuccessAnimation() {
  const toast = document.getElementById("saveSuccessToast");
  if (!toast) return;

  // Add the .show class to trigger the CSS animation
  toast.classList.add("show");

  // Remove the class after the animation completes (3 seconds)
  // so it can be triggered again later.
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function handleSaveScanConfirm() {
  const scanNameInput = document.getElementById("scanNameInput");
  const scanNameModalEl = document.getElementById("scanNameModal");
  const nameToSave = scanNameInput.value.trim();
  if (!nameToSave) {
    console.warn("Scan name cannot be empty.");
    return;
  }

  if (!parsedQueryForSave) {
    console.error("Error: Query data missing for save operation.");
    if (scanNameModalEl) {
      scanNameModalEl.classList.add("hidden");
      scanNameModalEl.classList.remove("flex");
    }
    return;
  }

  fetch("/screener/api/save_scan/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      name: nameToSave,
      filters: parsedQueryForSave,
      segment: segmentValueForSave,
    }),
  })
    .then((resp) =>
      resp.ok ? resp.json() : Promise.reject(new Error("Failed to save scan."))
    )
    .then((data) => {
      if (data.success) {
        if (scanNameModalEl) {
          scanNameModalEl.classList.add("hidden");
          scanNameModalEl.classList.remove("flex");
        }
        showSaveSuccessAnimation(); // Trigger the beautiful animation!
      } else {
        throw new Error(data.error || "Unknown error during save.");
      }
    })
    .catch((err) => console.error("Error saving scan:", err));
}

function updateResultsTable(
  results,
  queryIndicators = [],
  state = null,
  message = ""
) {
  const tableContainer = document.getElementById("resultsBodyContainer");
  const stockCountSpan = document.getElementById("stockCount");

  if (!tableContainer || !stockCountSpan) return;
  tableContainer.innerHTML = "";

  const table = document.createElement("table");
  table.className = "w-full text-sm text-left text-gray-400";
  const thead = document.createElement("thead");
  thead.className =
    "text-xs text-gray-400 uppercase bg-gray-700 sticky-table-header";
  const tbody = document.createElement("tbody");
  table.append(thead, tbody);
  tableContainer.appendChild(table);

  const baseHeaders = [
    "#",
    "Symbol",
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "% Chg",
    "Volume",
  ];
  const dynamicHeaders = queryIndicators || [];
  const allHeaders = [...baseHeaders, ...dynamicHeaders, "Actions"];
  const headerRow = thead.insertRow();
  allHeaders.forEach((text) => {
    const th = document.createElement("th");
    th.className = "px-4 py-3 whitespace-nowrap";
    th.textContent = text;
    headerRow.appendChild(th);
  });

  const colSpan = allHeaders.length;

  if (state) {
    let msgHtml = "";
    switch (state) {
      case "loading":
        msgHtml = `<i class="fas fa-spinner fa-spin fa-lg mr-2"></i>Running scan...`;
        break;
      case "empty-query":
        msgHtml = "Query is empty. Please enter a scan condition.";
        break;
      case "parse-error":
        msgHtml = `<strong>Query Syntax Error:</strong> ${message}`;
        break;
      case "fetch-error":
        msgHtml = `<strong>Scan Failed:</strong> ${message}`;
        break;
    }
    tbody.innerHTML = `<tr><td colspan="${colSpan}" class="px-6 py-12 text-center text-gray-400">${msgHtml}</td></tr>`;
    stockCountSpan.textContent = "Matching Stocks: 0";
    return;
  }

  if (!results || results.length === 0) {
    tbody.innerHTML = `<tr><td colspan="${colSpan}" class="px-6 py-12 text-center text-gray-500">No stocks match your scan criteria.</td></tr>`;
    stockCountSpan.textContent = "Matching Stocks: 0";
    return;
  }

  stockCountSpan.textContent = `Matching Stocks: ${results.length}`;
  results.forEach((stock, index) => {
    const row = tbody.insertRow();
    row.className = "border-b border-gray-700 hover:bg-gray-700/50";
    row.insertCell().textContent = index + 1;
    row.insertCell().innerHTML = `<span class="font-medium text-violet-400">${
      stock.symbol || "N/A"
    }</span>`;
    row.insertCell().textContent = stock.timestamp || "N/A";
    row.insertCell().textContent = stock.open || "N/A";
    row.insertCell().textContent = stock.high || "N/A";
    row.insertCell().textContent = stock.low || "N/A";
    row.insertCell().textContent = stock.close || "N/A";
    const changeCell = row.insertCell();
    const pct = parseFloat(stock.change_pct);
    changeCell.textContent = stock.change_pct || "N/A";
    if (!isNaN(pct))
      changeCell.className = pct >= 0 ? "text-green-400" : "text-red-400";
    row.insertCell().textContent = stock.volume || "N/A";
    dynamicHeaders.forEach((indicatorKey) => {
      const cell = row.insertCell();
      cell.textContent = stock.indicator_values?.[indicatorKey] ?? "N/A";
    });
    row.insertCell().innerHTML = `<button title="View Chart" class="text-violet-400 hover:text-violet-300"><i class="fas fa-chart-line"></i></button>`;
  });
}

// =================================================================
// SECTION: Autocomplete and Indicator Configuration
// =================================================================

function handleQueryInputChange(event, suggestionBox) {
  const queryInput = event.target;
  const cursorPos = queryInput.selectionStart;
  const textBeforeCursor = queryInput.value.substring(0, cursorPos);
  const match = textBeforeCursor.match(/(\b[a-zA-Z0-9_]+)$/);

  if (match) {
    currentWordForAutocomplete = match[1].toUpperCase();
    wordStartIndex = cursorPos - match[1].length;
    const suggestions = ALL_INDICATORS.filter(
      (ind) =>
        ind.value.toUpperCase().startsWith(currentWordForAutocomplete) ||
        ind.label.toUpperCase().includes(currentWordForAutocomplete)
    );
    populateSuggestionBox(suggestions, queryInput, suggestionBox);
  } else {
    suggestionBox.style.display = "none";
  }
}

function handleQueryInputKeyup(event, suggestionBox) {
  if (event.key === "Escape") {
    suggestionBox.style.display = "none";
  }
}

// In screener/js/builder.js, replace the entire function

function populateSuggestionBox(suggestions, textarea, suggestionBox) {
  if (!suggestions || suggestions.length === 0) {
    if (suggestionBox) suggestionBox.style.display = "none";
    return;
  }
  suggestionBox.innerHTML = "";

  // FIX 1: Increased slice limit from 7 to 20 to show more results.
  suggestions.slice(0, 20).forEach((indicatorDef) => {
    const li = document.createElement("li");
    li.className =
      "px-3 py-2 cursor-pointer hover:bg-gray-600 border-b border-gray-600/50 last:border-b-0";

    // FIX 2: Using innerHTML for a richer, more descriptive format.
    // This will show the friendly name in a larger font and the technical name below it.
    li.innerHTML = `
      <div class="font-semibold text-white text-sm">${indicatorDef.label}</div>
      <div class="text-xs text-gray-400 font-mono">${indicatorDef.value}</div>
    `;

    li.onmousedown = (e) => {
      e.preventDefault();
      selectIndicatorFromSuggestion(indicatorDef);
      suggestionBox.style.display = "none";
    };
    suggestionBox.appendChild(li);
  });

  const rect = textarea.getBoundingClientRect();
  suggestionBox.style.left = `${textarea.offsetLeft}px`;
  suggestionBox.style.top = `${textarea.offsetTop + rect.height}px`;
  suggestionBox.style.width = `${rect.width}px`;
  suggestionBox.style.display = "block";
}

function selectIndicatorFromSuggestion(indicatorDef) {
  activeIndicatorForConfig = {
    name: indicatorDef.value,
    label: indicatorDef.label,
    paramsFromDef: indicatorDef.params,
  };
  wordStartIndex =
    document.getElementById("queryInput").selectionStart -
    currentWordForAutocomplete.length;
  lastCursorPosition = wordStartIndex;
  openIndicatorConfigModal();
}

function openIndicatorConfigModal() {
  const modal = document.getElementById("indicatorConfigModal");
  if (!activeIndicatorForConfig || !modal) return;

  document.getElementById(
    "indicatorConfigModalLabelText"
  ).textContent = `Configure: ${activeIndicatorForConfig.label}`;
  const definedParams = activeIndicatorForConfig.paramsFromDef || [];

  // --- START of new logic ---
  const indicatorName = activeIndicatorForConfig.name.toUpperCase();
  const isCandlestickPattern = indicatorName.startsWith("CDL");
  const isOhlcvField = DEFAULT_FIELDS.includes(indicatorName);
  // --- END of new logic ---

  // Hide all parameter groups initially
  modal
    .querySelectorAll(".param-group")
    .forEach((el) => (el.style.display = "none"));

  // Always show timeframe group
  const timeframeGroup = document.getElementById(
    "indicatorConfigTimeframeGroup"
  );
  if (timeframeGroup) timeframeGroup.style.display = "block";

  const fieldGroup = document.getElementById("indicatorConfigFieldGroup");
  // **MODIFIED**: Only show the field group if it's NOT a candlestick pattern
  // and the indicator is not itself a field (like 'CLOSE').
  if (fieldGroup) {
    if (isCandlestickPattern || isOhlcvField) {
      fieldGroup.style.display = "none";
    } else {
      fieldGroup.style.display = "block";
    }
  }

  // Show other groups only if they are defined for the selected indicator
  const paramGroupMap = {
    period: "indicatorConfigPeriodGroup",
    fast_period: "indicatorConfigFastPeriodGroup",
    slow_period: "indicatorConfigSlowPeriodGroup",
    signal_period: "indicatorConfigSignalPeriodGroup",
  };
  definedParams.forEach((param) => {
    if (paramGroupMap[param]) {
      const group = document.getElementById(paramGroupMap[param]);
      if (group) group.style.display = "block";
    }
  });

  modal.classList.remove("hidden");
  modal.classList.add("flex");
}

function handleIndicatorConfigDone() {
  if (!activeIndicatorForConfig) return;
  const queryInput = document.getElementById("queryInput");
  const timeframe = document.getElementById("indicatorConfigTimeframe").value;
  const tfDisplay = timeframe.charAt(0).toUpperCase() + timeframe.slice(1);
  const indicatorName = activeIndicatorForConfig.name;
  const definedParams = activeIndicatorForConfig.paramsFromDef || [];
  const args = [];

  // --- START of new logic ---
  // Check if the indicator is a candlestick pattern.
  // We'll assume they all start with 'CDL' for simplicity.
  const isCandlestickPattern = indicatorName.toUpperCase().startsWith("CDL");

  // Only add arguments if it's NOT a candlestick pattern.
  if (!isCandlestickPattern) {
    // This is the original logic for non-candlestick indicators
    if (!DEFAULT_FIELDS.includes(indicatorName.toUpperCase())) {
      const fieldValue = document.getElementById("indicatorConfigField").value;
      if (fieldValue) {
        args.push(`${fieldValue.toUpperCase()}()`);
      }
    }

    // Collect OTHER parameter values from visible inputs in the modal based on original definitions.
    if (definedParams.includes("period"))
      args.push(document.getElementById("indicatorConfigPeriod").value);
    if (definedParams.includes("fast_period"))
      args.push(document.getElementById("indicatorConfigFastPeriod").value);
    if (definedParams.includes("slow_period"))
      args.push(document.getElementById("indicatorConfigSlowPeriod").value);
    if (definedParams.includes("signal_period"))
      args.push(document.getElementById("indicatorConfigSignalPeriod").value);
  }
  // For candlestick patterns, 'args' will remain empty, which is correct.
  // --- END of new logic ---

  const indicatorString = `${tfDisplay} ${indicatorName}(${args.join(", ")})`;

  const before = queryInput.value.substring(0, lastCursorPosition);
  const after = queryInput.value.substring(
    lastCursorPosition + currentWordForAutocomplete.length
  );
  queryInput.value = (before + indicatorString + " " + after).trim() + " ";
  queryInput.focus();

  document.getElementById("indicatorConfigModal").classList.add("hidden");
}

// =================================================================
// SECTION: DSL Parser & AST Transformer
// =================================================================

function transformQueryStringToBackendStructure(queryString) {
  if (!queryString || !queryString.trim()) return null;
  const tokens = [];
  let cursor = 0;
  const symbolOps = {
    ">=": "OPERATOR_COMPARISON",
    "<=": "OPERATOR_COMPARISON",
    "==": "OPERATOR_COMPARISON",
    ">": "OPERATOR_COMPARISON",
    "<": "OPERATOR_COMPARISON",
    "(": "BRACKET_OPEN",
    ")": "BRACKET_CLOSE",
    ",": "COMMA",
  };
  const multiWordOps = {
    "CROSSES ABOVE": "OPERATOR_COMPARISON",
    "CROSSES BELOW": "OPERATOR_COMPARISON",
  };
  const sortedMultiWordOps = Object.keys(multiWordOps).sort(
    (a, b) => b.length - a.length
  );

  while (cursor < queryString.length) {
    let char = queryString[cursor];
    if (/\s/.test(char)) {
      cursor++;
      continue;
    }

    let matched = false;
    for (const op of sortedMultiWordOps) {
      if (
        queryString.substring(cursor, cursor + op.length).toUpperCase() === op
      ) {
        tokens.push({ type: TOKEN_TYPES.OPERATOR_COMPARISON, value: op });
        cursor += op.length;
        matched = true;
        break;
      }
    }
    if (matched) continue;

    let twoCharOp = queryString.substring(cursor, cursor + 2);
    if (symbolOps[twoCharOp]) {
      tokens.push({
        type: TOKEN_TYPES[symbolOps[twoCharOp]] || TOKEN_TYPES.ERROR,
        value: twoCharOp,
      });
      cursor += 2;
      continue;
    }
    if (symbolOps[char]) {
      tokens.push({
        type: TOKEN_TYPES[symbolOps[char]] || TOKEN_TYPES.ERROR,
        value: char,
      });
      cursor++;
      continue;
    }

    const tfMatch = queryString
      .slice(cursor)
      .match(/^(daily|weekly|monthly|1hour|30min|15min|5min|1min)\b/i);
    if (tfMatch) {
      tokens.push({
        type: TOKEN_TYPES.TIME_FRAME,
        value: tfMatch[1].toLowerCase(),
      });
      cursor += tfMatch[1].length;
      continue;
    }

    if (/[0-9]/.test(char)) {
      let numStr = "";
      while (cursor < queryString.length && /[0-9\.]/.test(queryString[cursor]))
        numStr += queryString[cursor++];
      tokens.push({ type: TOKEN_TYPES.NUMBER, value: parseFloat(numStr) });
      continue;
    }

    if (/[a-zA-Z_]/.test(char)) {
      let identifier = "";
      while (
        cursor < queryString.length &&
        /[a-zA-Z0-9_]/.test(queryString[cursor])
      )
        identifier += queryString[cursor++];
      const upperId = identifier.toUpperCase();
      if (upperId === "AND" || upperId === "OR")
        tokens.push({ type: TOKEN_TYPES.OPERATOR_LOGICAL, value: upperId });
      // **CRITICAL FIX**: No special casing for FIELD. Rely entirely on KEYWORDS map.
      else if (KEYWORDS[upperId])
        tokens.push({ type: KEYWORDS[upperId], value: identifier });
      else tokens.push({ type: TOKEN_TYPES.IDENTIFIER, value: identifier });
      continue;
    }
    tokens.push({ type: TOKEN_TYPES.ERROR, value: char });
    cursor++;
  }
  tokens.push({ type: TOKEN_TYPES.EOF, value: "EOF" });

  let current = 0;
  const lookahead = () => tokens[current];
  const consume = (type) => {
    if (type && lookahead().type !== type)
      throw new Error(`Expected ${type} but found ${lookahead().type}`);
    return tokens[current++];
  };

  const getBindingPower = (token) => {
    if (!token) return 0;
    const op = token.value.toUpperCase();
    if (op === "OR") return 10;
    if (op === "AND") return 20;
    if (token.type === "OPERATOR_COMPARISON") return 30;
    return 0;
  };

  const parseExpression = (rbp) => {
    let token = consume();
    let left = nud(token);
    while (rbp < getBindingPower(lookahead())) {
      token = consume();
      left = led(left, token);
    }
    return left;
  };

  // In builder.js, replace the existing 'nud' function with this one.

  const nud = (token) => {
    // Handle numbers
    if (token.type === "NUMBER") {
      return { type: "NumberLiteral", value: token.value };
    }

    // Handle expressions in parentheses, like ( ... )
    if (token.type === "BRACKET_OPEN") {
      const expr = parseExpression(0);
      consume("BRACKET_CLOSE");
      return expr;
    }

    let timeframe = "daily"; // Use 'daily' as the default timeframe
    let indicatorToken = token;

    // If an explicit timeframe is provided, use it and move to the next token.
    if (token.type === "TIME_FRAME") {
      timeframe = token.value;
      indicatorToken = consume("INDICATOR_NAME");
    }

    // This block now correctly handles all indicator-like function calls,
    // including CLOSE, OPEN, VOLUME, etc.
    if (indicatorToken.type === "INDICATOR_NAME") {
      const name = indicatorToken.value;
      consume("BRACKET_OPEN");
      const args = [];

      // Parse arguments if there are any
      if (lookahead().type !== "BRACKET_CLOSE") {
        while (true) {
          args.push(parseExpression(0));
          if (lookahead().type === "BRACKET_CLOSE") break;
          consume("COMMA");
        }
      }
      consume("BRACKET_CLOSE");

      // The special check for DEFAULT_FIELDS has been removed.
      // We now ALWAYS create an 'IndicatorCall' node which correctly
      // includes the timeframe. The backend is already set up to handle this.
      return { type: "IndicatorCall", name, timeframe, arguments: args };
    }

    // If the token is none of the above, it's an error.
    throw new Error(
      `Unexpected token: ${token.type} with value ${token.value}`
    );
  };

  const led = (left, token) => {
    const bp = getBindingPower(token);
    const right = parseExpression(bp);
    return {
      type:
        token.type === "OPERATOR_LOGICAL" ? "BinaryExpression" : "Comparison",
      operator: token.value,
      left,
      right,
    };
  };

  try {
    if (tokens.length === 1 && tokens[0].type === "EOF") return null;
    const ast = parseExpression(0);
    if (lookahead().type !== "EOF")
      throw new Error("Unexpected tokens at end of query.");
    return ast;
  } catch (e) {
    console.error("Parsing Error:", e.message);
    return { type: "PARSE_ERROR", error: e.message };
  }
}

function transformBackendStructureToQueryString(astNode) {
  if (!astNode || !astNode.type) return "";
  switch (astNode.type) {
    case "Comparison":
    case "BinaryExpression":
      return `(${transformBackendStructureToQueryString(
        astNode.left
      )} ${astNode.operator.toUpperCase()} ${transformBackendStructureToQueryString(
        astNode.right
      )})`;
    case "IndicatorCall":
      const args = (astNode.arguments || [])
        .map((arg) => transformBackendStructureToQueryString(arg))
        .join(", ");
      const tf = astNode.timeframe
        ? astNode.timeframe.charAt(0).toUpperCase() + astNode.timeframe.slice(1)
        : "Daily";
      return `${tf} ${astNode.name}(${args})`;
    case "FieldLiteral": // This is now primarily for nested args like in SMA(CLOSE(), 14)
      return `${astNode.value.toUpperCase()}()`;
    case "NumberLiteral":
      return astNode.value.toString();
    default:
      return `[Unknown AST: ${astNode.type}]`;
  }
}

// =================================================================
// SECTION: Backtesting UI Handlers (Dummy)
// =================================================================
// In builder.js

function handleRunBacktest() {
  const overlay = document.getElementById("backtestOverlay");
  const rawQuery = document.getElementById("queryInput").value.trim();

  if (!rawQuery) {
    alert("Please enter a query before running a backtest.");
    return;
  }

  const ast_filter = transformQueryStringToBackendStructure(rawQuery);
  if (!ast_filter || ast_filter.type === "PARSE_ERROR") {
    alert("The query is invalid and cannot be backtested.");
    return;
  }

  if (overlay) overlay.style.display = "flex";

  const payload = {
    filters: ast_filter,
    start_date: document.getElementById("backtestStartDate").value,
    end_date: document.getElementById("backtestEndDate").value,
    initial_capital: document.getElementById("backtestInitialCapital").value,
    stop_loss_pct: document.getElementById("backtestStopLossPct").value,
    take_profit_pct: document.getElementById("backtestTakeProfitPct").value,
    position_size_pct: document.getElementById("backtestPositionSizePct").value,
  };

  fetch("/screener/api/run_backtest/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify(payload),
  })
    .then((resp) => {
      if (!resp.ok) {
        return resp.json().then((err) => Promise.reject(err));
      }
      return resp.json();
    })
    .then((data) => {
      if (data.error) throw new Error(data.error);
      renderBacktestResults(data);
    })
    .catch((err) => {
      console.error("Backtest failed:", err);
      alert(`Backtest failed: ${err.error || err.message}`);
    })
    .finally(() => {
      if (overlay) overlay.style.display = "none";
    });
}

function renderBacktestResults({
  summary = {},
  trades = [],
  equity_curve = [],
}) {
  const summaryDiv = document.getElementById("backtestSummaryStats");
  const tradesBody = document.getElementById("backtestTradesTableBody");
  const chartContainer = document.getElementById("equityChartContainer");

  // This part is now working correctly, but we'll keep it for completeness.
  if (summaryDiv) {
    const totalReturnClass =
      summary.total_return_pct >= 0 ? "text-green-400" : "text-red-400";
    summaryDiv.innerHTML = `
      <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
        <span class="text-gray-400">Total Return:</span>
        <span class="text-right font-semibold ${totalReturnClass}">${
      summary.total_return_pct?.toFixed(2) ?? "N/A"
    }%</span>
        <span class="text-gray-400">Total Trades:</span>
        <span class="text-right font-semibold">${
          summary.total_trades ?? "N/A"
        }</span>
        <span class="text-gray-400">Win Rate:</span>
        <span class="text-right font-semibold">${
          summary.win_rate?.toFixed(2) ?? "N/A"
        }%</span>
        <span class="text-gray-400">Profit Factor:</span>
        <span class="text-right font-semibold">${
          summary.profit_factor?.toFixed(2) ?? "N/A"
        }</span>
        <span class="text-gray-400">Max Drawdown:</span>
        <span class="text-right font-semibold">${
          summary.max_drawdown_pct?.toFixed(2) ?? "N/A"
        }%</span>
        <span class="text-gray-400">Avg Win PnL:</span>
        <span class="text-right font-semibold text-green-400">${
          summary.avg_win_pnl?.toFixed(2) ?? "N/A"
        }</span>
        <span class="text-gray-400">Avg Loss PnL:</span>
        <span class="text-right font-semibold text-red-400">${
          summary.avg_loss_pnl?.toFixed(2) ?? "N/A"
        }</span>
        <span class="text-gray-400">Longest Win Streak:</span>
        <span class="text-right font-semibold">${
          summary.longest_win_streak ?? "N/A"
        }</span>
        <span class="text-gray-400">Longest Loss Streak:</span>
        <span class="text-right font-semibold">${
          summary.longest_loss_streak ?? "N/A"
        }</span>
      </div>
    `;
  }

  // This part for the trades list is also working fine.
  if (tradesBody) {
    tradesBody.innerHTML = "";
    if (trades.length > 0) {
      trades.forEach((t, i) => {
        const pnlClass = t.pnl_pct >= 0 ? "text-green-400" : "text-red-400";
        const row = tradesBody.insertRow();
        row.className = "border-b border-gray-700 hover:bg-gray-700/50 text-xs";
        row.innerHTML = `<td class="p-2">${i + 1}</td><td class="p-2">${
          t.symbol
        }</td><td class="p-2">${t.entry_date}</td><td class="p-2">${
          t.exit_date
        }</td><td class="p-2 ${pnlClass}">${t.pnl_pct.toFixed(
          4
        )}%</td><td class="p-2">${t.reason}</td>`;
      });
    } else {
      tradesBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-gray-500">No trades were executed.</td></tr>`;
    }
  }

  // --- EQUITY CHART LOGIC ---
  if (chartContainer) {
    if (equityChartInstance) {
      equityChartInstance.remove();
      equityChartInstance = null;
    }

    if (equity_curve.length > 1) {
      if (
        typeof LightweightCharts === "undefined" ||
        !LightweightCharts.createChart
      ) {
        console.error("Lightweight Charts library is not loaded.");
        chartContainer.innerHTML =
          '<div class="p-4 text-center text-red-400">Error: Chart library not loaded.</div>';
        return;
      }

      equityChartInstance = LightweightCharts.createChart(chartContainer, {
        width: chartContainer.clientWidth,
        height: chartContainer.clientHeight,
        layout: {
          background: { type: "solid", color: "#1f2937" },
          textColor: "#d1d5db",
        },
        grid: {
          vertLines: { color: "#374151" },
          horzLines: { color: "#374151" },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
          borderColor: "#5f6368",
        },
        crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
        watermark: {
          visible: true,
          fontSize: 24,
          horzAlign: "center",
          vertAlign: "center",
          color: "rgba(200, 200, 200, 0.2)",
          text: "Equity Curve",
        },
      });

      // =================================================================
      // THIS IS THE CORRECTED LINE FOR THE CHART API
      // =================================================================
      const equitySeries = equityChartInstance.addAreaSeries({
        lineColor: "#8b5cf6",
        lineWidth: 2,
        priceFormat: { type: "price", precision: 2, minMove: 0.01 },
        topColor: "rgba(139, 92, 246, 0.4)",
        bottomColor: "rgba(17, 24, 39, 0.1)",
      });
      // =================================================================

      const chartData = equity_curve.map((point) => ({
        time: point.datetime,
        value: point.equity,
      }));

      equitySeries.setData(chartData);

      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          const { width, height } = entry.contentRect;
          if (width > 0 && height > 0) {
            equityChartInstance.applyOptions({ width, height });
          }
        }
        equityChartInstance.timeScale().fitContent();
      });

      resizeObserver.observe(chartContainer);
    } else {
      chartContainer.innerHTML =
        '<div class="p-4 text-center text-gray-500">Not enough data to draw equity curve.</div>';
    }
  }
}
