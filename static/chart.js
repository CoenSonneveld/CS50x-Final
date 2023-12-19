let rsiContainer = null;

document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();

    const symbol = document.getElementById('symbol').value;
    const interval = document.getElementById('interval').value;
    const indicator = document.getElementById('indicator-selector').value;  // Get the selected indicator from the dropdown

    fetch('/graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `symbol=${symbol}&interval=${interval}&indicator=${indicator}`
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        renderChart(symbol, data.data, data.smaData, data.rsiData, indicator);
    });
});

console.log("Received data:", data);

function renderChart(symbol, data, smaData, rsiData, indicator) {



    const container = document.getElementById('chart');
    container.innerHTML = '';

    if (rsiContainer) {
        rsiContainer.remove();
        rsiContainer = null;
    }

    const chart = LightweightCharts.createChart(document.getElementById('chart'), {
        width: 800,
        height: 400,
        watermark: {
            color: 'rgba(0, 0, 0, 0.4)',
            visible: true,
            text: symbol.toUpperCase(),
            fontSize: 48,
            horzAlign: 'center',
            vertAlign: 'center',
        },
    });
    const candleSeries = chart.addCandlestickSeries();
    candleSeries.setData(data.map(item => ({
        time: item.date,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
    })));

    if (indicator === 'SMA' && smaData) {
        const lineSeries = chart.addLineSeries();
        lineSeries.setData(smaData.map(item => ({
            time: item.time,
            value: item.value,
        })));
    } else if (indicator === 'RSI' && rsiData) {
        rsiContainer = document.createElement('div');
        rsiContainer.style.width = '800px';
        rsiContainer.style.height = '150px'; // Adjusted for demonstration purposes
        container.after(rsiContainer);

        const rsiChart = LightweightCharts.createChart(rsiContainer, {
            width: 800,
            height: 150,
        });
        const rsiLineSeries = rsiChart.addLineSeries();
        rsiLineSeries.setData(rsiData.map(item => ({
            time: item.time,
            value: item.value,
        })));

    }
}
