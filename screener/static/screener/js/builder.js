// --- Constants ---
let INDICATORS = []; // Populated by fetchIndicatorsAndRender
let INDICATOR_GROUPS = {}; // Populated by fetchIndicatorsAndRender
const INDICATOR_PARTS = {
  MACD: ["macd", "signal", "hist"],
  STOCH: ["k", "d"],
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
const DEFAULT_FIELDS = ["OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"];

// --- Token Types for Lexer/Parser ---
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

// --- Global State & Modal Instances ---
let currentQueryString = "";
let activeIndicatorForConfig = null;
let lastCursorPosition = 0;
let currentWordForAutocomplete = "";
let wordStartIndex = 0;

// Ensure these are declared so they can be assigned in DOMContentLoaded
let indicatorModalInstance, indicatorConfigModalInstance, scanNameModalInstance;

// Temporary storage for save operation
let parsedQueryForSave = null;
let segmentValueForSave = "";

let keywords = {}; // Define globally, populated after indicators fetch

// --- DOM Elements ---
// Declare these at a higher scope if they are consistently used across functions
let queryInputTextarea;
let suggestionBox;
let devParseButton;
let runScanButton;
let clearQueryButton;
let saveScanButton; // The main save button with id="saveScanButton"

let indicatorSearchInput;
let indicatorListUl;

let indicatorConfigModalLabel;
let indicatorConfigTimeframeSelect;
let indicatorConfigFieldSelect;
let indicatorConfigFieldGroup;
let indicatorConfigPeriodGroup;
let indicatorConfigPeriodInput;
let indicatorConfigFastPeriodGroup;
let indicatorConfigFastPeriodInput;
let indicatorConfigSlowPeriodGroup;
let indicatorConfigSlowPeriodInput;
let indicatorConfigSignalPeriodGroup;
let indicatorConfigSignalPeriodInput;
let indicatorConfigMultiplierGroup;
let indicatorConfigMultiplierInput;
let indicatorConfigNbdevGroup;
let indicatorConfigNbdevInput;
let indicatorConfigFastKPeriodGroup;
let indicatorConfigFastKPeriodInput;
let indicatorConfigSlowKPeriodGroup;
let indicatorConfigSlowKPeriodInput;
let indicatorConfigSlowDPeriodGroup;
let indicatorConfigSlowDPeriodInput;
let indicatorConfigDoneButton;

let resultsTableBody;
let stockCountSpan;
let confirmSaveScanBtn; // Save button inside the scan name modal (id="confirmSaveScanButton")
let scanNameInput; // Input field inside the scan name modal (id="scanNameInput")

// --- Initialization ---
document.addEventListener("DOMContentLoaded", () => {
  // Assign DOM elements
  queryInputTextarea = document.getElementById("queryInput");
  devParseButton = document.getElementById("add-filter"); // Assuming this is your dev parse button
  runScanButton = document.getElementById("runScan");
  clearQueryButton = document.getElementById("clearFiltersButton");
  saveScanButton = document.getElementById("saveScanButton"); // Main save button

  indicatorSearchInput = document.getElementById("indicatorSearch");
  indicatorListUl = document.getElementById("indicatorList");

  indicatorConfigModalLabel = document.getElementById(
    "indicatorConfigModalLabelText"
  );
  indicatorConfigTimeframeSelect = document.getElementById(
    "indicatorConfigTimeframe"
  );
  indicatorConfigFieldSelect = document.getElementById("indicatorConfigField");
  indicatorConfigFieldGroup = document.getElementById(
    "indicatorConfigFieldGroup"
  );
  indicatorConfigPeriodGroup = document.getElementById(
    "indicatorConfigPeriodGroup"
  );
  indicatorConfigPeriodInput = document.getElementById("indicatorConfigPeriod");
  indicatorConfigFastPeriodGroup = document.getElementById(
    "indicatorConfigFastPeriodGroup"
  );
  indicatorConfigFastPeriodInput = document.getElementById(
    "indicatorConfigFastPeriod"
  );
  indicatorConfigSlowPeriodGroup = document.getElementById(
    "indicatorConfigSlowPeriodGroup"
  );
  indicatorConfigSlowPeriodInput = document.getElementById(
    "indicatorConfigSlowPeriod"
  );
  indicatorConfigSignalPeriodGroup = document.getElementById(
    "indicatorConfigSignalPeriodGroup"
  );
  indicatorConfigSignalPeriodInput = document.getElementById(
    "indicatorConfigSignalPeriod"
  );
  indicatorConfigMultiplierGroup = document.getElementById(
    "indicatorConfigMultiplierGroup"
  );
  indicatorConfigMultiplierInput = document.getElementById(
    "indicatorConfigMultiplier"
  );
  indicatorConfigNbdevGroup = document.getElementById(
    "indicatorConfigNbdevGroup"
  );
  indicatorConfigNbdevInput = document.getElementById("indicatorConfigNbdev");
  indicatorConfigFastKPeriodGroup = document.getElementById(
    "indicatorConfigFastKPeriodGroup"
  );
  indicatorConfigFastKPeriodInput = document.getElementById(
    "indicatorConfigFastKPeriod"
  );
  indicatorConfigSlowKPeriodGroup = document.getElementById(
    "indicatorConfigSlowKPeriodGroup"
  );
  indicatorConfigSlowKPeriodInput = document.getElementById(
    "indicatorConfigSlowKPeriod"
  );
  indicatorConfigSlowDPeriodGroup = document.getElementById(
    "indicatorConfigSlowDPeriodGroup"
  );
  indicatorConfigSlowDPeriodInput = document.getElementById(
    "indicatorConfigSlowDPeriod"
  );
  indicatorConfigDoneButton = document.getElementById("indicatorConfigDone");

  resultsTableBody = document.getElementById("resultsTableBody");
  stockCountSpan = document.getElementById("stockCount");

  // Crucial for the new save modal
  confirmSaveScanBtn = document.getElementById("confirmSaveScanButton");
  scanNameInput = document.getElementById("scanNameInput");

  // Initialize Modals
  const indicatorModalEl = document.getElementById("indicatorModal");
  if (indicatorModalEl) {
    indicatorModalInstance = new bootstrap.Modal(indicatorModalEl);
  } else {
    console.error("Indicator modal element (#indicatorModal) not found!");
  }

  const indicatorConfigModalEl = document.getElementById(
    "indicatorConfigModal"
  );
  if (indicatorConfigModalEl) {
    indicatorConfigModalInstance = new bootstrap.Modal(indicatorConfigModalEl);
  } else {
    console.error(
      "Indicator config modal element (#indicatorConfigModal) not found!"
    );
  }

  const scanNameModalEl = document.getElementById("scanNameModal"); // HTML for this modal is in dashboard_html_complete_v1
  if (scanNameModalEl) {
    scanNameModalInstance = new bootstrap.Modal(scanNameModalEl);
    console.log("Scan Name Modal instance CREATED."); // For debugging
  } else {
    console.error(
      "Scan name modal element (#scanNameModal) not found! Ensure it's in your HTML."
    );
  }

  // Setup suggestion box (dynamically created)
  suggestionBox = document.createElement("ul");
  suggestionBox.id = "autocompleteSuggestionBox";
  suggestionBox.className = "list-group position-absolute shadow-lg"; // Bootstrap classes
  suggestionBox.style.zIndex = "1050"; // Ensure it's above other elements
  suggestionBox.style.maxHeight = "200px";
  suggestionBox.style.overflowY = "auto";
  suggestionBox.style.display = "none"; // Initially hidden
  if (queryInputTextarea && queryInputTextarea.parentNode) {
    // Insert after the textarea, within its container for relative positioning
    queryInputTextarea.parentNode.insertBefore(
      suggestionBox,
      queryInputTextarea.nextSibling
    );
  } else {
    console.error(
      "Query input textarea or its parent not found for suggestion box placement."
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
    DEFAULT_FIELDS.forEach((f) =>
      indicatorConfigFieldSelect.options.add(new Option(f, f.toLowerCase()))
    );
  }

  // Add event listeners
  if (queryInputTextarea) {
    queryInputTextarea.addEventListener("input", handleQueryInputChange);
    queryInputTextarea.addEventListener("keyup", handleQueryInputKeyup);
    queryInputTextarea.addEventListener("blur", () =>
      setTimeout(() => {
        // Delay hiding to allow click on suggestion
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

  // Attach the NEW function to the main save button
  if (saveScanButton) {
    saveScanButton.addEventListener("click", handleSaveScanInitiate);
    console.log(
      "Event listener for handleSaveScanInitiate ATTACHED to #saveScanButton."
    ); // For debugging
  } else {
    console.error("Main save button (#saveScanButton) not found!");
  }

  // Attach event listener to the "Save" button INSIDE the scan name modal
  if (confirmSaveScanBtn) {
    confirmSaveScanBtn.addEventListener("click", handleSaveScanConfirm);
    console.log(
      "Event listener for handleSaveScanConfirm ATTACHED to #confirmSaveScanButton."
    ); // For debugging
  } else {
    console.error(
      "Confirm save button inside modal (#confirmSaveScanButton) not found!"
    );
  }

  fetchIndicatorsAndRender(); // This populates INDICATORS and then keywords
  renderSavedScansList(); // Load saved scans on page load
});

// --- Saved Scans Logic ---
function renderSavedScansList() {
  const listContainer = document.getElementById("savedScansList");
  if (!listContainer) {
    console.error("Saved scans list container (#savedScansList) not found.");
    return;
  }
  listContainer.innerHTML = ""; // Clear existing entries

  fetch("/screener/api/saved_scans/")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} - ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      const scans = data.saved_scans || [];
      if (scans.length === 0) {
        const li = document.createElement("li");
        li.className = "p-2 rounded-md text-muted";
        li.textContent = "No saved scans yet.";
        listContainer.appendChild(li);
        return;
      }

      scans.forEach((scan) => {
        const li = document.createElement("li");
        li.className = "p-2 rounded-md"; // Tailwind classes for padding and rounded corners
        li.style.cursor = "pointer";
        li.style.fontSize = "0.85rem";
        li.textContent = scan.name;
        // Hover effect
        li.addEventListener(
          "mouseover",
          () => (li.style.backgroundColor = "#374151")
        ); // Darker gray on hover
        li.addEventListener("mouseout", () => (li.style.backgroundColor = "")); // Revert on mouse out

        li.addEventListener("click", () => {
          const queryString = transformBackendStructureToQueryString(
            scan.filters
          );
          if (queryInputTextarea) {
            queryInputTextarea.value = queryString;
            currentQueryString = queryString; // Update global state if you use it elsewhere
          }
          // Also set the segment dropdown
          const segmentDropdown = document.getElementById("segmentDropdown");
          if (segmentDropdown && scan.segment) {
            segmentDropdown.value = scan.segment;
          }
          alert(`Loaded scan: "${scan.name}"`); // Simple feedback
        });
        listContainer.appendChild(li);
      });
    })
    .catch((err) => {
      console.error("Error fetching saved scans:", err);
      if (listContainer) {
        // Check again in case it became null
        const li = document.createElement("li");
        li.className = "p-2 text-danger"; // Bootstrap text color for error
        li.textContent = "Failed to load saved scans.";
        listContainer.appendChild(li);
      }
    });
}

// NEW function to INITIATE save by showing the modal
function handleSaveScanInitiate() {
  console.log("handleSaveScanInitiate called."); // For debugging
  if (!queryInputTextarea) {
    alert("Internal error: query textarea not found.");
    return;
  }
  const rawQuery = queryInputTextarea.value.trim();
  if (!rawQuery) {
    alert("Cannot save an empty query.");
    return;
  }

  const parsed = transformQueryStringToBackendStructure(rawQuery);
  if (!parsed || parsed.type === "PARSE_ERROR") {
    alert(
      parsed && parsed.error
        ? `Cannot save: parsing error: ${parsed.error}`
        : "Cannot save: invalid query."
    );
    return;
  }

  // Store parsed data and segment for when the modal's save button is clicked
  parsedQueryForSave = parsed;
  const segmentDropdown = document.getElementById("segmentDropdown");
  segmentValueForSave = segmentDropdown ? segmentDropdown.value : "";

  if (scanNameInput) scanNameInput.value = ""; // Clear previous name from modal input

  if (scanNameModalInstance) {
    console.log("Attempting to show scanNameModalInstance."); // For debugging
    scanNameModalInstance.show();
  } else {
    alert(
      "Save scan modal is not properly initialized. Please refresh the page or check console for errors."
    );
    console.error(
      "scanNameModalInstance is null or undefined in handleSaveScanInitiate."
    );
  }
}

// NEW function to CONFIRM save FROM THE MODAL
function handleSaveScanConfirm() {
  console.log("handleSaveScanConfirm called."); // For debugging
  const nameToSave = scanNameInput ? scanNameInput.value.trim() : "";

  if (!nameToSave) {
    alert("Please enter a name for the scan.");
    return; // Keep modal open
  }

  if (!parsedQueryForSave) {
    alert(
      "Error: Query data not found for saving. Please try initiating the save again."
    );
    if (scanNameModalInstance) scanNameModalInstance.hide(); // Hide modal as something is wrong
    return;
  }

  // Proceed with the actual fetch call to save the scan
  fetch("/screener/api/save_scan/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"), // Ensure getCookie is defined and working
    },
    body: JSON.stringify({
      name: nameToSave,
      filters: parsedQueryForSave, // Use the stored parsed query
      segment: segmentValueForSave, // Use the stored segment
    }),
  })
    .then((response) => {
      if (!response.ok) {
        // Attempt to parse JSON error response from backend
        return response
          .json()
          .then((errData) => {
            // Use errData.error if available, otherwise a generic HTTP error
            throw new Error(errData.error || `HTTP error ${response.status}`);
          })
          .catch(() => {
            // If response.json() fails (e.g. HTML error page), throw generic HTTP error
            throw new Error(`HTTP error ${response.status}`);
          });
      }
      return response.json();
    })
    .then((data) => {
      if (data.success && data.scan) {
        alert(`Scan “${data.scan.name}” saved successfully.`);
        renderSavedScansList(); // Refresh the list of saved scans
        if (scanNameModalInstance) scanNameModalInstance.hide(); // Hide modal on success
      } else {
        // If backend returns success:false or no scan data
        throw new Error(data.error || "Unknown error saving scan.");
      }
    })
    .catch((err) => {
      console.error("Error saving scan:", err);
      alert(`Failed to save scan: ${err.message}`);
      // Modal remains open for user to retry or cancel
    })
    .finally(() => {
      // Clear the temporarily stored data regardless of outcome
      // to prevent accidental reuse on a subsequent save attempt if modal is re-shown.
      parsedQueryForSave = null;
      segmentValueForSave = "";
    });
}

// --- Autocomplete Logic ---
function handleQueryInputChange(event) {
  currentQueryString = event.target.value;
  const cursorPos = event.target.selectionStart;
  let textBeforeCursor = currentQueryString.substring(0, cursorPos);

  // Regex to find the start of the current word (alphanumeric or underscore)
  const match = textBeforeCursor.match(/(\b[a-zA-Z0-9_]+)$/);
  if (match) {
    currentWordForAutocomplete = match[1].toUpperCase(); // For case-insensitive matching
    wordStartIndex = cursorPos - match[1].length;

    // Filter indicators based on the current word
    const suggestions = INDICATORS.filter(
      (ind) =>
        ind.value.toUpperCase().startsWith(currentWordForAutocomplete) || // Match by value (e.g., "SMA")
        ind.label.toUpperCase().includes(currentWordForAutocomplete) // Match by label (e.g., "Simple Moving Average")
    );

    if (suggestions.length > 0 && currentWordForAutocomplete.length >= 1) {
      // Show suggestions if any and word is long enough
      populateSuggestionBox(suggestions, event.target);
    } else {
      if (suggestionBox) suggestionBox.style.display = "none";
    }
  } else {
    currentWordForAutocomplete = ""; // No current word being typed
    if (suggestionBox) suggestionBox.style.display = "none";
  }

  // Logic for suggesting indicator parts like .macd, .signal after an indicator
  const typedSoFarUpper = event.target.value.toUpperCase();
  const indicatorPattern = /\b([A-Z_]+)\s*\(([^)]*)\)$/i; // Matches "INDICATOR(...)"
  const indicatorMatch = typedSoFarUpper.match(indicatorPattern);

  if (indicatorMatch) {
    const indicatorNameFromInput = indicatorMatch[1].toUpperCase();
    const parts = INDICATOR_PARTS[indicatorNameFromInput]; // Get parts like ["macd", "signal"]
    if (parts) {
      // Check if the cursor is right after the closing parenthesis of an indicator
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
  // Potentially handle ArrowUp, ArrowDown, Enter for suggestion navigation here
}

function populateSuggestionBox(suggestions, textarea) {
  if (!suggestionBox) return;
  suggestionBox.innerHTML = ""; // Clear previous suggestions
  suggestions.slice(0, 7).forEach((indicatorDef) => {
    // Show a limited number of suggestions
    const li = document.createElement("li");
    li.className = "list-group-item list-group-item-action py-1 px-2"; // Bootstrap classes
    li.style.fontSize = "0.9em";
    li.textContent = `${indicatorDef.label} (${indicatorDef.value})`;
    li.onmousedown = (e) => {
      // Use onmousedown to fire before blur on textarea
      e.preventDefault(); // Prevent textarea from losing focus immediately
      selectIndicatorFromSuggestion(indicatorDef, textarea);
      suggestionBox.style.display = "none";
    };
    suggestionBox.appendChild(li);
  });

  // Position the suggestion box below the current word
  const textareaRect = textarea.getBoundingClientRect();
  // Estimate line height (can be tricky with variable fonts/styles)
  const DUMMY_LINE_HEIGHT =
    parseFloat(window.getComputedStyle(textarea).lineHeight) || 20;

  // Create a temporary span to measure text width up to the current word
  const dummySpan = document.createElement("span");
  dummySpan.style.visibility = "hidden";
  dummySpan.style.position = "absolute";
  dummySpan.style.whiteSpace = "pre"; // Important for accurate width measurement
  dummySpan.style.font = window.getComputedStyle(textarea).font;
  document.body.appendChild(dummySpan);
  dummySpan.textContent = textarea.value.substring(0, wordStartIndex);
  const textCoords = dummySpan.getBoundingClientRect();
  document.body.removeChild(dummySpan);

  // Calculate position based on textarea's position and text measurement
  const offsetX = textarea.offsetLeft + textCoords.width - textarea.scrollLeft;
  // Adjust offsetY by line height for multiline textareas
  const offsetY =
    textarea.offsetTop +
    DUMMY_LINE_HEIGHT +
    Math.floor(textCoords.height / DUMMY_LINE_HEIGHT) * DUMMY_LINE_HEIGHT -
    textarea.scrollTop;

  suggestionBox.style.left = `${offsetX}px`;
  suggestionBox.style.top = `${offsetY}px`;
  // Adjust width dynamically, or set a fixed max-width
  suggestionBox.style.width =
    textarea.clientWidth > 300
      ? "300px"
      : `${textarea.clientWidth - (textCoords.width % textarea.clientWidth)}px`;
  suggestionBox.style.display = suggestions.length > 0 ? "block" : "none";
}

function selectIndicatorFromSuggestion(indicatorDef, _textarea) {
  // textarea param not used here
  // Store the selected indicator and its parameters for configuration
  activeIndicatorForConfig = {
    name: indicatorDef.value,
    label: indicatorDef.label,
    paramsFromDef: indicatorDef.params || getImplicitParams(indicatorDef.value), // Use defined params or infer
  };
  lastCursorPosition = wordStartIndex; // Save cursor position where autocomplete started
  openIndicatorConfigModal(); // Open the modal to configure parameters
}

function openIndicatorConfigModal() {
  if (!activeIndicatorForConfig || !indicatorConfigModalInstance) {
    console.error("No indicator selected or config modal not initialized.");
    return;
  }
  indicatorConfigModalLabel.textContent = `Configure: ${activeIndicatorForConfig.label}`;
  const indicatorDefinedParams = activeIndicatorForConfig.paramsFromDef || [];

  // Reset timeframe to default
  indicatorConfigTimeframeSelect.value = "daily"; // Default timeframe

  // Hide all parameter input groups initially
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

  // Helper to show and set default for a parameter input
  const setupField = (paramKey, groupEl, inputEl, defaultValue) => {
    if (groupEl && indicatorDefinedParams.includes(paramKey)) {
      groupEl.style.display = "block"; // Show the group
      if (inputEl) inputEl.value = defaultValue; // Set default value
    } else if (groupEl) {
      groupEl.style.display = "none"; // Keep hidden if not applicable
    }
  };

  // Setup each parameter field based on what the selected indicator expects
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

function handleIndicatorConfigDone() {
  if (!activeIndicatorForConfig || !indicatorConfigModalInstance) return;

  const configuredParams = { timeframe: indicatorConfigTimeframeSelect.value };
  const definedParams = activeIndicatorForConfig.paramsFromDef || [];

  // Helper to read value from an input field
  const readParam = (key, groupEl, inputEl, isNum = true, isFlt = false) => {
    if (
      definedParams.includes(key) &&
      groupEl &&
      groupEl.style.display !== "none"
    ) {
      let val = inputEl.value;
      if (
        inputEl.type === "select-one" &&
        key !== "timeframe" &&
        key !== "field"
      ) {
        // For select elements that are not timeframe/field
        val = val.toLowerCase();
      } else if (inputEl.type === "select-one" && key === "field") {
        // For field select
        val = inputEl.value; // Keep case as is (e.g. 'close', 'open')
      } else if (isNum) {
        // For numeric inputs
        val = isFlt ? parseFloat(val) : parseInt(val, 10);
      }
      if (!(isNum && isNaN(val))) {
        // Add if valid number or not a number field
        configuredParams[key] = val;
      }
    }
  };

  // Read all configured parameters
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

  // Construct the indicator string
  let indicatorString =
    configuredParams.timeframe.charAt(0).toUpperCase() +
    configuredParams.timeframe.slice(1) +
    " " +
    activeIndicatorForConfig.name +
    "(";
  const paramValues = [];

  // Add 'field' parameter first if it's defined and configured
  if (definedParams.includes("field") && configuredParams.field) {
    let fieldValue = configuredParams.field.toUpperCase(); // Ensure field is uppercase
    if (DEFAULT_FIELDS.includes(fieldValue)) {
      // Check if it's a standard field
      fieldValue += "()"; // Append () for fields like CLOSE()
    }
    paramValues.push(fieldValue);
  }

  // Add other parameters in a defined order
  const otherParamsOrder = [
    // Define order to ensure consistency
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

  // Insert the configured indicator string into the query textarea
  const currentText = queryInputTextarea.value;
  const textBefore = currentText.substring(0, lastCursorPosition); // Text before the autocompleted word
  const textAfterAutocompleteWord = currentText.substring(
    lastCursorPosition + currentWordForAutocomplete.length
  ); // Text after
  queryInputTextarea.value =
    textBefore + indicatorString + " " + textAfterAutocompleteWord; // Add a space after indicator
  currentQueryString = queryInputTextarea.value; // Update global query string
  queryInputTextarea.focus();
  const newCursorPos = textBefore.length + indicatorString.length + 1; // Position cursor after the inserted string + space
  queryInputTextarea.setSelectionRange(newCursorPos, newCursorPos);

  // If the indicator has parts (e.g., MACD.macd), show suggestions for those parts
  const upperName = activeIndicatorForConfig.name.toUpperCase();
  if (INDICATOR_PARTS[upperName]) {
    showIndicatorPartSuggestions(INDICATOR_PARTS[upperName], newCursorPos);
  }

  activeIndicatorForConfig = null; // Reset active indicator
  indicatorConfigModalInstance.hide(); // Hide the configuration modal
}

function insertAtCursor(textarea, textToInsert) {
  const startPos = textarea.selectionStart;
  const endPos = textarea.selectionEnd;
  const textBefore = textarea.value.substring(0, startPos);
  const textAfter = textarea.value.substring(endPos, textarea.value.length);
  textarea.value = textBefore + textToInsert + textAfter;
  const newCursorPos = startPos + textToInsert.length;
  textarea.selectionStart = newCursorPos;
  textarea.selectionEnd = newCursorPos;
  textarea.focus();
  currentQueryString = textarea.value; // Update global state
}

function showIndicatorPartSuggestions(parts, _insertPosIgnored) {
  // insertPos might not be needed if always inserting at current cursor
  if (!suggestionBox) return;
  suggestionBox.innerHTML = ""; // Clear previous suggestions

  parts.forEach((part) => {
    const li = document.createElement("li");
    li.className =
      "list-group-item list-group-item-action py-1 px-2 text-white bg-dark"; // Darker theme for parts
    li.style.fontSize = "0.9em";
    li.textContent = "." + part; // e.g., .macd
    li.onmousedown = (e) => {
      e.preventDefault();
      insertAtCursor(queryInputTextarea, "." + part); // Insert the selected part
      suggestionBox.style.display = "none";
    };
    suggestionBox.appendChild(li);
  });

  // Position suggestion box (could be improved to be right after the indicator)
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

// --- Data Fetching & Initial Rendering ---
function setDefaultIndicatorsFallback() {
  console.warn(
    "Using fallback indicator definitions. API might be down or misconfigured."
  );
  // Define a minimal set of indicators if API fails
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
      }, // Added STOCH
    ],
  };
  INDICATORS = []; // Reset and repopulate
  Object.values(INDICATOR_GROUPS).forEach((group) => {
    if (Array.isArray(group)) {
      group.forEach((ind) => {
        ind.params = ind.params || getImplicitParams(ind.value) || []; // Ensure params array exists
        INDICATORS.push(ind);
      });
    }
  });
}

function fetchIndicatorsAndRender() {
  fetch("/screener/api/indicators/")
    .then((response) => {
      if (!response.ok) {
        // If HTTP error, try to get text, then throw
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
            // Ensure group is an array
            group.forEach((indicator) => {
              // Ensure each indicator has a 'params' array, even if empty
              indicator.params =
                indicator.params || getImplicitParams(indicator.value) || [];
              INDICATORS.push(indicator);
            });
          }
        });
        if (INDICATORS.length === 0) {
          console.warn(
            "API returned groups but no indicators were processed into INDICATORS array. Using fallback."
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
        setDefaultIndicatorsFallback(); // Use fallback if API data is bad
      }
    })
    .catch((error) => {
      console.error("Failed to fetch indicators:", error);
      setDefaultIndicatorsFallback(); // Use fallback on fetch error
    })
    .finally(() => {
      // Populate keywords AFTER INDICATORS array is filled (or from fallback)
      keywords = {}; // Clear and repopulate
      DEFAULT_TIMEFRAMES.forEach(
        (tf) => (keywords[tf.toUpperCase()] = TOKEN_TYPES.TIME_FRAME)
      );
      DEFAULT_FIELDS.forEach(
        (f) => (keywords[f.toUpperCase()] = TOKEN_TYPES.FIELD)
      );
      INDICATORS.forEach(
        (ind) =>
          (keywords[ind.value.toUpperCase()] = TOKEN_TYPES.INDICATOR_NAME)
      );
      keywords["AND"] = TOKEN_TYPES.OPERATOR_LOGICAL;
      keywords["OR"] = TOKEN_TYPES.OPERATOR_LOGICAL;
      console.log("Keywords populated:", keywords); // Debugging

      renderIndicatorModalList(); // Render the list in the modal regardless of success/failure
    });
}

function renderIndicatorModalList() {
  if (!indicatorListUl || !indicatorSearchInput) return;
  const searchTerm = indicatorSearchInput.value.toLowerCase();
  indicatorListUl.innerHTML = ""; // Clear previous list

  if (Object.keys(INDICATOR_GROUPS).length > 0) {
    Object.entries(INDICATOR_GROUPS).forEach(
      ([groupName, indicatorsInGroup]) => {
        if (!Array.isArray(indicatorsInGroup)) return; // Skip if not an array
        const filteredIndicators = indicatorsInGroup.filter(
          (ind) =>
            ind.label.toLowerCase().includes(searchTerm) ||
            ind.value.toLowerCase().includes(searchTerm)
        );
        if (filteredIndicators.length > 0) {
          const groupHeaderLi = document.createElement("li");
          groupHeaderLi.className =
            "list-group-item list-group-item-secondary fw-bold"; // Bootstrap classes
          groupHeaderLi.textContent = groupName;
          groupHeaderLi.style.background = "#232b3b"; // Darker background for group header
          groupHeaderLi.style.color = "#5eead4"; // Teal color for group header text
          indicatorListUl.appendChild(groupHeaderLi);
          filteredIndicators.forEach((indicatorDef) => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-action"; // Bootstrap classes
            li.innerHTML = `<span style="font-size:1.1em;" class="me-2">📊</span> ${indicatorDef.label}`; // Icon + Label
            li.addEventListener("click", () => {
              if (indicatorModalInstance) indicatorModalInstance.hide(); // Hide selection modal
              selectIndicatorFromSuggestion(indicatorDef, queryInputTextarea); // Proceed to config
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
// This is a simplified Pratt Parser (Top-Down Operator Precedence)
/**
 * transformQueryStringToBackendStructure
 *
 * Parses a user-entered query string (e.g. "(Daily SMA(CLOSE(), 14) > Daily SMA(CLOSE(), 50)) AND (15min RSI(CLOSE(), 14) > 60)")
 * into a JSON-like AST suitable for calling your backend.  This version correctly tokenizes timeframes like "15min" or "1h"
 * as a single TIME_FRAME token instead of splitting them into NUMBER + IDENTIFIER.
 */
function transformQueryStringToBackendStructure(queryString) {
  console.log("Starting transformation of query string:", queryString);
  const tokens = [];
  let cursor = 0;
  // `keywords` is assumed to be a global mapping populated elsewhere, e.g.:
  //   keywords = {
  //     "SMA": TOKEN_TYPES.INDICATOR_NAME,
  //     "RSI": TOKEN_TYPES.INDICATOR_NAME,
  //     "DAILY": TOKEN_TYPES.TIME_FRAME,
  //     "15MIN": TOKEN_TYPES.TIME_FRAME,
  //     // …and so on for all supported timeframes and indicator names…
  //   };

  // Define operators and their types for symbol-based tokenization
  const symbolOperators = {
    ">=": TOKEN_TYPES.OPERATOR_COMPARISON,
    "<=": TOKEN_TYPES.OPERATOR_COMPARISON,
    "==": TOKEN_TYPES.OPERATOR_COMPARISON,
    ">": TOKEN_TYPES.OPERATOR_COMPARISON,
    "<": TOKEN_TYPES.OPERATOR_COMPARISON,
    "(": TOKEN_TYPES.BRACKET_OPEN,
    ")": TOKEN_TYPES.BRACKET_CLOSE,
    ",": TOKEN_TYPES.COMMA,
  };

  // Multi-word symbol operators (like "CROSSES ABOVE", "CROSSES BELOW")
  const multiWordSymbolOperators = {
    "CROSSES ABOVE": TOKEN_TYPES.OPERATOR_COMPARISON,
    "CROSSES BELOW": TOKEN_TYPES.OPERATOR_COMPARISON,
  };
  const sortedMultiWordSymbolOps = Object.keys(multiWordSymbolOperators).sort(
    (a, b) => b.length - a.length
  );

  // Lexer: Tokenize the input string
  while (cursor < queryString.length) {
    let char = queryString[cursor];
    let tokenizedThisPass = false;

    // 1) Skip whitespace
    if (/\s/.test(char)) {
      cursor++;
      continue;
    }

    // 2) Try matching multi-word symbol operators first (e.g. "CROSSES ABOVE")
    for (const op of sortedMultiWordSymbolOps) {
      if (
        queryString.substring(cursor, cursor + op.length).toUpperCase() ===
        op.toUpperCase()
      ) {
        tokens.push({ type: multiWordSymbolOperators[op], value: op });
        cursor += op.length;
        tokenizedThisPass = true;
        break;
      }
    }
    if (tokenizedThisPass) continue;

    // 3) Try matching two-character symbol operators (e.g. ">=", "<=", "==", "!=")
    let twoCharOp = queryString.substring(cursor, cursor + 2);
    if (symbolOperators[twoCharOp]) {
      tokens.push({ type: symbolOperators[twoCharOp], value: twoCharOp });
      cursor += 2;
      continue;
    }

    // 4) Try matching single-character symbol operators (e.g. ">", "<", "(", ")", ",")
    if (symbolOperators[char]) {
      tokens.push({ type: symbolOperators[char], value: char });
      cursor++;
      continue;
    }

    // 5) MATCH TIME_FRAME (e.g. "1min", "5min", "15min", "30min", "1h", "4h", "daily", "weekly", "monthly")
    //    This must come BEFORE matching pure numbers, because otherwise "15min" would tokenize as NUMBER(15) + IDENTIFIER("min").
    {
      const rest = queryString.slice(cursor);
      // Adjust this regex to match exactly the timeframes your DSL supports.
      const tfMatch = rest.match(
        /^(1min|5min|15min|30min|1h|4h|daily|weekly|monthly)\b/i
      );
      if (tfMatch) {
        const timeframeText = tfMatch[1]; // e.g. "15min" or "daily"
        tokens.push({ type: TOKEN_TYPES.TIME_FRAME, value: timeframeText });
        cursor += timeframeText.length;
        continue;
      }
    }

    // 6) Match numbers (integers and decimals)
    if (/[0-9]/.test(char)) {
      let numStr = "";
      while (
        cursor < queryString.length &&
        /[0-9\.]/.test(queryString[cursor])
      ) {
        numStr += queryString[cursor++];
      }
      tokens.push({ type: TOKEN_TYPES.NUMBER, value: parseFloat(numStr) });
      continue;
    }

    // 7) Match identifiers (indicator names, field names, TIME_FRAME alternatives, AND, OR)
    if (/[a-zA-Z_]/.test(char)) {
      let identifier = "";
      while (
        cursor < queryString.length &&
        /[a-zA-Z0-9_]/.test(queryString[cursor])
      ) {
        identifier += queryString[cursor++];
      }
      const upperIdentifier = identifier.toUpperCase();

      // 7a) Check explicitly for logical operators "AND" / "OR"
      if (upperIdentifier === "AND" || upperIdentifier === "OR") {
        tokens.push({
          type: TOKEN_TYPES.OPERATOR_LOGICAL,
          value: upperIdentifier,
        });
        continue;
      }

      // 7b) Specifically check for FIELD() pattern, e.g., "CLOSE()"
      //     DEFAULT_FIELDS is assumed to be something like ["OPEN","HIGH","LOW","CLOSE","VOLUME"]
      if (
        DEFAULT_FIELDS.includes(upperIdentifier) &&
        queryString[cursor] === "(" &&
        queryString[cursor + 1] === ")"
      ) {
        tokens.push({ type: TOKEN_TYPES.FIELD, value: upperIdentifier }); // field names in uppercase
        tokens.push({ type: TOKEN_TYPES.BRACKET_OPEN, value: "(" });
        tokens.push({ type: TOKEN_TYPES.BRACKET_CLOSE, value: ")" });
        cursor += 2; // consume "()"
        continue;
      }

      // 7c) If it’s a known keyword (Indicator, Field, Timeframe), use that type
      if (keywords[upperIdentifier]) {
        // Example: keywords["SMA"] === TOKEN_TYPES.INDICATOR_NAME
        //          keywords["DAILY"] === TOKEN_TYPES.TIME_FRAME
        let valueToStore = identifier; // preserve original case for indicator/timeframe
        if (keywords[upperIdentifier] === TOKEN_TYPES.FIELD) {
          valueToStore = upperIdentifier; // store field names in uppercase
        }
        tokens.push({
          type: keywords[upperIdentifier],
          value: valueToStore,
        });
        continue;
      }

      // 7d) Otherwise, it's a generic IDENTIFIER (possibly an error or a complex name part)
      tokens.push({ type: TOKEN_TYPES.IDENTIFIER, value: identifier });
      continue;
    }

    // 8) If no other rule matched, emit an ERROR token
    tokens.push({
      type: TOKEN_TYPES.ERROR,
      value: char,
      message: `Unknown character: ${char}`,
    });
    cursor++;
  }

  // Append an EOF token to mark the end of the input
  tokens.push({ type: TOKEN_TYPES.EOF, value: "EOF" });

  console.log("Lexer Tokens:", JSON.parse(JSON.stringify(tokens))); // Deep‐copy for logging

  // --------------------------
  // Parser: Convert token stream into an AST
  // --------------------------
  let currentTokenIndex = 0;

  // Lookahead helper: get the token at currentTokenIndex without consuming it
  const lookahead = () => tokens[currentTokenIndex];

  // Consume helper: advance currentTokenIndex after optionally checking type
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

  // Given an operator token, return its binding power (precedence)
  const getBindingPower = (operatorToken) => {
    if (
      !operatorToken ||
      (operatorToken.type !== TOKEN_TYPES.OPERATOR_COMPARISON &&
        operatorToken.type !== TOKEN_TYPES.OPERATOR_LOGICAL)
    ) {
      return 0;
    }
    const op = operatorToken.value.toUpperCase();
    if (op === "OR") return 10;
    if (op === "AND") return 20;
    if (
      [">", ">=", "<", "<=", "==", "CROSSES ABOVE", "CROSSES BELOW"].includes(
        op
      )
    ) {
      return 30;
    }
    return 0; // default
  };

  // Null Denotation (nud): Handle tokens that appear at the start of an expression
  const nud = (token) => {
    // 1) Number literal
    if (token.type === TOKEN_TYPES.NUMBER) {
      return { type: "NumberLiteral", value: token.value };
    }

    // 2) Field literal, e.g. FIELD() → { type: "FieldLiteral", value: "CLOSE" }
    if (token.type === TOKEN_TYPES.FIELD) {
      // We already consumed the FIELD token itself. Next should be "(" ")" if any.
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

    // 3) TIME_FRAME followed by INDICATOR_NAME(...) or FIELD()
    if (token.type === TOKEN_TYPES.TIME_FRAME) {
      const nextToken = lookahead();

      // 3a) TIME_FRAME + INDICATOR_NAME(...) → IndicatorCall with explicit timeframe
      if (nextToken.type === TOKEN_TYPES.INDICATOR_NAME) {
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
          timeframe: token.value, // e.g. "15min" or "daily"
          arguments: args,
        };
      }

      // 3b) TIME_FRAME + FIELD() → treat as a zero-arg indicator call for that field
      if (nextToken.type === TOKEN_TYPES.FIELD) {
        const fieldToken = consume(TOKEN_TYPES.FIELD);
        if (
          lookahead().type === TOKEN_TYPES.BRACKET_OPEN &&
          tokens[currentTokenIndex + 1] &&
          tokens[currentTokenIndex + 1].type === TOKEN_TYPES.BRACKET_CLOSE
        ) {
          consume(TOKEN_TYPES.BRACKET_OPEN);
          consume(TOKEN_TYPES.BRACKET_CLOSE);
          return {
            type: "IndicatorCall",
            name: fieldToken.value,
            timeframe: token.value,
            arguments: [],
          };
        } else {
          throw new Error(
            `Syntax Error: Expected FIELD() after TimeFrame but found incomplete field expression for '${fieldToken.value}'`
          );
        }
      }

      // 3c) Anything else after TIME_FRAME is an error
      throw new Error(
        `Syntax Error: Expected INDICATOR_NAME or FIELD() after TIME_FRAME but found ${nextToken.type}`
      );
    }

    // 4) INDICATOR_NAME(...) without explicit timeframe → default to "Daily"
    if (token.type === TOKEN_TYPES.INDICATOR_NAME) {
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

    // 5) Parenthesized expression: "(" expr ")"
    if (token.type === TOKEN_TYPES.BRACKET_OPEN) {
      const expr = parseExpression(0);
      consume(TOKEN_TYPES.BRACKET_CLOSE);
      return expr;
    }

    throw new Error(
      `Syntax Error: Unexpected token at start of expression: ${token.type} ('${token.value}')`
    );
  };

  // Left Denotation (led): Handle infix operators (comparison, logical) and parts
  const led = (left, token) => {
    // 1) Logical or comparison operators → produce BinaryExpression or Comparison nodes
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

    // 2) If left is an IndicatorCall and token is an IDENTIFIER that matches a “part” (e.g. "hist" or "line" for MACD),
    //    we attach that part to the left node rather than producing a binary operator.
    if (
      token.type === TOKEN_TYPES.IDENTIFIER &&
      left.type === "IndicatorCall" &&
      INDICATOR_PARTS[left.name.toUpperCase()]?.includes(
        token.value.toLowerCase()
      )
    ) {
      left.part = token.value.toLowerCase();
      return left;
    }

    throw new Error(
      `Syntax Error: Unexpected infix token: ${token.type} ('${token.value}')`
    );
  };

  // Pratt parser main entry: parseExpression with a right-binding power
  const parseExpression = (rightBindingPower) => {
    let token = consume();
    let left = nud(token);

    while (rightBindingPower < getBindingPower(lookahead())) {
      token = consume();
      left = led(left, token);
    }
    return left;
  };

  // Attempt parsing and return either AST or an error object
  try {
    // If all we have is EOF, return null (empty query)
    if (tokens.length === 1 && tokens[0].type === TOKEN_TYPES.EOF) return null;

    const ast = parseExpression(0);

    if (lookahead().type !== TOKEN_TYPES.EOF) {
      throw new Error(
        `Syntax Error: Unexpected tokens remaining after parsing. Next token: '${
          lookahead().value
        }'`
      );
    }

    // If AST is just a literal or single indicator call, that means no actual comparison/logical group → incomplete query
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
      "\nTokens so far:",
      JSON.stringify(tokens.slice(0, currentTokenIndex))
    );
    return {
      type: "PARSE_ERROR",
      error: e.message,
      details: `Error near token: '${
        tokens[currentTokenIndex]?.value || "end of query"
      }'`,
    };
  }
}

// --- AST to Query String Transformation (for loading saved scans) ---
function transformBackendStructureToQueryString(astNode) {
  if (!astNode || !astNode.type) return "";

  switch (astNode.type) {
    case "Comparison":
    case "BinaryExpression":
      const leftStr = transformBackendStructureToQueryString(astNode.left);
      const rightStr = transformBackendStructureToQueryString(astNode.right);
      return `(${leftStr} ${astNode.operator.toUpperCase()} ${rightStr})`;

    case "IndicatorCall":
      let argsString = "";
      if (astNode.arguments && astNode.arguments.length > 0) {
        argsString = astNode.arguments
          .map((arg) => {
            if (
              arg.type === "FieldLiteral" &&
              DEFAULT_FIELDS.includes(arg.value.toUpperCase())
            ) {
              return `${arg.value.toUpperCase()}()`;
            }
            return transformBackendStructureToQueryString(arg);
          })
          .join(", ");
      }

      let timeframePrefix = "";
      if (astNode.timeframe) {
        const tfLower = astNode.timeframe.toLowerCase();
        if (
          tfLower !== "daily" ||
          DEFAULT_FIELDS.includes(astNode.name.toUpperCase())
        ) {
          timeframePrefix =
            astNode.timeframe.charAt(0).toUpperCase() +
            astNode.timeframe.slice(1) +
            " ";
        } else if (
          tfLower === "daily" &&
          !DEFAULT_FIELDS.includes(astNode.name.toUpperCase())
        ) {
          timeframePrefix = "Daily ";
        }
      } else if (!DEFAULT_FIELDS.includes(astNode.name.toUpperCase())) {
        timeframePrefix = "Daily ";
      }

      if (
        DEFAULT_FIELDS.includes(astNode.name.toUpperCase()) &&
        (!astNode.arguments || astNode.arguments.length === 0)
      ) {
        return `${timeframePrefix}${astNode.name.toUpperCase()}()`;
      }

      let indicatorString = `${timeframePrefix}${astNode.name}(${argsString})`;
      if (astNode.part) {
        indicatorString += `.${astNode.part}`;
      }
      return indicatorString;

    case "FieldLiteral":
      if (DEFAULT_FIELDS.includes(astNode.value.toUpperCase())) {
        return `${astNode.value.toUpperCase()}()`;
      }
      return astNode.value;

    case "NumberLiteral":
      return astNode.value.toString();

    default:
      console.warn(
        "Unknown AST node type in transformBackendStructureToQueryString:",
        astNode.type,
        astNode
      );
      return `[Unknown AST: ${astNode.type}]`;
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
  if (upperVal.startsWith("CDL")) return ["timeframe"];

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
    "STOCHRSI",
  ];
  if (periodOnlyImplicitField.includes(upperVal))
    return ["timeframe", "period"];

  const volumeBased = ["OBV", "AD", "ADOSC", "MFI"];
  if (volumeBased.includes(upperVal)) return ["timeframe", "period"];
  return ["timeframe", "field", "period"];
}

// --- Scan Execution & Results ---
function handleRunScan() {
  if (!resultsTableBody || !stockCountSpan || !queryInputTextarea) {
    console.error(
      "Required DOM elements for scan (resultsTableBody, stockCountSpan, queryInputTextarea) are missing."
    );
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
      segment: document.getElementById("segmentDropdown")?.value || "Nifty 500",
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
        resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Error from server: ${data.error}</td></tr>`;
        stockCountSpan.textContent = "Matching Stocks: 0";
      } else if (data.results) {
        updateResultsTable(data.results);
      } else {
        updateResultsTable([]);
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
  resultsTableBody.innerHTML = "";
  if (!results || results.length === 0) {
    resultsTableBody.innerHTML =
      '<tr><td colspan="10" class="text-center py-5" style="color:#6b7280;">No stocks match your scan criteria.</td></tr>';
    stockCountSpan.textContent = "Matching Stocks: 0";
    return;
  }
  stockCountSpan.textContent = `Matching Stocks: ${results.length}`;
  results.forEach((stock, index) => {
    const tr = resultsTableBody.insertRow();
    let cs = "",
      ct = stock.change_pct || "N/A";
    if (typeof ct === "string") {
      const nc = parseFloat(ct.replace("%", ""));
      if (!isNaN(nc)) {
        cs = nc >= 0 ? "color:#34d399;" : "color:#f87171;";
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
