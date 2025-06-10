// // static/dashboard/js/dashboard.js

// document.addEventListener("DOMContentLoaded", function () {
//   // --- State Variables ---
//   let liveTrades = [];
//   let priceHistories = {};
//   let lastNewsDataString = "";
//   let lastAnnouncementsDataString = "";

//   // --- DOM Element References ---
//   const openPositionsContainer = document.getElementById("open-positions");
//   const closedTradesContainer = document.getElementById("closed-trades-body");
//   const newsContainer = document.getElementById("live-news-feed");
//   const totalInvestmentEl = document.getElementById("total-investment");
//   const currentValueEl = document.getElementById("current-value");
//   const pnlValueEl = document.getElementById("pnl-value");
//   const pnlPctEl = document.getElementById("pnl-pct");
//   const todaysPnlValueEl = document.getElementById("todays-pnl-value");
//   const todaysPnlPctEl = document.getElementById("todays-pnl-pct");
//   const stocksInFocusContainer = document.getElementById(
//     "stocks-in-focus-container"
//   );
//   const stocksInFocusFeed = document.getElementById("stocks-in-focus-feed");
//   // NEW: Announcement DOM elements
//   const announcementTabsContainer =
//     document.getElementById("announcement-tabs");
//   const announcementContentContainer = document.getElementById(
//     "announcement-content"
//   );

//   async function fetchDashboardData() {
//     try {
//       const response = await fetch("/dashboard/api/live-data/");
//       if (!response.ok)
//         throw new Error(`HTTP error! status: ${response.status}`);
//       const data = await response.json();

//       // --- Trading Data Processing ---
//       data.live_trades.forEach((trade) => {
//         if (!priceHistories[trade.symbol]) {
//           priceHistories[trade.symbol] = [trade.currentPrice];
//         } else {
//           priceHistories[trade.symbol].push(trade.currentPrice);
//           if (priceHistories[trade.symbol].length > 30)
//             priceHistories[trade.symbol].shift();
//         }
//         trade.priceHistory = priceHistories[trade.symbol];
//       });
//       liveTrades = data.live_trades;

//       renderOpenPositions();
//       renderPortfolioSummary();
//       renderClosedTrades(data.closed_trades);

//       // --- CNBC News Handling ---
//       const newNewsDataString = JSON.stringify(data.market_news);
//       if (newNewsDataString !== lastNewsDataString) {
//         lastNewsDataString = newNewsDataString;
//         renderRegularNews(data.market_news.regular);
//         renderStocksToWatch(data.market_news.watch_list);
//       }

//       // --- NEW: NSE Announcements Handling ---
//       const newAnnouncementsDataString = JSON.stringify(data.nse_announcements);
//       if (newAnnouncementsDataString !== lastAnnouncementsDataString) {
//         lastAnnouncementsDataString = newAnnouncementsDataString;
//         renderNseAnnouncements(data.nse_announcements);
//       }
//     } catch (error) {
//       console.error("Failed to fetch dashboard data:", error);
//       // Update UI to show errors
//     }
//   }

//   // --- NEW: Function to render NSE Announcements ---
//   function renderNseAnnouncements(announcements) {
//     if (!announcementTabsContainer || !announcementContentContainer) return;

//     const categories = Object.keys(announcements);

//     if (categories.length === 0) {
//       announcementTabsContainer.innerHTML = `<div class="text-center text-gray-500 p-4 w-full">No announcements found.</div>`;
//       announcementContentContainer.innerHTML = "";
//       return;
//     }

//     announcementTabsContainer.innerHTML = "";
//     announcementContentContainer.innerHTML = "";

//     categories.forEach((category, index) => {
//       // Create Tab Button
//       const tabButton = document.createElement("button");
//       tabButton.className =
//         "tab-btn px-4 py-2 text-sm font-semibold text-gray-400";
//       tabButton.dataset.tab = `announcement-pane-${index}`;
//       tabButton.textContent = `${category} (${announcements[category].length})`;
//       if (index === 0) {
//         tabButton.classList.add("active");
//         tabButton.classList.remove("text-gray-400");
//         tabButton.classList.add("text-violet-400");
//       }
//       announcementTabsContainer.appendChild(tabButton);

//       // Create Content Pane
//       const contentPane = document.createElement("div");
//       contentPane.id = `announcement-pane-${index}`;
//       contentPane.className = "tab-content";
//       if (index === 0) {
//         contentPane.classList.add("active");
//       }

//       let tableHTML = `<div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-400 uppercase bg-gray-700/50"><tr><th class="p-3">Company</th><th class="p-3">Announcement</th><th class="p-3">Date</th><th class="p-3 text-center">Link</th></tr></thead><tbody class="divide-y divide-gray-700">`;
//       announcements[category].forEach((item) => {
//         tableHTML += `
//                   <tr>
//                       <td class="p-3 font-medium text-white align-top">${item.company}</td>
//                       <td class="p-3 text-gray-300 align-top">${item.description}</td>
//                       <td class="p-3 whitespace-nowrap align-top">${item.pub_date}</td>
//                       <td class="p-3 text-center align-top">
//                           <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="text-violet-400 hover:text-violet-300 font-bold">
//                               <i class="fas fa-file-pdf"></i>
//                           </a>
//                       </td>
//                   </tr>`;
//       });
//       tableHTML += "</tbody></table></div>";
//       contentPane.innerHTML = tableHTML;
//       announcementContentContainer.appendChild(contentPane);
//     });
//   }

//   function initTabs() {
//     // This function handles multiple tab systems on the page
//     const allTabContainers = document.querySelectorAll(
//       ".bg-gray-800.rounded-xl.shadow-lg"
//     );

//     allTabContainers.forEach((container) => {
//       const tabButtons = container.querySelectorAll(".tab-btn");
//       const tabContents = container.querySelectorAll(".tab-content");

//       if (tabButtons.length === 0) return;

//       tabButtons.forEach((button) => {
//         button.addEventListener("click", () => {
//           tabButtons.forEach((btn) =>
//             btn.classList.remove("active", "text-violet-400")
//           );
//           button.classList.add("active", "text-violet-400");

//           tabContents.forEach((content) => {
//             content.classList.remove("active");
//             if (content.id === button.dataset.tab) {
//               content.classList.add("active");
//             }
//           });
//         });
//       });
//     });
//   }

//   // --- All other rendering functions (renderOpenPositions, renderClosedTrades, etc.) remain unchanged ---

//   function renderRegularNews(newsData) {
//     if (!newsContainer) return;
//     if (!newsData || newsData.length === 0) {
//       newsContainer.innerHTML = `<div class="text-center text-gray-500 p-8">No news available at the moment.</div>`;
//       return;
//     }
//     newsContainer.innerHTML = "";
//     newsData.forEach((item, index) => {
//       let borderColor, textColor, bgColor;
//       switch (item.sentiment.toLowerCase()) {
//         case "positive":
//           borderColor = "border-green-500";
//           textColor = "text-green-300";
//           bgColor = "bg-green-500/10";
//           break;
//         case "negative":
//           borderColor = "border-red-500";
//           textColor = "text-red-300";
//           bgColor = "bg-red-500/10";
//           break;
//         default:
//           borderColor = "border-gray-600";
//           textColor = "text-gray-300";
//           bgColor = "bg-gray-500/10";
//           break;
//       }
//       const newsItem = document.createElement("div");
//       newsItem.className = `bg-gray-800/50 rounded-lg border-l-4 ${borderColor} mb-4`;
//       newsItem.innerHTML = `<div class="p-4"><div class="flex justify-between items-start gap-4"><div class="flex-grow"><div class="font-bold text-xs ${bgColor} ${textColor} px-3 py-1 rounded-full inline-block mb-2">${item.sentiment.toUpperCase()}: ${item.action.toUpperCase()} (${
//         item.confidence
//       }%)</div><a href="${
//         item.link
//       }" target="_blank" rel="noopener noreferrer" class="block font-semibold text-gray-200 hover:text-violet-400 transition-colors">${
//         item.headline
//       }</a><div class="text-xs text-gray-400 mt-1">${
//         item.publication_time
//       }</div></div><button class="read-more-btn flex-shrink-0 text-sm text-violet-400 hover:text-violet-300 font-semibold py-2 px-3 rounded-md hover:bg-gray-700 transition-colors" data-target="news-content-${index}">Read More</button></div><div id="news-content-${index}" class="news-full-text mt-4 pt-4 border-t border-gray-700 text-gray-400 text-sm leading-relaxed formatted-text" style="max-height: 0px;">${
//         item.full_text
//       }</div></div>`;
//       newsContainer.appendChild(newsItem);
//     });
//   }

//   function renderStocksToWatch(watchListData) {
//     if (!stocksInFocusFeed || !stocksInFocusContainer) return;
//     if (!watchListData || watchListData.length === 0) {
//       stocksInFocusContainer.classList.add("hidden");
//       return;
//     }
//     stocksInFocusContainer.classList.remove("hidden");
//     stocksInFocusFeed.innerHTML = "";
//     stocksInFocusFeed.className = "space-y-4";
//     watchListData.forEach((item) => {
//       let borderColor, textColor, bgColor;
//       switch (item.sentiment.toLowerCase()) {
//         case "positive":
//           borderColor = "border-green-500";
//           textColor = "text-green-300";
//           bgColor = "bg-green-500/10";
//           break;
//         case "negative":
//           borderColor = "border-red-500";
//           textColor = "text-red-300";
//           bgColor = "bg-red-500/10";
//           break;
//         default:
//           borderColor = "border-amber-500";
//           textColor = "text-amber-300";
//           bgColor = "bg-amber-500/10";
//           break;
//       }
//       const stockItem = document.createElement("div");
//       stockItem.className = `bg-gray-800/50 rounded-lg border-l-4 ${borderColor} p-4`;
//       stockItem.innerHTML = `<div class="flex-grow"><div class="flex flex-wrap items-center gap-x-3 gap-y-2 mb-3"><span class="font-bold text-xs ${bgColor} ${textColor} px-3 py-1 rounded-full whitespace-nowrap">${item.sentiment.toUpperCase()}: ${item.action.toUpperCase()} (${
//         item.confidence
//       }%)</span><span class="font-bold text-gray-200">${
//         item.stock_name
//       }</span></div><p class="text-xs text-gray-400 leading-relaxed formatted-text">${
//         item.text
//       }</p></div>`;
//       stocksInFocusFeed.appendChild(stockItem);
//     });
//   }

//   newsContainer.addEventListener("click", (event) => {
//     const button = event.target.closest(".read-more-btn");
//     if (!button) return;
//     const contentEl = document.getElementById(button.dataset.target);
//     if (!contentEl) return;
//     const isCollapsed = contentEl.style.maxHeight === "0px";
//     contentEl.style.maxHeight = isCollapsed
//       ? contentEl.scrollHeight + "px"
//       : "0px";
//     button.textContent = isCollapsed ? "Read Less" : "Read More";
//   });
//   // --- REWRITTEN: Function to render Stocks in Focus as a Table ---
//   function renderStocksInFocusTable(watchListData) {
//     if (!stocksInFocusBody) return;

//     stocksInFocusBody.innerHTML = ""; // Clear previous content

//     if (!watchListData || watchListData.length === 0) {
//       stocksInFocusBody.innerHTML = `
//         <tr>
//           <td colspan="3" class="text-center p-8 text-gray-500">
//             No specific stocks in focus at the moment.
//           </td>
//         </tr>`;
//       return;
//     }

//     watchListData.forEach((item) => {
//       let sentimentColor, sentimentBg;
//       switch (item.sentiment.toLowerCase()) {
//         case "positive":
//           sentimentColor = "text-green-300";
//           sentimentBg = "bg-green-500/10";
//           break;
//         case "negative":
//           sentimentColor = "text-red-300";
//           sentimentBg = "bg-red-500/10";
//           break;
//         default:
//           sentimentColor = "text-amber-300";
//           sentimentBg = "bg-amber-500/10";
//           break;
//       }

//       const row = document.createElement("tr");
//       row.innerHTML = `
//         <td class="p-3 font-medium text-white align-top">${item.stock_name}</td>
//         <td class="p-3 text-gray-300 align-top">${item.text}</td>
//         <td class="p-3 align-top">
//           <span class="font-bold text-xs ${sentimentColor} ${sentimentBg} px-3 py-1 rounded-full whitespace-nowrap">
//             ${item.sentiment.toUpperCase()}
//           </span>
//         </td>
//       `;
//       stocksInFocusBody.appendChild(row);
//     });
//   }
//   function renderOpenPositions() {
//     if (!openPositionsContainer) return;
//     if (liveTrades.length === 0) {
//       openPositionsContainer.innerHTML = `<div class="text-center text-gray-500 p-8">No open positions.</div>`;
//       return;
//     }
//     const groupedByAssetClass = liveTrades.reduce((acc, trade) => {
//       (acc[trade.assetClass] = acc[trade.assetClass] || []).push(trade);
//       return acc;
//     }, {});
//     openPositionsContainer.innerHTML = "";
//     for (const assetClass in groupedByAssetClass) {
//       const assetClassDiv = document.createElement("div");
//       assetClassDiv.className = "space-y-6";
//       assetClassDiv.innerHTML = `<h3 class="text-md font-semibold text-teal-400 border-b border-gray-700 pb-2">${assetClass}</h3>`;
//       const tradesInClass = groupedByAssetClass[assetClass];
//       const groupedByStrategy = tradesInClass.reduce((acc, trade) => {
//         (acc[trade.strategy] = acc[trade.strategy] || []).push(trade);
//         return acc;
//       }, {});
//       for (const strategy in groupedByStrategy) {
//         const strategyDiv = document.createElement("div");
//         const strategyTrades = groupedByStrategy[strategy];
//         const totalStrategyPnl = strategyTrades.reduce(
//           (pnl, t) => pnl + (t.currentPrice - t.entryPrice) * t.qty,
//           0
//         );
//         const pnlClass =
//           totalStrategyPnl >= 0 ? "text-green-400" : "text-red-400";
//         let tableHTML = `<div class="flex justify-between items-center mb-2"><h4 class="text-sm font-semibold text-gray-300">${strategy}</h4><span class="text-xs font-mono p-1 rounded ${pnlClass} bg-opacity-10 bg-gray-700">P/L: ${totalStrategyPnl.toLocaleString(
//           "en-IN",
//           { minimumFractionDigits: 2, maximumFractionDigits: 2 }
//         )}</span></div><div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-400 uppercase bg-gray-700/50"><tr><th class="p-3">Symbol</th><th class="p-3">Qty</th><th class="p-3">Entry Price</th><th class="p-3">Current Price</th><th class="p-3">Unrealized P/L</th><th class="p-3">7-Day Trend</th><th class="p-3 text-center">Actions</th></tr></thead><tbody class="divide-y divide-gray-700 align-middle">`;
//         strategyTrades.forEach((trade) => {
//           const pnl = (trade.currentPrice - trade.entryPrice) * trade.qty;
//           const pnlPct =
//             trade.entryPrice === 0
//               ? 0
//               : ((trade.currentPrice - trade.entryPrice) / trade.entryPrice) *
//                 100;
//           const pnlCellClass = pnl >= 0 ? "text-green-400" : "text-red-500";
//           const dayChange = trade.currentPrice - trade.dayOpen;
//           const dayChangePct =
//             trade.dayOpen === 0 ? 0 : (dayChange / trade.dayOpen) * 100;
//           const dayChangeClass =
//             dayChange >= 0 ? "text-green-400" : "text-red-500";
//           const tradeIndex = liveTrades.indexOf(trade);
//           tableHTML += `<tr><td class="p-3 font-medium text-white">${
//             trade.symbol
//           }</td><td class="p-3">${
//             trade.qty
//           }</td><td class="p-3">${trade.entryPrice.toFixed(
//             2
//           )}</td><td class="p-3 font-semibold">${trade.currentPrice.toFixed(
//             2
//           )} <span class="text-xs ${dayChangeClass}">(${dayChangePct.toFixed(
//             2
//           )}%)</span></td><td class="p-3 font-semibold rounded-md" data-pnl-cell="true"><div class="${pnlCellClass}">₹${pnl.toLocaleString(
//             "en-IN",
//             { minimumFractionDigits: 2, maximumFractionDigits: 2 }
//           )} <span class="text-xs">(${pnlPct.toFixed(
//             2
//           )}%)</span></div></td><td class="p-3"><canvas id="sparkline-${tradeIndex}" width="100" height="30"></canvas></td><td class="p-3 text-center"><button class="text-red-500 hover:text-red-400 text-xs font-semibold">CLOSE</button></td></tr>`;
//         });
//         tableHTML += `</tbody></table></div>`;
//         strategyDiv.innerHTML = tableHTML;
//         assetClassDiv.appendChild(strategyDiv);
//       }
//       openPositionsContainer.appendChild(assetClassDiv);
//     }
//     renderSparklines();
//   }

//   function renderClosedTrades(trades) {
//     if (!closedTradesContainer) return;
//     if (!trades || trades.length === 0) {
//       closedTradesContainer.innerHTML = `<tr><td colspan="5" class="text-center p-8 text-gray-500">No closed trades found.</td></tr>`;
//       return;
//     }
//     closedTradesContainer.innerHTML = "";
//     trades.forEach((trade) => {
//       const pnlClass = trade.pnl >= 0 ? "text-green-400" : "text-red-500";
//       const row = document.createElement("tr");
//       row.innerHTML = `<td class="p-3 font-medium text-white">${
//         trade.symbol
//       }</td><td class="p-3 font-semibold ${pnlClass}">₹${trade.pnl.toLocaleString(
//         "en-IN",
//         { minimumFractionDigits: 2, maximumFractionDigits: 2 }
//       )}</td><td class="p-3">${trade.entryDate}</td><td class="p-3">${
//         trade.exitDate
//       }</td><td class="p-3">${trade.reason}</td>`;
//       closedTradesContainer.appendChild(row);
//     });
//   }

//   function renderSparklines() {
//     liveTrades.forEach((trade, index) => {
//       const canvas = document.getElementById(`sparkline-${index}`);
//       if (!canvas || !trade.priceHistory || trade.priceHistory.length < 2)
//         return;
//       const ctx = canvas.getContext("2d");
//       ctx.clearRect(0, 0, canvas.width, canvas.height);
//       const prices = trade.priceHistory;
//       const maxPrice = Math.max(...prices);
//       const minPrice = Math.min(...prices);
//       const range = maxPrice - minPrice || 1;
//       ctx.beginPath();
//       ctx.moveTo(
//         0,
//         canvas.height - ((prices[0] - minPrice) / range) * canvas.height
//       );
//       for (let i = 1; i < prices.length; i++) {
//         ctx.lineTo(
//           (i / (prices.length - 1)) * canvas.width,
//           canvas.height - ((prices[i] - minPrice) / range) * canvas.height
//         );
//       }
//       ctx.strokeStyle =
//         prices[prices.length - 1] >= prices[0] ? "#4ade80" : "#f87171";
//       ctx.lineWidth = 1.5;
//       ctx.stroke();
//     });
//   }

//   function renderPortfolioSummary() {
//     const totalInvestment = liveTrades.reduce(
//       (acc, trade) => acc + trade.entryPrice * trade.qty,
//       0
//     );
//     const currentValue = liveTrades.reduce(
//       (acc, trade) => acc + trade.currentPrice * trade.qty,
//       0
//     );
//     const overallPnl = currentValue - totalInvestment;
//     const overallPnlPct =
//       totalInvestment === 0 ? 0 : (overallPnl / totalInvestment) * 100;
//     const dayOpenValue = liveTrades.reduce(
//       (acc, trade) => acc + trade.dayOpen * trade.qty,
//       0
//     );
//     const todaysPnl = currentValue - dayOpenValue;
//     const todaysPnlPct =
//       dayOpenValue === 0 ? 0 : (todaysPnl / dayOpenValue) * 100;
//     const overallPnlClass = overallPnl >= 0 ? "text-green-400" : "text-red-400";
//     const todaysPnlClass = todaysPnl >= 0 ? "text-green-400" : "text-red-400";
//     totalInvestmentEl.textContent = `₹${totalInvestment.toLocaleString(
//       "en-IN",
//       { minimumFractionDigits: 2, maximumFractionDigits: 2 }
//     )}`;
//     currentValueEl.textContent = `₹${currentValue.toLocaleString("en-IN", {
//       minimumFractionDigits: 2,
//       maximumFractionDigits: 2,
//     })}`;
//     pnlValueEl.textContent = `₹${overallPnl.toLocaleString("en-IN", {
//       minimumFractionDigits: 2,
//       maximumFractionDigits: 2,
//     })}`;
//     pnlValueEl.className = `font-semibold ${overallPnlClass}`;
//     pnlPctEl.textContent = `(${overallPnlPct.toFixed(2)}%)`;
//     pnlPctEl.className = `text-sm ml-2 ${overallPnlClass}`;
//     todaysPnlValueEl.textContent = `₹${todaysPnl.toLocaleString("en-IN", {
//       minimumFractionDigits: 2,
//       maximumFractionDigits: 2,
//     })}`;
//     todaysPnlValueEl.className = `font-semibold ${todaysPnlClass}`;
//     todaysPnlPctEl.textContent = `(${todaysPnlPct.toFixed(2)}%)`;
//     todaysPnlPctEl.className = `text-sm ml-2 ${todaysPnlClass}`;
//   }

//   function init() {
//     console.log("Initializing Dashboard...");
//     document.body.addEventListener("click", function (event) {
//       const button = event.target.closest(".tab-btn");
//       if (button) {
//         const parentContainer = button.closest(".bg-gray-800");
//         const allButtons = parentContainer.querySelectorAll(".tab-btn");
//         const allContent = parentContainer.querySelectorAll(".tab-content");

//         allButtons.forEach((btn) => {
//           btn.classList.remove("active", "text-violet-400");
//           btn.classList.add("text-gray-400");
//         });

//         button.classList.add("active", "text-violet-400");
//         button.classList.remove("text-gray-400");

//         allContent.forEach((content) => {
//           content.classList.remove("active");
//         });

//         const contentToShow = parentContainer.querySelector(
//           `#${button.dataset.tab}`
//         );
//         if (contentToShow) contentToShow.classList.add("active");
//       }
//     });

//     fetchDashboardData();
//     setInterval(fetchDashboardData, 60000); // Refresh every 60 seconds
//   }

//   init();
// });

// static/dashboard/js/dashboard.js

document.addEventListener("DOMContentLoaded", function () {
  // --- State Variables ---
  let liveTrades = [];
  let priceHistories = {};
  let lastNewsDataString = "";
  let lastAnnouncementsDataString = "";

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
  const totalInvestmentEl = document.getElementById("total-investment");
  const currentValueEl = document.getElementById("current-value");
  const pnlValueEl = document.getElementById("pnl-value");
  const pnlPctEl = document.getElementById("pnl-pct");
  const todaysPnlValueEl = document.getElementById("todays-pnl-value");
  const todaysPnlPctEl = document.getElementById("todays-pnl-pct");

  /**
   * Fetches all necessary data from the API endpoint and orchestrates rendering.
   */
  async function fetchDashboardData() {
    try {
      const response = await fetch("/dashboard/api/live-data/");
      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();

      // --- Process and Render Trading Data ---
      data.live_trades.forEach((trade) => {
        if (!priceHistories[trade.symbol]) {
          priceHistories[trade.symbol] = [trade.currentPrice];
        } else {
          priceHistories[trade.symbol].push(trade.currentPrice);
          if (priceHistories[trade.symbol].length > 30) {
            priceHistories[trade.symbol].shift();
          }
        }
        trade.priceHistory = priceHistories[trade.symbol];
      });
      liveTrades = data.live_trades;

      renderOpenPositions();
      renderPortfolioSummary();
      renderClosedTrades(data.closed_trades);

      // --- Process and Render News (if changed) ---
      const newNewsDataString = JSON.stringify(data.market_news);
      if (newNewsDataString !== lastNewsDataString) {
        console.log("New news data detected. Rendering news feeds.");
        lastNewsDataString = newNewsDataString;
        renderRegularNews(data.market_news.regular);
        renderStocksInFocusTable(data.market_news.watch_list);
      }

      // --- Process and Render Announcements (if changed) ---
      const newAnnouncementsDataString = JSON.stringify(data.nse_announcements);
      if (newAnnouncementsDataString !== lastAnnouncementsDataString) {
        console.log("New announcement data detected. Rendering announcements.");
        lastAnnouncementsDataString = newAnnouncementsDataString;
        renderNseAnnouncements(data.nse_announcements);
      }
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      if (openPositionsContainer)
        openPositionsContainer.innerHTML = `<div class="text-center text-red-500 p-8">Could not load live data.</div>`;
      if (newsContainer)
        newsContainer.innerHTML = `<div class="text-center text-red-500 p-8">Could not load news feed.</div>`;
      if (stocksInFocusBody)
        stocksInFocusBody.innerHTML = `<tr><td colspan="3" class="text-center text-red-500 p-8">Could not load stocks in focus.</td></tr>`;
      if (announcementTabsContainer)
        announcementTabsContainer.innerHTML = `<div class="text-center text-red-500 p-8">Could not load announcements.</div>`;
    }
  }

  /**
   * Renders the "Stocks in Focus" section as a table.
   * @param {Array} watchListData - Array of stock watch list objects.
   */
  function renderStocksInFocusTable(watchListData) {
    if (!stocksInFocusBody) return;

    stocksInFocusBody.innerHTML = ""; // Clear previous content

    if (!watchListData || watchListData.length === 0) {
      stocksInFocusBody.innerHTML = `
        <tr>
          <td colspan="3" class="text-center p-8 text-gray-500">
            No specific stocks in focus at the moment.
          </td>
        </tr>`;
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
      row.innerHTML = `
        <td class="p-3 font-medium text-white align-top">${item.stock_name}</td>
        <td class="p-3 text-gray-300 align-top">${item.text}</td>
        <td class="p-3 align-top">
          <span class="font-bold text-xs ${sentimentColor} ${sentimentBg} px-3 py-1 rounded-full whitespace-nowrap">
            ${item.sentiment.toUpperCase()}
          </span>
        </td>
      `;
      stocksInFocusBody.appendChild(row);
    });
  }

  /**
   * Renders the main market news feed.
   * @param {Array} newsData - Array of news article objects.
   */
  function renderRegularNews(newsData) {
    if (!newsContainer) return;
    if (!newsData || newsData.length === 0) {
      newsContainer.innerHTML = `<div class="text-center text-gray-500 p-8">No news available at the moment.</div>`;
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

  /**
   * Renders the tabbed table for NSE Corporate Announcements.
   * @param {Object} announcements - An object with categories as keys and announcement arrays as values.
   */
  function renderNseAnnouncements(announcements) {
    if (!announcementTabsContainer || !announcementContentContainer) return;

    const categories = Object.keys(announcements).sort(); // Sort categories alphabetically

    if (categories.length === 0) {
      announcementTabsContainer.innerHTML = `<div class="text-center text-gray-500 p-4 w-full">No announcements found.</div>`;
      announcementContentContainer.innerHTML = "";
      return;
    }

    announcementTabsContainer.innerHTML = "";
    announcementContentContainer.innerHTML = "";

    categories.forEach((category, index) => {
      const tabId = `announcement-pane-${index}`;

      // Create Tab Button
      const tabButton = document.createElement("button");
      tabButton.className =
        "tab-btn px-4 py-2 text-sm font-semibold text-gray-400";
      tabButton.dataset.tab = tabId;
      tabButton.textContent = `${category} (${announcements[category].length})`;

      // Create Content Pane
      const contentPane = document.createElement("div");
      contentPane.id = tabId;
      contentPane.className = "tab-content";

      let tableHTML = `<div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-400 uppercase bg-gray-700/50"><tr><th class="p-3">Company</th><th class="p-3">Announcement</th><th class="p-3">Date</th><th class="p-3 text-center">Link</th></tr></thead><tbody class="divide-y divide-gray-700">`;
      announcements[category].forEach((item) => {
        tableHTML += `
          <tr>
            <td class="p-3 font-medium text-white align-top">${item.company}</td>
            <td class="p-3 text-gray-300 align-top">${item.description}</td>
            <td class="p-3 whitespace-nowrap align-top">${item.pub_date}</td>
            <td class="p-3 text-center align-top">
              <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="text-violet-400 hover:text-violet-300 font-bold">
                  <i class="fas fa-file-alt"></i>
              </a>
            </td>
          </tr>`;
      });
      tableHTML += "</tbody></table></div>";
      contentPane.innerHTML = tableHTML;

      // Set first tab as active
      if (index === 0) {
        tabButton.classList.add("active", "text-violet-400");
        tabButton.classList.remove("text-gray-400");
        contentPane.classList.add("active");
      }

      announcementTabsContainer.appendChild(tabButton);
      announcementContentContainer.appendChild(contentPane);
    });
  }

  /**
   * Renders the portfolio summary cards.
   */
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

  /**
   * Renders the table of open positions.
   */
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
        )}</span></div><div class="overflow-x-auto"><table class="w-full text-sm text-left text-gray-400"><thead class="text-xs text-gray-400 uppercase bg-gray-700/50"><tr><th class="p-3">Symbol</th><th class="p-3">Qty</th><th class="p-3">Entry Price</th><th class="p-3">Current Price</th><th class="p-3">Unrealized P/L</th><th class="p-3">7-Day Trend</th><th class="p-3 text-center">Actions</th></tr></thead><tbody class="divide-y divide-gray-700 align-middle">`;
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

  /**
   * Renders the price trend sparklines.
   */
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

  /**
   * Renders the table of closed trades.
   */
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

  /**
   * Initializes the dashboard, sets up event listeners and starts the data fetch interval.
   */
  function init() {
    console.log("Initializing Dashboard...");

    // Generic event listener for all tab systems
    document.body.addEventListener("click", function (event) {
      const button = event.target.closest(".tab-btn");
      if (button) {
        const parentContainer = button.closest(".bg-gray-800");
        if (!parentContainer) return;

        const allButtons = parentContainer.querySelectorAll(".tab-btn");
        const allContent = parentContainer.querySelectorAll(".tab-content");

        allButtons.forEach((btn) => {
          btn.classList.remove("active", "text-violet-400");
          btn.classList.add("text-gray-400");
        });

        button.classList.add("active", "text-violet-400");
        button.classList.remove("text-gray-400");

        allContent.forEach((content) => {
          content.classList.remove("active");
        });

        const contentToShow = parentContainer.querySelector(
          `#${button.dataset.tab}`
        );
        if (contentToShow) contentToShow.classList.add("active");
      }
    });

    // Event listener for expanding news articles
    if (newsContainer) {
      newsContainer.addEventListener("click", (event) => {
        const button = event.target.closest(".read-more-btn");
        if (!button) return;
        const contentEl = document.getElementById(button.dataset.target);
        if (!contentEl) return;
        const isCollapsed = contentEl.style.maxHeight === "0px";
        contentEl.style.maxHeight = isCollapsed
          ? contentEl.scrollHeight + "px"
          : "0px";
        button.textContent = isCollapsed ? "Read Less" : "Read More";
      });
    }

    fetchDashboardData();
    setInterval(fetchDashboardData, 60000); // Refresh data every 60 seconds
  }

  init();
});
