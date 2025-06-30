// fundamentals/static/fundamentals/js/fundamentals_dashboard.js

$(document).ready(function () {
  let allStrongCompaniesData = []; // To store the full fetched strong companies data for client-side search
  let allUndervaluedCompaniesData = []; // To store the full fetched undervalued companies data

  // Sort states for strong companies table
  let strongCompaniesSortBy = "market_cap_category";
  let strongCompaniesSortOrder = "asc";

  // Sort states for undervalued companies table
  let undervaluedCompaniesSortBy = "stock_pe"; // Default for undervalued
  let undervaluedCompaniesSortOrder = "asc";

  // Function to render a generic table based on provided data and table ID
  function renderTable(tableId, dataToRender, colspanCount) {
    const tbody = $(`#${tableId} tbody`);
    tbody.empty();

    if (dataToRender.length === 0) {
      tbody.append(
        `<tr><td colspan="${colspanCount}" class="text-center py-4 text-gray-500">No companies found matching criteria.</td></tr>`
      );
      return;
    }

    dataToRender.forEach((company) => {
      let row = `<tr class="table-body-row">`;

      // Special handling for strong_companies_table's category column
      if (tableId === "strong_companies_table") {
        row += `<td class="table-body-cell">${company.market_cap_category}</td>`;
      }

      row += `
                <td class="table-body-cell">${company.name}</td>
                <td class="table-body-cell"><a href="/fundamentals/api/company/${
                  company.symbol
                }/" class="hover:underline">${company.symbol}</a></td>
                <td class="table-body-cell">${
                  company.market_cap !== null
                    ? company.market_cap.toFixed(2)
                    : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.current_price !== null
                    ? company.current_price.toFixed(2)
                    : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.stock_pe !== null
                    ? company.stock_pe.toFixed(2)
                    : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.book_value !== null
                    ? company.book_value.toFixed(2)
                    : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.price_to_book !== null
                    ? company.price_to_book.toFixed(2)
                    : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.dividend_yield !== null
                    ? company.dividend_yield.toFixed(2)
                    : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.roce !== null ? company.roce.toFixed(2) : "N/A"
                }</td>
                <td class="table-body-cell">${
                  company.roe !== null ? company.roe.toFixed(2) : "N/A"
                }</td>
            `;
      // Only include profit growth for strong companies table as it's part of its criteria
      if (tableId === "strong_companies_table") {
        row += `<td class="table-body-cell">${
          company.compounded_profit_growth_5yr !== null
            ? company.compounded_profit_growth_5yr.toFixed(2)
            : "N/A"
        }</td>`;
      }
      row += `<td class="table-body-cell">${company.industry}</td>`;
      row += `</tr>`;
      tbody.append(row);
    });
  }

  // Fetch and populate the main table with strong companies by market cap
  function fetchStrongCompaniesByMarketCap() {
    $("#loading_indicator_strong").show();

    const params = {
      sort_by: strongCompaniesSortBy,
      order: strongCompaniesSortOrder,
    };

    $.ajax({
      url: "/fundamentals/api/strong-companies-by-market-cap/",
      type: "GET",
      data: params,
      success: function (data) {
        $("#loading_indicator_strong").hide();
        allStrongCompaniesData = data; // Store the fetched data
        renderTable("strong_companies_table", allStrongCompaniesData, 13); // Render initially
      },
      error: function (xhr, status, error) {
        $("#loading_indicator_strong").hide();
        console.error("Error fetching strong companies:", status, error);
        $("#strong_companies_table tbody").html(
          '<tr class="table-body-row"><td colspan="13" class="text-center py-4 text-red-400">Error loading data. Please try again.</td></tr>'
        );
      },
    });
  }

  // Fetch and populate the new table with undervalued companies
  function fetchUndervaluedCompanies() {
    $("#loading_indicator_undervalued").show();

    const params = {
      sort_by: undervaluedCompaniesSortBy,
      order: undervaluedCompaniesSortOrder,
    };

    $.ajax({
      url: "/fundamentals/api/undervalued-companies/", // NEW API endpoint
      type: "GET",
      data: params,
      success: function (data) {
        $("#loading_indicator_undervalued").hide();
        allUndervaluedCompaniesData = data; // Store the fetched data
        renderTable(
          "undervalued_companies_table",
          allUndervaluedCompaniesData,
          11
        ); // Render initially (11 columns for this table)
      },
      error: function (xhr, status, error) {
        $("#loading_indicator_undervalued").hide();
        console.error("Error fetching undervalued companies:", status, error);
        $("#undervalued_companies_table tbody").html(
          '<tr class="table-body-row"><td colspan="11" class="text-center py-4 text-red-400">Error loading data. Please try again.</td></tr>'
        );
      },
    });
  }

  // Event listener for strong companies table header sorting
  $("#strong_companies_table thead th").on("click", function () {
    const sortBy = $(this).data("sort-by");
    if (sortBy) {
      if (strongCompaniesSortBy === sortBy) {
        strongCompaniesSortOrder =
          strongCompaniesSortOrder === "asc" ? "desc" : "asc";
      } else {
        strongCompaniesSortBy = sortBy;
        strongCompaniesSortOrder = "asc";
      }
      fetchStrongCompaniesByMarketCap();
    }
  });

  // Event listener for undervalued companies table header sorting
  $("#undervalued_companies_table thead th").on("click", function () {
    const sortBy = $(this).data("sort-by");
    if (sortBy) {
      if (undervaluedCompaniesSortBy === sortBy) {
        undervaluedCompaniesSortOrder =
          undervaluedCompaniesSortOrder === "asc" ? "desc" : "asc";
      } else {
        undervaluedCompaniesSortBy = sortBy;
        undervaluedCompaniesSortOrder = "asc";
      }
      fetchUndervaluedCompanies();
    }
  });

  // Client-side search functionality (only applies to strong companies table)
  $("#company_search_input").on("input", function () {
    const searchTerm = $(this).val().toLowerCase();
    if (allStrongCompaniesData.length === 0) return;

    const filteredData = allStrongCompaniesData.filter((company) => {
      return (
        (company.name && company.name.toLowerCase().includes(searchTerm)) ||
        (company.symbol && company.symbol.toLowerCase().includes(searchTerm))
      );
    });
    renderTable("strong_companies_table", filteredData, 13); // Render with filtered data
  });

  // Initial fetches when the page loads
  // fetchSidebarCompanyList(); // Removed sidebar
  fetchStrongCompaniesByMarketCap();
  fetchUndervaluedCompanies(); // Fetch undervalued companies as well
});
