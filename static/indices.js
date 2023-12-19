document.addEventListener("DOMContentLoaded", function() {
    const indicesInfo = {
        'AEX': 'Amsterdam',
        'EUROSTOXX 50': 'Europe',
        'NASDAQ': 'New York',
        'S&P 500': 'New York',
        'DAX': 'Frankfurt'
    };

    const tbody = document.getElementById("indices-data");

    fetch('/indices-data')
        .then(response => response.json())
        .then(data => {
            data.forEach(indexData => {
                const tr = document.createElement("tr");

                const link = `/index-details/${indexData.name}`; // Create a link to the desired endpoint.

                tr.innerHTML = `
                    <td><a href="${link}">${indexData.name}</a></td>
                    <td>${indicesInfo[indexData.name]}</td>
                    <td>${indexData.price.toFixed(2)}</td>
                    <td>${indexData.percentage_growth.toFixed(2)}%</td>
                `;

                tbody.appendChild(tr);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});
