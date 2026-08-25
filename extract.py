#!/usr/bin/env python3
"""Genera icons.json desde la fuente instalada con Cursor.

No publica ni copia la fuente. Solo lee Cursor.app y escribe metadatos + paths
para el companion local.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = Path(
    "/Applications/Cursor.app/Contents/Resources/app/out/media/cursor-icons-16.woff2"
)
OUT = Path(__file__).parent / "icons.json"
SIZE = 16

SYNONYMS = {
    "magnifying-glass": ["search", "find", "buscar", "lookup", "query"],
    "plus": ["add", "new", "añadir", "create"],
    "x": ["close", "cancel", "cerrar", "remove", "delete"],
    "gear": ["settings", "ajustes", "preferences", "config"],
    "cog": ["settings", "ajustes", "preferences", "config"],
    "agent": ["ai", "bot", "cursor", "assistant", "automation"],
    "agents-swarm": ["ai", "multi", "team", "agents"],
    "bugbot": ["bug", "review", "qa", "audit"],
    "sparkle": ["ai", "generate", "magic"],
    "sparkles": ["ai", "generate", "magic", "auto"],
    "wand": ["ai", "edit", "magic", "transform"],
    "chat-bubble": ["chat", "message", "composer", "conversation", "talk"],
    "terminal": ["cli", "shell", "console", "command"],
    "git-branch": ["git", "vcs", "source", "branch"],
    "git-commit": ["git", "vcs", "commit", "save"],
    "git-pull-request": ["git", "pr", "review", "merge", "pull request"],
    "folder": ["directory", "project", "path"],
    "file": ["document", "page"],
    "calendar": ["date", "schedule", "day", "month", "event"],
    "calendar-hourglass": [
        "appointment",
        "date",
        "day",
        "event",
        "hourglass",
        "length",
        "long",
        "month",
        "planner",
        "schedule",
        "time",
        "wait",
        "duration",
        "deadline",
    ],
    "clock": ["time", "history", "recent", "alarm"],
    "bell": ["notification", "alert", "ring"],
    "lock": ["private", "secure", "password", "protected"],
    "globe": ["web", "browser", "internet", "world"],
    "play": ["run", "start", "execute"],
    "stop": ["halt", "end", "pause"],
    "trash": ["delete", "remove", "bin"],
    "pencil": ["edit", "rename", "write"],
    "copy": ["clone", "duplicate", "clipboard"],
    "check": ["ok", "done", "success", "confirm", "tick"],
    "warning": ["alert", "caution", "danger"],
    "info": ["help", "about", "information"],
    "arrow-bracket-to-down": ["download", "export", "save"],
    "cloud-arrow-down": ["download", "import", "sync"],
    "cloud-arrow-up": ["upload", "export", "sync"],
}

TOKEN_SYNONYMS = {
    "agent": ["ai", "bot", "assistant", "automation"],
    "agents": ["ai", "multi", "team"],
    "alarm": ["alert", "reminder", "wake"],
    "archive": ["box", "storage", "backup"],
    "arrow": ["direction", "navigate", "pointer", "move"],
    "arrows": ["direction", "navigate", "resize", "move"],
    "at": ["email", "mention", "address"],
    "bell": ["notification", "alert", "ring"],
    "book": ["read", "documentation", "guide"],
    "bookmark": ["save", "mark", "favorite"],
    "bracket": ["import", "export", "enter", "exit"],
    "browser": ["web", "internet", "page"],
    "bug": ["issue", "error", "defect"],
    "calendar": ["date", "day", "month", "schedule", "event", "appointment", "planner"],
    "camera": ["photo", "picture", "capture"],
    "chat": ["message", "talk", "conversation"],
    "check": ["done", "ok", "success", "confirm", "tick"],
    "chevron": ["caret", "dropdown", "expand", "collapse"],
    "chevrons": ["caret", "dropdown", "expand", "collapse", "fast"],
    "circle": ["round", "radio", "shape"],
    "clock": ["time", "history", "recent", "alarm"],
    "cloud": ["sync", "remote", "online"],
    "code": ["develop", "programming", "source"],
    "cog": ["settings", "preferences", "config"],
    "comment": ["message", "note", "feedback"],
    "copy": ["duplicate", "clone", "clipboard"],
    "database": ["data", "storage", "sql", "server"],
    "display": ["screen", "monitor", "desktop"],
    "download": ["export", "save"],
    "edit": ["modify", "change", "write"],
    "eye": ["view", "preview", "visible", "show"],
    "file": ["document", "page"],
    "folder": ["directory", "project", "path"],
    "gear": ["settings", "preferences", "config"],
    "git": ["vcs", "version", "source", "control"],
    "glass": ["search", "find", "lookup"],
    "globe": ["web", "internet", "world"],
    "heart": ["like", "favorite", "love"],
    "history": ["recent", "undo", "past"],
    "hourglass": ["time", "wait", "duration", "timer", "long", "length", "deadline", "pending"],
    "image": ["photo", "picture", "media"],
    "info": ["help", "about", "information"],
    "key": ["password", "secure", "login"],
    "layout": ["grid", "panel", "sidebar", "split"],
    "link": ["url", "chain", "connect"],
    "list": ["menu", "items", "bullets"],
    "lock": ["secure", "private", "password", "protected"],
    "magnifying": ["search", "find", "lookup", "query"],
    "mail": ["email", "message", "envelope"],
    "minus": ["remove", "subtract", "delete"],
    "network": ["connection", "server", "topology"],
    "pause": ["halt", "wait", "stop"],
    "pencil": ["edit", "rename", "write"],
    "person": ["user", "account", "profile"],
    "people": ["users", "team", "group"],
    "play": ["run", "start", "execute"],
    "plus": ["add", "new", "create"],
    "pull": ["request", "merge", "review"],
    "request": ["pr", "merge", "review"],
    "search": ["find", "lookup", "query"],
    "settings": ["preferences", "config", "options"],
    "sparkle": ["ai", "generate", "magic"],
    "sparkles": ["ai", "generate", "magic", "auto"],
    "square": ["box", "shape", "tile"],
    "star": ["favorite", "bookmark", "rating"],
    "stop": ["halt", "end"],
    "tag": ["label", "category"],
    "terminal": ["cli", "shell", "console", "command"],
    "trash": ["delete", "remove", "bin"],
    "upload": ["import", "share"],
    "user": ["account", "profile", "person"],
    "warning": ["alert", "caution", "danger"],
    "x": ["close", "cancel", "remove", "delete"],
}

SKIP_TAGS = {"legacy", "filled", "type", "small", "simple", "from", "to", "file"}

CONCEPTS = [
    ("Agent", "agent", "Agente de Cursor"),
    ("Bugbot", "bugbot", "Revisión de bugs"),
    ("Composer", "chat-bubble", "Chat / composer"),
    ("Search", "magnifying-glass", "Búsqueda"),
    ("Source control", "git-branch", "Git"),
    ("Pull request", "git-pull-request", "PR"),
    ("Terminal", "terminal", "Terminal"),
    ("Settings", "cog", "Ajustes"),
    ("AI generate", "sparkles", "Generación"),
    ("Edit", "pencil", "Editar"),
    ("Run", "play", "Ejecutar"),
    ("File", "file", "Archivo"),
    ("Folder", "folder", "Carpeta"),
]


def kind(name: str) -> str:
    if name.startswith("file-type"):
        return "files"
    if name.endswith("-legacy"):
        return "legacy"
    if name.endswith("-filled"):
        return "filled"
    return "current"


def tags_for(name: str) -> list[str]:
    raw = name
    if raw.endswith("-legacy"):
        raw = raw[: -len("-legacy")]
    if raw.endswith("-filled"):
        raw = raw[: -len("-filled")]

    parts = [p for p in raw.split("-") if p and p not in SKIP_TAGS]
    seen: list[str] = []

    def add(*tags: str) -> None:
        for tag in tags:
            if tag and tag not in seen:
                seen.append(tag)

    add(*parts)
    add(*SYNONYMS.get(name, []))
    add(*SYNONYMS.get(raw, []))
    for part in parts:
        add(*TOKEN_SYNONYMS.get(part, []))
    for i in range(len(parts) - 1):
        add(*SYNONYMS.get(f"{parts[i]}-{parts[i+1]}", []))
    return seen


def round_path(d: str) -> str:
    def repl(m: re.Match[str]) -> str:
        n = float(m.group(0))
        r = round(n, 2)
        if r == int(r):
            return str(int(r))
        return f"{r:.2f}".rstrip("0").rstrip(".")

    return re.sub(r"-?\d+\.\d+", repl, d)


def glyph_layers(g, gs, transform) -> list[str]:
    from fontTools.pens.recordingPen import RecordingPen

    pen = RecordingPen()
    g.draw(TransformPen(pen, transform))
    chunks: list[list[tuple[str, tuple]]] = []
    current: list[tuple[str, tuple]] = []
    for op, args in pen.value:
        if op == "moveTo":
            if current:
                chunks.append(current)
            current = [(op, args)]
        else:
            current.append((op, args))
    if current:
        chunks.append(current)

    layers: list[str] = []
    for chunk in chunks:
        layer_pen = SVGPathPen(gs)
        for op, args in chunk:
            if op == "moveTo":
                layer_pen.moveTo(args[0])
            elif op == "lineTo":
                layer_pen.lineTo(args[0])
            elif op == "qCurveTo":
                layer_pen.qCurveTo(*args)
            elif op == "curveTo":
                layer_pen.curveTo(*args)
            elif op == "closePath":
                layer_pen.closePath()
        d = round_path(layer_pen.getCommands())
        if d:
            layers.append(d)
    return layers


def svg_for(d: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16" fill="none">'
        f'<path d="{d}" fill="#111111"/>'
        "</svg>"
    )


def main() -> None:
    if not FONT.exists():
        raise SystemExit(f"No encuentro la fuente en {FONT}")

    font = TTFont(FONT)
    upem = font["head"].unitsPerEm
    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = SIZE / upem
    transform = Transform(scale, 0, 0, -scale, 0, SIZE)

    icons = []
    for cp, name in sorted(cmap.items()):
        if name not in gs:
            continue
        g = gs[name]
        pen = SVGPathPen(gs)
        g.draw(TransformPen(pen, transform))
        d = round_path(pen.getCommands())
        if not d:
            continue
        icons.append(
            {
                "name": name,
                "cp": cp,
                "hex": f"{cp:04X}",
                "kind": kind(name),
                "tags": tags_for(name),
                "path": d,
            }
        )

    for icon in icons:
        g = gs[icon["name"]]
        if icon["kind"] == "files" or "logo" in icon["name"]:
            layers = glyph_layers(g, gs, transform)
            if len(layers) > 1:
                icon["layers"] = layers

    names = {icon["name"] for icon in icons}

    def base_name(name: str) -> str:
        n = name
        if n.endswith("-legacy"):
            n = n[: -len("-legacy")]
        if n.endswith("-filled"):
            n = n[: -len("-filled")]
        return n

    for icon in icons:
        base = base_name(icon["name"])
        icon["base"] = base
        if icon["name"].endswith("-filled"):
            mate = base if base in names else None
        else:
            filled = f"{base}-filled"
            mate = filled if filled in names else None
        icon["mate"] = mate

    payload = {
        "source": "Cursor Icons 16 · extraído en local desde Cursor.app",
        "article": "https://www.minoradventures.co/blog/the-making-of-cursors-icons",
        "author": "Marek Minor / Minor Adventures",
        "size": SIZE,
        "count": len(icons),
        "pairs": sum(1 for icon in icons if icon["mate"] and icon["kind"] == "current"),
        "concepts": CONCEPTS,
        "icons": icons,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    write_file_types_data(icons)
    print(f"{len(icons)} iconos · {payload['pairs']} pares outline/filled → {OUT}")


def write_file_types_data(icons: list[dict]) -> None:
    import colorsys

    def hex_to_rgb(h: str) -> tuple[float, float, float]:
        h = h.lstrip("#")
        return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def rgb_to_hex(r: float, g: float, b: float) -> str:
        return "#{:02X}{:02X}{:02X}".format(
            int(round(r * 255)), int(round(g * 255)), int(round(b * 255))
        )

    def companion_color(hex_color: str) -> str:
        upper = hex_color.upper()
        if upper in {"#FFFFFF", "#FFF"}:
            return "#F7F7F5"
        if upper in {"#000000", "#000"}:
            return "#3F3D38"
        r, g, b = hex_to_rgb(hex_color)
        h, lightness, sat = colorsys.rgb_to_hls(r, g, b)
        sat = min(max(sat, 0.32), 0.52)
        lightness = min(max(lightness + 0.18, 0.58), 0.76)
        return rgb_to_hex(*colorsys.hls_to_rgb(h, lightness, sat))

    brand = {
        "adobe-illustrator": ["#FF9A00", "#330000", "#FFFFFF", "#FF6600"],
        "adobe-photoshop": ["#001E36", "#31A8FF", "#00C8FF", "#FFFFFF"],
        "babel": ["#F5DA55", "#323330", "#FFFFFF"],
        "bazel": ["#43A047", "#78909C", "#FFD54F", "#FFFFFF"],
        "bevy": ["#232326", "#EA8295", "#FFFFFF"],
        "bicep": ["#0078D4", "#FFFFFF", "#000000"],
        "biomejs": ["#60A5FA", "#111827", "#FFFFFF"],
        "bower": ["#EF5734", "#FFCC2F", "#FFFFFF"],
        "bun": ["#FBF0DF", "#000000", "#F9F1E1"],
        "c-plus-plus": ["#00599C", "#004482", "#FFFFFF", "#659AD2"],
        "c-sharp": ["#68217A", "#FFFFFF", "#9B4F96"],
        "clojure": ["#5881D8", "#63B132", "#FFFFFF"],
        "crystal": ["#000000", "#FFFFFF", "#777777"],
        "cuda": ["#76B900", "#000000", "#FFFFFF"],
        "dart": ["#0175C2", "#FFFFFF", "#29B6F6"],
        "docker": ["#2496ED", "#FFFFFF", "#1D63ED"],
        "ejs": ["#FFB300", "#333333", "#FFFFFF"],
        "elixir": ["#4B275F", "#EB64AE", "#FFFFFF"],
        "eslint": ["#808080", "#4B32C3", "#FFFFFF"],
        "f-sharp": ["#378BBA", "#FFFFFF", "#000000"],
        "firebase": ["#FFCA28", "#FFA000", "#FFFFFF"],
        "geckodriver": ["#E24329", "#FFFFFF", "#333333"],
        "git-meta": ["#F05032", "#FFFFFF", "#333333"],
        "go": ["#00ADD8", "#FFFFFF", "#007D9C"],
        "godot": ["#478CBF", "#FFFFFF", "#000000"],
        "grails": ["#428BCA", "#FFFFFF", "#000000"],
        "graphql": ["#E10098", "#FFFFFF", "#600041"],
        "groovy": ["#4298B8", "#FFFFFF", "#000000"],
        "grunt": ["#FAA918", "#333333", "#FFFFFF"],
        "gulp": ["#CF4647", "#FFFFFF", "#333333"],
        "haml": ["#ECECEC", "#000000", "#FFFFFF"],
        "handlebars": ["#F7931E", "#000000", "#FFFFFF"],
        "haskell": ["#5D4F85", "#FFFFFF", "#333333"],
        "ionic": ["#3880FF", "#FFFFFF", "#000000"],
        "java": ["#007396", "#E76F00", "#FFFFFF", "#5382A1"],
        "javascript": ["#F7DF1E", "#000000", "#FFFFFF"],
        "julia": ["#9558B2", "#389826", "#CB3C33", "#FFFFFF"],
        "jupyter": ["#F37626", "#616161", "#767677", "#FFFFFF"],
        "karma": ["#56C5C9", "#FFFFFF", "#333333"],
        "kotlin": ["#7F52FF", "#FFFFFF", "#000000"],
        "latex": ["#008080", "#FFFFFF", "#333333"],
        "liquid": ["#95BF47", "#FFFFFF", "#333333"],
        "maven": ["#C71A36", "#FFFFFF", "#333333"],
        "mustache": ["#FFBE00", "#000000", "#FFFFFF"],
        "npm": ["#CB3837", "#FFFFFF", "#000000"],
        "nunjucks": ["#1C4913", "#FFFFFF", "#333333"],
        "ocaml": ["#EC6813", "#FFFFFF", "#333333"],
        "odata": ["#FF6900", "#FFFFFF", "#333333"],
        "pdf": ["#FF0000", "#FFFFFF", "#000000"],
        "perl": ["#39457A", "#FFFFFF", "#333333"],
        "platformio": ["#FF7F02", "#FFFFFF", "#333333"],
        "powershell": ["#012456", "#FFFFFF", "#333333"],
        "prettier": ["#EA5E5E", "#FFFFFF", "#333333"],
        "prisma": ["#2D3748", "#FFFFFF", "#333333"],
        "prolog": ["#000000", "#FFFFFF", "#333333"],
        "puppet": ["#FFAE1A", "#FFFFFF", "#333333"],
        "python": ["#3776AB", "#FFD43B", "#FFFFFF", "#2B5B84"],
        "reason": ["#DD4A39", "#FFFFFF", "#333333"],
        "rescript": ["#E6484F", "#FFFFFF", "#333333"],
        "rollup": ["#FF3333", "#FFFFFF", "#333333"],
        "rust": ["#000000", "#CE422B", "#FFFFFF"],
        "sass": ["#CD6799", "#FFFFFF", "#000000"],
        "sbt": ["#882AA3", "#FFFFFF", "#333333"],
        "scala": ["#DC322F", "#FFFFFF", "#000000"],
        "slim": ["#FF8C00", "#FFFFFF", "#333333"],
        "stylus": ["#FF6347", "#FFFFFF", "#333333"],
        "sublime": ["#FF9800", "#FFFFFF", "#333333"],
        "svelte": ["#FF3E00", "#FFFFFF", "#000000"],
        "swift": ["#F05138", "#FFFFFF", "#000000"],
        "terraform": ["#5C4EE5", "#FFFFFF", "#000000"],
        "typescript": ["#3178C6", "#FFFFFF", "#235A97"],
        "vala": ["#A56DE2", "#FFFFFF", "#333333"],
        "vite": ["#646CFF", "#FFD62E", "#FFFFFF"],
        "vsc": ["#007ACC", "#FFFFFF", "#333333"],
        "vue": ["#41B883", "#35495E", "#FFFFFF"],
        "web-assembly": ["#654FF0", "#FFFFFF", "#333333"],
        "webpack": ["#8ED6FB", "#1C78C0", "#FFFFFF"],
        "windows": ["#0078D4", "#FFFFFF", "#333333"],
        "yarn": ["#2C8EBB", "#FFFFFF", "#000000"],
        "zig": ["#F7A41D", "#000000", "#FFFFFF"],
    }

    meta_overrides = {
        "adobe-illustrator": ("Adobe Illustrator", "logo.ai", [".ai", ".eps"]),
        "adobe-photoshop": ("Adobe Photoshop", "design.psd", [".psd", ".psb"]),
        "babel": ("Babel", "babel.config.js", [".js", ".jsx", ".mjs"]),
        "bazel": ("Bazel", "BUILD", [".bazel", ".bzl"]),
        "bevy": ("Bevy", "bevy.toml", [".toml"]),
        "bicep": ("Bicep", "main.bicep", [".bicep"]),
        "biomejs": ("Biome", "biome.json", [".json"]),
        "bower": ("Bower", "bower.json", [".json"]),
        "bun": ("Bun", "bun.lockb", [".lockb", ".bun"]),
        "c-plus-plus": ("C++", "main.cpp", [".cpp", ".cc", ".hpp", ".h"]),
        "c-sharp": ("C#", "Program.cs", [".cs"]),
        "docker": ("Docker", "Dockerfile", [".dockerfile"]),
        "go": ("Go", "main.go", [".go"]),
        "java": ("Java", "App.java", [".java"]),
        "javascript": ("JavaScript", "index.js", [".js", ".mjs", ".cjs"]),
        "jupyter": ("Jupyter", "notebook.ipynb", [".ipynb"]),
        "kotlin": ("Kotlin", "App.kt", [".kt", ".kts"]),
        "pdf": ("PDF", "document.pdf", [".pdf"]),
        "python": ("Python", "main.py", [".py", ".pyw"]),
        "rust": ("Rust", "lib.rs", [".rs"]),
        "sass": ("Sass", "styles.scss", [".scss", ".sass"]),
        "scala": ("Scala", "App.scala", [".scala"]),
        "swift": ("Swift", "App.swift", [".swift"]),
        "svelte": ("Svelte", "App.svelte", [".svelte"]),
        "terraform": ("Terraform", "main.tf", [".tf", ".tfvars"]),
        "typescript": ("TypeScript", "index.ts", [".ts", ".tsx"]),
        "vue": ("Vue", "App.vue", [".vue"]),
        "web-assembly": ("WebAssembly", "module.wasm", [".wasm"]),
        "windows": ("Windows", "app.exe", [".exe", ".dll"]),
        "yarn": ("Yarn", "yarn.lock", [".lock"]),
    }

    label_fixes = {
        "c-plus-plus": "C++",
        "c-sharp": "C#",
        "f-sharp": "F#",
        "web-assembly": "WebAssembly",
        "biomejs": "Biome",
        "git-meta": "Git metadata",
        "platformio": "PlatformIO",
        "vsc": "Visual Studio Code",
        "ejs": "EJS",
        "odata": "OData",
        "sbt": "SBT",
        "npm": "npm",
    }

    ext_map = {
        "babel": ".js", "bazel": ".bazel", "bevy": ".toml", "bicep": ".bicep",
        "biomejs": ".json", "bower": ".json", "bun": ".ts", "clojure": ".clj",
        "crystal": ".cr", "cuda": ".cu", "dart": ".dart", "docker": "",
        "ejs": ".ejs", "elixir": ".ex", "eslint": ".js", "firebase": ".json",
        "geckodriver": ".js", "git-meta": ".git", "godot": ".gd", "grails": ".groovy",
        "groovy": ".groovy", "grunt": ".js", "gulp": ".js", "haml": ".haml",
        "handlebars": ".hbs", "haskell": ".hs", "ionic": ".tsx", "java": ".java",
        "javascript": ".js", "julia": ".jl", "jupyter": ".ipynb", "karma": ".js",
        "kotlin": ".kt", "latex": ".tex", "liquid": ".liquid", "maven": ".xml",
        "mustache": ".mustache", "npm": ".json", "nunjucks": ".njk", "ocaml": ".ml",
        "odata": ".odata", "pdf": ".pdf", "perl": ".pl", "platformio": ".ini",
        "powershell": ".ps1", "prettier": ".json", "prisma": ".prisma", "prolog": ".pl",
        "puppet": ".pp", "python": ".py", "reason": ".re", "rescript": ".res",
        "rollup": ".js", "rust": ".rs", "sass": ".scss", "sbt": ".sbt", "scala": ".scala",
        "slim": ".slim", "stylus": ".styl", "sublime": ".sublime-project", "svelte": ".svelte",
        "swift": ".swift", "terraform": ".tf", "typescript": ".ts", "vala": ".vala",
        "vite": ".ts", "vsc": ".code-workspace", "vue": ".vue", "web-assembly": ".wasm",
        "webpack": ".js", "windows": ".exe", "yarn": ".lock", "zig": ".zig",
    }

    bases = sorted({i["base"] for i in icons if i["kind"] == "files"})
    file_meta: dict[str, dict] = {}
    file_palettes: dict[str, list[str]] = {}
    for base in bases:
        slug = base.replace("file-type-", "")
        if slug in meta_overrides:
            label, sample, extensions = meta_overrides[slug]
        else:
            label = label_fixes.get(slug, slug.replace("-", " ").title())
            ext = ext_map.get(slug, f".{slug.split('-')[-1]}")
            sample = f"file{ext}" if ext else slug
            extensions = [ext] if ext else [f".{slug}"]
        file_meta[base] = {"label": label, "sample": sample, "ext": extensions}
        colors = brand.get(slug, ["#6A6863", "#B4B1AA", "#FFFFFF"])
        file_palettes[base] = [companion_color(c) for c in colors]

    file_meta["cube-nodes"] = {"label": "3D Model", "sample": "model.obj", "ext": [".obj"]}
    file_meta["package-zipper"] = {"label": "Archive", "sample": "archive.zip", "ext": [".zip"]}

    file_types_curated = [
        {"icon": "cube-nodes-filled", "slug": "cube-nodes", "label": "3D Model", "sample": "model.obj", "ext": [".obj"], "color": "#DE9076"},
        {"icon": "file-type-adobe-illustrator-filled", "slug": "file-type-adobe-illustrator", "label": "Adobe Illustrator", "sample": "logo.ai", "ext": [".ai", ".eps"], "color": "#C19688"},
        {"icon": "file-type-adobe-photoshop-filled", "slug": "file-type-adobe-photoshop", "label": "Adobe Photoshop", "sample": "design.psd", "ext": [".psd", ".psb"], "color": "#81A1C1"},
        {"icon": "file-type-swift-filled", "slug": "file-type-swift", "label": "Swift", "sample": "App.swift", "ext": [".swift"], "color": "#EB7C6E"},
        {"icon": "package-zipper-filled", "slug": "package-zipper", "label": "Archive", "sample": "archive.zip", "ext": [".zip"], "color": "#D0A268"},
        {"icon": "file-type-babel-filled", "slug": "file-type-babel", "label": "Babel", "sample": "babel.config.js", "ext": [".js", ".jsx", ".mjs"], "color": "#F5D28E"},
        {"icon": "file-type-bazel-filled", "slug": "file-type-bazel", "label": "Bazel", "sample": "BUILD", "ext": [".bazel", ".bzl"], "color": "#6DA481"},
        {"icon": "file-type-bevy-filled", "slug": "file-type-bevy", "label": "Bevy", "sample": "bevy.toml", "ext": [".toml"], "color": "#7FB4CA"},
        {"icon": "file-type-bicep-filled", "slug": "file-type-bicep", "label": "Bicep", "sample": "main.bicep", "ext": [".bicep"], "color": "#7698D9"},
        {"icon": "file-type-windows-filled", "slug": "file-type-windows", "label": "Windows", "sample": "app.exe", "ext": [".exe", ".dll"], "color": "#909090"},
        {"icon": "file-type-biomejs-filled", "slug": "file-type-biomejs", "label": "Biome", "sample": "biome.json", "ext": [".json"], "color": "#A691D8"},
        {"icon": "file-type-bower-filled", "slug": "file-type-bower", "label": "Bower", "sample": "bower.json", "ext": [".json"], "color": "#E28A7A"},
        {"icon": "file-type-bun-filled", "slug": "file-type-bun", "label": "Bun", "sample": "bun.lockb", "ext": [".lockb", ".bun"], "color": "#F6AD7E"},
    ]

    logo_palettes = {
        "cursor-logo": ["#3F3D38", "#F7F7F5", "#E24E1B", "#6A6863"],
        "logo-github": ["#3F3D38", "#F7F7F5"],
        "logo-python": ["#5B9BD5", "#FFD966", "#3F3D38", "#F7F7F5"],
        "logo-azure": ["#0078D4", "#FFFFFF", "#333333"],
        "logo-azure-devops": ["#0078D4", "#FFFFFF", "#333333"],
        "logo-mcp": ["#3F3D38", "#F7F7F5"],
        "logo-vscode": ["#007ACC", "#FFFFFF", "#333333"],
        "logo-vscode-insiders": ["#007ACC", "#FFFFFF", "#333333"],
        "logo-markdown": ["#3F3D38", "#F7F7F5"],
    }
    for name, colors in list(logo_palettes.items()):
        logo_palettes[name] = [companion_color(c) for c in colors]
        filled = f"{name}-filled"
        if any(i["name"] == filled for i in icons):
            logo_palettes[filled] = logo_palettes[name]

    out = Path(__file__).parent / "file-types-data.js"
    out.write_text(
        "/* generated by extract.py — do not edit */\n"
        f"const FILE_TYPE_META = {json.dumps(file_meta, ensure_ascii=False, separators=(',', ':'))};\n"
        f"const FILE_PALETTES = {json.dumps(file_palettes, ensure_ascii=False, separators=(',', ':'))};\n"
        f"const LOGO_PALETTES = {json.dumps(logo_palettes, ensure_ascii=False, separators=(',', ':'))};\n"
        f"const FILE_TYPES_CURATED = {json.dumps(file_types_curated, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
