// --- Constants ---
let INDICATORS = []; // Populated by fetchIndicatorsAndRender
let INDICATOR_GROUPS = {}; // Populated by fetchIndicatorsAndRender
const INDICATOR_PARTS = {
  MACD: ["macd", "signal", "hist"],
  STOCH: ["k", "d"], // Corrected from STOCH: ["slowk", "slowd"] if 'k' and 'd' are the desired parts
  BBANDS: ["upper", "middle", "lower"],
};

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
// CRITICAL FIX: DEFAULT_FIELDS must be all uppercase for lexer rules to work correctly
const DEFAULT_FIELDS = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"];

// --- Token Types for Lexer/Parser ---
const TOKEN_TYPES = {
  NUMBER: "NUMBER",
  IDENTIFIER: "IDENTIFIER", // General identifiers before specific classification
  INDICATOR_NAME: "INDICATOR_NAME",
  TIME_FRAME: "TIME_FRAME", // Corrected from "TIME FRAME" to avoid space issues if used as object key directly
  FIELD: "FIELD",
  OPERATOR_COMPARISON: "OPERATOR_COMPARISON",
  OPERATOR_LOGICAL: "OPERATOR_LOGICAL",
  BRACKET_OPEN: "BRACKET_OPEN",
  BRACKET_CLOSE: "BRACKET_CLOSE",
  COMMA: "COMMA",
  EOF: "EOF", // End Of File/Input
  ERROR: "ERROR", // For lexer errors
};

// --- Global State ---
let currentQueryString = "";
let activeIndicatorForConfig = null;
let lastCursorPosition = 0;
let currentWordForAutocomplete = ""; // Moved here for better scope visibility if needed
let wordStartIndex = 0; // Moved here for better scope visibility if needed

// --- Modal Instances (Bootstrap) ---
let indicatorModalInstance, indicatorConfigModalInstance;

// --- DOM Elements ---
const queryInputTextarea = document.getElementById("queryInput");
const suggestionBox = document.createElement("ul");

const devParseButton = document.getElementById("add-filter"); // Assuming this is the "Parse Query (Dev)" button
const runScanButton = document.getElementById("runScan");
const clearQueryButton = document.getElementById("clearFiltersButton");

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

const resultsTableBody = document.getElementById("resultsTableBody");
const stockCountSpan = document.getElementById("stockCount");

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  // Ensure Bootstrap Modal instances are created correctly
  const indicatorModalEl = document.getElementById("indicatorModal");
  if (indicatorModalEl) {
    indicatorModalInstance = new bootstrap.Modal(indicatorModalEl);
  } else {
    console.error("Indicator modal element not found!");
  }

  const indicatorConfigModalEl = document.getElementById(
    "indicatorConfigModal"
  );
  if (indicatorConfigModalEl) {
    indicatorConfigModalInstance = new bootstrap.Modal(indicatorConfigModalEl);
  } else {
    console.error("Indicator config modal element not found!");
  }

  // Setup suggestion box
  suggestionBox.id = "autocompleteSuggestionBox";
  suggestionBox.className = "list-group position-absolute shadow-lg"; // Bootstrap classes
  suggestionBox.style.zIndex = "1050"; // Ensure it's above other elements
  suggestionBox.style.maxHeight = "200px";
  suggestionBox.style.overflowY = "auto";
  suggestionBox.style.display = "none"; // Initially hidden
  if (queryInputTextarea && queryInputTextarea.parentNode) {
    queryInputTextarea.parentNode.insertBefore(
      suggestionBox,
      queryInputTextarea.nextSibling
    );
  } else {
    console.error(
      "Query input textarea not found for suggestion box placement."
    );
  }

  // Populate dropdowns
  if (indicatorConfigTimeframeSelect) {
    DEFAULT_TIMEFRAMES.forEach((tf) =>
      indicatorConfigTimeframeSelect.options.add(
        new Option(tf, tf.toLowerCase())
      )
    );
  }
  if (indicatorConfigFieldSelect) {
    DEFAULT_FIELDS.forEach(
      (
        f // Uses the corrected uppercase DEFAULT_FIELDS
      ) =>
        indicatorConfigFieldSelect.options.add(new Option(f, f.toLowerCase())) // Value is lowercase for config
    );
  }

  // Add event listeners
  if (queryInputTextarea) {
    queryInputTextarea.addEventListener("input", handleQueryInputChange);
    queryInputTextarea.addEventListener("keyup", handleQueryInputKeyup);
    queryInputTextarea.addEventListener("blur", () =>
      setTimeout(() => {
        if (suggestionBox) suggestionBox.style.display = "none";
      }, 200)
    );
  }

  if (devParseButton) {
    devParseButton.innerHTML =
      '<i class="fas fa-cogs me-2"></i>Parse Query (Dev)';
    devParseButton.title =
      "Parse the current query and show its structure in console (for development)";
    devParseButton.addEventListener("click", () => {
      const queryString = queryInputTextarea.value;
      if (!queryString.trim()) {
        alert("Query is empty.");
        return;
      }
      console.log("Attempting to parse query:", queryString);
      try {
        const parsedStructure =
          transformQueryStringToBackendStructure(queryString);
        console.log(
          "Parsed Structure (for backend):",
          JSON.stringify(parsedStructure, null, 2)
        );
        if (parsedStructure && parsedStructure.type === "PARSE_ERROR") {
          alert(
            `Parsing Error: ${parsedStructure.error}\nDetails: ${
              parsedStructure.details || ""
            }\nCheck console.`
          );
        } else if (parsedStructure) {
          alert(
            "Query parsed. Check console for the structured representation."
          );
        } else {
          alert("Parsing returned null or undefined. Check console.");
        }
      } catch (e) {
        console.error("Error during parsing:", e);
        alert(`Parsing Exception: ${e.message}. Check console.`);
      }
    });
  }

  if (indicatorSearchInput) {
    indicatorSearchInput.addEventListener("input", renderIndicatorModalList);
  }
  if (indicatorConfigDoneButton) {
    indicatorConfigDoneButton.addEventListener(
      "click",
      handleIndicatorConfigDone
    );
  }
  if (runScanButton) {
    runScanButton.addEventListener("click", handleRunScan);
  }
  if (clearQueryButton) {
    clearQueryButton.addEventListener("click", () => {
      if (queryInputTextarea) queryInputTextarea.value = "";
      currentQueryString = "";
      if (suggestionBox) suggestionBox.style.display = "none";
      if (resultsTableBody)
        resultsTableBody.innerHTML =
          '<tr id="initialMessageRow"><td colspan="10" class="text-center py-5">Query cleared.</td></tr>';
      if (stockCountSpan) stockCountSpan.textContent = "Matching Stocks: 0";
    });
  }

  fetchIndicatorsAndRender();
});

// --- Autocomplete Logic ---
function handleQueryInputChange(event) {
  currentQueryString = event.target.value;
  const cursorPos = event.target.selectionStart;
  let textBeforeCursor = currentQueryString.substring(0, cursorPos);

  // Regex to find the word being typed (can include numbers for timeframes like "15min")
  const match = textBeforeCursor.match(/(\b[a-zA-Z0-9_]+)$/);
  if (match) {
    currentWordForAutocomplete = match[1].toUpperCase();
    wordStartIndex = cursorPos - match[1].length; // Use match[1].length for original case length

    // Filter indicators based on the current word
    const suggestions = INDICATORS.filter(
      (ind) =>
        ind.value.toUpperCase().startsWith(currentWordForAutocomplete) ||
        ind.label.toUpperCase().includes(currentWordForAutocomplete)
    );

    if (suggestions.length > 0 && currentWordForAutocomplete.length >= 1) {
      populateSuggestionBox(suggestions, event.target);
    } else {
      suggestionBox.style.display = "none";
    }
  } else {
    currentWordForAutocomplete = "";
    suggestionBox.style.display = "none";
  }

  // Suggest indicator parts (e.g., .macd, .signal for MACD)
  const typedSoFarUpper = event.target.value.toUpperCase();
  // Regex to find an indicator call like MACD(...)
  const indicatorPattern = /\b([A-Z_]+)\s*\(([^)]*)\)$/i; // Case-insensitive for indicator name
  const indicatorMatch = typedSoFarUpper.match(indicatorPattern);

  if (indicatorMatch) {
    const indicatorNameFromInput = indicatorMatch[1].toUpperCase(); // Ensure it's uppercase for lookup
    const parts = INDICATOR_PARTS[indicatorNameFromInput];
    if (parts) {
      // Check if a dot is already typed or if the cursor is right after the closing parenthesis
      const charAfterIndicator = queryInputTextarea.value.charAt(cursorPos);
      const previousChar = queryInputTextarea.value.charAt(cursorPos - 1);

      if (
        previousChar === ")" &&
        (charAfterIndicator === "" || charAfterIndicator === " ")
      ) {
        showIndicatorPartSuggestions(parts, cursorPos);
      }
    }
  }
}

function handleQueryInputKeyup(event) {
  if (event.key === "Escape") {
    if (suggestionBox) suggestionBox.style.display = "none";
  }
}

function populateSuggestionBox(suggestions, textarea) {
  if (!suggestionBox) return;
  suggestionBox.innerHTML = "";
  suggestions.slice(0, 7).forEach((indicatorDef) => {
    const li = document.createElement("li");
    li.className = "list-group-item list-group-item-action py-1 px-2";
    li.style.fontSize = "0.9em";
    li.textContent = `${indicatorDef.label} (${indicatorDef.value})`;
    li.onmousedown = (e) => {
      e.preventDefault();
      selectIndicatorFromSuggestion(indicatorDef, textarea);
      suggestionBox.style.display = "none";
    };
    suggestionBox.appendChild(li);
  });

  const textareaRect = textarea.getBoundingClientRect();
  const DUMMY_LINE_HEIGHT =
    parseFloat(window.getComputedStyle(textarea).lineHeight) || 20;

  // Create a dummy span to measure text width up to the word start
  const dummySpan = document.createElement("span");
  dummySpan.style.visibility = "hidden";
  dummySpan.style.position = "absolute"; // Keep it out of flow
  dummySpan.style.whiteSpace = "pre"; // Important for spaces
  dummySpan.style.font = window.getComputedStyle(textarea).font;
  document.body.appendChild(dummySpan);
  dummySpan.textContent = textarea.value.substring(0, wordStartIndex);
  const textCoords = dummySpan.getBoundingClientRect(); // Get width of text before current word
  document.body.removeChild(dummySpan);

  // Position the suggestion box
  // offsetX from textarea's own border/padding
  const offsetX = textarea.offsetLeft + textCoords.width - textarea.scrollLeft;
  // offsetY from textarea's top + line height for current line - scroll
  const offsetY =
    textarea.offsetTop +
    DUMMY_LINE_HEIGHT +
    Math.floor(textCoords.height / DUMMY_LINE_HEIGHT) * DUMMY_LINE_HEIGHT -
    textarea.scrollTop;

  suggestionBox.style.left = `${offsetX}px`;
  suggestionBox.style.top = `${offsetY}px`;
  suggestionBox.style.width =
    textarea.clientWidth > 300
      ? "300px"
      : `${textarea.clientWidth - (textCoords.width % textarea.clientWidth)}px`; // Adjust width
  suggestionBox.style.display = suggestions.length > 0 ? "block" : "none";
}

function selectIndicatorFromSuggestion(indicatorDef, textarea) {
  activeIndicatorForConfig = {
    name: indicatorDef.value, // Store original case value
    label: indicatorDef.label,
    paramsFromDef: indicatorDef.params || getImplicitParams(indicatorDef.value),
  };
  lastCursorPosition = wordStartIndex; // This is where the indicator name will be inserted
  openIndicatorConfigModal();
}

function openIndicatorConfigModal() {
  if (!activeIndicatorForConfig || !indicatorConfigModalInstance) {
    console.error("No indicator selected or config modal not initialized.");
    return;
  }
  indicatorConfigModalLabel.textContent = `Configure: ${activeIndicatorForConfig.label}`;
  const indicatorDefinedParams = activeIndicatorForConfig.paramsFromDef || []; // Ensure it's an array

  // Reset all to defaults or hide
  indicatorConfigTimeframeSelect.value = "daily"; // Default timeframe

  const allConfigGroups = [
    indicatorConfigFieldGroup,
    indicatorConfigPeriodGroup,
    indicatorConfigFastPeriodGroup,
    indicatorConfigSlowPeriodGroup,
    indicatorConfigSignalPeriodGroup,
    indicatorConfigNbdevGroup,
    indicatorConfigMultiplierGroup,
    indicatorConfigFastKPeriodGroup,
    indicatorConfigSlowKPeriodGroup,
    indicatorConfigSlowDPeriodGroup,
  ];
  allConfigGroups.forEach((group) => {
    if (group) group.style.display = "none";
  });

  const setupField = (paramKey, groupEl, inputEl, defaultValue) => {
    if (groupEl && indicatorDefinedParams.includes(paramKey)) {
      groupEl.style.display = "block";
      if (inputEl) inputEl.value = defaultValue;
    } else if (groupEl) {
      groupEl.style.display = "none";
    }
  };

  // Setup fields based on what the selected indicator defines
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
    "2.0"
  ); // nbdev is float
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

function handleIndicatorConfigDone() {
  if (!activeIndicatorForConfig || !indicatorConfigModalInstance) return;

  const configuredParams = {
    timeframe: indicatorConfigTimeframeSelect.value, // Always present
  };
  const definedParams = activeIndicatorForConfig.paramsFromDef || [];

  // Helper to read param if its group is visible
  const readParam = (key, groupEl, inputEl, isNum = true, isFlt = false) => {
    if (
      definedParams.includes(key) &&
      groupEl &&
      groupEl.style.display !== "none"
    ) {
      let val = inputEl.value;
      // For 'field', its value from select is already lowercase "close", "open" etc.
      // For other selects (if any), they might need .toLowerCase()
      if (
        inputEl.type === "select-one" &&
        key !== "timeframe" &&
        key !== "field"
      ) {
        val = val.toLowerCase();
      } else if (inputEl.type === "select-one" && key === "field") {
        val = inputEl.value; // This is already "close", "open" etc.
      } else if (isNum) {
        val = isFlt ? parseFloat(val) : parseInt(val, 10);
      }
      if (!(isNum && isNaN(val))) {
        configuredParams[key] = val;
      }
    }
  };

  // Read all potentially configured parameters
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
  ); // nbdev is float
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

  // Build the indicator string
  let indicatorString =
    configuredParams.timeframe.charAt(0).toUpperCase() +
    configuredParams.timeframe.slice(1) + // e.g., "Daily"
    " " +
    activeIndicatorForConfig.name + // e.g., "SMA" (original case from definition)
    "(";

  const paramValues = [];
  // Iterate over the defined params for the indicator in their expected order
  // This assumes paramsFromDef is somewhat ordered or we handle specific orders.
  // A more robust way would be to have a fixed order for common params.

  // Correctly handle 'field' parameter to be "CLOSE()"
  if (definedParams.includes("field") && configuredParams.field) {
    let fieldValue = configuredParams.field.toUpperCase(); // e.g., "CLOSE"
    // DEFAULT_FIELDS is already all uppercase
    if (DEFAULT_FIELDS.includes(fieldValue)) {
      fieldValue += "()"; // Becomes "CLOSE()"
    }
    paramValues.push(fieldValue);
  }

  // Add other parameters, ensuring they were defined and configured
  const otherParamsOrder = [
    "period",
    "fast_period",
    "slow_period",
    "signal_period",
    "nbdev",
    "multiplier",
    "fastk_period",
    "slowk_period",
    "slowd_period",
  ];
  otherParamsOrder.forEach((pKey) => {
    if (
      pKey !== "field" &&
      definedParams.includes(pKey) &&
      configuredParams[pKey] !== undefined
    ) {
      paramValues.push(configuredParams[pKey]);
    }
  });

  indicatorString += paramValues.join(", ") + ")";

  // Insert into textarea
  const currentText = queryInputTextarea.value;
  const textBefore = currentText.substring(0, lastCursorPosition);
  // currentWordForAutocomplete was the indicator name typed initially
  const textAfterAutocompleteWord = currentText.substring(
    lastCursorPosition + currentWordForAutocomplete.length
  );

  queryInputTextarea.value =
    textBefore + indicatorString + " " + textAfterAutocompleteWord;
  currentQueryString = queryInputTextarea.value;
  queryInputTextarea.focus();
  const newCursorPos = textBefore.length + indicatorString.length + 1; // +1 for the space after
  queryInputTextarea.setSelectionRange(newCursorPos, newCursorPos);

  // Suggest parts if applicable
  const upperName = activeIndicatorForConfig.name.toUpperCase();
  if (INDICATOR_PARTS[upperName]) {
    showIndicatorPartSuggestions(INDICATOR_PARTS[upperName], newCursorPos);
  }

  activeIndicatorForConfig = null;
  indicatorConfigModalInstance.hide();
}

function insertAtCursor(textarea, textToInsert) {
  const startPos = textarea.selectionStart;
  const endPos = textarea.selectionEnd;
  const textBefore = textarea.value.substring(0, startPos);
  const textAfter = textarea.value.substring(endPos, textarea.value.length);

  textarea.value = textBefore + textToInsert + textAfter;

  // Move cursor to after the inserted text
  const newCursorPos = startPos + textToInsert.length;
  textarea.selectionStart = newCursorPos;
  textarea.selectionEnd = newCursorPos;
  textarea.focus();
  currentQueryString = textarea.value; // Update global query string
}

function showIndicatorPartSuggestions(parts, _insertPosIgnored) {
  // insertPos is tricky with current logic, better to append
  if (!suggestionBox) return;
  suggestionBox.innerHTML = ""; // Clear previous suggestions

  parts.forEach((part) => {
    const li = document.createElement("li");
    li.className =
      "list-group-item list-group-item-action py-1 px-2 text-white bg-dark"; // Darker theme for parts
    li.style.fontSize = "0.9em";
    li.textContent = "." + part; // e.g., .macd
    li.onmousedown = (e) => {
      // Use mousedown to fire before blur
      e.preventDefault(); // Prevent textarea from losing focus
      insertAtCursor(queryInputTextarea, "." + part);
      suggestionBox.style.display = "none";
    };
    suggestionBox.appendChild(li);
  });

  // Position suggestion box relative to the textarea cursor or end of text
  // This is a simplified positioning; more advanced might use cursor coordinates
  const textareaRect = queryInputTextarea.getBoundingClientRect();
  suggestionBox.style.left = `${
    queryInputTextarea.offsetLeft + textareaRect.width / 2
  }px`; // Example positioning
  suggestionBox.style.top = `${
    queryInputTextarea.offsetTop + textareaRect.height
  }px`;
  suggestionBox.style.width = `150px`; // Fixed width for part suggestions
  suggestionBox.style.display = parts.length > 0 ? "block" : "none";
}

function setDefaultIndicatorsFallback() {
  console.warn("Using fallback indicator definitions.");
  INDICATOR_GROUPS = {
    "Price & Volume": [
      { value: "OPEN", label: "Open Price (OPEN)", params: ["timeframe"] },
      { value: "HIGH", label: "High Price (HIGH)", params: ["timeframe"] },
      { value: "LOW", label: "Low Price (LOW)", params: ["timeframe"] },
      { value: "CLOSE", label: "Close Price (CLOSE)", params: ["timeframe"] },
      { value: "VOLUME", label: "Volume (VOLUME)", params: ["timeframe"] },
    ],
    "Overlap Studies": [
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
      {
        value: "BBANDS",
        label: "Bollinger Bands (BBANDS)",
        params: ["timeframe", "field", "period", "nbdev"],
      },
    ],
    "Momentum Indicators": [
      {
        value: "RSI",
        label: "Relative Strength Index (RSI)",
        params: ["timeframe", "field", "period"],
      },
      {
        value: "MACD",
        label: "Moving Average Conv/Div (MACD)",
        params: [
          "timeframe",
          "field",
          "fast_period",
          "slow_period",
          "signal_period",
        ],
      },
      {
        value: "STOCH",
        label: "Stochastic (STOCH)",
        params: ["timeframe", "fastk_period", "slowk_period", "slowd_period"],
      }, // STOCH typically uses HLC
    ],
  };
  INDICATORS = []; // Reset and rebuild
  Object.values(INDICATOR_GROUPS).forEach((group) => {
    if (Array.isArray(group)) {
      group.forEach((ind) => {
        // Ensure params is always an array, even if empty
        ind.params = ind.params || getImplicitParams(ind.value) || [];
        INDICATORS.push(ind);
      });
    }
  });
}

function fetchIndicatorsAndRender() {
  fetch("/screener/api/indicators/")
    .then((response) => {
      if (!response.ok) {
        return response.text().then((text) => {
          throw new Error(
            `Server error: ${response.status} - ${text || "Unknown error"}`
          );
        });
      }
      return response.json();
    })
    .then((data) => {
      if (
        data &&
        data.groups &&
        typeof data.groups === "object" &&
        Object.keys(data.groups).length > 0
      ) {
        INDICATOR_GROUPS = data.groups;
        INDICATORS = []; // Clear previous indicators
        Object.values(INDICATOR_GROUPS).forEach((group) => {
          if (Array.isArray(group)) {
            group.forEach((indicator) => {
              // Ensure params is always an array, falling back to implicit if not defined
              indicator.params =
                indicator.params || getImplicitParams(indicator.value) || [];
              INDICATORS.push(indicator);
            });
          }
        });
        if (INDICATORS.length === 0) {
          console.warn(
            "API returned groups but no indicators were processed. Using fallback."
          );
          setDefaultIndicatorsFallback();
        } else {
          console.log("Indicators loaded from API:", INDICATORS.length);
        }
      } else {
        console.error(
          "Invalid or empty data received from indicators API:",
          data
        );
        setDefaultIndicatorsFallback();
      }
    })
    .catch((error) => {
      console.error("Failed to fetch indicators:", error);
      setDefaultIndicatorsFallback();
    })
    .finally(() => {
      renderIndicatorModalList(); // Render with whatever indicators are available
    });
}

function renderIndicatorModalList() {
  if (!indicatorListUl || !indicatorSearchInput) return;
  const searchTerm = indicatorSearchInput.value.toLowerCase();
  indicatorListUl.innerHTML = ""; // Clear previous list

  if (Object.keys(INDICATOR_GROUPS).length > 0) {
    Object.entries(INDICATOR_GROUPS).forEach(
      ([groupName, indicatorsInGroup]) => {
        if (!Array.isArray(indicatorsInGroup)) return;

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
          groupHeaderLi.style.background = "#232b3b"; // Dark background for group header
          groupHeaderLi.style.color = "#5eead4"; // Teal color for text
          indicatorListUl.appendChild(groupHeaderLi);

          filteredIndicators.forEach((indicatorDef) => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-action"; // Standard item
            li.innerHTML = `<span style="font-size:1.1em;" class="me-2">📊</span> ${indicatorDef.label}`;
            li.addEventListener("click", () => {
              if (indicatorModalInstance) indicatorModalInstance.hide();
              // Pass the full indicatorDef to preserve original case of 'value'
              selectIndicatorFromSuggestion(indicatorDef, queryInputTextarea);
            });
            indicatorListUl.appendChild(li);
          });
        }
      }
    );
  } else {
    indicatorListUl.innerHTML =
      '<li class="list-group-item">No indicators loaded or available.</li>';
  }
}

// --- PARSER: Query String to Backend Structure ---
// This is the fully corrected version
function transformQueryStringToBackendStructure(queryString) {
  console.log("Starting transformation of query string:", queryString);

  const tokens = [];
  let cursor = 0;

  const keywords = {};
  DEFAULT_TIMEFRAMES.forEach(
    (tf) => (keywords[tf.toUpperCase()] = TOKEN_TYPES.TIME_FRAME)
  );
  // DEFAULT_FIELDS is already all uppercase
  DEFAULT_FIELDS.forEach((f) => (keywords[f] = TOKEN_TYPES.FIELD));
  INDICATORS.forEach(
    // Assumes INDICATORS list is populated with { value: "SMA", ... }
    (ind) => (keywords[ind.value.toUpperCase()] = TOKEN_TYPES.INDICATOR_NAME)
  );

  const operators = {
    ">=": TOKEN_TYPES.OPERATOR_COMPARISON,
    "<=": TOKEN_TYPES.OPERATOR_COMPARISON,
    "==": TOKEN_TYPES.OPERATOR_COMPARISON,
    ">": TOKEN_TYPES.OPERATOR_COMPARISON,
    "<": TOKEN_TYPES.OPERATOR_COMPARISON,
    "CROSSES ABOVE": TOKEN_TYPES.OPERATOR_COMPARISON,
    "CROSSES BELOW": TOKEN_TYPES.OPERATOR_COMPARISON,
    AND: TOKEN_TYPES.OPERATOR_LOGICAL,
    OR: TOKEN_TYPES.OPERATOR_LOGICAL,
    "(": TOKEN_TYPES.BRACKET_OPEN,
    ")": TOKEN_TYPES.BRACKET_CLOSE,
    ",": TOKEN_TYPES.COMMA,
  };
  const sortedMultiWordOps = Object.keys(operators)
    .filter((op) => op.includes(" "))
    .sort((a, b) => b.length - a.length);

  while (cursor < queryString.length) {
    let char = queryString[cursor];
    let tokenizedThisPass = false;

    if (/\s/.test(char)) {
      cursor++;
      continue;
    }

    // 1. Timeframe check (prioritized)
    let matchedTimeframe = false;
    const sortedTimeframes = [...DEFAULT_TIMEFRAMES].sort(
      (a, b) => b.length - a.length
    );
    for (const tf of sortedTimeframes) {
      // tf from DEFAULT_TIMEFRAMES like "15min", "Daily"
      if (
        queryString.substring(cursor).toUpperCase().startsWith(tf.toUpperCase())
      ) {
        const nextCharAfterTf = queryString.charAt(cursor + tf.length);
        if (!nextCharAfterTf || !/[a-zA-Z0-9_]/.test(nextCharAfterTf)) {
          tokens.push({ type: TOKEN_TYPES.TIME_FRAME, value: tf }); // Store original case "15min"
          cursor += tf.length;
          matchedTimeframe = true;
          break;
        }
      }
    }
    if (matchedTimeframe) continue;

    // 2. Multi-word operators
    for (const op of sortedMultiWordOps) {
      if (
        queryString.substring(cursor).toUpperCase().startsWith(op.toUpperCase())
      ) {
        // Case insensitive match for operators
        tokens.push({ type: operators[op], value: op }); // Store original operator case
        cursor += op.length;
        tokenizedThisPass = true;
        break;
      }
    }
    if (tokenizedThisPass) continue;

    // 3. Single/double character operators
    let twoCharOp = queryString.substring(cursor, cursor + 2);
    if (operators[twoCharOp.toUpperCase()]) {
      // Check uppercase version for map key
      tokens.push({
        type: operators[twoCharOp.toUpperCase()],
        value: twoCharOp,
      });
      cursor += 2;
      continue;
    }
    if (operators[char]) {
      tokens.push({ type: operators[char], value: char });
      cursor++;
      continue;
    }

    // 4. Numbers
    if (/[0-9]/.test(char)) {
      let numStr = "";
      while (
        cursor < queryString.length &&
        /[0-9\.]/.test(queryString[cursor])
      ) {
        numStr += queryString[cursor++];
      }
      const numVal = parseFloat(numStr);
      tokens.push({ type: TOKEN_TYPES.NUMBER, value: numVal });
      continue;
    }

    // 5. Identifiers (Indicators, Fields)
    if (/[a-zA-Z_]/.test(char)) {
      let identifier = "";
      while (
        cursor < queryString.length &&
        /[a-zA-Z0-9_]/.test(queryString[cursor])
      ) {
        identifier += queryString[cursor++];
      }
      const upperIdentifier = identifier.toUpperCase();

      // Special handling for FIELD() like CLOSE()
      if (
        DEFAULT_FIELDS.includes(upperIdentifier) &&
        queryString[cursor] === "(" &&
        queryString[cursor + 1] === ")"
      ) {
        tokens.push({ type: TOKEN_TYPES.FIELD, value: upperIdentifier });
        tokens.push({ type: TOKEN_TYPES.BRACKET_OPEN, value: "(" });
        tokens.push({ type: TOKEN_TYPES.BRACKET_CLOSE, value: ")" });
        cursor += 2; // Consume "()"
        continue;
      }

      if (keywords[upperIdentifier]) {
        // Check against keywords map (which includes indicators)
        // For TIME_FRAME and INDICATOR_NAME, store original case `identifier`
        // For FIELD (if not caught by FIELD() above, though less likely now), use upperIdentifier
        let valueToStore = identifier;
        if (keywords[upperIdentifier] === TOKEN_TYPES.FIELD) {
          valueToStore = upperIdentifier;
        }
        tokens.push({ type: keywords[upperIdentifier], value: valueToStore });
      } else {
        tokens.push({ type: TOKEN_TYPES.IDENTIFIER, value: identifier }); // Fallback
      }
      continue;
    }

    tokens.push({
      type: TOKEN_TYPES.ERROR,
      value: char,
      message: `Unknown character: ${char}`,
    });
    cursor++;
  }
  tokens.push({ type: TOKEN_TYPES.EOF, value: "EOF" });
  console.log("Lexer Tokens:", JSON.parse(JSON.stringify(tokens)));

  let currentTokenIndex = 0;
  const lookahead = () => tokens[currentTokenIndex];
  const consume = (expectedType) => {
    const token = tokens[currentTokenIndex];
    if (expectedType && token.type !== expectedType) {
      throw new Error(
        `Syntax Error: Expected ${expectedType} but found ${token.type} ('${token.value}') at index ${currentTokenIndex}`
      );
    }
    currentTokenIndex++;
    return token;
  };

  const getBindingPower = (operatorToken) => {
    if (
      !operatorToken ||
      (operatorToken.type !== TOKEN_TYPES.OPERATOR_COMPARISON &&
        operatorToken.type !== TOKEN_TYPES.OPERATOR_LOGICAL)
    )
      return 0;
    const op = operatorToken.value.toUpperCase();
    if (op === "OR") return 10;
    if (op === "AND") return 20;
    if (
      [">", ">=", "<", "<=", "==", "CROSSES ABOVE", "CROSSES BELOW"].includes(
        op
      )
    )
      return 30;
    return 0;
  };

  const nud = (token) => {
    if (token.type === TOKEN_TYPES.NUMBER) {
      return { type: "NumberLiteral", value: token.value };
    }
    if (token.type === TOKEN_TYPES.FIELD) {
      // Handles FIELD() patterns
      if (
        lookahead().type === TOKEN_TYPES.BRACKET_OPEN &&
        tokens[currentTokenIndex + 1] &&
        tokens[currentTokenIndex + 1].type === TOKEN_TYPES.BRACKET_CLOSE
      ) {
        consume(TOKEN_TYPES.BRACKET_OPEN);
        consume(TOKEN_TYPES.BRACKET_CLOSE);
        return { type: "FieldLiteral", value: token.value };
      }
      return { type: "FieldLiteral", value: token.value };
    }
    if (token.type === TOKEN_TYPES.TIME_FRAME) {
      const nextToken = lookahead(); // See what token comes after the timeframe

      if (nextToken.type === TOKEN_TYPES.INDICATOR_NAME) {
        // Original logic: Timeframe followed by an indicator like SMA, MACD_LINE
        const indicatorNameToken = consume(TOKEN_TYPES.INDICATOR_NAME);
        consume(TOKEN_TYPES.BRACKET_OPEN);
        const args = [];
        if (lookahead().type !== TOKEN_TYPES.BRACKET_CLOSE) {
          while (true) {
            args.push(parseExpression(0));
            if (lookahead().type === TOKEN_TYPES.BRACKET_CLOSE) break;
            consume(TOKEN_TYPES.COMMA);
          }
        }
        consume(TOKEN_TYPES.BRACKET_CLOSE);
        return {
          type: "IndicatorCall",
          name: indicatorNameToken.value,
          timeframe: token.value, // The TIME_FRAME token's value, e.g., "Daily"
          arguments: args,
        };
      } else if (nextToken.type === TOKEN_TYPES.FIELD) {
        // New logic: Timeframe followed by a FIELD() like CLOSE()
        const fieldToken = consume(TOKEN_TYPES.FIELD); // Consume "CLOSE"
        // Expect and consume the parentheses for the field, e.g., "()"
        if (
          lookahead().type === TOKEN_TYPES.BRACKET_OPEN &&
          tokens[currentTokenIndex + 1] && // Ensure next token exists
          tokens[currentTokenIndex + 1].type === TOKEN_TYPES.BRACKET_CLOSE
        ) {
          consume(TOKEN_TYPES.BRACKET_OPEN);
          consume(TOKEN_TYPES.BRACKET_CLOSE);
          // Represent this as an "IndicatorCall" for backend consistency
          return {
            type: "IndicatorCall",
            name: fieldToken.value, // e.g., "CLOSE"
            timeframe: token.value, // e.g., "Daily"
            arguments: [], // CLOSE() has no explicit arguments here
          };
        } else {
          throw new Error(
            `Syntax Error: Expected FIELD() (e.g., CLOSE()) after TimeFrame but found incomplete field expression for '${fieldToken.value}' at index ${currentTokenIndex}`
          );
        }
      } else {
        // If it's neither an INDICATOR_NAME nor a FIELD after a TIME_FRAME
        throw new Error(
          `Syntax Error: Expected INDICATOR_NAME or FIELD() after TIME_FRAME but found ${nextToken.type} ('${nextToken.value}') at index ${currentTokenIndex}`
        );
      }
    }
    if (token.type === TOKEN_TYPES.INDICATOR_NAME) {
      // Default timeframe = Daily
      consume(TOKEN_TYPES.BRACKET_OPEN);
      const args = [];
      if (lookahead().type !== TOKEN_TYPES.BRACKET_CLOSE) {
        while (true) {
          args.push(parseExpression(0));
          if (lookahead().type === TOKEN_TYPES.BRACKET_CLOSE) break;
          consume(TOKEN_TYPES.COMMA);
        }
      }
      consume(TOKEN_TYPES.BRACKET_CLOSE);
      return {
        type: "IndicatorCall",
        name: token.value,
        timeframe: "Daily",
        arguments: args,
      };
    }
    if (token.type === TOKEN_TYPES.BRACKET_OPEN) {
      const expr = parseExpression(0);
      consume(TOKEN_TYPES.BRACKET_CLOSE);
      return expr;
    }
    throw new Error(
      `Syntax Error: Unexpected token at start of expression: ${token.type} ('${token.value}')`
    );
  };

  const led = (left, token) => {
    if (
      token.type === TOKEN_TYPES.OPERATOR_COMPARISON ||
      token.type === TOKEN_TYPES.OPERATOR_LOGICAL
    ) {
      const right = parseExpression(getBindingPower(token));
      return {
        type:
          token.type === TOKEN_TYPES.OPERATOR_LOGICAL
            ? "BinaryExpression"
            : "Comparison",
        operator: token.value,
        left: left,
        right: right,
      };
    }
    throw new Error(
      `Syntax Error: Unexpected infix token: ${token.type} ('${token.value}')`
    );
  };

  const parseExpression = (rightBindingPower) => {
    let token = consume();
    let left = nud(token);
    while (rightBindingPower < getBindingPower(lookahead())) {
      token = consume();
      left = led(left, token);
    }
    return left;
  };

  try {
    if (tokens.length === 1 && tokens[0].type === TOKEN_TYPES.EOF) return null;
    const ast = parseExpression(0);
    if (lookahead().type !== TOKEN_TYPES.EOF) {
      const remainingTokensForError = tokens.slice(currentTokenIndex);
      const lastGoodTokenBeforeError =
        currentTokenIndex > 0
          ? tokens[currentTokenIndex - 1]
          : { value: "start of query" };
      throw new Error(
        `Syntax Error: Unexpected tokens remaining after parsing: ${JSON.stringify(
          remainingTokensForError
        )}. Error likely near token: '${lastGoodTokenBeforeError.value}'`
      );
    }
    if (
      ast.type === "IndicatorCall" ||
      ast.type === "NumberLiteral" ||
      ast.type === "FieldLiteral"
    ) {
      throw new Error(
        "Incomplete query: Expression does not form a complete condition or logical group."
      );
    }
    return ast;
  } catch (e) {
    console.error(
      "Parser Exception:",
      e.message,
      "\nTokens so far (before current failing token):",
      JSON.stringify(tokens.slice(0, currentTokenIndex))
    );
    return {
      type: "PARSE_ERROR",
      error: e.message,
      details: `Error near token: '${
        tokens[currentTokenIndex]?.value ||
        tokens[currentTokenIndex - 1]?.value ||
        "unknown"
      }' (Index: ${currentTokenIndex})`,
    };
  }
}

// --- Utilities ---
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
  const upperVal = indicatorValue.toUpperCase();
  if (upperVal.startsWith("CDL")) return ["timeframe"]; // Candlestick patterns

  // Indicators that typically only need a period and might implicitly use 'close' or OHLC
  const periodOnlyImplicitField = [
    "ATR",
    "NATR",
    "TRANGE",
    "AVGPRICE",
    "MEDPRICE",
    "TYPPRICE",
    "WCLPRICE",
    "STOCH",
    "STOCHF",
    "STOCHRSI", // Stochastic functions use HLC
  ];
  if (periodOnlyImplicitField.includes(upperVal))
    return ["timeframe", "period"];

  // Indicators that primarily use volume
  const volumeBased = ["OBV", "AD", "ADOSC", "MFI"];
  if (volumeBased.includes(upperVal)) return ["timeframe", "period"]; // MFI also needs HLC, ADOSC needs HLCV

  // Default for most other indicators (like SMA, EMA, RSI on a specific field)
  return ["timeframe", "field", "period"];
}

// --- Scan Execution & Results ---
function handleRunScan() {
  if (!resultsTableBody || !stockCountSpan || !queryInputTextarea) {
    console.error("Required DOM elements for scan are missing.");
    return;
  }
  resultsTableBody.innerHTML =
    '<tr><td colspan="10" class="text-center py-5"><i class="fas fa-spinner fa-spin fa-2x me-2"></i>Running scan...</td></tr>';
  stockCountSpan.textContent = "Matching Stocks: -";
  currentQueryString = queryInputTextarea.value;

  if (!currentQueryString.trim()) {
    resultsTableBody.innerHTML =
      '<tr><td colspan="10" class="text-center py-5">Query is empty.</td></tr>';
    stockCountSpan.textContent = "Matching Stocks: 0";
    return;
  }

  const backendPayload =
    transformQueryStringToBackendStructure(currentQueryString);

  if (!backendPayload || backendPayload.type === "PARSE_ERROR") {
    const errorMsg =
      backendPayload && backendPayload.error
        ? `Parsing Error: ${backendPayload.error} ${
            backendPayload.details || ""
          }`
        : "Could not build a valid query. Check syntax.";
    resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">${errorMsg}</td></tr>`;
    stockCountSpan.textContent = "Matching Stocks: 0";
    return;
  }

  console.log("Sending to backend:", JSON.stringify(backendPayload, null, 2));

  fetch("/screener/api/run_screener/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      filters: backendPayload,
      segment: document.getElementById("segmentDropdown")?.value || "Nifty 500", // Ensure segmentDropdown exists or provide default
    }),
  })
    .then((response) => {
      if (!response.ok) {
        return response
          .json()
          .then((err) =>
            Promise.reject(
              err.error ||
                `Server error: ${response.statusText} (${response.status})`
            )
          );
      }
      return response.json();
    })
    .then((data) => {
      if (data.error) {
        // Error from backend logic (e.g. data processing)
        resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Error from server: ${data.error}</td></tr>`;
        stockCountSpan.textContent = "Matching Stocks: 0";
      } else if (data.results) {
        updateResultsTable(data.results);
      } else {
        updateResultsTable([]); // No results or unexpected format
      }
    })
    .catch((error) => {
      console.error("Scan execution error:", error);
      resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Network or Scan Error: ${
        error.message || error
      }</td></tr>`;
      stockCountSpan.textContent = "Matching Stocks: 0";
    });
}

function updateResultsTable(results) {
  if (!resultsTableBody || !stockCountSpan) return;
  tbody = resultsTableBody; // Use the global const
  countSpan = stockCountSpan; // Use the global const

  tbody.innerHTML = ""; // Clear previous results
  if (!results || results.length === 0) {
    tbody.innerHTML =
      '<tr><td colspan="10" class="text-center py-5" style="color:#6b7280;">No stocks match your scan criteria.</td></tr>';
    countSpan.textContent = "Matching Stocks: 0";
    return;
  }
  countSpan.textContent = `Matching Stocks: ${results.length}`;
  results.forEach((stock, index) => {
    const tr = tbody.insertRow();
    let cs = "",
      ct = stock.change_pct || "N/A";
    if (typeof ct === "string") {
      const nc = parseFloat(ct.replace("%", ""));
      if (!isNaN(nc)) {
        cs = nc >= 0 ? "color:#34d399;" : "color:#f87171;"; // Green for positive, Red for negative
        ct = `${nc.toFixed(2)}%`;
      }
    }
    const f = (n, d = 2) =>
      typeof n === "number" ||
      (typeof n === "string" && n !== "" && !isNaN(Number(n)))
        ? Number(n).toFixed(d)
        : n || "N/A";

    tr.innerHTML = `<td>${index + 1}</td>
                    <td class="fw-medium" style="color:#a78bfa;">${
                      stock.symbol || "N/A"
                    }</td>
                    <td>${stock.timestamp || "N/A"}</td>
                    <td>${f(stock.open)}</td>
                    <td>${f(stock.high)}</td>
                    <td>${f(stock.low)}</td>
                    <td>${f(stock.close)}</td>
                    <td style="${cs}">${ct}</td>
                    <td>${f(stock.volume, 0)}</td>
                    <td>
                        <button type="button" class="icon-btn text-info btn-sm" title="View Chart"><i class="fas fa-chart-line"></i></button>
                        <button type="button" class="icon-btn text-primary btn-sm" title="Add to Watchlist"><i class="fas fa-plus-square"></i></button>
                    </td>`;
  });
}
