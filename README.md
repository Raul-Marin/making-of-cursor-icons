# Companion local · Cursor Icons

**Live:** [https://cursoricons.vercel.app](https://cursoricons.vercel.app)

Studio interno inspirado en el companion que Marek Minor describe en
[The making of Cursor’s icons](https://www.minoradventures.co/blog/the-making-of-cursors-icons),
con la estructura de catálogo de un icon explorer (packs, inspector, copy SVG)
y la paleta de cursor.com. La UI usa **Cursor Gothic** y **Cursor Display** (copias locales en `fonts/`).

No está afiliado a Cursor ni a Minor Adventures. El trabajo de diseño es de Marek Minor / Minor Adventures; los iconos son de Cursor.

## Qué hace (no se ha quitado nada)

- Grid con búsqueda por **nombre y tags** (`/` enfoca el buscador; `search` encuentra `magnifying-glass`)
- Hover: copiar **SVG listo para Figma**, copiar nombre, descargar `.svg`
- Inspector: escala, tags, símbolo, codepoint CSS, snippet React
- Tabla de **conceptos** (un icono por idea) y crédito al artículo
- Filtros: actuales, todos, filled, file type, legacy
- Vista 16 / 24 (24 es escala del corte 16; Cursor.app no incluye el woff2 de 24)

## Lo nuevo del studio

- Sidebar de **packs** (Outline, Filled, File type, Legacy, Git, AI…)
- Un glifo = un path de `cursor-icons-16.woff2` (outline y filled son cortes reales de la fuente)
- Tinta única para copiar a Figma; 16 / 24 es solo escala de vista

## Cómo arrancarlo

Hace falta tener Cursor instalado en macOS. La fuente **no se sube al repo**.

```bash
cd icon-showcase
python3 extract.py
python3 -m http.server 8765
```

Abre [http://127.0.0.1:8765/](http://127.0.0.1:8765/)

## Compartir con la comunidad

Publicable: este visor, `extract.py`, el crédito al artículo.

No publicar: `cursor-icons-16.woff2`, `icons.json`, `fonts/*.woff2`, ni un pack de 1.609 SVG.

Las UI fonts (Cursor Gothic / Cursor Display) se copian a `fonts/` desde tu carpeta local, p. ej. `~/Desktop/cursor-fonts`. No van en el repo.
