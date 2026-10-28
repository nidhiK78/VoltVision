// ==========================================
// VOLTVISION
// Main Application Logic
// ==========================================


// ==========================================
// 1. SAMPLE FORECAST DATA
// ==========================================
//
// Temporary data.
// This will later be replaced by Asuni's
// ML prediction output.
//

let forecastData = [
    { time: "00:00", demand: 125 },
    { time: "01:00", demand: 118 },
    { time: "02:00", demand: 112 },
    { time: "03:00", demand: 108 },
    { time: "04:00", demand: 110 },
    { time: "05:00", demand: 120 },
    { time: "06:00", demand: 135 },
    { time: "07:00", demand: 145 },
    { time: "08:00", demand: 155 },
    { time: "09:00", demand: 162 },
    { time: "10:00", demand: 158 },
    { time: "11:00", demand: 165 },
    { time: "12:00", demand: 172 },
    { time: "13:00", demand: 180 },
    { time: "14:00", demand: 200 },
    { time: "15:00", demand: 188 },
    { time: "16:00", demand: 175 },
    { time: "17:00", demand: 168 },
    { time: "18:00", demand: 185 },
    { time: "19:00", demand: 195 },
    { time: "20:00", demand: 220 },
    { time: "21:00", demand: 205 },
    { time: "22:00", demand: 180 },
    { time: "23:00", demand: 150 }
];


// ==========================================
// 2. FORECAST STATISTICS
// ==========================================

function getDemandValues() {

    return forecastData.map(
        item => item.demand
    );

}


function getPeakDemand() {

    return Math.max(
        ...getDemandValues()
    );

}


function getAverageDemand() {

    const values =
        getDemandValues();

    return values.reduce(
        (sum, value) => sum + value,
        0
    ) / values.length;

}


function getCriticalAlerts() {

    return getDemandValues()
        .filter(
            value => value >= 200
        )
        .length;

}


// ==========================================
// 3. SMART GRID CONTROLLER
// ==========================================

function determineGridMode(
    demand,
    timestamp
) {

    const hour =
        parseInt(
            timestamp.split(":")[0],
            10
        );


    /*
        Rule 1:
        Demand above 160 kW
        → Renewable Storage

        Rule 2:
        18:00–22:00
        → Renewable Storage

        Otherwise:
        → Main Grid
    */

    if (
        demand > 160 ||
        (hour >= 18 && hour <= 22)
    ) {

        return "Renewable Storage";

    }


    return "Main Grid";

}


function checkOverload(demand) {

    return demand >= 200;

}


function makeGridDecision(
    timestamp,
    demand
) {

    const gridMode =
        determineGridMode(
            demand,
            timestamp
        );


    const overload =
        checkOverload(demand);


    return {

        timestamp: timestamp,

        demand: demand,

        gridMode: gridMode,

        overload: overload

    };

}


// ==========================================
// 4. CREATE GRID DECISIONS
// ==========================================

const gridDecisions =
    forecastData.map(
        item =>
            makeGridDecision(
                item.time,
                item.demand
            )
    );


// ==========================================
// 5. CURRENT DECISION
// ==========================================

function getCurrentDecision() {

    const currentHour =
        new Date().getHours();


    const decision =
        gridDecisions.find(
            item => {

                const hour =
                    parseInt(
                        item.timestamp
                            .split(":")[0],
                        10
                    );

                return hour === currentHour;

            }
        );


    return (
        decision ||
        gridDecisions.find(
            item =>
                item.timestamp === "19:00"
        ) ||
        gridDecisions[0]
    );

}


// ==========================================
// 6. UPDATE OVERVIEW
// ==========================================

function updateOverview() {

    const currentDecision =
        getCurrentDecision();


    const currentDemand =
        document.getElementById(
            "currentDemand"
        );


    const gridMode =
        document.getElementById(
            "gridMode"
        );


    const controlSource =
        document.getElementById(
            "controlSource"
        );


    if (currentDemand) {

        currentDemand.textContent =
            currentDecision.demand;

    }


    if (gridMode) {

        gridMode.textContent =
            currentDecision.gridMode;

    }


    if (controlSource) {

        controlSource.textContent =
            currentDecision.gridMode;

    }


    const peak =
        document.getElementById(
            "peakDemand"
        );


    if (peak) {

        peak.textContent =
            `${getPeakDemand()} kW`;

    }


    const average =
        document.getElementById(
            "averageDemand"
        );


    if (average) {

        average.textContent =
            `${Math.round(
                getAverageDemand()
            )} kW`;

    }

}


// ==========================================
// 7. UPDATE ANALYTICS
// ==========================================

function updateAnalytics() {

    const peak =
        getPeakDemand();


    const average =
        Math.round(
            getAverageDemand()
        );


    const alerts =
        getCriticalAlerts();


    const analyticsPeak =
        document.getElementById(
            "analyticsPeak"
        );


    const analyticsAverage =
        document.getElementById(
            "analyticsAverage"
        );


    const criticalAlerts =
        document.getElementById(
            "criticalAlerts"
        );


    const forecastPeak =
        document.getElementById(
            "forecastPeak"
        );


    if (analyticsPeak) {

        analyticsPeak.textContent =
            `${peak} kW`;

    }


    if (analyticsAverage) {

        analyticsAverage.textContent =
            `${average} kW`;

    }


    if (criticalAlerts) {

        criticalAlerts.textContent =
            alerts;

    }


    if (forecastPeak) {

        forecastPeak.textContent =
            `${peak} kW`;

    }

}


// ==========================================
// 8. GRID DECISION TABLE
// ==========================================

function displayGridDecisions() {

    const table =
        document.getElementById(
            "decisionTable"
        );


    if (!table) {
        return;
    }


    table.innerHTML = "";


    gridDecisions.forEach(
        decision => {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "decision-row";


            const sourceIcon =
                decision.gridMode ===
                "Renewable Storage"

                    ? "🔋"

                    : "⚡";


            const status =
                decision.overload

                    ? `
                        <span class="decision-alert">
                            Critical Overload
                        </span>
                      `

                    : `
                        <span>
                            Normal
                        </span>
                      `;


            row.innerHTML = `

                <span>
                    ${decision.timestamp}
                </span>

                <span>
                    ${decision.demand} kW
                </span>

                <span class="decision-source">
                    ${sourceIcon}
                    ${decision.gridMode}
                </span>

                ${status}

            `;


            table.appendChild(row);

        }
    );

}


// ==========================================
// 9. CURRENT DATE
// ==========================================

function displayCurrentDate() {

    const dateElement =
        document.getElementById(
            "currentDate"
        );


    if (!dateElement) {
        return;
    }


    const today =
        new Date();


    dateElement.textContent =
        today.toLocaleDateString(
            "en-IN",
            {
                day: "numeric",
                month: "short",
                year: "numeric"
            }
        );

}


// ==========================================
// 10. CHART CONFIGURATION
// ==========================================

function getChartOptions() {

    return {

        responsive: true,

        maintainAspectRatio: false,

        interaction: {

            intersect: false,

            mode: "index"

        },

        plugins: {

            legend: {

                display: false

            },

            tooltip: {

                displayColors: false,

                backgroundColor: "#102a43",

                titleColor: "#ffffff",

                bodyColor: "#ffffff",

                padding: 10,

                callbacks: {

                    label: function(context) {

                        return (
                            `${context.parsed.y} kW`
                        );

                    }

                }

            }

        },

        scales: {

            x: {

                grid: {

                    display: false

                },

                ticks: {

                    color: "#71808a",

                    font: {

                        size: 9

                    },

                    maxRotation: 0

                }

            },

            y: {

                beginAtZero: false,

                grid: {

                    color: "#e3e9ec"

                },

                ticks: {

                    color: "#71808a",

                    font: {

                        size: 9

                    },

                    callback: function(value) {

                        return `${value} kW`;

                    }

                }

            }

        }

    };

}


// ==========================================
// 11. OVERVIEW CHART
// ==========================================

let overviewChart = null;


function createOverviewChart() {

    const canvas =
        document.getElementById(
            "demandChart"
        );


    if (!canvas) {
        return;
    }


    if (overviewChart) {

        overviewChart.destroy();

    }


    const context =
        canvas.getContext("2d");


    overviewChart =
        new Chart(
            context,
            {

                type: "line",

                data: {

                    labels:
                        forecastData.map(
                            item =>
                                item.time
                        ),

                    datasets: [

                        {

                            data:
                                forecastData.map(
                                    item =>
                                        item.demand
                                ),

                            borderColor:
                                "#20b7c9",

                            backgroundColor:
                                "rgba(32, 183, 201, 0.10)",

                            borderWidth: 2.5,

                            pointRadius: 0,

                            pointHoverRadius: 5,

                            tension: 0.35,

                            fill: true

                        }

                    ]

                },

                options:
                    getChartOptions()

            }
        );

}


// ==========================================
// 12. FORECAST PAGE CHART
// ==========================================

let forecastChart = null;


function createForecastChart() {

    const canvas =
        document.getElementById(
            "forecastChart"
        );


    if (!canvas) {
        return;
    }


    if (forecastChart) {

        forecastChart.destroy();

    }


    const context =
        canvas.getContext("2d");


    forecastChart =
        new Chart(
            context,
            {

                type: "line",

                data: {

                    labels:
                        forecastData.map(
                            item =>
                                item.time
                        ),

                    datasets: [

                        {

                            data:
                                forecastData.map(
                                    item =>
                                        item.demand
                                ),

                            borderColor:
                                "#20b7c9",

                            backgroundColor:
                                "rgba(32, 183, 201, 0.10)",

                            borderWidth: 2.5,

                            pointRadius: 2,

                            pointHoverRadius: 6,

                            pointBackgroundColor:
                                "#b8df45",

                            tension: 0.35,

                            fill: true

                        }

                    ]

                },

                options:
                    getChartOptions()

            }
        );

}


// ==========================================
// 13. NAVIGATION
// ==========================================

function setupNavigation() {

    const links =
        document.querySelectorAll(
            ".nav-link"
        );


    links.forEach(
        link => {

            link.addEventListener(
                "click",
                function() {

                    links.forEach(
                        item =>
                            item.classList
                                .remove(
                                    "active"
                                )
                    );


                    this.classList.add(
                        "active"
                    );

                }
            );

        }
    );

}


// ==========================================
// 14. CSV UPLOAD
// ==========================================

const csvInput =
    document.getElementById(
        "csvFile"
    );


if (csvInput) {

    csvInput.addEventListener(
        "change",
        function(event) {

            const file =
                event.target.files[0];


            if (!file) {
                return;
            }


            if (
                !file.name
                    .toLowerCase()
                    .endsWith(".csv")
            ) {

                alert(
                    "Please upload a CSV file."
                );

                csvInput.value = "";

                return;

            }


            const reader =
                new FileReader();


            reader.onload =
                function(event) {

                    validateCSV(
                        event.target.result
                    );

                };


            reader.readAsText(file);

        }
    );

}


// ==========================================
// 15. CSV VALIDATION
// ==========================================

function validateCSV(csvText) {

    const rows =
        csvText
            .trim()
            .split(/\r?\n/)
            .map(
                row => row.trim()
            );


    if (rows.length < 2) {

        alert(
            "The CSV file does not contain enough data."
        );

        return;

    }


    const headers =
        rows[0]
            .split(",")
            .map(
                header =>
                    header.trim()
            );


    const requiredColumns = [

        "timestamp",

        "ambient_temp_c",

        "humidity_pct",

        "solar_irradiance_wm2"

    ];


    const missingColumns =
        requiredColumns.filter(
            column =>
                !headers.includes(
                    column
                )
        );


    if (missingColumns.length > 0) {

        alert(

            "Invalid CSV.\n\n" +

            "Missing columns:\n" +

            missingColumns.join(
                "\n"
            )

        );

        return;

    }


    const telemetryData = [];


    for (
        let i = 1;
        i < rows.length;
        i++
    ) {

        const values =
            rows[i].split(",");


        if (
            values.length !==
            headers.length
        ) {

            alert(
                `Invalid data on row ${i + 1}.`
            );

            return;

        }


        const rowData = {};


        headers.forEach(
            (header, index) => {

                rowData[header] =
                    values[index].trim();

            }
        );


        if (!rowData.timestamp) {

            alert(
                `Missing timestamp on row ${i + 1}.`
            );

            return;

        }


        const numericColumns = [

            "ambient_temp_c",

            "humidity_pct",

            "solar_irradiance_wm2"

        ];


        for (
            const column of numericColumns
        ) {

            const value =
                Number(
                    rowData[column]
                );


            if (
                !Number.isFinite(
                    value
                )
            ) {

                alert(

                    `Invalid ${column} ` +
                    `on row ${i + 1}.`

                );

                return;

            }

        }


        telemetryData.push({

            timestamp:
                rowData.timestamp,

            temperature:
                Number(
                    rowData.ambient_temp_c
                ),

            humidity:
                Number(
                    rowData.humidity_pct
                ),

            solar:
                Number(
                    rowData.solar_irradiance_wm2
                )

        });

    }


    updateTelemetryDisplay(
        telemetryData
    );


    alert(

        "CSV uploaded successfully!\n\n" +

        `${telemetryData.length} hourly records found.`

    );


    console.log(
        "Validated telemetry:",
        telemetryData
    );

}


// ==========================================
// 16. UPDATE TELEMETRY
// ==========================================

function updateTelemetryDisplay(data) {

    if (
        !data ||
        data.length === 0
    ) {

        return;

    }


    /*
        For now we display the first
        uploaded record.

        Later we can select the
        current/latest timestamp.
    */

    const currentData =
        data[0];


    const temperature =
        document.getElementById(
            "temperatureValue"
        );


    const humidity =
        document.getElementById(
            "humidityValue"
        );


    const solar =
        document.getElementById(
            "solarValue"
        );


    if (temperature) {

        temperature.textContent =
            `${currentData.temperature}°C`;

    }


    if (humidity) {

        humidity.textContent =
            `${currentData.humidity}%`;

    }


    if (solar) {

        solar.textContent =
            `${currentData.solar} W/m²`;

    }

}


// ==========================================
// 17. INITIALIZE VOLTVISION
// ==========================================

function initializeVoltVision() {

    displayCurrentDate();

    updateOverview();

    updateAnalytics();

    displayGridDecisions();

    createOverviewChart();

    createForecastChart();

    setupNavigation();

}


// ==========================================
// START
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    initializeVoltVision
);

async function connectVoltVisionAPI() {
    try {
        const response = await fetch(
            "http://127.0.0.1:8000/forecast/24h",
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!response.ok) {
            throw new Error(`API returned HTTP ${response.status}`);
        }

        const result = await response.json();

        if (
            !Array.isArray(result.forecasts) ||
            result.forecasts.length !== 24
        ) {
            throw new Error("API did not return 24 forecast points.");
        }

        const forecasts = result.forecasts;

        // Save the complete forecast for other dashboard components.
        window.voltVisionForecast = forecasts;

        // Save the first predicted demand for the main display.
        const firstPrediction = Number(
            forecasts[0].predicted_demand_kw
        );

        if (!Number.isFinite(firstPrediction)) {
            throw new Error("Invalid demand prediction received.");
        }

        window.voltVisionLatestPrediction = firstPrediction;

        // Update the main demand display.
        [
            "#currentDemand",
            "#current-demand",
            ".current-demand"
        ].forEach(selector => {
            document.querySelectorAll(selector).forEach(element => {
                element.textContent = firstPrediction.toFixed(2);
            });
        });

        // Make the 24 forecast points available to chart components.
        window.forecastData = forecasts.map(item => ({
            time: item.timestamp.slice(11, 16),
            demand: Number(item.predicted_demand_kw),
            timestamp: item.timestamp,
            gridMode: item.grid_mode,
            criticalOverloadAlert: item.critical_overload_alert
        }));

        // Update dashboard sections if their functions exist.
        if (typeof updateOverview === "function") updateOverview();
        if (typeof updateAnalytics === "function") updateAnalytics();
        if (typeof displayGridDecisions === "function") displayGridDecisions();
        if (typeof createOverviewChart === "function") createOverviewChart();
        if (typeof createForecastChart === "function") createForecastChart();

        console.log("VoltVision 24-hour forecast loaded:", forecasts);
        console.log("Forecast points:", forecasts.length);
        console.log("First predicted demand:", firstPrediction, "kW");

    } catch (error) {
        console.error("VoltVision forecast connection failed:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    connectVoltVisionAPI();
});