def leer_tasas_archivo():
    ruta_archivo="tasas.txt"
    # Tasas predeterminadas en caso de error o datos faltantes
    tasas_predeterminadas = {
        "EUR": 0.01,
        "ARS": 0.01,
        "CLP": 0.01,
        "BRL": 0.01
    }
    
    # Diccionario para almacenar las tasas leídas
    tasas = {}
    
    try:
        # Abrir el archivo de tasas
        with open(ruta_archivo, 'r') as archivo:
            for linea in archivo:
                # Filtrar líneas vacías o con formato incorrecto
                linea = linea.strip()
                if not linea:
                    continue
                
                # Dividir la línea en el par de monedas y la tasa
                try:
                    par, tasa = linea.split(":")
                    tasa = float(tasa.strip())
                    
                    # Verificar el formato del par (USD_X o X_USD)
                    if par.startswith("USD_"):
                        moneda_secundaria = par.split("_")[1]
                        tasas[moneda_secundaria] = tasa
                    elif par.endswith("_USD"):
                        moneda_secundaria = par.split("_")[0]
                        tasas[moneda_secundaria] = 1 / tasa
                    else:
                        # Si el formato no es reconocido, continuar con la siguiente línea
                        continue
                except ValueError:
                    # Si no se puede procesar la línea correctamente, ignorar
                    continue
    except Exception as e:
        # Si ocurre cualquier error al abrir o leer el archivo, se devuelve un error predeterminado
        print(f"Error al leer el archivo: {e}")
    
    # Si no se encontraron tasas válidas, usar las tasas predeterminadas
    if not tasas:
        return tasas_predeterminadas
    
    # Asegurarse de que todas las monedas secundarias estén presentes
    for moneda in tasas_predeterminadas:
        if moneda not in tasas:
            tasas[moneda] = tasas_predeterminadas[moneda]
    
    return tasas

def convertir_moneda(monto, moneda_base, moneda_destino, tasas):
    # Si la moneda base y la moneda destino son la misma, no hay conversión
    if moneda_base == moneda_destino:
        return monto
    
    # Si la moneda base es USD, simplemente se multiplica por la tasa
    if moneda_base == "USD":
        if moneda_destino in tasas:
            return monto * tasas[moneda_destino]
        else:
            print(f"Tasa no encontrada para {moneda_destino}")
            return None
    
    # Si la moneda destino es USD, se invierte la tasa
    if moneda_destino == "USD":
        if moneda_base in tasas:
            return monto / tasas[moneda_base]
        else:
            print(f"Tasa no encontrada para {moneda_base}")
            return None
    
    # Si la moneda base no es USD, primero la convertimos a USD y luego a la moneda destino
    if moneda_base in tasas and moneda_destino in tasas:
        # Convertir la moneda base a USD
        monto_en_usd = monto / tasas[moneda_base]
        # Convertir el monto en USD a la moneda destino
        return monto_en_usd * tasas[moneda_destino]
    
    print(f"Tasa no encontrada para {moneda_base} o {moneda_destino}")
    return None

