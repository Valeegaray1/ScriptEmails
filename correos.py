import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Función para extraer correos electrónicos de una URL
def extract_emails_from_url(url):
    try:
        if not isinstance(url, str) or pd.isna(url):
            return []

        if not url.startswith("http"):
            url = "http://" + url

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar correos en el texto general
        text = soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

        # Buscar en los enlaces con 'mailto:'
        for mailto in soup.select('a[href^=mailto]'):
            email_link = mailto.get('href')
            if email_link:
                email_address = email_link.replace('mailto:', '').split('?')[0]
                emails.append(email_address)

        return list(set(emails))

    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return []

# Leer el archivo Excel con las URLs
df = pd.read_excel('Top_100_Centros_Comerciales_España_Final.xlsx')

# Crear una lista para almacenar los resultados
results = []

# Iterar sobre las URLs en la columna 'URL'
for url in df['URL']:
    print(f"Extrayendo correos de: {url}")
    emails = extract_emails_from_url(url)
    if emails:
        print(f"Correos electrónicos encontrados: {emails}")
        results.append({"URL": url, "Emails": ", ".join(emails)})
    else:
        print("No se encontraron correos electrónicos.")
        results.append({"URL": url, "Emails": "No se encontraron correos."})

    time.sleep(1)

# Guardar los resultados en un nuevo archivo Excel
results_df = pd.DataFrame(results)
results_df.to_excel('Resultados_Correos_Extraidos_Mejorado.xlsx', index=False)
