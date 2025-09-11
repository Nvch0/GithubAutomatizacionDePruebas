document.addEventListener('DOMContentLoaded', function () {
    const apiKey = 'ac0d4ddc6eb67e5b634f3c85';  // Asegúrate de reemplazar esto con tu clave de API
    const url = `https://v6.exchangerate-api.com/v6/${apiKey}/latest/CLP`;
    const countryUrl = `https://v6.exchangerate-api.com/v6/${apiKey}/codes`;

    // Obtener tasas de cambio y nombres de países cuando se carga la página
    Promise.all([
        fetch(url).then(response => response.json()),
        fetch(countryUrl).then(response => response.json())
    ])
        .then(([rateData, countryData]) => {
            const select = document.getElementById('currency-select');
            const rates = rateData.conversion_rates;
            const countryCodes = countryData.supported_codes;

            // Crear un mapa de códigos de moneda a nombres de países
            const countryMap = {};
            countryCodes.forEach(([currencyCode, countryName]) => {
                countryMap[currencyCode] = countryName;
            });

            // Llenar el select con las opciones de monedas, nombres de países y banderas
            for (let currency in rates) {
                let option = document.createElement('option');
                option.value = rates[currency];
                option.text = `${currency} - ${countryMap[currency] || 'Unknown Country'}`;
                option.dataset.currency = currency;  // Guardar el código de moneda en un dataset
                select.appendChild(option);
            }
        });

    // Convertir el importe total cuando se selecciona una moneda
    document.getElementById('currency-select').addEventListener('change', function () {
        const rate = parseFloat(this.value);
        const total = parseFloat(document.getElementById('importe-total').dataset.value);
        const convertedTotal = (total * rate).toFixed(2);
        document.getElementById('converted-importe-total').textContent = convertedTotal;
    });



});