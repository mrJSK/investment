/**
 * Handles clicks on peer company links within the deep-dive view.
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

document.addEventListener("DOMContentLoaded", function () {
  // --- 1. DOM Element References ---
  const searchInput = document.getElementById("search-input");
  const marketCapSearchInput = document.getElementById(
    "market-cap-search-input"
  );
  const companyList = document.getElementById("company-list");
  const mainContentArea = document.querySelector(".w-3\\/4");

  const deepDiveContent = document.getElementById("deep-dive-content");
  const marketCapContent = document.getElementById("market-cap-content");

  const dataContainer = document.getElementById("data-container");
  const loader = document.getElementById("loader");
  const marketCapLoader = document.getElementById("market-cap-loader");
  const marketCapDataContainer = document.getElementById("market-cap-data");

  // --- 2. State Cache ---
  let allCompanies = []; // Cache for the flat sidebar list
  let marketCapDataCache = null; // Cache for the categorized market cap data

  // --- 3. Formatting & Utility Functions ---
  const formatters = {
    default: (value) => (value !== null && value !== undefined ? value : "-"),
    number: (value, decimals = 2) => {
      const num = Number(String(value).replace(/,/g, ""));
      if (value === null || value === undefined || isNaN(num)) return "-";
      return num.toLocaleString("en-IN", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals,
      });
    },
    addPercentage: (value) =>
      value === null || value === undefined
        ? "-"
        : `${formatters.number(value)}%`,
    addCr: (value) =>
      value === null || value === undefined
        ? "-"
        : `${formatters.number(value)} Cr.`,
    addRupee: (value) =>
      value === null || value === undefined
        ? "-"
        : `₹${formatters.number(value)}`,
  };

  const createEmptyState = (
    message = "No Data Available",
    icon = "fa-table"
  ) => {
    return `<div class="text-center text-gray-500 p-8"><i class="fas ${icon} fa-2x mb-3"></i><p>${message}</p></div>`;
  };

  const safeJsonParse = (json, fallback = null) => {
    if (typeof json !== "string") return json;
    try {
      return JSON.parse(json);
    } catch (e) {
      console.error("JSON parsing error:", e);
      return fallback;
    }
  };

  const transformFinancialData = (financialData) => {
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
  };

  const createList = (items, type) => {
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
  };

  const createTable = (config, data) => {
    if (!data || data.length === 0) return createEmptyState();
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
            const isDescription =
              col.key === "Description" ||
              (index === 0 &&
                !config.columns.some((c) => c.key === "Description"));
            return `<td class="p-3 text-sm ${
              isDescription
                ? "sticky left-0 bg-gray-800 font-medium text-left"
                : "text-right"
            }">${formatter(value, row)}</td>`;
          })
          .join("");
        return `<tr class="border-b border-gray-700 hover:bg-gray-700">${cellsHtml}</tr>`;
      })
      .join("");
    return `<div class="overflow-x-auto custom-scrollbar"><table class="min-w-full"><thead class="bg-gray-800"><tr>${headerHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`;
  };

  const createSimpleTable = (data) => {
    if (!data || Object.keys(data).length === 0) return createEmptyState();
    const rows = Object.entries(data)
      .map(
        ([key, value]) =>
          `<tr class="border-b border-gray-700 last:border-b-0"><td class="p-3 text-sm font-medium text-gray-300">${key}</td><td class="p-3 text-sm text-right">${formatters.addPercentage(
            value
          )}</td></tr>`
      )
      .join("");
    return `<div class="overflow-x-auto"><table class="min-w-full"><tbody>${rows}</tbody></table></div>`;
  };

  const transformShareholdingData = (obj) => {
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
  };

  const createShareholdingTables = (data) => {
    if (!data || !data.quarterly || Object.keys(data.quarterly).length === 0)
      return createEmptyState(undefined, "fa-pie-chart");
    const transformedData = transformShareholdingData(data.quarterly);
    if (transformedData.length === 0)
      return createEmptyState(undefined, "fa-pie-chart");
    const columns = [
      { key: "Holder", title: "Holder" },
      ...Object.keys(transformedData[0])
        .filter((k) => k !== "Holder")
        .map((date) => ({
          key: date,
          title: date,
          formatter: formatters.addPercentage,
        })),
    ];
    return createTable({ columns }, transformedData);
  };

  // --- 4. Main Rendering Functions ---

  /**
   * Renders the full company detail view, replacing the market cap view.
   * @param {object} data - The detailed data for a single company.
   */
  function renderCompanyData(data) {
    const pros = data.pros || [];
    const cons = data.cons || [];
    const peerComparison = data.peer_comparison || [];
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
    const shareholding = safeJsonParse(data.shareholding_pattern, {});
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
    const peerComparisonConfig = {
      columns: [
        {
          key: "Name",
          title: "Name",
          formatter: (value, row) =>
            `<a href="#" class="text-violet-400 hover:underline" onclick="event.preventDefault(); window.handlePeerClick('${row.symbol}')">${value}</a>`,
        },
        {
          key: "CMP",
          title: "CMP",
          formatter: (val) => formatters.addRupee(val),
        },
        {
          key: "P/E",
          title: "P/E",
          formatter: (val) => formatters.number(val),
        },
        {
          key: "Mar Cap",
          title: "Market Cap (Cr)",
          formatter: (val) => formatters.addCr(val),
        },
        {
          key: "Div Yld",
          title: "Div Yld %",
          formatter: (val) => formatters.addPercentage(val),
        },
        {
          key: "ROCE",
          title: "ROCE %",
          formatter: (val) => formatters.addPercentage(val),
        },
      ],
    };
    const getColumns = (d) =>
      (d && d[0] ? Object.keys(d[0]) : []).map((k) => ({ key: k, title: k }));

    dataContainer.innerHTML = `<div class="card"><div class="flex justify-between items-start"><div><h1 class="text-3xl font-bold text-white">${
      data.name || "Company"
    }</h1><p class="text-md text-violet-400">${
      data.symbol || "SYMBOL"
    }</p></div><a href="${
      data.website || "#"
    }" target="_blank" rel="noopener noreferrer" class="text-violet-400 hover:underline ${
      data.website ? "inline-block" : "hidden"
    }">Visit Website <i class="fas fa-external-link-alt ml-1"></i></a></div><p class="mt-4 text-gray-400 border-t border-gray-700 pt-4">${
      data.about || "No description available."
    }</p></div><div class="card"><h2 class="section-title"><i class="fas fa-tachometer-alt fa-icon"></i><span>Key Metrics</span></h2><div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 text-center">${Object.entries(
      keyMetrics
    )
      .map(
        ([key, value]) =>
          `<div class="p-4 bg-gray-900 rounded-lg shadow-md"><p class="text-sm font-medium text-gray-400">${key}</p><p class="text-xl font-semibold text-white mt-1">${value}</p></div>`
      )
      .join(
        ""
      )}</div></div><div class="grid grid-cols-1 md:grid-cols-2 gap-6"><div class="card"><h2 class="section-title"><i class="fas fa-thumbs-up fa-icon"></i><span>Pros</span></h2><div>${createList(
      pros,
      "pros"
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-thumbs-down fa-icon"></i><span>Cons</span></h2><div>${createList(
      cons,
      "cons"
    )}</div></div></div><div class="card"><h2 class="section-title"><i class="fas fa-users fa-icon"></i><span>Peer Comparison</span></h2><div>${createTable(
      peerComparisonConfig,
      peerComparison
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-calendar-alt fa-icon"></i><span>Quarterly Results</span></h2><div>${createTable(
      { title: "Quarterly Results", columns: getColumns(quarterlyResults) },
      quarterlyResults
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-file-invoice-dollar fa-icon"></i><span>Profit & Loss</span></h2><div>${createTable(
      { title: "Profit & Loss", columns: getColumns(profitLoss) },
      profitLoss
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-balance-scale fa-icon"></i><span>Balance Sheet</span></h2><div>${createTable(
      { title: "Balance Sheet", columns: getColumns(balanceSheet) },
      balanceSheet
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-hand-holding-usd fa-icon"></i><span>Cash Flow</span></h2><div>${createTable(
      { title: "Cash Flow", columns: getColumns(cashFlow) },
      cashFlow
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-divide fa-icon"></i><span>Ratios</span></h2><div>${createTable(
      { title: "Ratios", columns: getColumns(ratios) },
      ratios
    )}</div></div><div class="grid grid-cols-1 md:grid-cols-2 gap-6"><div class="card"><h2 class="section-title"><i class="fas fa-chart-line fa-icon"></i><span>Compounded Sales Growth</span></h2><div>${createSimpleTable(
      salesGrowth
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-chart-area fa-icon"></i><span>Compounded Profit Growth</span></h2><div>${createSimpleTable(
      profitGrowth
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-chart-bar fa-icon"></i><span>Stock Price CAGR</span></h2><div>${createSimpleTable(
      stockCagr
    )}</div></div><div class="card"><h2 class="section-title"><i class="fas fa-percentage fa-icon"></i><span>Return on Equity</span></h2><div>${createSimpleTable(
      roe
    )}</div></div></div><div class="card"><h2 class="section-title"><i class="fas fa-pie-chart fa-icon"></i><span>Shareholding Pattern</span></h2><div>${createShareholdingTables(
      shareholding
    )}</div></div>`;
  }

  function renderSidebarList(companies) {
    companyList.innerHTML = "";
    if (companies.length === 0) {
      companyList.innerHTML = `<li class="p-3 text-sm text-center text-gray-500">No companies found.</li>`;
      return;
    }
    companies.forEach((company) => {
      const li = document.createElement("li");
      li.innerHTML = `<a href="#" class="block p-3 text-sm rounded-lg hover:bg-gray-700" data-symbol="${company.symbol}"><p class="font-semibold text-gray-200 truncate">${company.name}</p><p class="text-xs text-gray-400">${company.symbol}</p></a>`;
      li.addEventListener("click", (e) => {
        e.preventDefault();
        document
          .querySelectorAll("#company-list li a")
          .forEach((a) => a.classList.remove("bg-gray-700"));
        e.currentTarget.querySelector("a").classList.add("bg-gray-700");
        fetchCompanyData(company.symbol);
      });
      companyList.appendChild(li);
    });
  }

  /**
   * Renders the categorized lists for the market cap view.
   * @param {object} data - The categorized company data to render.
   */
  function renderMarketCapData(data) {
    const populateList = (listId, companies) => {
      const listEl = document.getElementById(listId);
      if (!listEl) return;
      if (!companies || companies.length === 0) {
        listEl.innerHTML = '<li class="text-gray-500 text-sm p-2">None</li>';
        return;
      }
      listEl.innerHTML = companies
        .map(
          (c) => `
            <li class="p-2 rounded-md hover:bg-gray-700 cursor-pointer" data-symbol="${
              c.symbol
            }">
                <div class="flex justify-between items-center">
                    <div><p class="font-semibold text-gray-200">${
                      c.name
                    }</p><p class="text-xs text-gray-400">${c.symbol}</p></div>
                    <p class="text-sm font-mono text-gray-300">${formatters.addCr(
                      c.market_cap
                    )}</p>
                </div>
            </li>`
        )
        .join("");
    };

    populateList("large-cap-list", data.large_caps);
    populateList("mid-cap-list", data.mid_caps);
    populateList("small-cap-list", data.small_caps);

    marketCapDataContainer.classList.remove("hidden");

    document
      .querySelectorAll("#market-cap-data [data-symbol]")
      .forEach((item) => {
        item.addEventListener("click", () => {
          const symbol = item.dataset.symbol;
          const sidebarLink = document.querySelector(
            `#company-list a[data-symbol="${symbol}"]`
          );
          if (sidebarLink) {
            document
              .querySelectorAll("#company-list li a")
              .forEach((a) => a.classList.remove("bg-gray-700"));
            sidebarLink.classList.add("bg-gray-700");
          }
          fetchCompanyData(symbol);
        });
      });
  }

  // --- 5. Data Fetching & UI Switching ---
  window.fetchCompanyData = function (symbol) {
    marketCapContent.classList.add("hidden");
    deepDiveContent.classList.remove("hidden");

    loader.classList.remove("hidden");
    dataContainer.classList.add("hidden");

    fetch(`/fundamentals/api/company/${symbol}/`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        renderCompanyData(data);
      })
      .catch((err) => {
        console.error("Error fetching company data:", err);
        dataContainer.innerHTML = createEmptyState(
          `Failed to load company data.`,
          "fa-exclamation-triangle"
        );
      })
      .finally(() => {
        loader.classList.add("hidden");
        dataContainer.classList.remove("hidden");
        mainContentArea.scrollTo(0, 0);
      });
  };

  function fetchAndRenderMarketCapData() {
    marketCapLoader.classList.remove("hidden");
    marketCapDataContainer.classList.add("hidden");

    fetch("/fundamentals/api/market-cap-data/")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then((data) => {
        marketCapDataCache = data;
        renderMarketCapData(data);
      })
      .catch((err) => {
        console.error("Failed to load market cap data:", err);
        // Hide the loader and show an error message in the main container
        marketCapLoader.classList.add("hidden");
        marketCapDataContainer.innerHTML = createEmptyState(
          "Failed to load market cap data.",
          "fa-exclamation-triangle"
        );
        marketCapDataContainer.classList.remove("hidden");
      });
  }

  // --- 6. Event Listeners & Initial Calls ---
  searchInput.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    const filtered = allCompanies.filter(
      (c) =>
        c.name.toLowerCase().includes(searchTerm) ||
        c.symbol.toLowerCase().includes(searchTerm)
    );
    renderSidebarList(filtered);
  });

  marketCapSearchInput.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    if (!marketCapDataCache) return;

    if (!searchTerm) {
      renderMarketCapData(marketCapDataCache);
      return;
    }

    const filteredData = {
      large_caps: marketCapDataCache.large_caps.filter(
        (c) =>
          c.name.toLowerCase().includes(searchTerm) ||
          c.symbol.toLowerCase().includes(searchTerm)
      ),
      mid_caps: marketCapDataCache.mid_caps.filter(
        (c) =>
          c.name.toLowerCase().includes(searchTerm) ||
          c.symbol.toLowerCase().includes(searchTerm)
      ),
      small_caps: marketCapDataCache.small_caps.filter(
        (c) =>
          c.name.toLowerCase().includes(searchTerm) ||
          c.symbol.toLowerCase().includes(searchTerm)
      ),
    };
    renderMarketCapData(filteredData);
  });

  fetch("/fundamentals/api/companies/")
    .then((response) => response.json())
    .then((data) => {
      allCompanies = data;
      renderSidebarList(allCompanies);
    })
    .catch((error) => {
      console.error("Error fetching company list:", error);
      companyList.innerHTML = `<li class="p-3 text-sm text-center text-red-500">Could not load company list.</li>`;
    });

  fetchAndRenderMarketCapData();
});
