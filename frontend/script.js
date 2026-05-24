let analysisData = null;
let lineChartInstance = null;
let barChartInstance = null;
let predictionChartInstance = null;

async function uploadFile() {

  const fileInput = document.getElementById("fileInput");
  const uploadStatus = document.getElementById("uploadStatus");

  if (!fileInput.files.length) {

    uploadStatus.innerText =
      "Please select a CSV or Excel file first.";

    uploadStatus.style.color = "red";

    return;
  }

  const formData = new FormData();

  formData.append(
    "file",
    fileInput.files[0]
  );

  uploadStatus.innerText =
    "Analyzing your data...";

  uploadStatus.style.color = "#2563eb";

  try {

    const response = await fetch(
      "http://127.0.0.1:5000/analyze",
      {
        method: "POST",
        body: formData
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.error || "Something went wrong"
      );
    }

    // Save globally
    analysisData = data;

    // Save for simulator page
    localStorage.setItem(
      "analysisData",
      JSON.stringify(data)
    );

    // Fill dashboard
    fillDashboard(data);

    // Dynamic chart builder
    setupDynamicChartBuilder(data);

    // Other charts
    drawBarChart(data.bar_chart);

    drawPredictionChart(
      data.prediction
    );

    updateHeatmap(data);

    uploadStatus.innerText =
      "File uploaded successfully";

    uploadStatus.style.color =
      "#16a34a";

  } catch (error) {

    uploadStatus.innerText =
      error.message;

    uploadStatus.style.color =
      "red";
  }
}

function fillDashboard(data) {
  document.getElementById("fileName").innerText = data.file_name;
  document.getElementById("fileType").innerText = data.file_type;
  document.getElementById("rows").innerText = data.rows.toLocaleString();
  document.getElementById("columns").innerText = data.columns;
  document.getElementById("uploadedOn").innerText = new Date().toLocaleString();

  document.getElementById("cleanStatus").innerText = "Cleaned";
  document.getElementById("cleanStatus").style.background = "#ecfdf5";
  document.getElementById("cleanStatus").style.color = "#15803d";

  document.getElementById("numericCount").innerText = data.numeric_columns ?? "-";
  document.getElementById("duplicates").innerText = data.duplicates_removed;
  document.getElementById("missing").innerText = data.missing_values_fixed;

  document.getElementById("sideDomain").innerText = data.domain;
  document.getElementById("confidenceText").innerText = `${data.confidence}%`;
  document.getElementById("confidenceBar").style.width = `${data.confidence}%`;

  const anomalyCount = data.anomalies && data.anomalies[0] !== "No major anomalies detected."
    ? data.anomalies.length
    : 0;

  document.getElementById("anomalyStatus").innerText =
    anomalyCount > 0 ? `${anomalyCount} Found` : "Safe";

  document.getElementById("predictedValue").innerText =
    typeof data.prediction.next_value === "number"
      ? data.prediction.next_value.toLocaleString()
      : data.prediction.next_value;

  fillList("insightList", data.insights, "↓");
  fillList("recommendationList", data.recommendations, "🎯");
  fillList("anomalyText", data.anomalies, "", true);

  document.getElementById("alertText").innerText =
    anomalyCount > 0
      ? "Warning: Unusual patterns detected in your dataset."
      : "No critical alerts detected.";
}

function fillList(elementId, items, icon = "•", asText = false) {
  const element = document.getElementById(elementId);

  if (asText) {
    element.innerText = items.join("\n");
    return;
  }

  element.innerHTML = "";

  items.forEach((item) => {
    const div = document.createElement("div");
    div.className = "list-item";

    div.innerHTML = `
      <div class="list-badge">${icon}</div>
      <div>${item}</div>
    `;

    element.appendChild(div);
  });
}

function drawCharts(data) {
  drawLineChart(data.line_chart);
  drawBarChart(data.bar_chart);
  drawPredictionChart(data.prediction);
  updateHeatmap(data);
}

<<<<<<< HEAD
lineChartInstance = new Chart(ctx, {
  type: "line",
  data: {
    labels: chartData.labels,
    datasets: [{
      label: "Trend",
      data: chartData.values,
      borderWidth: 3,
      tension: 0.4,
      fill: true
    }]
  },
  options: {
    responsive: true
  }
});

ctx.onclick = () => {
  showChartInsight("Trend Chart", chartData);
};
=======
function drawLineChart(chartData) {
  const ctx = document.getElementById("lineChart");

  if (lineChartInstance) {
    lineChartInstance.destroy();
  }

  lineChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: chartData.labels,
      datasets: [{
        label: "Trend",
        data: chartData.values,
        borderWidth: 3,
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
function drawBarChart(chartData) {
  const ctx = document.getElementById("barChart");

  if (barChartInstance) {
    barChartInstance.destroy();
  }

  barChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: chartData.labels,
      datasets: [{
        label: "Category Count",
        data: chartData.values,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "right"
        }
      }
    }
  });
}
<<<<<<< HEAD
ctx.onclick = () => {
  showChartInsight("Category Distribution Chart", chartData);
};
=======
>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15

function drawPredictionChart(prediction) {
  const ctx = document.getElementById("predictionChart");

  if (predictionChartInstance) {
    predictionChartInstance.destroy();
  }

  const actual = prediction.actual || [];
  const predicted = prediction.predicted || [];

  predictionChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: actual.map((_, index) => `Point ${index + 1}`),
      datasets: [
        {
          label: "Actual",
          data: actual,
          borderWidth: 3,
          tension: 0.4
        },
        {
          label: "Predicted",
          data: predicted,
          borderWidth: 3,
          borderDash: [6, 6],
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "top"
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
<<<<<<< HEAD
ctx.onclick = () => {
  showChartInsight("Prediction Chart", {
    labels: prediction.actual.map((_, index) => `Point ${index + 1}`),
    values: prediction.predicted
  });
};
=======

>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
function updateHeatmap(data) {
  const heatmap = document.getElementById("heatmap");

  heatmap.innerHTML = `
    <div>
      <strong>Smart Relationship View</strong>
      <p style="margin-top: 10px;">
        Domain: ${data.domain}<br>
        Correlation and relationship analysis completed.
      </p>
    </div>
  `;
}

function scrollToSection(sectionId) {
  const section = document.getElementById(sectionId);

  if (section) {
    section.scrollIntoView({
      behavior: "smooth"
    });
  }
}

function downloadReport() {
  if (!analysisData) {
    alert("Please upload and analyze a dataset first.");
    return;
  }

  let report = "";
  report += "AI-Powered Smart Data Analyzer Report\n";
  report += "=====================================\n\n";

  report += `File Name: ${analysisData.file_name}\n`;
  report += `File Type: ${analysisData.file_type}\n`;
  report += `Rows: ${analysisData.rows}\n`;
  report += `Columns: ${analysisData.columns}\n`;
  report += `Detected Domain: ${analysisData.domain}\n`;
  report += `Confidence: ${analysisData.confidence}%\n\n`;

  report += "Cleaning Summary\n";
  report += "----------------\n";
  report += `Duplicates Removed: ${analysisData.duplicates_removed}\n`;
  report += `Missing Values Fixed: ${analysisData.missing_values_fixed}\n\n`;

  report += "AI Insights\n";
  report += "-----------\n";
  analysisData.insights.forEach((item) => {
    report += `- ${item}\n`;
  });

  report += "\nRecommendations\n";
  report += "---------------\n";
  analysisData.recommendations.forEach((item) => {
    report += `- ${item}\n`;
  });

  report += "\nAnomaly Detection\n";
  report += "-----------------\n";
  analysisData.anomalies.forEach((item) => {
    report += `- ${item}\n`;
  });

  const blob = new Blob([report], {
    type: "text/plain"
  });

  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");

  a.href = url;
  a.download = "analysis_report.txt";
  a.click();

  URL.revokeObjectURL(url);
}

function downloadCleaned() {
  if (!analysisData) {
    alert("Please upload and analyze a dataset first.");
    return;
  }

  alert("Cleaned dataset export will be added in the next backend update.");
}
function setupDynamicChartBuilder(data) {
  if (!data.chart_columns || !data.chart_columns.all) {
    alert("Chart column data not received from backend. Restart Flask backend and upload again.");
    return;
  }

  const xAxisSelect = document.getElementById("xAxisSelect");
  const yAxisSelect = document.getElementById("yAxisSelect");

  xAxisSelect.innerHTML = `<option value="">X-Axis</option>`;
  yAxisSelect.innerHTML = `<option value="">Y-Axis</option>`;

  data.chart_columns.all.forEach(col => {
    const option = document.createElement("option");
    option.value = col;
    option.textContent = col;
    xAxisSelect.appendChild(option);
  });

  data.chart_columns.numeric.forEach(col => {
    const option = document.createElement("option");
    option.value = col;
    option.textContent = col;
    yAxisSelect.appendChild(option);
  });

  if (data.chart_columns.all.length > 0) {
    xAxisSelect.value = data.chart_columns.all[0];
  }

  if (data.chart_columns.numeric.length > 0) {
    yAxisSelect.value = data.chart_columns.numeric[0];
  }

  updateDynamicChart();
}
function updateDynamicChart() {
  if (!analysisData) return;

  const chartType = document.getElementById("chartType").value;
  const xCol = document.getElementById("xAxisSelect").value;
  const yCol = document.getElementById("yAxisSelect").value;

  if (!xCol || !yCol) return;

  const labels = analysisData.chart_dataset.map(row => row[xCol]);
  const values = analysisData.chart_dataset.map(row => Number(row[yCol]));

  const ctx = document.getElementById("lineChart");

  if (lineChartInstance) {
    lineChartInstance.destroy();
  }

  let finalChartType = chartType;

  if (chartType === "scatter") {
    finalChartType = "scatter";
  }

  let chartData;

  if (chartType === "scatter") {
    chartData = {
      datasets: [{
        label: `${xCol} vs ${yCol}`,
        data: analysisData.chart_dataset.map(row => ({
          x: Number(row[xCol]),
          y: Number(row[yCol])
        })),
        borderWidth: 2
      }]
    };
  } else {
    chartData = {
      labels: labels,
      datasets: [{
        label: yCol,
        data: values,
        borderWidth: 3,
        tension: 0.4,
        fill: chartType === "line"
      }]
    };
  }

  lineChartInstance = new Chart(ctx, {
    type: finalChartType,
    data: chartData,
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}
function openChat() {
  document.getElementById("chatbot").style.display = "flex";
}

function closeChat() {
  document.getElementById("chatbot").style.display = "none";
}

async function sendChatQuestion() {
  const input = document.getElementById("chatInput");
  const messages = document.getElementById("chatMessages");

  const question = input.value.trim();

  if (!question) return;

  const userDiv = document.createElement("div");
  userDiv.className = "user-message";
  userDiv.innerText = question;
  messages.appendChild(userDiv);

  input.value = "";

  const loadingDiv = document.createElement("div");
  loadingDiv.className = "bot-message";
  loadingDiv.innerText = "Thinking...";
  messages.appendChild(loadingDiv);

  messages.scrollTop = messages.scrollHeight;

  try {
    const response = await fetch("http://127.0.0.1:5000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        question: question
      })
    });

    const data = await response.json();

    loadingDiv.innerText = data.answer;

  } catch (error) {
    loadingDiv.innerText = "Error connecting to AI chat backend.";
  }

  messages.scrollTop = messages.scrollHeight;
}
// ================= AI DECISION SIMULATOR =================

let storedData = localStorage.getItem("analysisData");
let simulatorData = storedData ? JSON.parse(storedData) : null;

function getElement(id) {
  return document.getElementById(id);
}

function updateSliderValues() {
  const marketingSlider = getElement("marketingSlider");
  const discountSlider = getElement("discountSlider");
  const customerSlider = getElement("customerSlider");

  if (!marketingSlider || !discountSlider || !customerSlider) return;

  getElement("marketingValue").innerText = `${marketingSlider.value}%`;
  getElement("discountValue").innerText = `${discountSlider.value}%`;
  getElement("customerValue").innerText = `${customerSlider.value}%`;
}

function loadSimulatorBase() {
  const marketingSlider = getElement("marketingSlider");
  const discountSlider = getElement("discountSlider");
  const customerSlider = getElement("customerSlider");

  if (!marketingSlider || !discountSlider || !customerSlider) return;

  marketingSlider.addEventListener("input", updateSliderValues);
  discountSlider.addEventListener("input", updateSliderValues);
  customerSlider.addEventListener("input", updateSliderValues);

  updateSliderValues();

  if (!simulatorData || !simulatorData.simulator_base) {
    getElement("simulationAdvice").innerText =
      "Please upload and analyze a dataset from the dashboard first.";
    return;
  }

  const base = simulatorData.simulator_base;

  if (getElement("baseSales")) {
    getElement("baseSales").innerText = Number(base.avg_sales || 0).toFixed(2);
  }

  if (getElement("baseProfit")) {
    getElement("baseProfit").innerText = Number(base.avg_profit || 0).toFixed(2);
  }

  if (getElement("baseDiscount")) {
    getElement("baseDiscount").innerText = Number(base.avg_discount || 0).toFixed(2);
  }

  if (getElement("baseCustomers")) {
    getElement("baseCustomers").innerText = base.customer_count || 0;
  }
}

function runSimulation() {
  if (!simulatorData || !simulatorData.simulator_base) {
    alert("Please upload and analyze a dataset from the dashboard first.");
    return;
  }

  const marketingSlider = getElement("marketingSlider");
  const discountSlider = getElement("discountSlider");
  const customerSlider = getElement("customerSlider");

  if (!marketingSlider || !discountSlider || !customerSlider) {
    alert("Simulator controls not found.");
    return;
  }

  const base = simulatorData.simulator_base;

  const baseSales = Number(base.avg_sales || 0);
  const baseProfit = Number(base.avg_profit || 0);

  const marketing = Number(marketingSlider.value);
  const discount = Number(discountSlider.value);
  const customers = Number(customerSlider.value);

  const predictedSales =
    baseSales *
    (1 + marketing * 0.0035 + customers * 0.0045 - discount * 0.0015);

  const predictedProfit =
    baseProfit *
    (1 + marketing * 0.002 + customers * 0.004 - discount * 0.005);

  const salesImpact =
    baseSales !== 0 ? ((predictedSales - baseSales) / baseSales) * 100 : 0;

  const profitImpact =
    baseProfit !== 0 ? ((predictedProfit - baseProfit) / baseProfit) * 100 : 0;

  const roi = profitImpact - marketing * 0.1;

  let risk = "Low";
  if (discount < -25 || marketing > 70) risk = "Medium";
  if (discount < -40 || marketing > 85) risk = "High";

  let strategyScore =
    50 + profitImpact * 0.6 + salesImpact * 0.3 - Math.abs(discount) * 0.2;

  strategyScore = Math.max(0, Math.min(100, strategyScore));

  getElement("salesImpact").innerText = `${salesImpact.toFixed(1)}%`;
  getElement("profitImpact").innerText = `${profitImpact.toFixed(1)}%`;

  if (getElement("roiValue")) {
    getElement("roiValue").innerText = `${roi.toFixed(1)}%`;
  }

  if (getElement("riskLevel")) {
    getElement("riskLevel").innerText = risk;
  }

  if (getElement("strategyScore")) {
    getElement("strategyScore").innerText = `${strategyScore.toFixed(0)}/100`;
  }

  getElement("simulationAdvice").innerText =
    `Based on your uploaded dataset, average sales may change from ${baseSales.toFixed(2)} to ${predictedSales.toFixed(2)}, and average profit may change from ${baseProfit.toFixed(2)} to ${predictedProfit.toFixed(2)}.`;

  if (getElement("decisionSummary")) {
    getElement("decisionSummary").innerText =
      `Detected columns: Sales = ${base.sales_col || "Not found"}, Profit = ${base.profit_col || "Not found"}, Discount = ${base.discount_col || "Not found"}. Risk level is ${risk}.`;
  }
}
<<<<<<< HEAD
function showChartInsight(chartName, chartData) {

  const popup =
    document.getElementById("chartAiPopup");

  const text =
    document.getElementById("chartInsightText");

  if (
    !chartData ||
    !chartData.values ||
    chartData.values.length === 0
  ) {
    text.innerText =
      "Not enough data available to generate AI insight.";

    popup.style.display = "flex";
    return;
  }

  const values =
    chartData.values
      .map(Number)
      .filter(v => !isNaN(v));

  const labels =
    chartData.labels || [];

  const maxValue =
    Math.max(...values);

  const minValue =
    Math.min(...values);

  const maxIndex =
    values.indexOf(maxValue);

  const minIndex =
    values.indexOf(minValue);

  const maxLabel =
    labels[maxIndex] || "highest point";

  const minLabel =
    labels[minIndex] || "lowest point";

  const firstValue =
    values[0];

  const lastValue =
    values[values.length - 1];

  let trendText = "";

  if (lastValue > firstValue) {

    const growth =
      (
        ((lastValue - firstValue) / firstValue) * 100
      ).toFixed(1);

    trendText =
      `The chart shows an upward trend with ${growth}% growth.`;

  } else if (lastValue < firstValue) {

    const drop =
      (
        ((firstValue - lastValue) / firstValue) * 100
      ).toFixed(1);

    trendText =
      `The chart shows a downward trend with ${drop}% decline.`;

  } else {

    trendText =
      "The chart appears stable overall.";
  }

  text.innerText = `
${chartName}

${trendText}

Highest value:
${maxValue.toFixed(2)} at ${maxLabel}

Lowest value:
${minValue.toFixed(2)} at ${minLabel}

AI Suggestion:
Focus on low-performing areas like '${minLabel}' and compare them with '${maxLabel}' to understand what caused the difference.
`;

  popup.style.display = "flex";
}

function closeChartInsight() {

  document.getElementById(
    "chartAiPopup"
  ).style.display = "none";
}
function updateHeatmap(data) {
  const heatmap = document.getElementById("heatmap");

  if (
    !data.heatmap_data ||
    !data.heatmap_data.columns ||
    data.heatmap_data.columns.length < 2
  ) {
    heatmap.innerHTML = `
      <div>
        <strong>Not enough numeric columns</strong>
        <p style="margin-top: 10px;">
          Correlation heatmap needs at least 2 numeric columns.
        </p>
      </div>
    `;
    return;
  }

  const columns = data.heatmap_data.columns;
  const matrix = data.heatmap_data.matrix;

  let html = `<div class="real-heatmap">`;

  html += `<div class="heatmap-row heatmap-header-row">`;
  html += `<div class="heatmap-label"></div>`;

  columns.forEach(col => {
    html += `<div class="heatmap-header">${col}</div>`;
  });

  html += `</div>`;

  matrix.forEach((row, i) => {
    html += `<div class="heatmap-row">`;
    html += `<div class="heatmap-label">${columns[i]}</div>`;

    row.forEach(value => {
      const intensity = Math.abs(value);
      const color =
        value >= 0
          ? `rgba(37, 99, 235, ${intensity})`
          : `rgba(239, 68, 68, ${intensity})`;

      html += `
        <div
          class="heatmap-cell"
          style="background:${color}"
          title="Correlation: ${value}"
        >
          ${value}
        </div>
      `;
    });

    html += `</div>`;
  });

  html += `</div>`;

  heatmap.innerHTML = html;

  heatmap.onclick = () => {
    showChartInsight("Correlation Heatmap", {
      labels: columns,
      values: matrix.flat()
    });
  };
}
function openAllInsights() {
  if (!analysisData || !analysisData.insights) {
    alert("Please upload and analyze a dataset first.");
    return;
  }

  document.getElementById("fullListTitle").innerText = "All AI Insights";

  document.getElementById("fullListContent").innerHTML =
    `<ul>${analysisData.insights.map(item => `<li>${item}</li>`).join("")}</ul>`;

  document.getElementById("fullListPopup").style.display = "flex";
}

function openAllRecommendations() {
  if (!analysisData || !analysisData.recommendations) {
    alert("Please upload and analyze a dataset first.");
    return;
  }

  document.getElementById("fullListTitle").innerText = "All Recommendations";

  document.getElementById("fullListContent").innerHTML =
    `<ul>${analysisData.recommendations.map(item => `<li>${item}</li>`).join("")}</ul>`;

  document.getElementById("fullListPopup").style.display = "flex";
}

function closeFullList() {
  document.getElementById("fullListPopup").style.display = "none";
}
function openAnomalies() {

  if (!analysisData) {
    alert("Please upload and analyze a dataset first.");
    return;
  }

  document.getElementById(
    "fullListTitle"
  ).innerText = "Detected Anomalies";

  document.getElementById(
    "fullListContent"
  ).innerHTML =
    `<ul>${
      analysisData.anomalies
        .map(item => `<li>${item}</li>`)
        .join("")
    }</ul>`;

  document.getElementById(
    "fullListPopup"
  ).style.display = "flex";
}

function openAlerts() {

  if (!analysisData) {
    alert("Please upload and analyze a dataset first.");
    return;
  }

  let alerts = [];

  if (
    analysisData.anomalies &&
    analysisData.anomalies.length
  ) {

    analysisData.anomalies.forEach(
      item => {
        alerts.push(
          `⚠ ${item}`
        );
      }
    );
  }

  alerts.push(
    "📈 Review charts for performance changes."
  );

  alerts.push(
    "🤖 AI recommends checking weak trends."
  );

  document.getElementById(
    "fullListTitle"
  ).innerText = "All Alerts";

  document.getElementById(
    "fullListContent"
  ).innerHTML =
    `<ul>${
      alerts
        .map(item => `<li>${item}</li>`)
        .join("")
    }</ul>`;

  document.getElementById(
    "fullListPopup"
  ).style.display = "flex";
}
=======

>>>>>>> 539198ff1ae450bdf1aae0ee1b372fd52de5ca15
window.addEventListener("load", loadSimulatorBase);
