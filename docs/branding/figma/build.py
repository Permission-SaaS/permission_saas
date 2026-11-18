"""Gera, a partir do tokens.json, os arquivos para colar no plugin Tokens Studio do Figma.

Uso (na raiz do repositório):
    python3 -I docs/branding/figma/build.py           # (re)escreve os arquivos desta pasta
    python3 -I docs/branding/figma/build.py --check   # só confere se estão em dia (sai com 1 se não)

Cada arquivo é um conjunto (token set) do Tokens Studio, no formato padrão dele ("legacy":
chaves value/type, sem o $). No plano gratuito, cada conjunto exportado vira uma coleção de
variáveis no Figma, com um modo só:

    primitive.json  as escalas de cor (neutral, gold, red...)
    light.json      as cores semânticas do tema claro, que apontam para as primitivas
    dark.json       as do tema escuro (exportar só se precisar; o mockup usa o claro)
    base.json       espaçamento e raio (variáveis numéricas), estilos de texto e sombras

Não edite os arquivos gerados: mude o tokens.json e rode de novo.
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOKENS = json.loads((HERE.parent / "tokens.json").read_text(encoding="utf-8"))


def lookup(path):
    node = TOKENS
    for part in path.split("."):
        node = node[part]
    return node["$value"]


def resolve(value):
    match = re.fullmatch(r"\{(.+)\}", str(value))
    return resolve(lookup(match.group(1))) if match else value


def px(value):
    """'16px' -> '16' (o plugin descarta a unidade nas variáveis numéricas)."""
    return str(value).removesuffix("px")


def reference(value):
    """'{primitive.neutral.50}' -> '{neutral.50}': no plugin, o conjunto não faz parte do nome."""
    return value.replace("{primitive.", "{")


def primitives():
    out = {}
    for group, node in TOKENS["primitive"].items():
        if "$value" in node:
            out[group] = {"value": node["$value"], "type": "color"}
        else:
            out[group] = {tone: {"value": tok["$value"], "type": "color"} for tone, tok in node.items()}
    return out


def theme(name):
    return {key: {"value": reference(tok["$value"]), "type": "color"} for key, tok in TOKENS[name].items()}


def typography(token):
    value = token["$value"]
    family = resolve(value["fontFamily"])[0]
    return {
        "value": {
            "fontFamily": family,
            "fontWeight": str(resolve(value["fontWeight"])),
            "fontSize": px(resolve(value["fontSize"])),
            "lineHeight": px(resolve(value["lineHeight"])),
            "letterSpacing": "0",
            "paragraphSpacing": "0",
            "paragraphIndent": "0",
            "textCase": "none",
            "textDecoration": "none",
        },
        "type": "typography",
        "description": token["$description"],
    }


def text_styles(node):
    if node.get("$type") == "typography":
        return typography(node)
    return {key: text_styles(child) for key, child in node.items()}


def shadow(token):
    layers = [
        {
            "x": px(layer["offsetX"]),
            "y": px(layer["offsetY"]),
            "blur": px(layer["blur"]),
            "spread": px(layer["spread"]),
            "color": layer["color"],
            "type": "dropShadow",
        }
        for layer in token["$value"]
    ]
    return {"value": layers, "type": "boxShadow", "description": token["$description"]}


def base():
    spacing = {px(tok["$value"]): {"value": px(tok["$value"]), "type": "spacing"} for tok in TOKENS["spacing"].values()}
    radius = TOKENS["radius"]
    return {
        "espaco": spacing,
        "raio": {
            "padrao": {"value": px(radius["default"]["$value"]), "type": "borderRadius", "description": radius["default"]["$description"]},
            "total": {"value": px(radius["full"]["$value"]), "type": "borderRadius", "description": radius["full"]["$description"]},
        },
        "texto": text_styles(TOKENS["textStyle"]),
        "sombra": {
            "1-card": shadow(TOKENS["shadow"]["sm"]),
            "2-menu": shadow(TOKENS["shadow"]["md"]),
            "3-modal": shadow(TOKENS["shadow"]["lg"]),
        },
    }


FILES = {
    "primitive.json": primitives,
    "light.json": lambda: theme("light"),
    "dark.json": lambda: theme("dark"),
    "base.json": base,
}


def main():
    check = "--check" in sys.argv
    stale = []
    for name, build in FILES.items():
        content = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
        path = HERE / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        print("Desatualizado em relação ao tokens.json: " + ", ".join(stale), file=sys.stderr)
        print("Rode: python3 -I docs/branding/figma/build.py", file=sys.stderr)
        sys.exit(1)
    print("OK: arquivos do Figma " + ("em dia." if check else "gerados."), file=sys.stderr)


if __name__ == "__main__":
    main()
