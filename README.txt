SERVIDOR SPOTICLONE — Deploy gratuito en Render.com
====================================================

PASOS PARA DESPLEGARLO (5 minutos):

1. Crea cuenta gratis en https://render.com

2. Sube esta carpeta a GitHub:
   - Crea repo en github.com/nuevo
   - Sube los 3 archivos: main.py, requirements.txt, render.yaml

3. En Render.com:
   - New → Web Service
   - Conecta tu repo de GitHub
   - Render detecta render.yaml automáticamente
   - Deploy

4. Te dará una URL tipo:
   https://spoticlone-server.onrender.com

5. Copia esa URL y ponla en la app Android:
   Abre: app/src/main/java/com/spoticlone/app/api/AudioApiManager.java
   Cambia: SERVER_URL = "https://TU-URL.onrender.com"

ENDPOINTS:
  GET /audio?id=VIDEO_ID  → devuelve URL directa del audio
  GET /search?q=QUERY     → busca canciones
  GET /health             → comprueba que está vivo

NOTA: El plan gratuito de Render apaga el servidor si no hay peticiones
en 15 minutos. La primera petición tarda ~30 segundos en arrancar.
Para evitarlo, usa UptimeRobot (gratis) para hacer ping cada 10 min.
