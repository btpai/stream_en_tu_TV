#!/bin/bash

# Configuración
LISTA_CANALES="canales.txt"
EPG_FILE="twitch_epg.xml"

# Cabecera EPG
cat > "$EPG_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv generator-info-name="yt-dlp EPG">
EOF

# Procesar cada canal
while IFS= read -r canal; do
    echo "Procesando $canal..."
    
    # Obtener metadatos con yt-dlp
    METADATA=$(yt-dlp --dump-json "https://www.twitch.tv/$canal" 2>/dev/null)
    
    if [ -n "$METADATA" ]; then
        TITLE=$(echo "$METADATA" | jq -r '.title // "Stream en vivo"')
        UPLOADER=$(echo "$METADATA" | jq -r '.uploader // "'"$canal"'"')
        THUMBNAIL=$(echo "$METADATA" | jq -r '.thumbnail // ""')
        
        # Descargar thumbnail si existe
        if [[ "$THUMBNAIL" == http* ]]; then
            wget -q "$THUMBNAIL" -O "$canal.jpg"
            IMAGE_TAG="<icon src=\"$canal.jpg\" />"
        else
            IMAGE_TAG=""
        fi

        # Añadir al EPG
        cat >> "$EPG_FILE" <<EOF
<channel id="$canal">
    <display-name>$UPLOADER</display-name>
    $IMAGE_TAG
</channel>
<programme channel="$canal" start="$(date -u +%Y%m%d%H%M%S)" stop="$(date -u -d '+1 hour' +%Y%m%d%H%M%S)">
    <title>$TITLE</title>
    <desc>Stream en vivo de $UPLOADER</desc>
    $IMAGE_TAG
</programme>
EOF
        echo "✅ $canal añadido"
    else
        echo "❌ $canal no disponible"
    fi
done < "$LISTA_CANALES"

echo "</tv>" >> "$EPG_FILE"
echo "EPG generado en $EPG_FILE"
