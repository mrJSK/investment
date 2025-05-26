let featureConfigs = [];
let nextFeatureId = 1;
let modalFeatureId = "";
const PROGRESS_STEPS = [
  { pct: 10, msg: "Loading stock data..." },
  { pct: 55, msg: "Training model..." },
  { pct: 85, msg: "Generating report..." },
  { pct: 100, msg: "Done!" },
];
let previousResults = [];

// Fetch previous runs and populate dropdown
function loadPreviousResults() {
  fetch("/ml/previous/")
    .then((res) => res.json())
    .then((data) => {
      previousResults = data.results || [];
      let options = previousResults.map(
        (r) =>
          `<option value="${r.hash}">${r.name || r.hash} (${
            r.date || ""
          })</option>`
      );
      $("#previous-results").html(
        `<option value="">Select Previous Training</option>` + options.join("")
      );
    });
}
$(document).ready(function () {
  loadPreviousResults();
  $("#previous-results").on("change", function () {
    let hash = $(this).val();
    if (!hash) return;
    fetch(`/ml/result/?hash=${hash}`)
      .then((res) => res.json())
      .then((result) => showResult(result));
  });
});

// Select2 picker
$("#feature-picker").select2({
  placeholder: "Add indicator...",
  allowClear: true,
  minimumResultsForSearch: 1,
});
$("#feature-picker").on("select2:select", function (e) {
  const selected = e.params.data.id;
  featureConfigs.push({
    type: selected,
    id: selected + "_" + nextFeatureId++,
    args: { ...TALIB_ARGS[selected] },
  });
  renderFeatureCards();
  $("#feature-picker").val(null).trigger("change");
});
function showProgressStep(step) {
  let bar = document.getElementById("progress-bar");
  bar.style.width = PROGRESS_STEPS[step].pct + "%";
  bar.innerText = PROGRESS_STEPS[step].msg;
  document.getElementById("progress-stats").innerText =
    PROGRESS_STEPS[step].msg;
}
function renderFeatureCards() {
  let html = "";
  featureConfigs.forEach((feat, idx) => {
    let argString = Object.entries(feat.args)
      .map(([k, v]) => v)
      .join(", ");
    html += `
      <div class="feature-card">
        <span class="feature-label">
          <i class="bi bi-activity"></i> ${feat.type} ${
      argString
        ? `<span style="font-weight:400;color:#115299;">${argString}</span>`
        : ""
    }
        </span>
        <button type="button" class="icon-btn" onclick="openSettingsModal('${
          feat.id
        }')" title="Configure">
          <i class="bi bi-gear-fill"></i>
        </button>
        <button type="button" class="remove-btn" onclick="removeFeature('${
          feat.id
        }')">Remove</button>
      </div>`;
  });
  $("#feature-cards").html(html);
}
window.openSettingsModal = function (fid) {
  modalFeatureId = fid;
  const feat = featureConfigs.find((f) => f.id === fid);
  if (!feat) return;
  let formHtml = "";
  Object.entries(feat.args).forEach(([aname, aval]) => {
    if (aname === "price") {
      formHtml += `
        <div class="mb-2"><label>${aname}:</label>
          <select class="form-select form-select-sm" name="${aname}">
            <option value="open" ${
              aval == "open" ? "selected" : ""
            }>Open</option>
            <option value="high" ${
              aval == "high" ? "selected" : ""
            }>High</option>
            <option value="low" ${aval == "low" ? "selected" : ""}>Low</option>
            <option value="close" ${
              aval == "close" ? "selected" : ""
            }>Close</option>
          </select>
        </div>
      `;
    } else {
      formHtml += `
        <div class="mb-2"><label>${aname}:</label>
          <input type="number" class="form-control form-control-sm" name="${aname}" value="${aval}">
        </div>
      `;
    }
  });
  $("#featureSettingsForm").html(formHtml);
  var myModal = new bootstrap.Modal(
    document.getElementById("featureSettingsModal")
  );
  myModal.show();
};
window.saveFeatureSettings = function () {
  const feat = featureConfigs.find((f) => f.id === modalFeatureId);
  if (feat) {
    $("#featureSettingsForm")
      .serializeArray()
      .forEach(({ name, value }) => {
        feat.args[name] = value;
      });
  }
  bootstrap.Modal.getInstance(
    document.getElementById("featureSettingsModal")
  ).hide();
  renderFeatureCards();
};
window.removeFeature = function (fid) {
  featureConfigs = featureConfigs.filter((f) => f.id !== fid);
  renderFeatureCards();
};

document.getElementById("ml-form").onsubmit = async function (e) {
  e.preventDefault();
  document.getElementById("result-area").innerHTML = ""; // Clear previous results
  document.getElementById("progress-area").style.display = "";
  showProgressStep(0);

  const form = e.target;
  const data = new FormData(form);
  data.append("feature_configs", JSON.stringify(featureConfigs));
  setTimeout(() => showProgressStep(1), 900);
  setTimeout(() => showProgressStep(2), 2100);

  let result;
  try {
    let response = await fetch("/ml/train/", {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      body: data,
    });
    result = await response.json();
    showProgressStep(3);
    setTimeout(() => {
      document.getElementById("progress-area").style.display = "none";
      showResult(result);
    }, 800);
  } catch (err) {
    document.getElementById("progress-area").style.display = "none";
    document.getElementById("result-area").innerHTML = `
      <div class="alert alert-danger mt-3">
        Error during training. Please try again.<br>
        <small>${err && err.message ? err.message : ""}</small>
      </div>
    `;
  }
};

function showResult(result) {
  let html = "";
  if (!result || result.status !== "success") {
    html = `
      <div class="alert alert-danger mt-3">
        <b>Training failed!</b><br>
        ${result && result.error ? result.error : "Unknown error"}
      </div>
      <pre class="mt-2" style="background:#f9fbe7;max-height:200px;overflow:auto;">${
        result && result.logs ? result.logs : ""
      }</pre>
    `;
    document.getElementById("result-area").innerHTML = html;
    return;
  }
  let summary_html = `
    <div class="metrics-card p-3 mb-2">
      <h6>Status</h6>
      <span style="color:#43a047;font-weight:bold;">Training completed successfully.</span>
    </div>
    <div class="metrics-card p-3 mb-2">
      <h6>Report</h6>
      <div>${result.report_html || "No details available."}</div>
    </div>
  `;
  html = `
    <ul class="nav nav-tabs mb-2" id="resultTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button class="nav-link active" id="summary-tab" data-bs-toggle="tab" data-bs-target="#summary" type="button" role="tab">Summary</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="features-tab" data-bs-toggle="tab" data-bs-target="#features" type="button" role="tab">Feature Importance</button>
      </li>
      <li class="nav-item" role="presentation">
        <button class="nav-link" id="logs-tab" data-bs-toggle="tab" data-bs-target="#logs" type="button" role="tab">Logs</button>
      </li>
    </ul>
    <div class="tab-content" id="resultTabsContent">
      <div class="tab-pane fade show active" id="summary" role="tabpanel">${summary_html}</div>
      <div class="tab-pane fade" id="features" role="tabpanel">
        <div class="text-center p-3">
          <canvas id="fiChart" style="max-height:300px;"></canvas>
          <div id="fiTopFeatures" class="mb-3"></div>
          <canvas id="shapChart" style="max-height:300px;"></canvas>
          <div id="shapTopFeatures"></div>
        </div>
      </div>
      <div class="tab-pane fade" id="logs" role="tabpanel">
        <pre style="height:180px;overflow:auto;background:#f9fbe7;">${
          result.logs || "No logs."
        }</pre>
      </div>
    </div>
  `;
  document.getElementById("result-area").innerHTML = html;
  renderFeatureCharts(result);
  flashComplete();
}
function renderFeatureCharts(result) {
  // FI chart
  if (result.fi_labels && result.fi_values && result.fi_labels.length > 0) {
    var ctx = document.getElementById("fiChart").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: result.fi_labels,
        datasets: [
          {
            label: "Feature Importance",
            data: result.fi_values,
            backgroundColor: "#1976d2",
            borderRadius: 9,
          },
        ],
      },
      options: {
        plugins: { legend: { display: false } },
        indexAxis: "y",
        scales: { x: { beginAtZero: true } },
      },
    });
    document.getElementById("fiTopFeatures").innerHTML =
      `<div class="mb-2">
         <strong>Top Features:</strong> ` +
      result.fi_labels
        .slice(0, 5)
        .map(
          (f) =>
            `<span class="badge rounded-pill text-bg-primary mx-1">${f}</span>`
        )
        .join(" ") +
      `</div>`;
  }
  if (
    result.shap_labels &&
    result.shap_values &&
    result.shap_labels.length > 0
  ) {
    var ctx2 = document.getElementById("shapChart").getContext("2d");
    new Chart(ctx2, {
      type: "bar",
      data: {
        labels: result.shap_labels,
        datasets: [
          {
            label: "SHAP Value",
            data: result.shap_values,
            backgroundColor: "#43a047",
            borderRadius: 9,
          },
        ],
      },
      options: {
        plugins: { legend: { display: false } },
        indexAxis: "y",
        scales: { x: { beginAtZero: true } },
      },
    });
    document.getElementById("shapTopFeatures").innerHTML =
      `<div class="mb-2">
         <strong>Top SHAP Features:</strong> ` +
      result.shap_labels
        .slice(0, 5)
        .map(
          (f) =>
            `<span class="badge rounded-pill text-bg-success mx-1">${f}</span>`
        )
        .join(" ") +
      `</div>`;
  }
}
function flashComplete() {
  let area = document.getElementById("result-area");
  if (
    area.innerHTML &&
    area.innerHTML.indexOf("Training failed!") === -1 &&
    area.innerHTML.indexOf("Error during training") === -1
  ) {
    area.innerHTML =
      '<div id="training-complete">🎉 Training Complete! 🎉</div>' +
      area.innerHTML;
  }
}
// For CSRF:
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    let cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
