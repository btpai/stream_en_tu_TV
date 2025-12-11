import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import time
import random

# 1. Configuración de Seguridad
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
]
REQUEST_DELAY = 3  # Segundos entre requests
TIMEOUT = 15  # Segundos para timeout

def load_channels():
    """Carga canales con validación de archivo"""
    if not os.path.exists('canales.txt'):
        raise FileNotFoundError("❌ El archivo canales.txt no existe")
    
    with open('canales.txt', 'r') as f:
        channels = [line.strip() for line in f if line.strip()]
        
    if not channels:
        raise ValueError("❌ canales.txt está vacío")
    
    return channels

def scrape_twitchtracker(channel):
    url = f"https://twitchtracker.com/{channel}/streams"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate'
    }
    
    try:
        # Usa sesiones con cookies
        session = requests.Session()
        session.headers.update(headers)
        
        # Añade delay aleatorio
        time.sleep(random.uniform(2.5, 5.0))
        
        # Simula navegación real
        session.get("https://twitchtracker.com/", timeout=10)
        response = session.get(url, timeout=15)
        
        # Verifica CloudFlare
        if "cloudflare" in response.text.lower():
            raise ConnectionError("🔒 CloudFlare ha bloqueado el acceso")
            
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
            
        # 5. Extracción robusta con fallbacks
        title_elem = soup.find('h2', class_='stream-title')
        game_elem = soup.find('a', class_='game-link')
        
        return {
            'channel': channel,
            'title': title_elem.get_text(strip=True) if title_elem else "Transmisión en vivo",
            'game': game_elem.get_text(strip=True) if game_elem else "Juego no especificado",
            'thumbnail': f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{channel}-320x180.jpg",
            'status': 'live' if title_elem else 'offline'
        }
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error en {channel}: {type(e).__name__} - {str(e)}")
        return None

def download_thumbnail(url, channel):
    """Descarga imágenes con manejo de errores"""
    try:
        os.makedirs('images', exist_ok=True)
        if not os.path.exists(f'images/{channel}.jpg'):
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            with open(f'images/{channel}.jpg', 'wb') as f:
                f.write(response.content)
        return f'images/{channel}.jpg'
    except Exception as e:
        print(f"❌ No se pudo descargar thumbnail de {channel}")
        return None

def generate_epg():
    """Genera el EPG con todas las protecciones"""
    try:
        channels = load_channels()
        print(f"📡 Procesando {len(channels)} canales...")
        
        epg = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv generator-info-name="TwitchTracker EPG" source="canales.txt">"""
        
        now = datetime.utcnow()
        end_time = now + timedelta(hours=1)
        
        for channel in channels:
            data = scrape_twitchtracker(channel)
            if not data:
                continue
                
            thumb_path = download_thumbnail(data['thumbnail'], channel)
            icon_tag = f'<icon src="{thumb_path}"/>' if thumb_path else ''
            
            # 6. Formato XML seguro (escape de caracteres)
            title = data['title'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            game = data['game'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            epg += f"""
<channel id="{channel}">
    <display-name>{channel}</display-name>
    {icon_tag}
</channel>
<programme channel="{channel}" start="{now.strftime('%Y%m%d%H%M%S')}" stop="{end_time.strftime('%Y%m%d%H%M%S')}">
    <title>{title}</title>
    <desc>Jugando: {game}</desc>
    <category>{game}</category>
    {icon_tag}
</programme>"""
        
        epg += "\n</tv>"
        
        with open('twitch_epg.xml', 'w', encoding='utf-8') as f:
            f.write(epg)
        
        print(f"✅ EPG generado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        return False

if __name__ == "__main__":
    generate_epg()
