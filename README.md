# Panel de seguimiento de coches de segunda mano

Vigila precios y bajas (vendido/retirado) de anuncios en coches.net, Wallapop,
Milanuncios y Autocasion, y detecta anuncios nuevos según tus criterios.
Todo corre solo, gratis, en GitHub Actions — tú solo entras a ver el panel.

## 1. Crear tu cuenta y repositorio (una vez)

1. Crea una cuenta gratuita en https://github.com/signup
2. Crea un repositorio nuevo (botón verde "New"), llámalo por ejemplo `car-tracker`.
   Que sea **público** (para poder usar GitHub Pages gratis) o privado si tienes
   plan que lo permita.
3. Sube todos los archivos de esta carpeta al repositorio. La forma más fácil:
   - Entra al repo → "Add file" → "Upload files" → arrastra toda la carpeta
     descomprimida (o usa `git` si te manejas con la terminal).

## 2. Activar GitHub Pages (para ver el panel en una URL)

1. En el repositorio: **Settings → Pages**
2. En "Source" elige: **Deploy from a branch**
3. Branch: `main`, carpeta: **/docs** → Guardar
4. En un par de minutos tu panel estará en:
   `https://TU-USUARIO.github.io/car-tracker/`

## 3. Activar la ejecución automática

1. Ve a la pestaña **Actions** del repositorio.
2. Si te pide habilitarlas, acepta ("I understand my workflows, go ahead and enable them").
3. Verás el workflow **"Seguimiento de anuncios de coches"**. Se ejecutará
   solo cada 8 horas a partir de ahora.
4. Para probarlo ya mismo sin esperar: entra al workflow → botón **"Run workflow"**.

## 4. Configurar qué quieres seguir

Edita el archivo `scraper/config.yaml` directamente desde GitHub (icono del
lápiz) o en tu ordenador:

- `tracked_urls`: pega aquí las URLs de anuncios concretos que te interesan.
- `searches`: define criterios (marca, modelo, precio máximo, ciudad) para
  que te avise de anuncios **nuevos** que aparezcan.

Cada vez que guardes cambios en este archivo, la siguiente ejecución
automática (o una manual con "Run workflow") ya los tendrá en cuenta.

## 5. Ver el panel

Abre `https://TU-USUARIO.github.io/car-tracker/` cuando quieras. Verás:

- **Seguimiento**: cada anuncio guardado, su historial de precio (gráfica),
  si sigue activo o ha sido retirado/vendido, y cuándo se comprobó por última vez.
- **Nuevas ofertas**: anuncios que han aparecido nuevos según tus búsquedas
  guardadas, desde la última comprobación.

## Cosas a tener en cuenta

- **Frecuencia**: por defecto cada 8 horas. Se cambia en
  `.github/workflows/scrape.yml`, línea `cron: "0 */8 * * *"`.
- **Los sitios cambian su web de vez en cuando.** Si en algún momento un sitio
  deja de detectar precios o anuncios correctamente, seguramente cambiaron su
  HTML. Los archivos en `scraper/sites/` tienen comentarios
  `AJUSTAR SI CAMBIA LA WEB` en los puntos más sensibles — puedes traerme el
  HTML de un anuncio de ejemplo y te ayudo a arreglarlo.
- **Términos de uso**: haz un uso moderado (la frecuencia de 8h ya es
  conservadora) y personal, no comercial ni masivo.
- **Wallapop** usa su API interna (no oficial) en vez de HTML, que suele ser
  más estable pero también puede cambiar sin aviso.

## Estructura del proyecto

```
car-tracker/
├── scraper/
│   ├── config.yaml          ← tus anuncios y búsquedas (edítalo)
│   ├── scraper.py            ← orquestador principal
│   ├── utils.py
│   └── sites/                ← un módulo por cada web
│       ├── coches_net.py
│       ├── wallapop.py
│       ├── milanuncios.py
│       └── autocasion.py
├── .github/workflows/scrape.yml   ← automatización (GitHub Actions)
└── docs/
    ├── index.html             ← el panel (GitHub Pages sirve esto)
    └── data/listings.json     ← histórico de datos (se actualiza solo)
```
