#!/usr/bin/env bash
#
# Regressão do checar-copy contra o próprio corpus.
#
# Por que existe: as regras são expressões regulares. Mexer numa para pegar um
# caso novo quebra outro em silêncio — o script continua rodando, só que errado.
# Aqui o corpus vira a suíte: cada trecho reprovado tem que continuar reprovando
# pela regra dele, e cada versão corrigida tem que continuar passando limpa.
#
# Uso: ./testes/rodar.sh
# Sai 0 se tudo bate, 1 se alguma coisa regrediu.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

GATE=./checar-copy
CORPUS=corpus/tiques-pt-br.jsonl

[ -x "$GATE" ] || { echo "não achei o $GATE"; exit 2; }
[ -f "$CORPUS" ] || { echo "não achei o $CORPUS — rode corpus/montar.py"; exit 2; }

tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
falhas=0; total=0

# Mapeia o nome que o script imprime de volta para o id da regra.
id_da_linha() {
  case "$1" in
    *"Construcao binaria"*) echo binaria ;;
    *'"pra"'*|*"pra em vez"*) echo pra ;;
    *Emoji*)                echo emoji ;;
    *Preco*)                echo preco ;;
    *Anedota*)              echo anedota ;;
    *"Palavra-marca"*)      echo generico ;;
    *Urgencia*)             echo urgencia ;;
  esac
}

# `< /dev/null` no perl é obrigatório: sem isso ele consome o stdin do laço de
# fora, que está lendo o corpus, e o teste some com as linhas restantes.
disparos() {  # $1 = arquivo de texto → ids das regras que dispararam, um por linha
  perl "$GATE" "$1" < /dev/null 2>&1 | grep -E '^\[(REPROVA|AVISO)\]' | while read -r l; do id_da_linha "$l"; done | sort -u
}

while IFS= read -r linha <&3; do
  [ -z "$linha" ] && continue
  total=$((total + 1))

  regra=$(printf '%s' "$linha" | python3 -c 'import sys,json;print(json.load(sys.stdin)["regra"])')
  printf '%s' "$linha" | python3 -c 'import sys,json;print(json.load(sys.stdin)["texto"])'  > "$tmp/ruim.txt"
  printf '%s' "$linha" | python3 -c 'import sys,json;print(json.load(sys.stdin)["certo"])'  > "$tmp/bom.txt"
  eid=$(printf '%s' "$linha" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

  # 1. o trecho reprovado tem que disparar a PRÓPRIA regra.
  # Guarda a saída antes de testar: `disparos | grep -q` sob `pipefail` reporta
  # falha mesmo quando o grep ACHA — o -q sai no primeiro acerto, mata o
  # processo de cima com SIGPIPE, e o pipefail devolve esse status.
  achou=$(disparos "$tmp/ruim.txt")
  if ! printf '%s\n' "$achou" | grep -qx "$regra"; then
    echo "FALHOU  $eid — o reprovado deixou de disparar '$regra'"
    falhas=$((falhas + 1))
  fi

  # 2. a versão corrigida tem que sair limpa de TODAS
  sujo=$(disparos "$tmp/bom.txt" | tr '\n' ' ')
  if [ -n "${sujo// /}" ]; then
    echo "FALHOU  $eid — a versão corrigida passou a disparar: $sujo"
    falhas=$((falhas + 1))
  fi
done 3< "$CORPUS"

echo
if [ "$falhas" -eq 0 ]; then
  echo "OK — $total exemplos, nenhuma regressão."
  exit 0
fi
echo "$falhas falha(s) em $total exemplos."
echo "Alguma regra mudou de comportamento. Confira o diff do checar-copy."
exit 1
