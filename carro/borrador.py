# Obtener el total del carro desde el context processor
    context = importe_total_carro(request)
    total_carro = context['importe_total_carro']

    # Inicializar variables
    monedas_disponibles = []
    moneda_seleccionada = 'CLP'
    numero_convertido = total_carro

    # Obtener lista de monedas disponibles
    response = requests.get(f'https://v6.exchangerate-api.com/v6/{api_key}/codes')
    if response.status_code == 200:
        monedas_disponibles = response.json().get('supported_codes', [])

    if request.method == 'POST':
        moneda_seleccionada = request.POST.get('moneda')
        cantidad = total_carro

        # Obtener tasas de cambio
        response = requests.get(f'https://v6.exchangerate-api.com/v6/{api_key}/latest/CLP')
        exchange_rates = response.json().get('conversion_rates', {})

        # Convertir la cantidad a la moneda seleccionada
        tasa_cambio = exchange_rates.get(moneda_seleccionada, 1)
        numero_convertido = cantidad * tasa_cambio

'moneda_seleccionada': moneda_seleccionada,
        'numero_convertido': numero_convertido,
        'monedas_disponibles': monedas_disponibles,