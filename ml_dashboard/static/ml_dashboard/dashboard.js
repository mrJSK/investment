let featureConfigs = [];
let nextFeatureId = 1;
let modalFeatureId = "";

// Select2 picker: add a feature as chip on every selection (supports multi same indicator)
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

function renderFeatureCards() {
  let html = "";
  featureConfigs.forEach((feat, idx) => {
    // Format the args as "20, close" etc.
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

function showProgressBar() {
  document.getElementById("progress-area").style.display = "";
  let bar = document.getElementById("progress-bar");
  bar.style.width = "10%";
  bar.innerText = "Initializing...";
  document.getElementById("progress-stats").innerHTML = "Starting training...";
  setTimeout(() => {
    bar.style.width = "55%";
    bar.innerText = "Training model...";
    document.getElementById("progress-stats").innerHTML =
      "Model fitting in progress...";
  }, 700);
}
function finishProgressBar() {
  let bar = document.getElementById("progress-bar");
  bar.style.width = "100%";
  bar.innerText = "Completed!";
  document.getElementById("progress-stats").innerHTML = "Finalizing...";
  setTimeout(() => {
    document.getElementById("progress-area").style.display = "none";
    bar.style.width = "0%";
    bar.innerText = "0%";
  }, 1300);
}
function flashComplete() {
  let area = document.getElementById("result-area");
  area.innerHTML =
    '<div id="training-complete">🎉 Training Complete! 🎉</div>' +
    area.innerHTML;
}
document.getElementById("ml-form").onsubmit = async function (e) {
  e.preventDefault();
  showProgressBar();
  const form = e.target;
  const data = new FormData(form);
  data.append("feature_configs", JSON.stringify(featureConfigs));
  let response = await fetch("/ml/train/", {
    method: "POST",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    body: data,
  });
  let result = await response.json();
  finishProgressBar();
  let fi_html = "";
  if (result.fi_img) {
    fi_html += `<div><strong>Model Feature Importance</strong><br>
    <img src="data:image/png;base64,${result.fi_img}" class="img-fluid" style="max-width:340px;border-radius:16px;box-shadow:0 0 12px #eee;margin-bottom:12px;"></div>`;
  }
  if (result.shap_img) {
    fi_html += `<div><strong>SHAP Summary (Model Explainability)</strong><br>
    <img src="data:image/png;base64,${result.shap_img}" class="img-fluid" style="max-width:340px;border-radius:16px;box-shadow:0 0 12px #eee;margin-bottom:12px;"></div>`;
  }
  if (result.feature_importances && result.features) {
    fi_html += `<div class="metrics-card p-3 mb-2">
      <h6 class="mb-1">Top Features</h6>
      <div>
        ${result.feature_importances
          .map(
            (v, i) =>
              `<span class="feature-badge" style="background:#ffe0b2;color:#e65100">${
                result.features[i]
              }: ${v.toFixed(3)}</span>`
          )
          .join(" ")}
      </div>
    </div>`;
  }
  let html = `
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
      <div class="tab-pane fade show active" id="summary" role="tabpanel">
        <div class="metrics-card p-3 mb-2">
          <h6>Status</h6>
          <span style="color:#43a047;font-weight:bold;">Training completed successfully.</span>
        </div>
      </div>
      <div class="tab-pane fade" id="features" role="tabpanel">
        <div class="text-center p-3">${
          fi_html || "No feature importance available."
        }</div>
      </div>
      <div class="tab-pane fade" id="logs" role="tabpanel">
        <pre style="height:180px;overflow:auto;background:#f9fbe7;">${
          result.logs || "No logs."
        }</pre>
      </div>
    </div>
  `;
  document.getElementById("result-area").innerHTML = html;
  flashComplete();
};
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
