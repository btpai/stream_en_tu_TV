#!/bin/bash
#!/bin/bash

# Configuración
LISTA_CANALES="canales.txt"
LISTA_IPTV="twitch_iptv.m3u"

echo "#EXTM3U" > $LISTA_IPTV

while IFS= read -r canal; do
  echo "Procesando $canal..."
  URL=$(yt-dlp -g "https://www.twitch.tv/$canal" --no-live-from-start 2>/dev/null)
  
  if [ -n "$URL" ]; then
    echo "#EXTINF:-1 group-title=\"Twitch\" tvg-id=\"$canal\",$canal" >> $LISTA_IPTV
    echo "$URL" >> $LISTA_IPTV
    echo "✅ $canal añadido"
  else
    echo "❌ $canal no disponible"
  fi
done < $LISTA_CANALES

echo "Lista actualizada en $LISTA_IPTV"
