// --- Constants ---
let INDICATORS = []; // Populated by fetchIndicatorsAndRender
let INDICATOR_GROUPS = {}; // Populated by fetchIndicatorsAndRender

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

// --- Token Types for Lexer/Parser ---
const TOKEN_TYPES = {
  NUMBER: "NUMBER",
  IDENTIFIER: "IDENTIFIER", // General identifiers before specific classification
  INDICATOR_NAME: "INDICATOR_NAME",
  TIME_FRAME: "TIME FRAME",
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

// --- Modal Instances (Bootstrap) ---
let indicatorModalInstance, indicatorConfigModalInstance;

// --- DOM Elements ---
const queryInputTextarea = document.getElementById("queryInput");
const suggestionBox = document.createElement("ul");

const devParseButton = document.getElementById("add-filter");
const runScanButton = document.getElementById("runScan");
const clearQueryButton = document.getElementById("clearFiltersButton");

const indicatorSearchInput = document.getElementById("indicatorSearch");
const indicatorListUl = document.getElementById("indicatorList");

// Indicator Config Modal Elements (as before)
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
  indicatorModalInstance = new bootstrap.Modal(
    document.getElementById("indicatorModal")
  );
  indicatorConfigModalInstance = new bootstrap.Modal(
    document.getElementById("indicatorConfigModal")
  );

  suggestionBox.id = "autocompleteSuggestionBox";
  suggestionBox.className = "list-group position-absolute shadow-lg";
  suggestionBox.style.zIndex = "1050";
  suggestionBox.style.maxHeight = "200px";
  suggestionBox.style.overflowY = "auto";
  suggestionBox.style.display = "none";
  if (queryInputTextarea && queryInputTextarea.parentNode) {
    // Ensure textarea exists
    queryInputTextarea.parentNode.insertBefore(
      suggestionBox,
      queryInputTextarea.nextSibling
    );
  } else {
    console.error(
      "Query input textarea not found for suggestion box placement."
    );
  }

  DEFAULT_TIMEFRAMES.forEach((tf) =>
    indicatorConfigTimeframeSelect.options.add(new Option(tf, tf.toLowerCase()))
  );
  DEFAULT_FIELDS.forEach((f) =>
    indicatorConfigFieldSelect.options.add(new Option(f, f.toLowerCase()))
  );

  if (queryInputTextarea) {
    queryInputTextarea.addEventListener("input", handleQueryInputChange);
    queryInputTextarea.addEventListener("keyup", handleQueryInputKeyup);
    queryInputTextarea.addEventListener("blur", () =>
      setTimeout(() => (suggestionBox.style.display = "none"), 200)
    ); // Increased delay
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
          // Assuming parser returns this structure on error
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
  if (indicatorSearchInput)
    indicatorSearchInput.addEventListener("input", renderIndicatorModalList);
  if (indicatorConfigDoneButton)
    indicatorConfigDoneButton.addEventListener(
      "click",
      handleIndicatorConfigDone
    );
  if (runScanButton) runScanButton.addEventListener("click", handleRunScan);
  if (clearQueryButton) {
    clearQueryButton.addEventListener("click", () => {
      if (queryInputTextarea) queryInputTextarea.value = "";
      currentQueryString = "";
      suggestionBox.style.display = "none";
      resultsTableBody.innerHTML =
        '<tr id="initialMessageRow"><td colspan="10" class="text-center py-5">Query cleared.</td></tr>';
      stockCountSpan.textContent = "Matching Stocks: 0";
    });
  }
  fetchIndicatorsAndRender();
});

// --- Autocomplete Logic ---
let currentWordForAutocomplete = "";
let wordStartIndex = 0;

function handleQueryInputChange(event) {
  currentQueryString = event.target.value;
  const cursorPos = event.target.selectionStart;
  let textBeforeCursor = currentQueryString.substring(0, cursorPos);

  const match = textBeforeCursor.match(/(\b[a-zA-Z_][a-zA-Z0-9_]*)$/); // Word can start with letter or _
  if (match) {
    currentWordForAutocomplete = match[1].toUpperCase();
    wordStartIndex = cursorPos - currentWordForAutocomplete.length;

    const suggestions = INDICATORS.filter(
      (ind) =>
        ind.value.toUpperCase().startsWith(currentWordForAutocomplete) ||
        ind.label.toUpperCase().includes(currentWordForAutocomplete) // Broader search in label
    );

    if (suggestions.length > 0 && currentWordForAutocomplete.length >= 1) {
      // Show if word is at least 1 char
      populateSuggestionBox(suggestions, event.target);
    } else {
      suggestionBox.style.display = "none";
    }
  } else {
    currentWordForAutocomplete = "";
    suggestionBox.style.display = "none";
  }
}
function handleQueryInputKeyup(event) {
  if (event.key === "Escape") {
    suggestionBox.style.display = "none";
  }
}

function populateSuggestionBox(suggestions, textarea) {
  suggestionBox.innerHTML = "";
  suggestions.slice(0, 7).forEach((indicatorDef) => {
    // Limit suggestions
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
  const DUMMY_CHAR_WIDTH = 8;
  const DUMMY_LINE_HEIGHT =
    parseFloat(window.getComputedStyle(textarea).lineHeight) || 20;

  // More accurate positioning attempt using a dummy span
  const dummySpan = document.createElement("span");
  dummySpan.style.visibility = "hidden";
  dummySpan.style.position = "absolute";
  dummySpan.style.whiteSpace = "pre"; // Preserve spaces
  dummySpan.style.font = window.getComputedStyle(textarea).font;
  document.body.appendChild(dummySpan);
  dummySpan.textContent = textarea.value.substring(0, wordStartIndex);
  const textCoords = dummySpan.getBoundingClientRect();
  document.body.removeChild(dummySpan);

  suggestionBox.style.left = `${
    textarea.offsetLeft + (textCoords.width % textarea.clientWidth)
  }px`;
  suggestionBox.style.top = `${
    textarea.offsetTop +
    textCoords.height +
    DUMMY_LINE_HEIGHT -
    textarea.scrollTop
  }px`; // Adjust for scroll
  suggestionBox.style.width =
    textarea.clientWidth > 300 ? "300px" : `${textarea.clientWidth}px`;
  suggestionBox.style.display = suggestions.length > 0 ? "block" : "none";
}

function selectIndicatorFromSuggestion(indicatorDef, textarea) {
  activeIndicatorForConfig = {
    name: indicatorDef.value,
    label: indicatorDef.label,
    paramsFromDef: indicatorDef.params || getImplicitParams(indicatorDef.value),
  };
  lastCursorPosition = wordStartIndex;
  openIndicatorConfigModal();
}

function openIndicatorConfigModal() {
  /* ... same as before ... */
  if (!activeIndicatorForConfig) {
    console.error("No indicator selected for configuration.");
    return;
  }
  indicatorConfigModalLabel.textContent = `Configure: ${activeIndicatorForConfig.label}`;
  const indicatorDefinedParams = activeIndicatorForConfig.paramsFromDef;
  indicatorConfigTimeframeSelect.value = "daily";
  const setupField = (paramKey, groupEl, inputEl, defaultValue) => {
    if (indicatorDefinedParams.includes(paramKey)) {
      groupEl.style.display = "block";
      inputEl.value = defaultValue;
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

function handleIndicatorConfigDone() {
  /* ... same as before, constructs indicatorString and inserts it ... */
  if (!activeIndicatorForConfig) {
    indicatorConfigModalInstance.hide();
    return;
  }
  const configuredParams = { timeframe: indicatorConfigTimeframeSelect.value };
  const definedParams = activeIndicatorForConfig.paramsFromDef;
  const readParam = (key, groupEl, inputEl, isNum = true, isFlt = false) => {
    if (definedParams.includes(key) && groupEl.style.display !== "none") {
      let val = inputEl.value;
      if (inputEl.type === "select-one" && key !== "timeframe")
        val = val.toLowerCase();
      else if (isNum) val = isFlt ? parseFloat(val) : parseInt(val, 10);
      if (!(isNum && isNaN(val))) configuredParams[key] = val;
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

  let indicatorString = `${
    configuredParams.timeframe.charAt(0).toUpperCase() +
    configuredParams.timeframe.slice(1)
  } ${activeIndicatorForConfig.name}(`; // Capitalize timeframe
  const paramValues = [];
  // Attempt to maintain a somewhat standard order for common params
  if (
    activeIndicatorForConfig.paramsFromDef.includes("field") &&
    configuredParams.field
  )
    paramValues.push(configuredParams.field.toUpperCase()); // Fields often uppercase
  if (
    activeIndicatorForConfig.paramsFromDef.includes("period") &&
    configuredParams.period
  )
    paramValues.push(configuredParams.period);
  if (
    activeIndicatorForConfig.paramsFromDef.includes("fast_period") &&
    configuredParams.fast_period
  )
    paramValues.push(configuredParams.fast_period);
  if (
    activeIndicatorForConfig.paramsFromDef.includes("slow_period") &&
    configuredParams.slow_period
  )
    paramValues.push(configuredParams.slow_period);
  if (
    activeIndicatorForConfig.paramsFromDef.includes("signal_period") &&
    configuredParams.signal_period
  )
    paramValues.push(configuredParams.signal_period);
  if (
    activeIndicatorForConfig.paramsFromDef.includes("nbdev") &&
    configuredParams.nbdev
  )
    paramValues.push(configuredParams.nbdev);
  if (
    activeIndicatorForConfig.paramsFromDef.includes("multiplier") &&
    configuredParams.multiplier
  )
    paramValues.push(configuredParams.multiplier);
  // Add any other params that were defined and configured but not explicitly ordered above
  definedParams.forEach((pKey) => {
    if (
      ![
        "timeframe",
        "field",
        "period",
        "fast_period",
        "slow_period",
        "signal_period",
        "nbdev",
        "multiplier",
      ].includes(pKey) &&
      configuredParams[pKey] !== undefined
    ) {
      paramValues.push(configuredParams[pKey]);
    }
  });
  indicatorString += paramValues.join(", ") + ")";

  const currentText = queryInputTextarea.value;
  const textBefore = currentText.substring(0, lastCursorPosition);
  const textAfterAutocompleteWord = currentText.substring(
    lastCursorPosition + currentWordForAutocomplete.length
  );
  queryInputTextarea.value =
    textBefore + indicatorString + " " + textAfterAutocompleteWord; // Add a space after
  currentQueryString = queryInputTextarea.value;
  queryInputTextarea.focus();
  const newCursorPos = textBefore.length + indicatorString.length + 1;
  queryInputTextarea.setSelectionRange(newCursorPos, newCursorPos);
  activeIndicatorForConfig = null;
  indicatorConfigModalInstance.hide();
}

function setDefaultIndicatorsFallback() {
  /* ... same as before ... */
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
  Object.values(INDICATOR_GROUPS).forEach((group) =>
    group.forEach((ind) => {
      ind.params = ind.params || getImplicitParams(ind.value);
      INDICATORS.push(ind);
    })
  );
  console.warn("Using fallback indicator definitions.");
}
function fetchIndicatorsAndRender() {
  /* ... same as before ... */
  fetch("/screener/api/indicators/")
    .then((r) => (r.ok ? r.json() : Promise.reject(r.statusText || r.status)))
    .then((d) => {
      if (
        d &&
        d.groups &&
        typeof d.groups === "object" &&
        Object.keys(d.groups).length > 0
      ) {
        INDICATOR_GROUPS = d.groups;
        INDICATORS = [];
        Object.values(INDICATOR_GROUPS).forEach((g) => {
          if (Array.isArray(g))
            g.forEach((i) => {
              i.params = i.params || getImplicitParams(i.value);
              INDICATORS.push(i);
            });
        });
        if (INDICATORS.length === 0) setDefaultIndicatorsFallback();
        else console.log("Indicators loaded:", INDICATORS.length);
      } else {
        setDefaultIndicatorsFallback();
        console.error("Bad API data for indicators:", d);
      }
    })
    .catch((e) => {
      setDefaultIndicatorsFallback();
      console.error("Fetch indicators error:", e);
    })
    .finally(() => {
      renderIndicatorModalList();
    });
}
function renderIndicatorModalList() {
  /* ... same as before, for the full picker modal ... */
  const searchTerm = indicatorSearchInput.value.toLowerCase();
  indicatorListUl.innerHTML = "";
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
          groupHeaderLi.style.background = "#232b3b";
          groupHeaderLi.style.color = "#5eead4";
          indicatorListUl.appendChild(groupHeaderLi);
          filteredIndicators.forEach((indicatorDef) => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-action";
            li.innerHTML = `<span style="font-size:1.1em;" class="me-2">📊</span> ${indicatorDef.label}`;
            li.addEventListener("click", () => {
              indicatorModalInstance.hide();
              selectIndicatorFromSuggestion(indicatorDef, queryInputTextarea);
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

// --- PARSER: Query String to Backend Structure ---
function transformQueryStringToBackendStructure(queryString) {
  console.log("Starting transformation of query string:", queryString);

  // --- 1. Lexer (Tokenizer) ---
  const tokens = [];
  let cursor = 0;

  // Keywords and Operators Definitions
  const keywords = {};
  DEFAULT_TIMEFRAMES.forEach(
    (tf) => (keywords[tf.toUpperCase()] = TOKEN_TYPES.TIME_FRAME)
  );
  DEFAULT_FIELDS.forEach(
    (f) => (keywords[f.toUpperCase()] = TOKEN_TYPES.FIELD)
  );
  INDICATORS.forEach(
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
  // Sort multi-word operators by length descending to match longest first
  const sortedMultiWordOps = Object.keys(operators)
    .filter((op) => op.includes(" "))
    .sort((a, b) => b.length - a.length);

  while (cursor < queryString.length) {
    let char = queryString[cursor];
    let tokenized = false;

    if (/\s/.test(char)) {
      cursor++;
      continue;
    } // Skip whitespace

    // Try matching multi-word operators first
    for (const op of sortedMultiWordOps) {
      if (queryString.substring(cursor).toUpperCase().startsWith(op)) {
        tokens.push({ type: operators[op], value: op });
        cursor += op.length;
        tokenized = true;
        break;
      }
    }
    if (tokenized) continue;

    // Single/double character operators
    let twoCharOp = queryString.substring(cursor, cursor + 2);
    if (operators[twoCharOp]) {
      tokens.push({ type: operators[twoCharOp], value: twoCharOp });
      cursor += 2;
      continue;
    }
    if (operators[char]) {
      tokens.push({ type: operators[char], value: char });
      cursor++;
      continue;
    }

    // Numbers
    if (/[0-9]/.test(char)) {
      let numStr = "";
      while (
        cursor < queryString.length &&
        /[0-9\.]/.test(queryString[cursor])
      ) {
        numStr += queryString[cursor++];
      }
      const numVal = parseFloat(numStr);
      if (isNaN(numVal)) {
        tokens.push({
          type: TOKEN_TYPES.ERROR,
          value: numStr,
          message: `Invalid number format: ${numStr}`,
        });
      } else {
        tokens.push({ type: TOKEN_TYPES.NUMBER, value: numVal });
      }
      continue;
    }

    // Identifiers (Indicators, Timeframes, Fields)
    if (/[a-zA-Z_]/.test(char)) {
      let identifier = "";
      while (
        cursor < queryString.length &&
        /[a-zA-Z0-9_]/.test(queryString[cursor])
      ) {
        identifier += queryString[cursor++];
      }
      const upperIdentifier = identifier.toUpperCase();
      if (keywords[upperIdentifier]) {
        tokens.push({ type: keywords[upperIdentifier], value: identifier }); // Store original case for INDICATOR_NAME
      } else {
        // This could be an error, or a part of a multi-word op not yet fully typed
        tokens.push({ type: TOKEN_TYPES.IDENTIFIER, value: identifier });
      }
      continue;
    }

    tokens.push({
      type: TOKEN_TYPES.ERROR,
      value: char,
      message: `Unknown character: ${char}`,
    });
    cursor++; // Move past unknown char
  }
  tokens.push({ type: TOKEN_TYPES.EOF, value: "EOF" });
  console.log("Lexer Tokens:", JSON.parse(JSON.stringify(tokens))); // Deep copy for logging

  // --- 2. Parser (Pratt Parser Implementation) ---
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
    return 0; // Default for non-operators or lowest precedence
  };

  // NUD: Null Denotation (for prefixes, literals, grouping)
  const nud = (token) => {
    if (token.type === TOKEN_TYPES.NUMBER) {
      return { type: "NumberLiteral", value: token.value };
    }
    if (token.type === TOKEN_TYPES.FIELD) {
      // e.g., CLOSE inside indicator params
      return { type: "FieldLiteral", value: token.value };
    }
    if (token.type === TOKEN_TYPES.TIME_FRAME) {
      // Expect an indicator name next
      const indicatorNameToken = lookahead();
      if (indicatorNameToken.type === TOKEN_TYPES.INDICATOR_NAME) {
        consume(TOKEN_TYPES.INDICATOR_NAME);
        // Now parse the indicator call (name, timeframe, args)
        consume(TOKEN_TYPES.BRACKET_OPEN);
        const args = [];
        if (lookahead().type !== TOKEN_TYPES.BRACKET_CLOSE) {
          while (true) {
            args.push(parseExpression(0)); // Parse each argument as an expression
            if (lookahead().type === TOKEN_TYPES.BRACKET_CLOSE) break;
            consume(TOKEN_TYPES.COMMA);
          }
        }
        consume(TOKEN_TYPES.BRACKET_CLOSE);
        return {
          type: "IndicatorCall",
          name: indicatorNameToken.value,
          timeframe: token.value,
          arguments: args,
        };
      } else {
        throw new Error(
          `Syntax Error: Expected INDICATOR_NAME after TIME_FRAME '${token.value}', got ${indicatorNameToken.type}`
        );
      }
    }
    if (token.type === TOKEN_TYPES.INDICATOR_NAME) {
      // Indicator without explicit timeframe (default to Daily)
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
      return expr; // The expression within the brackets
    }
    // Add prefix operators here if needed (e.g., NOT)
    throw new Error(
      `Syntax Error: Unexpected token at start of expression: ${token.type} ('${token.value}')`
    );
  };

  // LED: Left Denotation (for infix operators)
  const led = (left, token) => {
    if (token.type === TOKEN_TYPES.OPERATOR_COMPARISON) {
      const right = parseExpression(getBindingPower(token));
      return {
        type: "Comparison",
        operator: token.value,
        left: left,
        right: right,
      };
    }
    if (token.type === TOKEN_TYPES.OPERATOR_LOGICAL) {
      const right = parseExpression(getBindingPower(token));
      return {
        type: "BinaryExpression",
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
    let token = consume(); // Consume the first token for the current expression part
    let left = nud(token);

    while (rightBindingPower < getBindingPower(lookahead())) {
      token = consume(); // Consume the operator
      left = led(left, token);
    }
    return left;
  };

  try {
    if (tokens.length === 1 && tokens[0].type === TOKEN_TYPES.EOF) return null; // Empty query
    const ast = parseExpression(0);
    if (lookahead().type !== TOKEN_TYPES.EOF) {
      throw new Error(
        `Syntax Error: Unexpected tokens remaining after parsing: ${JSON.stringify(
          tokens.slice(currentTokenIndex)
        )}`
      );
    }
    // The final AST structure should ideally be a single root node (e.g. a BinaryExpression or a Comparison)
    // If it's just an IndicatorCall or NumberLiteral, it's an incomplete query for the backend.
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
      JSON.stringify(tokens.slice(0, currentTokenIndex + 1))
    );
    return {
      type: "PARSE_ERROR",
      error: e.message,
      details: `Error near token: '${
        tokens[currentTokenIndex - 1]?.value || "start"
      }'`,
    };
  }
}

// --- Utilities (getCookie, getImplicitParams same as before) ---
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
function getImplicitParams(val) {
  if (val.toUpperCase().startsWith("CDL")) return ["timeframe"];
  const nf = [
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
  if (nf.includes(val.toUpperCase())) return ["timeframe", "period"];
  return ["timeframe", "field", "period"];
}

// --- Scan Execution & Results ---
function handleRunScan() {
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
      // Option 1: Send raw string and parse on backend (safer if client parser is not fully trusted)
      // query_string: currentQueryString,
      filters: backendPayload, // Option 2: Send client-parsed structure
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
        resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Error from server: ${data.error}</td></tr>`;
        stockCountSpan.textContent = "Matching Stocks: 0";
      } else if (data.results) updateResultsTable(data.results);
      else updateResultsTable([]);
    })
    .catch((error) => {
      resultsTableBody.innerHTML = `<tr><td colspan="10" class="text-center py-5 text-danger">Network or Scan Error: ${
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
        cs = nc >= 0 ? "color:#34d399;" : "color:#f87171;";
        ct = `${nc.toFixed(2)}%`;
      }
    }
    const f = (n, d = 2) =>
      typeof n === "number" ||
      (typeof n === "string" && n !== "" && !isNaN(Number(n)))
        ? Number(n).toFixed(d)
        : n || "N/A";
    tr.innerHTML = `<td>${
      index + 1
    }</td><td class="fw-medium" style="color:#a78bfa;">${
      stock.symbol || "N/A"
    }</td><td>${stock.timestamp || "N/A"}</td><td>${f(stock.open)}</td><td>${f(
      stock.high
    )}</td><td>${f(stock.low)}</td><td>${f(
      stock.close
    )}</td><td style="${cs}">${ct}</td><td>${f(
      stock.volume,
      0
    )}</td><td><button type="button" class="icon-btn text-info btn-sm" title="View Chart"><i class="fas fa-chart-line"></i></button><button type="button" class="icon-btn text-primary btn-sm" title="Add to Watchlist"><i class="fas fa-plus-square"></i></button></td>`;
  });
}
