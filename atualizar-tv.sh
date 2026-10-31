#!/bin/bash
# Reempacota o painel e reinstala na TV Samsung (modo desenvolvedor ligado, mesma rede).
# Uso: ./atualizar-tv.sh [IP_DA_TV]
set -e
TV_IP="${1:-192.168.15.2}"
TARGET="UN58RU7100GXZD"
HERE="$(cd "$(dirname "$0")" && pwd)"
TIZEN="$HOME/tizen-studio/tools/ide/bin/tizen"
SDB="$HOME/tizen-studio/tools/sdb"

cp "$HERE/index.html" "$HERE/tizen-app/index.html"
mkdir -p "$HERE/dist"
"$TIZEN" package -t wgt -s PainelTV -o "$HERE/dist" -- "$HERE/tizen-app" | tail -1
mv -f "$HERE/dist/Painel da Sala.wgt" "$HERE/dist/PainelDaSala.wgt"

"$SDB" connect "$TV_IP:26101"
"$TIZEN" install -n PainelDaSala.wgt -t "$TARGET" -- "$HERE/dist" | tail -2
"$TIZEN" run -p paineltv01.PainelDaSala -t "$TARGET" | tail -1
