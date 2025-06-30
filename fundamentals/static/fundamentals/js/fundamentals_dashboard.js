/**
 * Global function to handle clicks on peer company links within the deep-dive view.
 * This is placed on the window scope to be accessible from `onclick` attributes in dynamically generated HTML.
 * @param {string} symbol - The stock symbol of the peer company to load.
 */
window.handlePeerClick = function (symbol) {
  // Find the corresponding company in the sidebar list to highlight it
  const companyLink = document.querySelector(
    `#company-list a[data-symbol="${symbol}"]`
  );
  if (companyLink) {
    // Remove highlight from all other company links in the sidebar
    document
      .querySelectorAll("#company-list li a")
      .forEach((a) => a.classList.remove("bg-gray-700"));
    // Add highlight to the newly selected company
    companyLink.classList.add("bg-gray-700");
    // Scroll the sidebar to make the newly selected company visible
    companyLink.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  // Fetch and render the data for the clicked peer (deep-dive view)
  fetchCompanyDeepDiveData(symbol);
};

document.addEventListener("DOMContentLoaded", function () {
  // --- 1. DOM Element References ---
  const searchInput = document.getElementById("search-input");
  const companyList = document.getElementById("company-list");
  const loadingSpinner = document.getElementById("loading-spinner");
  const errorMessageDiv = document.getElementById("error-message");
  const errorMessageText = document.getElementById("error-message-text");

  const fundamentalScreenerContent = document.getElementById(
    "fundamental-screener-content"
  );
  const deepDiveContent = document.getElementById("deep-dive-content");

  // --- 2. State Cache ---
  let allCompaniesCache = []; // Cache for the flat sidebar list of all companies
  let fundamentalScreenerDataCache = null; // Cache for the categorized fundamental screener data

  // --- 3. Utility Functions ---

  /**
   * Helper for consistent number formatting.
   * @param {*} value - The value to format.
   * @param {number} decimals - Number of decimal places.
   * @returns {string} Formatted number or "-".
   */
  const formatNumber = (value, decimals = 2) => {
    const num = Number(String(value).replace(/,/g, ""));
    if (value === null || value === undefined || isNaN(num)) return "-";
    return num.toLocaleString("en-IN", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  /**
   * Formatter for percentage values.
   * @param {*} value - The value to format.
   * @returns {string} Formatted percentage or "-".
   */
  const formatPercentage = (value) =>
    value === null || value === undefined ? "-" : `${formatNumber(value)}%`;

  /**
   * Formatter for market capitalization in Crores.
   * @param {*} value - The value to format (expected in raw numbers, e.g., 100000000).
   * @returns {string} Formatted value with " Cr." suffix or "-".
   */
  const formatMarketCap = (value) => {
    const num = Number(String(value).replace(/,/g, ""));
    if (value === null || value === undefined || isNaN(num) || num === 0)
      return "-";
    return `${formatNumber(num / 10 ** 7, 2)} Cr.`; // Convert to Crores
  };

  /**
   * Formatter for Rupee values.
   * @param {*} value - The value to format.
   * @returns {string} Formatted Rupee value or "-".
   */
  const formatRupee = (value) =>
    value === null || value === undefined ? "-" : `₹${formatNumber(value)}`;

  /**
   * Displays a generic empty state message.
   * @param {string} message - Message to display.
   * @param {string} icon - Font Awesome icon class.
   * @returns {string} HTML for the empty state.
   */
  const createEmptyState = (
    message = "No Data Available",
    icon = "fa-table"
  ) => {
    return `<div class="text-center text-gray-500 p-8"><i class="fas ${icon} fa-2x mb-3"></i><p>${message}</p></div>`;
  };

  /**
   * Safely parses JSON string.
   * @param {string} jsonString - The JSON string to parse.
   * @param {*} fallback - Fallback value if parsing fails.
   * @returns {object} Parsed JSON object or fallback.
   */
  const safeJsonParse = (jsonString, fallback = null) => {
    if (typeof jsonString !== "string") return jsonString; // Already an object
    try {
      return JSON.parse(jsonString);
    } catch (e) {
      console.error("JSON parsing error:", e);
      return fallback;
    }
  };

  /**
   * Transforms financial data from a raw JSON format (headers/body) into a list of objects.
   * @param {object} financialData - Financial data with 'headers' and 'body' properties.
   * @returns {Array<object>} Transformed data.
   */
  const transformFinancialData = (financialData) => {
    // Ensure financialData is an object and has headers and body
    if (
      !financialData ||
      typeof financialData !== "object" ||
      !financialData.headers ||
      !financialData.body
    ) {
      return [];
    }
    const { headers, body } = financialData;
    return body.map((row) => {
      const rowObject = { Description: row.Description };
      headers.forEach((header, index) => {
        rowObject[header] = row.values[index];
      });
      return rowObject;
    });
  };

  /**
   * Creates an HTML unordered list from an array of items.
   * @param {Array<string>} items - List items.
   * @param {'pros' | 'cons'} type - Type of list (for styling).
   * @returns {string} HTML for the list.
   */
  const createDescriptiveList = (items, type) => {
    if (!items || items.length === 0)
      return `<p class="text-sm text-gray-500">No ${type} available.</p>`;
    const color = type === "pros" ? "text-green-600" : "text-red-600";
    const icon = type === "pros" ? "fa-circle-check" : "fa-circle-xmark";
    return `<ul class="space-y-2">${items
      .map(
        (item) =>
          `<li class="flex items-start"><i class="fas ${icon} ${color} mt-1 mr-2 text-xs"></i><span class="text-sm text-gray-700">${item}</span></li>`
      )
      .join("")}</ul>`;
  };

  /**
   * Creates a generic HTML table for financial data.
   * @param {object} config - Table configuration (e.g., columns).
   * @param {Array<object>} data - Table data.
   * @returns {string} HTML for the table.
   */
  const createTable = (config, data) => {
    if (!data || data.length === 0)
      return createEmptyState("No data for this table.");

    const headers = config.columns.map((col) => col.title);
    const headerHtml = headers
      .map(
        (header) =>
          `<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">${header}</th>`
      )
      .join("");

    const bodyHtml = data
      .map((row) => {
        const cellsHtml = config.columns
          .map((col) => {
            const value = row[col.key];
            // Apply specific formatters based on column key or default
            let formattedValue;
            if (col.key.includes("Y")) {
              // Assuming 'Y' for year columns in financial statements
              formattedValue = formatNumber(value, 0); // No decimals for years/large numbers
            } else if (col.key === "Description") {
              formattedValue = value;
            } else {
              formattedValue = formatNumber(value);
            }
            return `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${formattedValue}</td>`;
          })
          .join("");
        return `<tr class="border-b border-gray-200 hover:bg-gray-50">${cellsHtml}</tr>`;
      })
      .join("");

    return `
            <div class="overflow-x-auto shadow rounded-lg mb-4">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>${headerHtml}</tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${bodyHtml}
                    </tbody>
                </table>
            </div>`;
  };

  /**
   * Creates a simple key-value table for growth data or ratios.
   * @param {object} data - Data object (e.g., {'10Y': 15.2, '5Y': 12.0}).
   * @returns {string} HTML for the simple table.
   */
  const createSimpleMetricTable = (data) => {
    if (!data || Object.keys(data).length === 0)
      return createEmptyState("No data available.");
    const rows = Object.entries(data)
      .map(
        ([key, value]) => `
            <tr class="border-b border-gray-200 last:border-b-0">
                <td class="px-6 py-3 whitespace-nowrap text-sm font-medium text-gray-700">${key}</td>
                <td class="px-6 py-3 whitespace-nowrap text-sm text-right text-gray-900">${formatPercentage(
                  value
                )}</td>
            </tr>
        `
      )
      .join("");
    return `
            <div class="overflow-x-auto shadow rounded-lg">
                <table class="min-w-full divide-y divide-gray-200">
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${rows}
                    </tbody>
                </table>
            </div>`;
  };

  /**
   * Transforms raw shareholding data into a table-friendly format.
   * @param {object} obj - Raw shareholding data.
   * @returns {Array<object>} Transformed data.
   */
  const transformShareholdingData = (obj) => {
    if (!obj) return [];
    const tableData = [];
    const allHeaders = new Set();
    for (const holder in obj) {
      for (const date in obj[holder]) {
        allHeaders.add(date);
      }
    }
    const sortedDateHeaders = Array.from(allHeaders).sort(
      (a, b) => new Date(b) - new Date(a)
    ); // Sort dates descending

    for (const holder in obj) {
      const row = { Description: holder }; // Using Description for the holder name
      sortedDateHeaders.forEach((date) => {
        row[date] = obj[holder][date] || "-";
      });
      tableData.push(row);
    }
    return tableData;
  };

  // --- 4. Main Rendering Functions ---

  /**
   * Renders the fundamentally strong companies by market cap and score.
   * @param {object} categorizedCompanies - The structured data for the screener.
   */
  function renderFundamentalScreener(categorizedCompanies) {
    let html = "";
    if (
      !categorizedCompanies ||
      Object.keys(categorizedCompanies).length === 0
    ) {
      fundamentalScreenerContent.innerHTML = createEmptyState(
        "No fundamental data available yet. Please ensure data fetching tasks are running."
      );
      return;
    }

    for (const category in categorizedCompanies) {
      const data = categorizedCompanies[category];
      html += `
                <div class="card p-6">
                    <h2 class="text-2xl font-semibold text-gray-800 mb-4 pb-2 border-b-2 border-indigo-400">${category} Companies</h2>
            `;

      // Render Score 9+ companies
      if (data.score_9_plus && data.score_9_plus.length > 0) {
        html += `
                    <div class="mb-6">
                        <h3 class="section-header px-4 py-2 font-medium rounded-t-lg">
                            Score 9 and Above <span class="text-xs ml-2">(${
                              data.score_9_plus.length
                            } companies)</span>
                        </h3>
                        <div class="overflow-x-auto shadow-md rounded-b-lg">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="table-header bg-gray-50">
                                    <tr>
                                        <th scope="col" class="px-6 py-3">Symbol</th>
                                        <th scope="col" class="px-6 py-3">Name</th>
                                        <th scope="col" class="px-6 py-3">Score</th>
                                        <th scope="col" class="px-6 py-3">P/E</th>
                                        <th scope="col" class="px-6 py-3">D/E</th>
                                        <th scope="col" class="px-6 py-3">ROE</th>
                                        <th scope="col" class="px-6 py-3">ROC</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    ${data.score_9_plus
                                      .map(
                                        (company) => `
                                        <tr class="table-row hover:bg-gray-100 cursor-pointer" data-symbol="${
                                          company.symbol
                                        }">
                                            <td class="px-6 py-4 whitespace-nowrap font-medium text-indigo-600">${
                                              company.symbol
                                            }</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${
                                              company.name
                                            }</td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full score-9-plus">
                                                    ${formatNumber(
                                                      company.fundamental_score,
                                                      1
                                                    )}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatNumber(
                                              company.stock_pe,
                                              1
                                            )}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatNumber(
                                              company.debt_to_equity,
                                              1
                                            )}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatPercentage(
                                              company.roe
                                            )}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatPercentage(
                                              company.roc
                                            )}</td>
                                        </tr>
                                    `
                                      )
                                      .join("")}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
      } else {
        html += `<p class="text-gray-600 text-sm mb-4">No companies with score 9 or above in this category.</p>`;
      }

      // Render Score <8 companies
      if (data.score_8_below && data.score_8_below.length > 0) {
        html += `
                    <div>
                        <h3 class="section-header px-4 py-2 font-medium rounded-t-lg">
                            Score 8 and Below <span class="text-xs ml-2">(${
                              data.score_8_below.length
                            } companies)</span>
                        </h3>
                        <div class="overflow-x-auto shadow-md rounded-b-lg">
                            <table class="min-w-full divide-y divide-gray-200">
                                <thead class="table-header bg-gray-50">
                                    <tr>
                                        <th scope="col" class="px-6 py-3">Symbol</th>
                                        <th scope="col" class="px-6 py-3">Name</th>
                                        <th scope="col" class="px-6 py-3">Score</th>
                                        <th scope="col" class="px-6 py-3">P/E</th>
                                        <th scope="col" class="px-6 py-3">D/E</th>
                                        <th scope="col" class="px-6 py-3">ROE</th>
                                        <th scope="col" class="px-6 py-3">ROC</th>
                                    </tr>
                                </thead>
                                <tbody class="bg-white divide-y divide-gray-200">
                                    ${data.score_8_below
                                      .map(
                                        (company) => `
                                        <tr class="table-row hover:bg-gray-100 cursor-pointer" data-symbol="${
                                          company.symbol
                                        }">
                                            <td class="px-6 py-4 whitespace-nowrap font-medium text-indigo-600">${
                                              company.symbol
                                            }</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${
                                              company.name
                                            }</td>
                                            <td class="px-6 py-4 whitespace-nowrap">
                                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full score-8-below">
                                                    ${formatNumber(
                                                      company.fundamental_score,
                                                      1
                                                    )}
                                                </span>
                                            </td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatNumber(
                                              company.stock_pe,
                                              1
                                            )}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatNumber(
                                              company.debt_to_equity,
                                              1
                                            )}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatPercentage(
                                              company.roe
                                            )}</td>
                                            <td class="px-6 py-4 whitespace-nowrap">${formatPercentage(
                                              company.roc
                                            )}</td>
                                        </tr>
                                    `
                                      )
                                      .join("")}
                                </tbody>
                            </table>
                        </div>
                    </div>
                `;
      } else {
        html += `<p class="text-gray-600 text-sm">No companies with score 8 or below in this category.</p>`;
      }
      html += `</div>`; // Close card
    }
    fundamentalScreenerContent.innerHTML = html;

    // Add event listeners to newly rendered table rows for deep dive
    fundamentalScreenerContent
      .querySelectorAll(".table-row[data-symbol]")
      .forEach((row) => {
        row.addEventListener("click", (event) => {
          const symbol = row.dataset.symbol;
          // Highlight corresponding item in sidebar
          const sidebarLink = document.querySelector(
            `#company-list a[data-symbol="${symbol}"]`
          );
          if (sidebarLink) {
            document
              .querySelectorAll("#company-list li a")
              .forEach((a) => a.classList.remove("bg-gray-700"));
            sidebarLink.classList.add("bg-gray-700");
            sidebarLink.scrollIntoView({ behavior: "smooth", block: "center" });
          }
          fetchCompanyDeepDiveData(symbol);
        });
      });
  }

  /**
   * Renders the detailed deep-dive view for a single company.
   * @param {object} data - The detailed data for a single company.
   */
  function renderCompanyDeepDive(data) {
    // Hide the fundamental screener content
    fundamentalScreenerContent.classList.add("hidden");
    // Show the deep dive content
    deepDiveContent.classList.remove("hidden");

    const pros = data.pros || [];
    const cons = data.cons || [];
    const peerComparison = data.peer_comparison || [];
    // Safely parse JSON fields
    const quarterlyResults = transformFinancialData(
      safeJsonParse(data.quarterly_results, { headers: [], body: [] })
    );
    const profitLoss = transformFinancialData(
      safeJsonParse(data.profit_loss_statement, { headers: [], body: [] })
    );
    const balanceSheet = transformFinancialData(
      safeJsonParse(data.balance_sheet, { headers: [], body: [] })
    );
    const cashFlow = transformFinancialData(
      safeJsonParse(data.cash_flow_statement, { headers: [], body: [] })
    );
    const ratios = transformFinancialData(
      safeJsonParse(data.ratios, { headers: [], body: [] })
    );
    const salesGrowth = safeJsonParse(data.compounded_sales_growth, {});
    const profitGrowth = safeJsonParse(data.compounded_profit_growth, {});
    const stockCagr = safeJsonParse(data.stock_price_cagr, {});
    const roe = safeJsonParse(data.return_on_equity, {});
    const shareholding = transformShareholdingData(
      safeJsonParse(data.shareholding_pattern, {})
    );

    const keyMetrics = {
      "Market Cap": formatMarketCap(data.market_cap),
      "Current Price": formatRupee(data.current_price),
      "Stock P/E": formatNumber(data.stock_pe),
      "Book Value": formatRupee(data.book_value),
      "Dividend Yield": formatPercentage(data.dividend_yield),
      ROCE: formatPercentage(data.roce),
      ROE: formatPercentage(data.roe),
      "Face Value": formatRupee(data.face_value),
      "52W High/Low": data.high_low || "-",
    };

    const peerComparisonConfig = {
      columns: [
        { key: "Name", title: "Name" },
        { key: "CMP", title: "CMP", formatter: (val) => formatRupee(val) },
        { key: "P/E", title: "P/E", formatter: (val) => formatNumber(val) },
        {
          key: "Mar Cap",
          title: "Market Cap (Cr)",
          formatter: (val) => formatMarketCap(val),
        },
        {
          key: "Div Yld",
          title: "Div Yld %",
          formatter: (val) => formatPercentage(val),
        },
        {
          key: "ROCE",
          title: "ROCE %",
          formatter: (val) => formatPercentage(val),
        },
        {
          key: "ROE",
          title: "ROE %",
          formatter: (val) => formatPercentage(val),
        },
      ],
    };

    // Helper to dynamically get columns for financial tables (Description + years)
    const getFinancialTableColumns = (d) => {
      if (!d || d.length === 0)
        return [{ key: "Description", title: "Description" }];
      const columns = [{ key: "Description", title: "Description" }];
      // Assuming financial data rows have keys like '2023', '2022', etc.
      const dataKeys = Object.keys(d[0]).filter((key) => key !== "Description");
      dataKeys.sort((a, b) => parseInt(b) - parseInt(a)); // Sort years descending
      dataKeys.forEach((key) => columns.push({ key: key, title: key }));
      return columns;
    };

    let htmlContent = `
            <div class="card p-6 bg-white rounded-xl shadow-lg">
                <div class="flex justify-between items-start">
                    <div>
                        <h1 class="text-3xl font-bold text-gray-800">${
                          data.name || "Company"
                        }</h1>
                        <p class="text-md text-indigo-600">${
                          data.symbol || "SYMBOL"
                        }</p>
                    </div>
                    <a href="${
                      data.website || "#"
                    }" target="_blank" rel="noopener noreferrer" class="text-indigo-600 hover:underline ${
      data.website ? "inline-block" : "hidden"
    }">
                        Visit Website <i class="fas fa-external-link-alt ml-1"></i>
                    </a>
                </div>
                <p class="mt-4 text-gray-700 border-t border-gray-200 pt-4">${
                  data.about || "No description available."
                }</p>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-tachometer-alt fa-icon"></i><span>Key Metrics</span></h2>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 text-center">
                    ${Object.entries(keyMetrics)
                      .map(
                        ([key, value]) => `
                        <div class="p-4 bg-gray-100 rounded-lg shadow-sm">
                            <p class="text-sm font-medium text-gray-500">${key}</p>
                            <p class="text-xl font-semibold text-gray-900 mt-1">${value}</p>
                        </div>
                    `
                      )
                      .join("")}
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div class="card p-6">
                    <h2 class="section-title"><i class="fas fa-thumbs-up fa-icon"></i><span>Pros</span></h2>
                    <div>${createDescriptiveList(pros, "pros")}</div>
                </div>
                <div class="card p-6">
                    <h2 class="section-title"><i class="fas fa-thumbs-down fa-icon"></i><span>Cons</span></h2>
                    <div>${createDescriptiveList(cons, "cons")}</div>
                </div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-users fa-icon"></i><span>Peer Comparison</span></h2>
                <div>${createTable(peerComparisonConfig, peerComparison)}</div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-calendar-alt fa-icon"></i><span>Quarterly Results</span></h2>
                <div>${createTable(
                  { columns: getFinancialTableColumns(quarterlyResults) },
                  quarterlyResults
                )}</div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-file-invoice-dollar fa-icon"></i><span>Profit & Loss</span></h2>
                <div>${createTable(
                  { columns: getFinancialTableColumns(profitLoss) },
                  profitLoss
                )}</div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-balance-scale fa-icon"></i><span>Balance Sheet</span></h2>
                <div>${createTable(
                  { columns: getFinancialTableColumns(balanceSheet) },
                  balanceSheet
                )}</div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-hand-holding-usd fa-icon"></i><span>Cash Flow</span></h2>
                <div>${createTable(
                  { columns: getFinancialTableColumns(cashFlow) },
                  cashFlow
                )}</div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-divide fa-icon"></i><span>Ratios</span></h2>
                <div>${createTable(
                  { columns: getFinancialTableColumns(ratios) },
                  ratios
                )}</div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                <div class="card p-6">
                    <h2 class="section-title"><i class="fas fa-chart-line fa-icon"></i><span>Compounded Sales Growth</span></h2>
                    <div>${createSimpleMetricTable(salesGrowth)}</div>
                </div>
                <div class="card p-6">
                    <h2 class="section-title"><i class="fas fa-chart-area fa-icon"></i><span>Compounded Profit Growth</span></h2>
                    <div>${createSimpleMetricTable(profitGrowth)}</div>
                </div>
                <div class="card p-6">
                    <h2 class="section-title"><i class="fas fa-chart-bar fa-icon"></i><span>Stock Price CAGR</span></h2>
                    <div>${createSimpleMetricTable(stockCagr)}</div>
                </div>
                <div class="card p-6">
                    <h2 class="section-title"><i class="fas fa-percentage fa-icon"></i><span>Return on Equity</span></h2>
                    <div>${createSimpleMetricTable(roe)}</div>
                </div>
            </div>

            <div class="card p-6 mt-6">
                <h2 class="section-title"><i class="fas fa-pie-chart fa-icon"></i><span>Shareholding Pattern</span></h2>
                <div>${createTable(
                  { columns: getFinancialTableColumns(shareholding) },
                  shareholding
                )}</div>
            </div>
        `;
    deepDiveContent.innerHTML = htmlContent;
    // Scroll to top of main content area when deep dive is loaded
    deepDiveContent.scrollTop = 0;
  }

  /**
   * Renders the sidebar list of companies.
   * @param {Array<object>} companies - List of company objects.
   */
  function renderSidebarList(companies) {
    companyList.innerHTML = "";
    if (companies.length === 0) {
      companyList.innerHTML = `<li class="p-3 text-sm text-center text-gray-500">No companies found.</li>`;
      return;
    }
    companies.forEach((company) => {
      const li = document.createElement("li");
      li.innerHTML = `
                <a href="#" class="block p-3 text-sm rounded-lg hover:bg-gray-700 text-white" data-symbol="${company.symbol}">
                    <p class="font-semibold text-gray-200 truncate">${company.name}</p>
                    <p class="text-xs text-gray-400">${company.symbol}</p>
                </a>
            `;
      li.addEventListener("click", (e) => {
        e.preventDefault();
        // Remove highlight from previous selection
        document
          .querySelectorAll("#company-list li a")
          .forEach((a) => a.classList.remove("bg-gray-700"));
        // Add highlight to current selection
        e.currentTarget.querySelector("a").classList.add("bg-gray-700");
        fetchCompanyDeepDiveData(company.symbol);
      });
      companyList.appendChild(li);
    });
  }

  // --- 5. Data Fetching & UI Management ---

  /**
   * Shows the loading spinner and hides content/errors.
   */
  function showLoading() {
    loadingSpinner.classList.remove("hidden");
    fundamentalScreenerContent.classList.add("hidden");
    deepDiveContent.classList.add("hidden");
    errorMessageDiv.classList.add("hidden");
  }

  /**
   * Shows an error message.
   * @param {string} message - The error message to display.
   */
  function showError(message) {
    loadingSpinner.classList.add("hidden");
    fundamentalScreenerContent.classList.add("hidden");
    deepDiveContent.classList.add("hidden");
    errorMessageText.textContent = message;
    errorMessageDiv.classList.remove("hidden");
  }

  /**
   * Fetches and renders the fundamental screener data.
   */
  async function fetchAndRenderFundamentalScreener() {
    showLoading();
    try {
      const response = await fetch("/fundamentals/api/fundamental-screener/");
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }
      const data = await response.json();
      fundamentalScreenerDataCache = data; // Cache the data
      renderFundamentalScreener(data);
      fundamentalScreenerContent.classList.remove("hidden"); // Show content
    } catch (error) {
      console.error("Error fetching fundamental screener data:", error);
      showError(`Failed to load fundamental screener data: ${error.message}`);
    } finally {
      loadingSpinner.classList.add("hidden");
    }
  }

  /**
   * Fetches and renders the deep-dive data for a specific company.
   * @param {string} symbol - The stock symbol.
   */
  async function fetchCompanyDeepDiveData(symbol) {
    showLoading();
    try {
      const response = await fetch(`/fundamentals/api/company/${symbol}/`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }
      const data = await response.json();
      renderCompanyDeepDive(data);
    } catch (error) {
      console.error("Error fetching company deep dive data:", error);
      showError(
        `Failed to load deep-dive data for ${symbol}: ${error.message}`
      );
    } finally {
      loadingSpinner.classList.add("hidden");
    }
  }

  /**
   * Fetches the initial list of all companies for the sidebar.
   */
  async function fetchAndRenderSidebarList() {
    try {
      const response = await fetch("/fundamentals/api/companies/");
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! status: ${response.status}`
        );
      }
      const data = await response.json();
      allCompaniesCache = data;
      renderSidebarList(allCompaniesCache);
    } catch (error) {
      console.error("Error fetching sidebar company list:", error);
      companyList.innerHTML = `<li class="p-3 text-sm text-center text-red-500">Could not load company list: ${error.message}</li>`;
    }
  }

  // --- 6. Event Listeners & Initial Calls ---

  // Sidebar search input listener
  searchInput.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    const filteredCompanies = allCompaniesCache.filter(
      (company) =>
        company.name.toLowerCase().includes(searchTerm) ||
        company.symbol.toLowerCase().includes(searchTerm)
    );
    renderSidebarList(filteredCompanies);
  });

  // Initial data fetches on page load
  fetchAndRenderSidebarList(); // Populate the sidebar
  fetchAndRenderFundamentalScreener(); // Populate the main screener view initially
});
