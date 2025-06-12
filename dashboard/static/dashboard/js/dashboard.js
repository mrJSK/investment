// static/dashboard/js/dashboard.js

document.addEventListener("DOMContentLoaded", function () {
  // --- State Variables ---
  let liveTrades = [];
  let priceHistories = {};

  // --- DOM Element References ---
  const openPositionsContainer = document.getElementById("open-positions");
  const closedTradesContainer = document.getElementById("closed-trades-body");
  const newsContainer = document.getElementById("live-news-feed");
  const stocksInFocusBody = document.getElementById("stocks-in-focus-body");
  const announcementTabsContainer =
    document.getElementById("announcement-tabs");
  const announcementContentContainer = document.getElementById(
    "announcement-content"
  );
  const annualReportsContainer = document.getElementById(
    "financial-reports-content"
  );
  const quarterlyResultsContainer = document.getElementById(
    "quarterly-results-content"
  );
  const totalInvestmentEl = document.getElementById("total-investment");
  const currentValueEl = document.getElementById("current-value");
  const pnlValueEl = document.getElementById("pnl-value");
  const pnlPctEl = document.getElementById("pnl-pct");
  const todaysPnlValueEl = document.getElementById("todays-pnl-value");
  const todaysPnlPctEl = document.getElementById("todays-pnl-pct");

  // --- Independent Data Fetching Functions ---

  async function fetchTradingData() {
    try {
      const response = await fetch("/dashboard/api/trading-data/");
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      data.live_trades.forEach((trade) => {
        if (!priceHistories[trade.symbol])
          priceHistories[trade.symbol] = [trade.currentPrice];
        else {
          priceHistories[trade.symbol].push(trade.currentPrice);
          if (priceHistories[trade.symbol].length > 30)
            priceHistories[trade.symbol].shift();
        }
        trade.priceHistory = priceHistories[trade.symbol];
      });
      liveTrades = data.live_trades;
      renderOpenPositions();
      renderPortfolioSummary();
      renderClosedTrades(data.closed_trades);
    } catch (error) {
      console.error("Failed to fetch trading data:", error);
      if (openPositionsContainer)
        openPositionsContainer.innerHTML = `<div class="text-center text-red-400 p-8">Could not load trading data.</div>`;
    }
  }

  async function fetchNewsData() {
    try {
      const response = await fetch("/dashboard/api/market-news/");
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      renderRegularNews(data.regular);
      renderStocksInFocusTable(data.watch_list);
    } catch (error) {
      console.error("Failed to fetch news data:", error);
      if (newsContainer)
        newsContainer.innerHTML = `<div class="text-center text-red-400 p-8">Could not load news feed.</div>`;
      if (stocksInFocusBody)
        stocksInFocusBody.innerHTML = `<tr><td colspan="3" class="text-center p-8 text-red-400">Could not load stocks in focus.</td></tr>`;
    }
  }

  async function fetchAnnouncementsData() {
    try {
      const response = await fetch("/dashboard/api/nse-announcements/");
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      renderNseAnnouncements(data);
    } catch (error) {
      console.error("Failed to fetch announcements data:", error);
      if (announcementTabsContainer)
        announcementTabsContainer.innerHTML = `<div class="text-center text-red-400 p-4 w-full">Could not load announcements.</div>`;
    }
  }

  async function fetchAnnualReportsData() {
    try {
      const response = await fetch("/dashboard/api/financial-reports/");
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      renderFinancialReports(data.financial_reports, "annual");
    } catch (error) {
      console.error("Failed to fetch annual reports:", error);
      if (annualReportsContainer)
        annualReportsContainer.innerHTML = `<div class="text-center text-red-400 p-8">Could not load annual reports.</div>`;
    }
  }

  async function fetchQuarterlyResultsData() {
    try {
      const response = await fetch("/dashboard/api/quarterly-financials/");
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      renderFinancialReports(data.quarterly_reports, "quarterly");
    } catch (error) {
      console.error("Failed to fetch quarterly results:", error);
      if (quarterlyResultsContainer)
        quarterlyResultsContainer.innerHTML = `<div class="text-center text-red-400 p-8">Could not load quarterly results.</div>`;
    }
  }

  // --- Rendering Functions ---

  function renderFinancialReports(reports, type) {
    const container =
      type === "annual" ? annualReportsContainer : quarterlyResultsContainer;
    if (!container) return;
    if (!reports || reports.length === 0) {
      container.innerHTML = `<div class="text-center text-gray-500 p-8">No recent ${type} reports found.</div>`;
      return;
    }
    container.innerHTML = reports
      .map((report, index) => {
        const general = report.general || {};
        const companyName =
          report.company_name || general.NameOfTheCompany || "Unnamed Report";
        const reportDate =
          report.periods?.current || general.ReportingQuarter || "N/A";
        const symbol = general.Symbol || "";
        return `
          <div class="fr-accordion-item bg-gray-800/60 rounded-lg border border-gray-700" id="${type}-report-item-${index}">
              <button class="fr-accordion-header w-full flex justify-between items-center p-4 focus:outline-none">
                  <div class="text-left">
                      <p class="font-semibold text-white">${companyName} ${
          symbol ? `(${symbol})` : ""
        }</p>
                      <p class="text-xs text-gray-400">${
                        type === "annual" ? "Annual Report" : "Quarterly Report"
                      } - ${reportDate}</p>
                  </div>
                  <svg class="w-6 h-6 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              <div class="fr-accordion-content">
                  <div class="p-4 border-t border-gray-700 space-y-3">
                      ${renderFinancialStatements(report, type, index)}
                  </div>
              </div>
          </div>`;
      })
      .join("");
  }

  function renderFinancialStatements(reportData, type, reportIndex) {
    const statements = reportData.statements;
    if (!statements)
      return '<p class="text-gray-500 text-sm p-4">No detailed statements available.</p>';

    const statementHierarchy = {
      "Statement of Profit and Loss": [
        "RevenueFromOperations",
        "OtherIncome",
        "Income",
        "Expenses",
        "ProfitBeforeTax",
        "TaxExpense",
        "ProfitLossForPeriod",
        "BasicEarningsLossPerShareFromContinuingAndDiscontinuedOperations",
      ],
      "Key Ratios": [
        "DebtEquityRatio",
        "DebtServiceCoverageRatio",
        "InterestServiceCoverageRatio",
      ],
    };

    return Object.entries(statementHierarchy)
      .map(([statementName, concepts]) => {
        const availableConcepts = concepts
          .map((c) => statements[c])
          .filter(Boolean);
        if (availableConcepts.length === 0) return "";

        const headers = [
          ...new Set(
            availableConcepts.flatMap((fact) =>
              (fact.main || []).map((v) => v.context.period_label)
            )
          ),
        ];

        return `
              <div class="fr-accordion-item bg-gray-900/50 rounded-md border border-gray-700/50" id="${type}-statement-item-${reportIndex}-${statementName.replace(
          /\s+/g,
          ""
        )}">
                  <button class="fr-accordion-header w-full flex justify-between items-center p-3 text-left">
                      <span class="text-sm font-semibold text-cyan-300">${statementName}</span>
                      <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </button>
                  <div class="fr-accordion-content">
                      <div class="overflow-x-auto p-2">
                          <table class="w-full text-xs">
                              <thead class="text-gray-400">
                                  <tr>
                                      <th class="p-2 text-left font-medium w-2/5">Description</th>
                                      ${headers
                                        .map(
                                          (h) =>
                                            `<th class="p-2 text-right font-medium">${h
                                              .replace("From ", "")
                                              .replace("to ", "~ ")}</th>`
                                        )
                                        .join("")}
                                  </tr>
                              </thead>
                              <tbody class="divide-y divide-gray-700/50">
                                  ${availableConcepts
                                    .map((fact) =>
                                      renderFinancialTableRows(fact, headers)
                                    )
                                    .join("")}
                              </tbody>
                          </table>
                      </div>
                  </div>
              </div>
          `;
      })
      .join("");
  }

  function renderFinancialTableRows(fact, headers) {
    if (!fact.main || fact.main.length === 0) return "";
    const conceptName = fact.main[0].concept.replace(/([A-Z])/g, " $1").trim();
    const valuesByPeriod = fact.main.reduce((acc, v) => {
      const scalingFactor = v.decimals < 0 ? 100000 : 1; // Handle Lakhs
      acc[v.context.period_label] = v.value * scalingFactor;
      return acc;
    }, {});

    let rowHtml = `<tr class="hover:bg-gray-900/20"><td class="p-2 font-medium text-gray-300">${conceptName}</td>
                   ${headers
                     .map(
                       (h) =>
                         `<td class="p-2 text-right font-mono">${
                           valuesByPeriod[h] !== undefined
                             ? valuesByPeriod[h].toLocaleString("en-IN")
                             : "—"
                         }</td>`
                     )
                     .join("")}</tr>`;

    if (fact.details && fact.details.length > 0) {
      const detailsByDesc = fact.details.reduce((acc, d) => {
        if (!acc[d.description]) acc[d.description] = {};
        const scalingFactor = d.decimals < 0 ? 100000 : 1;
        acc[d.description][d.context.period_label] = d.value * scalingFactor;
        return acc;
      }, {});
      for (const [desc, values] of Object.entries(detailsByDesc)) {
        rowHtml += `<tr class="hover:bg-gray-900/20"><td class="p-2 pl-8 text-gray-400">${desc}</td>
                        ${headers
                          .map(
                            (h) =>
                              `<td class="p-2 text-right font-mono text-gray-400">${
                                values[h] !== undefined
                                  ? values[h].toLocaleString("en-IN")
                                  : "—"
                              }</td>`
                          )
                          .join("")}</tr>`;
      }
    }
    return rowHtml;
  }

  // ... (All other rendering functions: renderStocksInFocusTable, renderRegularNews, etc. remain here unchanged)

  function renderStocksInFocusTable(watchListData) {
    if (!stocksInFocusBody) return;
    stocksInFocusBody.innerHTML = "";
    if (!watchListData || watchListData.length === 0) {
      stocksInFocusBody.innerHTML = `<tr><td colspan="3" class="text-center p-8 text-gray-500">No specific stocks in focus today.</td></tr>`;
      return;
    }
    watchListData.forEach((item) => {
      let sentimentColor, sentimentBg;
      switch (item.sentiment.toLowerCase()) {
        case "positive":
          sentimentColor = "text-green-300";
          sentimentBg = "bg-green-500/10";
          break;
        case "negative":
          sentimentColor = "text-red-300";
          sentimentBg = "bg-red-500/10";
          break;
        default:
          sentimentColor = "text-amber-300";
          sentimentBg = "bg-amber-500/10";
          break;
      }
      const row = document.createElement("tr");
      row.innerHTML = `<td class="p-3 font-medium text-white align-top">${
        item.stock_name
      }</td><td class="p-3 text-gray-300 align-top">${
        item.text
      }</td><td class="p-3 align-top"><span class="font-bold text-xs ${sentimentColor} ${sentimentBg} px-3 py-1 rounded-full whitespace-nowrap">${item.sentiment.toUpperCase()}</span></td>`;
      stocksInFocusBody.appendChild(row);
    });
  }

  function renderRegularNews(newsData) {
    if (!newsContainer) return;
    if (!newsData || newsData.length === 0) {
      newsContainer.innerHTML = `<div class="text-center text-gray-500 p-8">No news available.</div>`;
      return;
    }
    newsContainer.innerHTML = "";
    newsData.forEach((item, index) => {
      let borderColor, textColor, bgColor;
      switch (item.sentiment.toLowerCase()) {
        case "positive":
          borderColor = "border-green-500";
          textColor = "text-green-300";
          bgColor = "bg-green-500/10";
          break;
        case "negative":
          borderColor = "border-red-500";
          textColor = "text-red-300";
          bgColor = "bg-red-500/10";
          break;
        default:
          borderColor = "border-gray-600";
          textColor = "text-gray-300";
          bgColor = "bg-gray-500/10";
          break;
      }
      const newsItem = document.createElement("div");
      newsItem.className = `bg-gray-800/50 rounded-lg border-l-4 ${borderColor} mb-4`;
      newsItem.innerHTML = `<div class="p-4"><div class="flex justify-between items-start gap-4"><div class="flex-grow"><div class="font-bold text-xs ${bgColor} ${textColor} px-3 py-1 rounded-full inline-block mb-2">${item.sentiment.toUpperCase()}: ${item.action.toUpperCase()} (${
        item.confidence
      }%)</div><a href="${
        item.link
      }" target="_blank" rel="noopener noreferrer" class="block font-semibold text-gray-200 hover:text-violet-400 transition-colors">${
        item.headline
      }</a><div class="text-xs text-gray-400 mt-1">${
        item.publication_time
      }</div></div><button class="read-more-btn flex-shrink-0 text-sm text-violet-400 hover:text-violet-300 font-semibold py-2 px-3 rounded-md hover:bg-gray-700 transition-colors" data-target="news-content-${index}">Read More</button></div><div id="news-content-${index}" class="news-full-text mt-4 pt-4 border-t border-gray-700 text-gray-400 text-sm leading-relaxed formatted-text" style="max-height: 0px;">${
        item.full_text
      }</div></div>`;
      newsContainer.appendChild(newsItem);
    });
  }

  function renderNseAnnouncements(announcements) {
    if (!announcementTabsContainer || !announcementContentContainer) return;
    const categories = Object.keys(announcements);
    if (categories.length === 0) {
      announcementTabsContainer.innerHTML = `<div class="text-center text-gray-500 p-4 w-full">No announcements found.</div>`;
      announcementContentContainer.innerHTML = "";
      return;
    }
    announcementTabsContainer.innerHTML = "";
    announcementContentContainer.innerHTML = "";
    categories.forEach((category, index) => {
      const tabId = `announcement-pane-${index}`;
      const tabButton = document.createElement("button");
      tabButton.className =
        "tab-btn px-4 py-2 text-sm font-semibold text-gray-400";
      tabButton.dataset.tab = tabId;
      tabButton.textContent = `${category} (${announcements[category].length})`;
      const contentPane = document.createElement("div");
      contentPane.id = tabId;
      contentPane.className = "tab-content";
      let tableHTML = `<div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-400 uppercase bg-gray-700/50"><tr><th class="p-3">Company</th><th class="p-3">Announcement</th><th class="p-3">Date</th><th class="p-3 text-center">Link</th></tr></thead><tbody class="divide-y divide-gray-700">`;
      announcements[category].forEach((item) => {
        tableHTML += `<tr><td class="p-3 font-medium text-white align-top">${item.company}</td><td class="p-3 text-gray-300 align-top">${item.description}</td><td class="p-3 whitespace-nowrap align-top">${item.pub_date}</td><td class="p-3 text-center align-top"><a href="${item.link}" target="_blank" rel="noopener noreferrer" class="text-violet-400 hover:text-violet-300 font-bold"><i class="fas fa-file-alt"></i></a></td></tr>`;
      });
      tableHTML += "</tbody></table></div>";
      contentPane.innerHTML = tableHTML;
      if (index === 0) {
        tabButton.classList.add("active", "text-violet-400");
        tabButton.classList.remove("text-gray-400");
        contentPane.classList.add("active");
      }
      announcementTabsContainer.appendChild(tabButton);
      announcementContentContainer.appendChild(contentPane);
    });
  }

  function renderPortfolioSummary() {
    const totalInvestment = liveTrades.reduce(
      (acc, trade) => acc + trade.entryPrice * trade.qty,
      0
    );
    const currentValue = liveTrades.reduce(
      (acc, trade) => acc + trade.currentPrice * trade.qty,
      0
    );
    const overallPnl = currentValue - totalInvestment;
    const overallPnlPct =
      totalInvestment === 0 ? 0 : (overallPnl / totalInvestment) * 100;
    const dayOpenValue = liveTrades.reduce(
      (acc, trade) => acc + trade.dayOpen * trade.qty,
      0
    );
    const todaysPnl = currentValue - dayOpenValue;
    const todaysPnlPct =
      dayOpenValue === 0 ? 0 : (todaysPnl / dayOpenValue) * 100;
    const formatCurrency = (value) =>
      `₹${value.toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;
    const pnlClass = (value) =>
      value >= 0 ? "text-green-400" : "text-red-400";
    totalInvestmentEl.textContent = formatCurrency(totalInvestment);
    currentValueEl.textContent = formatCurrency(currentValue);
    pnlValueEl.textContent = formatCurrency(overallPnl);
    pnlValueEl.className = `font-semibold ${pnlClass(overallPnl)}`;
    pnlPctEl.textContent = `(${overallPnlPct.toFixed(2)}%)`;
    pnlPctEl.className = `text-sm ml-2 ${pnlClass(overallPnl)}`;
    todaysPnlValueEl.textContent = formatCurrency(todaysPnl);
    todaysPnlValueEl.className = `font-semibold ${pnlClass(todaysPnl)}`;
    todaysPnlPctEl.textContent = `(${todaysPnlPct.toFixed(2)}%)`;
    todaysPnlPctEl.className = `text-sm ml-2 ${pnlClass(todaysPnl)}`;
  }

  function renderOpenPositions() {
    if (!openPositionsContainer) return;
    if (liveTrades.length === 0) {
      openPositionsContainer.innerHTML = `<div class="text-center text-gray-500 p-8">No open positions.</div>`;
      return;
    }
    const groupedByAssetClass = liveTrades.reduce((acc, trade) => {
      (acc[trade.assetClass] = acc[trade.assetClass] || []).push(trade);
      return acc;
    }, {});
    openPositionsContainer.innerHTML = "";
    for (const assetClass in groupedByAssetClass) {
      const assetClassDiv = document.createElement("div");
      assetClassDiv.className = "space-y-6";
      assetClassDiv.innerHTML = `<h3 class="text-md font-semibold text-teal-400 border-b border-gray-700 pb-2">${assetClass}</h3>`;
      const tradesInClass = groupedByAssetClass[assetClass];
      const groupedByStrategy = tradesInClass.reduce((acc, trade) => {
        (acc[trade.strategy] = acc[trade.strategy] || []).push(trade);
        return acc;
      }, {});
      for (const strategy in groupedByStrategy) {
        const strategyDiv = document.createElement("div");
        const strategyTrades = groupedByStrategy[strategy];
        const totalStrategyPnl = strategyTrades.reduce(
          (pnl, t) => pnl + (t.currentPrice - t.entryPrice) * t.qty,
          0
        );
        const pnlClass =
          totalStrategyPnl >= 0 ? "text-green-400" : "text-red-400";
        let tableHTML = `<div class="flex justify-between items-center mb-2"><h4 class="text-sm font-semibold text-gray-300">${strategy}</h4><span class="text-xs font-mono p-1 rounded ${pnlClass} bg-opacity-10 bg-gray-700">P/L: ${totalStrategyPnl.toLocaleString(
          "en-IN",
          { minimumFractionDigits: 2, maximumFractionDigits: 2 }
        )}</span></div><div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-400 uppercase bg-gray-700/50"><tr><th class="p-3">Symbol</th><th class="p-3">Qty</th><th class="p-3">Entry</th><th class="p-3">Current</th><th class="p-3">Unrealized P/L</th><th class="p-3">Trend</th><th class="p-3 text-center">Actions</th></tr></thead><tbody class="divide-y divide-gray-700 align-middle">`;
        strategyTrades.forEach((trade, tradeIndex) => {
          const pnl = (trade.currentPrice - trade.entryPrice) * trade.qty;
          const pnlPct =
            trade.entryPrice === 0
              ? 0
              : ((trade.currentPrice - trade.entryPrice) / trade.entryPrice) *
                100;
          const pnlCellClass = pnl >= 0 ? "text-green-400" : "text-red-500";
          const dayChange = trade.currentPrice - trade.dayOpen;
          const dayChangePct =
            trade.dayOpen === 0 ? 0 : (dayChange / trade.dayOpen) * 100;
          const dayChangeClass =
            dayChange >= 0 ? "text-green-400" : "text-red-500";
          tableHTML += `<tr><td class="p-3 font-medium text-white">${
            trade.symbol
          }</td><td class="p-3">${
            trade.qty
          }</td><td class="p-3">${trade.entryPrice.toFixed(
            2
          )}</td><td class="p-3 font-semibold">${trade.currentPrice.toFixed(
            2
          )} <span class="text-xs ${dayChangeClass}">(${dayChangePct.toFixed(
            2
          )}%)</span></td><td class="p-3 font-semibold rounded-md" data-pnl-cell="true"><div class="${pnlCellClass}">₹${pnl.toLocaleString(
            "en-IN",
            { minimumFractionDigits: 2, maximumFractionDigits: 2 }
          )} <span class="text-xs">(${pnlPct.toFixed(
            2
          )}%)</span></div></td><td class="p-3"><canvas id="sparkline-${
            trade.symbol
          }-${tradeIndex}" width="100" height="30"></canvas></td><td class="p-3 text-center"><button class="text-red-500 hover:text-red-400 text-xs font-semibold">CLOSE</button></td></tr>`;
        });
        tableHTML += `</tbody></table></div>`;
        strategyDiv.innerHTML = tableHTML;
        assetClassDiv.appendChild(strategyDiv);
      }
      openPositionsContainer.appendChild(assetClassDiv);
    }
    renderSparklines();
  }

  function renderSparklines() {
    liveTrades.forEach((trade, tradeIndex) => {
      const canvas = document.getElementById(
        `sparkline-${trade.symbol}-${tradeIndex}`
      );
      if (!canvas || !trade.priceHistory || trade.priceHistory.length < 2)
        return;
      const ctx = canvas.getContext("2d");
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const prices = trade.priceHistory;
      const maxPrice = Math.max(...prices);
      const minPrice = Math.min(...prices);
      const range = maxPrice - minPrice || 1;
      ctx.beginPath();
      ctx.moveTo(
        0,
        canvas.height - ((prices[0] - minPrice) / range) * canvas.height
      );
      for (let i = 1; i < prices.length; i++) {
        ctx.lineTo(
          (i / (prices.length - 1)) * canvas.width,
          canvas.height - ((prices[i] - minPrice) / range) * canvas.height
        );
      }
      ctx.strokeStyle =
        prices[prices.length - 1] >= prices[0] ? "#4ade80" : "#f87171";
      ctx.lineWidth = 1.5;
      ctx.stroke();
    });
  }

  function renderClosedTrades(trades) {
    if (!closedTradesContainer) return;
    if (!trades || trades.length === 0) {
      closedTradesContainer.innerHTML = `<tr><td colspan="5" class="text-center p-8 text-gray-500">No closed trades found.</td></tr>`;
      return;
    }
    closedTradesContainer.innerHTML = "";
    trades.forEach((trade) => {
      const pnlClass = trade.pnl >= 0 ? "text-green-400" : "text-red-500";
      const row = document.createElement("tr");
      row.innerHTML = `<td class="p-3 font-medium text-white">${
        trade.symbol
      }</td><td class="p-3 font-semibold ${pnlClass}">₹${trade.pnl.toLocaleString(
        "en-IN",
        { minimumFractionDigits: 2, maximumFractionDigits: 2 }
      )}</td><td class="p-3">${trade.entryDate}</td><td class="p-3">${
        trade.exitDate
      }</td><td class="p-3">${trade.reason}</td>`;
      closedTradesContainer.appendChild(row);
    });
  }

  // --- Main Initialization Function ---
  function init() {
    console.log("Initializing Dashboard...");

    document.body.addEventListener("click", function (event) {
      const tabButton = event.target.closest(".tab-btn");
      if (tabButton) {
        const parentContainer = tabButton.closest(".bg-gray-800");
        if (!parentContainer) return;
        const allButtons = parentContainer.querySelectorAll(".tab-btn");
        const allContent = parentContainer.querySelectorAll(".tab-content");
        allButtons.forEach((btn) => {
          btn.classList.remove("active", "text-violet-400");
          btn.classList.add("text-gray-400");
        });
        tabButton.classList.add("active", "text-violet-400");
        tabButton.classList.remove("text-gray-400");
        allContent.forEach((content) => {
          content.classList.remove("active");
        });
        const contentToShow = parentContainer.querySelector(
          `#${tabButton.dataset.tab}`
        );
        if (contentToShow) contentToShow.classList.add("active");
      }

      const newsButton = event.target.closest(".read-more-btn");
      if (newsButton) {
        const contentEl = document.getElementById(newsButton.dataset.target);
        if (!contentEl) return;
        const isCollapsed = contentEl.style.maxHeight === "0px";
        contentEl.style.maxHeight = isCollapsed
          ? contentEl.scrollHeight + "px"
          : "0px";
        newsButton.textContent = isCollapsed ? "Read Less" : "Read More";
      }

      const frHeader = event.target.closest(".fr-accordion-header");
      if (frHeader) {
        frHeader.parentElement.classList.toggle("open");
      }
    });

    // Fire off all data fetches concurrently
    fetchTradingData();
    fetchNewsData();
    fetchAnnouncementsData();
    fetchAnnualReportsData();
    fetchQuarterlyResultsData();

    // Refresh only the fast-moving trading data periodically
    setInterval(fetchTradingData, 30000); // Poll trading data every 30 seconds
  }

  init();
});
