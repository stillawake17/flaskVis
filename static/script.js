console.log("script.js loaded");

// Use the injected data
var data = {
    x: injectedData.categories,
    y: injectedData.counts,
    type: 'bar'
};

// Render the chart
Plotly.newPlot('bar-chart', [data]);
