document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();

    const symbol = document.getElementById('symbol').value;

    fetch(`/quote`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `symbol=${symbol}`  // sending symbol as form data
    })
    .then(response => response.json())
    .then(data => {
        renderChart(symbol, data.graph_data);  // adjust to match the structure of the response
    });
});

function renderChart(symbol, data) {
    const container = document.getElementById('quote-chart');
    container.innerHTML = '';

    const chart = LightweightCharts.createChart(container, {
        width: 800,
        height: 400,
    });
    const candleSeries = chart.addCandlestickSeries();
    candleSeries.setData(data.map(item => ({
        time: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
    })));
}
