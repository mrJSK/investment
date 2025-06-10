/**
 * Handles clicks on peer company links. Fetches the new company's data.
 * This function is on the window scope to be accessible from `onclick` attributes.
 * @param {string} symbol - The stock symbol of the peer company to load.
 */
window.handlePeerClick = function (symbol) {
  // Find the corresponding company in the main list to highlight it
  const companyLink = document.querySelector(
    `#company-list a[data-symbol="${symbol}"]`
  );
  if (companyLink) {
    document
      .querySelectorAll("#company-list li a")
      .forEach((a) => a.classList.remove("bg-gray-700"));
    companyLink.classList.add("bg-gray-700");
    // Scroll the sidebar to make the newly selected company visible
    companyLink.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  // Fetch and render the data for the clicked peer
  fetchCompanyData(symbol);
};

/**
 * Main function that runs after the DOM is fully loaded.
 */
document.addEventListener("DOMContentLoaded", function () {
  // DOM element references
  const companyList = document.getElementById("company-list");
  const searchInput = document.getElementById("search-input");
  const dataContainer = document.getElementById("data-container");
  const loader = document.getElementById("loader");
  const introMessage = document.getElementById("intro-message");
  let allCompanies = []; // Cache for the full company list

  // --- UTILITY AND FORMATTING FUNCTIONS ---

  const formatters = {
    /** Default formatter: returns value or '-' */
    default: (value) => (value !== null && value !== undefined ? value : "-"),

    /** Formats a number with commas and decimal places. */
    number: (value, row, decimals = 2) => {
      const num = Number(String(value).replace(/,/g, ""));
      if (value === null || value === undefined || isNaN(num)) return "-";
      return num.toLocaleString("en-IN", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
    },

    /** Appends a percentage sign. */
    addPercentage: (value, row) => {
      if (value === null || value === undefined) return "-";
      const num = Number(String(value).replace("%", ""));
      if (isNaN(num)) return "-";
      return `${formatters.number(num, row, 2)}%`;
    },

    /** Appends 'Cr.' for crores. */
    addCr: (value, row) => {
      if (value === null || value === undefined || isNaN(Number(value)))
        return "-";
      return `${formatters.number(value, row)} Cr.`;
    },

    /** Prepends the Rupee symbol. */
    addRupee: (value, row) => {
      if (value === null || value === undefined || isNaN(Number(value)))
        return "-";
      return `₹${formatters.number(value, row)}`;
    },
  };

  /** Creates a placeholder element for when data is not available. */
  function createEmptyState(
    message = "No Data Available",
    iconClass = "fa-table"
  ) {
    return `<div class="text-center text-gray-500 p-8"><i class="fas ${iconClass} fa-2x mb-3"></i><p>${message}</p></div>`;
  }

  /** Safely parses a JSON string; returns the default value on error. */
  function safeJsonParse(jsonString, defaultValue = null) {
    if (typeof jsonString !== "string") return jsonString;
    try {
      return JSON.parse(jsonString);
    } catch (e) {
      console.error("JSON parsing error:", e);
      return defaultValue;
    }
  }

  // --- DYNAMIC ELEMENT CREATION ---

  /** Generic function to create a data table from a config and data array. */
  function createTable(config, data) {
    if (!data || data.length === 0) {
      return createEmptyState();
    }
    const headers = config.columns.map((col) => col.title);
    const headerHtml = headers
      .map(
        (header, index) =>
          `<th class="p-3 text-sm font-semibold text-left ${
            index === 0 ? "sticky left-0 bg-gray-800" : ""
          }">${header}</th>`
      )
      .join("");

    const bodyHtml = data
      .map((row) => {
        const cellsHtml = config.columns
          .map((col, index) => {
            const value = row[col.key];
            const formatter = col.formatter || formatters.default;
            const formattedContent = formatter(value, row); // Pass the whole row
            const isDescription =
              col.key === "Description" ||
              (index === 0 &&
                !config.columns.some((c) => c.key === "Description"));

            return `<td class="p-3 text-sm ${
              isDescription
                ? "sticky left-0 bg-gray-800 font-medium text-left"
                : "text-right"
            }">${formattedContent}</td>`;
          })
          .join("");
        return `<tr class="border-b border-gray-700 hover:bg-gray-700">${cellsHtml}</tr>`;
      })
      .join("");

    return `<div class="overflow-x-auto custom-scrollbar"><table class="min-w-full"><thead class="bg-gray-800"><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`;
  }

  /** Creates a simple two-column table for growth metrics. */
  function createSimpleTable(data) {
    if (!data || Object.keys(data).length === 0) return createEmptyState();
    const rows = Object.entries(data)
      .map(
        ([key, value]) => `
      <tr class="border-b border-gray-700 last:border-b-0">
        <td class="p-3 text-sm font-medium text-gray-300">${key}</td>
        <td class="p-3 text-sm text-right">${formatters.addPercentage(
          value
        )}</td>
      </tr>`
      )
      .join("");
    return `<div class="overflow-x-auto"><table class="min-w-full"><tbody>${rows}</tbody></table></div>`;
  }

  /** Transforms shareholding data into a table-friendly format. */
  function transformShareholdingData(obj) {
    if (!obj) return [];
    const tableData = [];
    const allHeaders = new Set();
    Object.values(obj).forEach((dates) =>
      Object.keys(dates).forEach((date) => allHeaders.add(date))
    );

    const sortedDateHeaders = Array.from(allHeaders).sort(
      (a, b) => new Date(b) - new Date(a)
    );

    for (const holder in obj) {
      const row = { Holder: holder };
      sortedDateHeaders.forEach((date) => {
        row[date] = obj[holder][date] || "-";
      });
      tableData.push(row);
    }
    return tableData;
  }

  /** Creates the shareholding pattern table. */
  function createShareholdingTables(data) {
    if (!data || !data.quarterly || Object.keys(data.quarterly).length === 0) {
      return createEmptyState(undefined, "fa-pie-chart");
    }
    const quarterlyData = data.quarterly;
    const transformedData = transformShareholdingData(quarterlyData);

    const columns = [
      { key: "Holder", title: "Holder", formatter: formatters.default },
      ...Object.keys(transformedData[0])
        .filter((k) => k !== "Holder")
        .map((date) => ({
          key: date,
          title: date,
          formatter: formatters.addPercentage,
        })),
    ];
    return createTable(
      { title: "Shareholding Pattern (Quarterly)", columns },
      transformedData
    );
  }

  /** Creates a list for pros and cons. */
  function createList(items, type) {
    if (!items || items.length === 0)
      return `<p class="text-sm text-gray-500">No ${type} available.</p>`;
    const color = type === "pros" ? "text-green-400" : "text-red-400";
    const icon = type === "pros" ? "fa-plus" : "fa-minus";
    return `<ul class="space-y-2">${items
      .map(
        (item) =>
          `<li class="flex items-start"><i class="fas ${icon} ${color} mt-1 mr-2 fa-xs"></i><span class="text-sm">${item}</span></li>`
      )
      .join("")}</ul>`;
  }

  // --- DATA FETCHING AND RENDERING ---

  /** Fetches data for a given company symbol and triggers rendering. */
  window.fetchCompanyData = function (symbol) {
    loader.classList.remove("hidden");
    dataContainer.classList.add("hidden");
    introMessage.classList.add("hidden");

    fetch(`/fundamentals/api/company/${symbol}/`)
      .then((response) => {
        if (!response.ok)
          throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then((data) => renderCompanyData(data))
      .catch((error) => {
        console.error("Error fetching company data:", error);
        dataContainer.innerHTML = createEmptyState(
          `Failed to load company data. ${error.message}`,
          "fa-exclamation-triangle"
        );
      })
      .finally(() => {
        document.querySelector(".w-3\\/4").scrollTo(0, 0); // Scroll main content to top
        loader.classList.add("hidden");
        dataContainer.classList.remove("hidden");
      });
  };

  /** Pivots financial data from the API into a row-based format for the table generator. */
  function transformFinancialData(financialData) {
    if (!financialData || !financialData.headers || !financialData.body)
      return [];
    const { headers, body } = financialData;
    return body.map((row) => {
      const rowObject = { Description: row.Description };
      headers.forEach((header, index) => {
        rowObject[header] = row.values[index];
      });
      return rowObject;
    });
  }

  /** Renders all the fetched company data into the DOM. */
  function renderCompanyData(data) {
    // Correctly handle data types from the API
    const pros = data.pros || [];
    const cons = data.cons || [];
    const peerComparison = data.peer_comparison || []; // It's already an array, no parsing needed.

    // Parse JSON strings for financial tables
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

    // Parse JSON for growth metrics and shareholding
    const salesGrowth = safeJsonParse(data.compounded_sales_growth, {});
    const profitGrowth = safeJsonParse(data.compounded_profit_growth, {});
    const stockCagr = safeJsonParse(data.stock_price_cagr, {});
    const roe = safeJsonParse(data.return_on_equity, {});
    const shareholding = safeJsonParse(data.shareholding_pattern, {});

    // Render Header
    document.getElementById("company-name").textContent =
      data.name || "Company";
    document.getElementById("company-symbol").textContent =
      data.symbol || "SYMBOL";
    document.getElementById("company-about").textContent =
      data.about || "No description available.";
    const websiteLink = document.getElementById("company-website");
    websiteLink.href = data.website || "#";
    websiteLink.style.display = data.website ? "inline-block" : "none";

    // Render Pros & Cons
    document.getElementById("pros-list").innerHTML = createList(pros, "pros");
    document.getElementById("cons-list").innerHTML = createList(cons, "cons");

    // Render Key Metrics
    const keyMetrics = {
      "Market Cap": formatters.addCr(data.market_cap),
      "Current Price": formatters.addRupee(data.current_price),
      "Stock P/E": formatters.number(data.stock_pe),
      "Book Value": formatters.addRupee(data.book_value),
      "Dividend Yield": formatters.addPercentage(data.dividend_yield),
      ROCE: formatters.addPercentage(data.roce),
      ROE: formatters.addPercentage(data.roe),
      "Face Value": formatters.addRupee(data.face_value),
    };
    document.getElementById("key-metrics-grid").innerHTML = Object.entries(
      keyMetrics
    )
      .map(
        ([key, value]) =>
          `<div class="p-4 bg-gray-900 rounded-lg shadow-md"><p class="text-sm font-medium text-gray-400">${key}</p><p class="text-xl font-semibold text-white mt-1">${value}</p></div>`
      )
      .join("");

    // --- TABLE CONFIGURATIONS ---
    const peerComparisonConfig = {
      title: "Peer Comparison",
      columns: [
        {
          key: "Name",
          title: "Name",
          formatter: (value, row) =>
            `<a href="#" class="text-violet-400 hover:underline" onclick="event.preventDefault(); window.handlePeerClick('${row.symbol}')">${value}</a>`,
        },
        { key: "CMP", title: "CMP", formatter: formatters.addRupee },
        { key: "P/E", title: "P/E", formatter: formatters.number },
        {
          key: "Mar Cap",
          title: "Market Cap (Cr)",
          formatter: formatters.addCr,
        },
        {
          key: "Div Yld",
          title: "Div Yld %",
          formatter: formatters.addPercentage,
        },
        { key: "ROCE", title: "ROCE %", formatter: formatters.addPercentage },
      ],
    };

    // Render all tables
    document.getElementById("peer-comparison").innerHTML = createTable(
      peerComparisonConfig,
      peerComparison
    );
    document.getElementById("quarterly-results").innerHTML = createTable(
      {
        title: "Quarterly Results",
        columns: (quarterlyResults[0]
          ? Object.keys(quarterlyResults[0])
          : []
        ).map((k) => ({ key: k, title: k })),
      },
      quarterlyResults
    );
    document.getElementById("profit-loss-statement").innerHTML = createTable(
      {
        title: "Profit & Loss",
        columns: (profitLoss[0] ? Object.keys(profitLoss[0]) : []).map((k) => ({
          key: k,
          title: k,
        })),
      },
      profitLoss
    );
    document.getElementById("balance-sheet").innerHTML = createTable(
      {
        title: "Balance Sheet",
        columns: (balanceSheet[0] ? Object.keys(balanceSheet[0]) : []).map(
          (k) => ({ key: k, title: k })
        ),
      },
      balanceSheet
    );
    document.getElementById("cash-flow-statement").innerHTML = createTable(
      {
        title: "Cash Flow",
        columns: (cashFlow[0] ? Object.keys(cashFlow[0]) : []).map((k) => ({
          key: k,
          title: k,
        })),
      },
      cashFlow
    );
    document.getElementById("ratios").innerHTML = createTable(
      {
        title: "Ratios",
        columns: (ratios[0] ? Object.keys(ratios[0]) : []).map((k) => ({
          key: k,
          title: k,
        })),
      },
      ratios
    );

    document.getElementById("compounded-sales-growth").innerHTML =
      createSimpleTable(salesGrowth);
    document.getElementById("compounded-profit-growth").innerHTML =
      createSimpleTable(profitGrowth);
    document.getElementById("stock-price-cagr").innerHTML =
      createSimpleTable(stockCagr);
    document.getElementById("return-on-equity").innerHTML =
      createSimpleTable(roe);
    document.getElementById("shareholding-pattern").innerHTML =
      createShareholdingTables(shareholding);
  }

  // --- INITIALIZATION ---

  /** Renders the list of companies in the sidebar. */
  function renderCompanyList(companies) {
    companyList.innerHTML = "";
    if (companies.length === 0) {
      companyList.innerHTML = `<li class="p-3 text-sm text-center text-gray-500">No companies found.</li>`;
      return;
    }
    companies.forEach((company) => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="#" class="block p-3 text-sm rounded-lg hover:bg-gray-700 transition-colors duration-200" data-symbol="${company.symbol}"><p class="font-semibold text-gray-200 truncate">${company.name}</p><p class="text-xs text-gray-400">${company.symbol}</p></a>`;
      li.addEventListener("click", function (e) {
        e.preventDefault();
        const symbol = this.querySelector("a").dataset.symbol;
        fetchCompanyData(symbol);
        document
          .querySelectorAll("#company-list li a")
          .forEach((a) => a.classList.remove("bg-gray-700"));
        this.querySelector("a").classList.add("bg-gray-700");
      });
      companyList.appendChild(li);
    });
  }

  /** Sets up the search input filter. */
  searchInput.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    const filteredCompanies = allCompanies.filter(
      (c) =>
        c.name.toLowerCase().includes(searchTerm) ||
        c.symbol.toLowerCase().includes(searchTerm)
    );
    renderCompanyList(filteredCompanies);
  });

  /** Fetches the initial list of all companies to populate the sidebar. */
  fetch("/fundamentals/api/companies/")
    .then((response) => response.json())
    .then((data) => {
      allCompanies = data;
      renderCompanyList(allCompanies);
    })
    .catch((error) => {
      console.error("Error fetching company list:", error);
      companyList.innerHTML = `<li class="p-3 text-sm text-center text-red-500">Could not load company list.</li>`;
    });
});
