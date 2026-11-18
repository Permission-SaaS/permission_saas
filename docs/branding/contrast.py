"""Confere os tokens do branding e imprime as tabelas de contraste.

Uso (na raiz do repositório):  python3 -I docs/branding/contrast.py

O que ele faz:
  1. Lê o tokens.json (a fonte da verdade) e resolve as referências {primitive...}.
  2. Confere se as cores (:root e .dark) e as sombras do tokens.css são as mesmas do tokens.json.
  3. Confere se espaçamentos, alturas de linha e breakpoints são múltiplos de 4, e se o raio
     do projeto é o de 2px (o rounded-xs do Tailwind).
  4. Calcula o contraste (WCAG 2.x) de cada par de texto e fundo e imprime em Markdown.

Sai com código 1 se alguma conferência falhar. Não usa nenhuma biblioteca externa.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKENS = json.loads((HERE / "tokens.json").read_text(encoding="utf-8"))
CSS = (HERE / "tokens.css").read_text(encoding="utf-8")

# Mínimos do WCAG 2.x: texto normal 4,5:1 (AA) e 7:1 (AAA);
# componentes de interface e texto grande 3:1 (AA).
MINIMUM = {"texto": 4.5, "componente": 3.0}
AAA = {"texto": 7.0}


def lookup(path):
    node = TOKENS
    for part in path.split("."):
        node = node[part]
    return node


def resolve(value):
    match = re.fullmatch(r"\{(.+)\}", value)
    return resolve(lookup(match.group(1))["$value"]) if match else value.lower()


def luminance(hex_color):
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    r, g, b = linear
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    light, dark = sorted((luminance(a), luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def theme(name):
    return {key: resolve(tok["$value"]) for key, tok in TOKENS[name].items()}


def css_block(selector):
    match = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", CSS, re.S)
    if not match:
        return {}
    pairs = re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\s*;", match.group(1))
    return {name: value.lower() for name, value in pairs}


# (texto ou elemento, fundo, tipo, onde aparece)
PAIRS = [
    ("foreground", "background", "texto", "texto principal"),
    ("card-foreground", "card", "texto", "texto dentro de card"),
    ("popover-foreground", "popover", "texto", "menu e popover"),
    ("muted-foreground", "background", "texto", "texto secundário"),
    ("muted-foreground", "card", "texto", "texto secundário em card"),
    ("muted-foreground", "muted", "texto", "selo Inativo, área apagada"),
    ("primary-foreground", "primary", "texto", "botão primário"),
    ("secondary-foreground", "secondary", "texto", "botão secundário, destaque"),
    ("accent-foreground", "accent", "texto", "item com hover ou selecionado"),
    ("link", "background", "texto", "link"),
    ("link", "card", "texto", "link em card"),
    ("destructive-foreground", "destructive", "texto", "botão de perigo"),
    ("destructive", "background", "texto", "mensagem de erro"),
    ("destructive", "card", "texto", "erro de campo em card"),
    ("destructive", "destructive-subtle", "texto", "alerta de erro"),
    ("success-foreground", "success", "texto", "botão ou toast de sucesso"),
    ("success", "card", "texto", "texto de sucesso em card"),
    ("success", "success-subtle", "texto", "selo Ativo, alerta de sucesso"),
    ("warning-foreground", "warning", "texto", "toast de aviso"),
    ("warning", "card", "texto", "texto de aviso em card"),
    ("warning", "warning-subtle", "texto", "alerta de aviso"),
    ("info-foreground", "info", "texto", "toast de informação"),
    ("info", "card", "texto", "texto informativo em card"),
    ("info", "info-subtle", "texto", "alerta informativo"),
    ("method-get", "method-get-subtle", "texto", "selo GET"),
    ("method-post", "method-post-subtle", "texto", "selo POST"),
    ("method-put", "method-put-subtle", "texto", "selo PUT"),
    ("method-patch", "method-patch-subtle", "texto", "selo PATCH"),
    ("method-delete", "method-delete-subtle", "texto", "selo DELETE"),
    ("method-get", "card", "texto", "método GET numa tabela"),
    ("method-patch", "card", "texto", "método PATCH numa tabela"),
    ("input", "background", "componente", "borda de campo"),
    ("input", "card", "componente", "borda de campo em card"),
    ("ring", "background", "componente", "anel de foco"),
    ("ring", "card", "componente", "anel de foco em card"),
]

# O dourado só pode ser texto ou ícone no escuro. No claro ele é proibido como texto.
THEME_PAIRS = {
    "light": [
        ("primary", "background", "proibido", "dourado como texto ou ícone"),
        ("primary", "card", "proibido", "dourado como texto ou ícone em card"),
    ],
    "dark": [
        ("primary", "background", "texto", "dourado como texto ou ícone"),
        ("primary", "card", "texto", "dourado como texto ou ícone em card"),
    ],
}

errors = []


def check_css():
    for name, selector in (("light", ":root"), ("dark", ".dark")):
        expected = theme(name)
        found = css_block(selector)
        for key, value in expected.items():
            if found.get(key) != value:
                errors.append(f"tokens.css {selector} --{key}: {found.get(key)} (tokens.json: {value})")
        for key in found.keys() - expected.keys():
            errors.append(f"tokens.css {selector} --{key} não existe no tokens.json")


def css_shadow(layers):
    """Escreve as camadas de sombra do tokens.json do jeito que estão no tokens.css."""
    parts = []
    for layer in layers:
        px = [layer[key] for key in ("offsetX", "offsetY", "blur")]
        if layer["spread"] != "0px":
            px.append(layer["spread"])
        px = ["0" if value == "0px" else value for value in px]
        color = layer["color"]
        r, g, b, a = (int(color[i : i + 2], 16) for i in (1, 3, 5, 7))
        parts.append(f"{' '.join(px)} rgb({r} {g} {b} / {a / 255:.2f})")
    return ", ".join(parts)


def check_shadows():
    for key, tok in TOKENS["shadow"].items():
        expected = css_shadow(tok["$value"])
        match = re.search(rf"--shadow-{key}:\s*([^;]+);", CSS)
        found = match.group(1).strip() if match else None
        if found != expected:
            errors.append(f"tokens.css --shadow-{key}: {found} (tokens.json: {expected})")


def check_multiples_of_four():
    groups = {
        "spacing": TOKENS["spacing"],
        "font.lineHeight": TOKENS["font"]["lineHeight"],
        "breakpoint": TOKENS["breakpoint"],
    }
    for group, tokens in groups.items():
        for key, tok in tokens.items():
            px = int(tok["$value"].removesuffix("px"))
            if px % 4:
                errors.append(f"{group}.{key} = {px}px não é múltiplo de 4")
    if TOKENS["radius"]["default"]["$value"] != "2px":
        errors.append("radius.default não é 2px, o rounded-xs do Tailwind")


def contrast_table(name):
    colors = theme(name)
    rows = []
    for fg, bg, kind, usage in PAIRS + THEME_PAIRS[name]:
        ratio = contrast(colors[fg], colors[bg])
        if kind == "proibido":
            rows.append(f"| `{fg}` `{colors[fg]}` | `{bg}` `{colors[bg]}` | {ratio:.2f}:1 | — | ❌ proibido | — | {usage} |")
            if ratio >= MINIMUM["texto"]:
                errors.append(f"{name}: {fg} sobre {bg} passou ({ratio:.2f}); revise a regra de proibido")
            continue
        minimum = MINIMUM[kind]
        aa = ratio >= minimum
        aaa = "✓" if kind in AAA and ratio >= AAA[kind] else "—"
        if not aa:
            errors.append(f"{name}: {fg} sobre {bg} = {ratio:.2f}:1, abaixo de {minimum}:1")
        rows.append(
            f"| `{fg}` `{colors[fg]}` | `{bg}` `{colors[bg]}` | {ratio:.2f}:1 | {minimum}:1 | "
            f"{'✓' if aa else '❌'} | {aaa} | {usage} |"
        )
    header = "| Texto ou elemento | Fundo | Contraste | Mínimo | AA | AAA | Onde aparece |\n|---|---|---|---|---|---|---|"
    return header + "\n" + "\n".join(rows)


def main():
    check_css()
    check_shadows()
    check_multiples_of_four()
    for name, title in (("light", "Tema claro"), ("dark", "Tema escuro")):
        print(f"### {title}\n")
        print(contrast_table(name))
        print()
    if errors:
        print("FALHOU:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    print("OK: tokens.css igual ao tokens.json, múltiplos de 4 e raio de 2px conferidos, todos os pares no AA.", file=sys.stderr)


if __name__ == "__main__":
    main()
