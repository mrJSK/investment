// fundamentals/static/fundamentals/js/custom_screener.js

$(document).ready(function () {
  let currentSortBy = "market_cap"; // Default sort for screener table
  let currentOrder = "desc"; // Default order for screener table

  function fetchCustomScreenerCompanies() {
    $("#screener_loading_indicator").show();
    $("#screener_companies_table tbody").empty();

    const min_roce = $("#min_roce").val();
    const min_roe = $("#min_roe").val();
    const min_profit_growth_5yr = $("#min_profit_growth_5yr").val();
    const max_pe = $("#max_pe").val();
    const max_pb = $("#max_pb").val();
    const industry_id = $("#industry_filter").val();

    const params = {
      min_roce: min_roce,
      min_roe: min_roe,
      min_profit_growth_5yr: min_profit_growth_5yr,
      max_pe: max_pe,
      max_pb: max_pb,
      industry: industry_id,
      sort_by: currentSortBy,
      order: currentOrder,
    };

    $.ajax({
      url: "/fundamentals/api/custom-screener/", // Custom screener API endpoint
      type: "GET",
      data: params,
      success: function (data) {
        $("#screener_loading_indicator").hide();
        const tbody = $("#screener_companies_table tbody");
        if (data.length === 0) {
          tbody.append(
            '<tr><td colspan="12">No companies found matching your custom criteria.</td></tr>'
          );
          return;
        }

        data.forEach((company) => {
          const row = `
                        <tr>
                            <td>${company.name}</td>
                            <td><a href="/fundamentals/api/company/${
                              company.symbol
                            }/">${company.symbol}</a></td>
                            <td>${
                              company.market_cap !== null
                                ? company.market_cap.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.current_price !== null
                                ? company.current_price.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.stock_pe !== null
                                ? company.stock_pe.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.book_value !== null
                                ? company.book_value.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.price_to_book !== null
                                ? company.price_to_book.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.dividend_yield !== null
                                ? company.dividend_yield.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.roce !== null
                                ? company.roce.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.roe !== null
                                ? company.roe.toFixed(2)
                                : "N/A"
                            }</td>
                            <td>${
                              company.compounded_profit_growth_5yr !== null
                                ? company.compounded_profit_growth_5yr.toFixed(
                                    2
                                  )
                                : "N/A"
                            }</td>
                            <td>${company.industry}</td>
                        </tr>
                    `;
          tbody.append(row);
        });
      },
      error: function (xhr, status, error) {
        $("#screener_loading_indicator").hide();
        console.error(
          "Error fetching custom screener companies:",
          status,
          error
        );
        $("#screener_companies_table tbody").html(
          '<tr><td colspan="12">Error loading data. Please try again.</td></tr>'
        );
      },
    });
  }

  // Event listener for Apply Filters button on custom screener page
  $("#apply_filters").on("click", function () {
    fetchCustomScreenerCompanies();
  });

  // Event listener for Clear Filters button on custom screener page
  $("#clear_filters").on("click", function () {
    $("#min_roce").val("");
    $("#min_roe").val("");
    $("#min_profit_growth_5yr").val("");
    $("#max_pe").val("");
    $("#max_pb").val("");
    $("#industry_filter").val("");
    currentSortBy = "market_cap"; // Reset sort
    currentOrder = "desc"; // Reset order
    fetchCustomScreenerCompanies();
  });

  // Event listeners for table header sorting on custom screener page
  $("#screener_companies_table thead th").on("click", function () {
    const sortBy = $(this).data("sort-by");
    if (sortBy) {
      if (currentSortBy === sortBy) {
        currentOrder = currentOrder === "asc" ? "desc" : "asc";
      } else {
        currentSortBy = sortBy;
        currentOrder = "asc";
      }
      fetchCustomScreenerCompanies();
    }
  });

  // Initial fetch of companies when the custom screener page loads
  fetchCustomScreenerCompanies();
});
