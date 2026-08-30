#!/usr/bin/env python3
"""
Monta o corpus verificando cada exemplo contra o `checar-copy` de verdade.

Por que existe: corpus de exemplos onde os exemplos não foram testados é
opinião com cara de dado. Aqui todo exemplo passa pelo gate real antes de
entrar — o que é marcado como reprovado tem que reprovar, o que é marcado
como corrigido tem que passar, e o que não bater fica de fora com o motivo
registrado.

Entrada:  bruto.json   (saída dos geradores, por regra + negativos)
Saída:    tiques-pt-br.jsonl · negativos.jsonl · RELATORIO.md

Uso: python3 corpus/montar.py
"""
import json
import pathlib
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
GATE = RAIZ / "checar-copy"
BRUTO = RAIZ / "corpus" / "bruto.json"


def rodar_gate(texto: str) -> tuple[set[str], str]:
    """Roda o checar-copy num trecho. Devolve (ids das regras que dispararam, saída crua)."""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8", delete=False) as f:
        f.write(texto if texto.endswith("\n") else texto + "\n")
        caminho = f.name
    try:
        r = subprocess.run(
            ["perl", str(GATE), caminho],
            capture_output=True, text=True, timeout=30,
        )
    finally:
        pathlib.Path(caminho).unlink(missing_ok=True)

    saida = r.stdout + r.stderr
    # O script imprime o NOME da regra, não o id. Mapeia de volta.
    nomes = {
        "Construcao binaria": "binaria",
        "pra": "pra",
        "Emoji": "emoji",
        "Preco": "preco",
        "Anedota": "anedota",
        "Palavra-marca": "generico",
        "Urgencia": "urgencia",
    }
    disparou = set()
    for linha in saida.splitlines():
        if linha.startswith("[REPROVA]") or linha.startswith("[AVISO]"):
            for marca, rid in nomes.items():
                if marca in linha:
                    disparou.add(rid)
    return disparou, saida


def main() -> int:
    if not BRUTO.exists():
        print(f"falta {BRUTO} — rode o gerador antes", file=sys.stderr)
        return 2

    dados = json.loads(BRUTO.read_text(encoding="utf-8"))
    aceitos, rejeitados = [], []
    n = 0

    for bloco in dados.get("porRegra", []):
        # O id vem injetado por quem monta o bruto.json — os geradores devolvem
        # `regra` como descrição longa, que não serve de chave.
        regra = bloco["id"]
        for ex in bloco.get("exemplos", []):
            n += 1
            disp_ruim, _ = rodar_gate(ex["texto"])
            disp_bom, _ = rodar_gate(ex["certo"])

            # O reprovado TEM que disparar a própria regra. Quando não dispara,
            # não é exemplo ruim — é BURACO DE COBERTURA do verificador, e vale
            # mais publicado do que descartado.
            if regra not in disp_ruim:
                rejeitados.append({**ex, "regra": regra, "tipo": "nao_pego",
                                   "motivo": f"o exemplo reprovado não disparou '{regra}' (disparou: {sorted(disp_ruim) or 'nada'})"})
                continue
            # O corrigido tem que sair limpo de TUDO, não só da própria regra.
            if disp_bom:
                rejeitados.append({**ex, "regra": regra, "tipo": "corrigido_sujo",
                                   "motivo": f"a versão corrigida ainda dispara {sorted(disp_bom)}"})
                continue

            aceitos.append({
                "id": f"{regra}-{len([a for a in aceitos if a['regra'] == regra]) + 1:03d}",
                "regra": regra,
                "nivel": "aviso" if regra in ("generico", "urgencia") else "reprova",
                "formato": ex.get("formato", ""),
                "texto": ex["texto"],
                "porque": ex["porque"],
                "certo": ex["certo"],
                "verificado": True,
            })

    # Negativos: contêm o padrão e MESMO ASSIM devem passar por julgamento humano.
    # O gate vai disparar neles — é esse o ponto. Registramos o que ele acusa.
    negativos = []
    for caso in (dados.get("negativos") or {}).get("casos", []):
        disp, _ = rodar_gate(caso["texto"])
        negativos.append({
            "id": f"neg-{len(negativos) + 1:03d}",
            "situacao": caso.get("situacao", ""),
            "texto": caso["texto"],
            "regra_que_dispara": caso["regra_que_dispara"],
            "gate_disparou": sorted(disp),
            "por_que_passa": caso["por_que_passa"],
            "veredito_humano": "passa",
        })

    saida = RAIZ / "corpus"
    with (saida / "tiques-pt-br.jsonl").open("w", encoding="utf-8") as f:
        for a in aceitos:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")
    with (saida / "negativos.jsonl").open("w", encoding="utf-8") as f:
        for x in negativos:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    # Buracos de cobertura: violações plausíveis que o verificador NÃO pega.
    # É o arquivo mais honesto do corpus — mede o alcance real da ferramenta em
    # vez de assumir que a regra cobre tudo que a descrição dela promete.
    nao_pegos = [x for x in rejeitados if x.get("tipo") == "nao_pego"]
    with (saida / "nao-pegos.jsonl").open("w", encoding="utf-8") as f:
        for i, x in enumerate(nao_pegos, 1):
            f.write(json.dumps({
                "id": f"gap-{i:03d}",
                "regra_esperada": x["regra"],
                "texto": x["texto"],
                "porque_deveria_pegar": x["porque"],
                "gate_disparou": [],
            }, ensure_ascii=False) + "\n")

    por_regra: dict[str, int] = {}
    for a in aceitos:
        por_regra[a["regra"]] = por_regra.get(a["regra"], 0) + 1

    linhas = [
        "# Relatório de verificação do corpus",
        "",
        "Gerado por `corpus/montar.py`. Todo exemplo abaixo passou pelo `checar-copy`",
        "de verdade: o trecho reprovado dispara a própria regra, e a versão corrigida",
        "sai limpa de todas as sete.",
        "",
        f"- Exemplos gerados: **{n}**",
        f"- Aceitos no corpus: **{len(aceitos)}**",
        f"- Descartados na verificação: **{len(rejeitados)}**",
        f"- Casos negativos: **{len(negativos)}**",
        f"- Buracos de cobertura registrados: **{len([x for x in rejeitados if x.get('tipo') == 'nao_pego'])}**",
        "",
        "## Por regra",
        "",
        "| Regra | Nível | Exemplos |",
        "|---|---|---|",
    ]
    for r, q in sorted(por_regra.items()):
        nivel = "aviso" if r in ("generico", "urgencia") else "reprova"
        linhas.append(f"| `{r}` | {nivel} | {q} |")

    gaps = [x for x in rejeitados if x.get("tipo") == "nao_pego"]
    sujos = [x for x in rejeitados if x.get("tipo") == "corrigido_sujo"]

    if gaps:
        por_regra_gap: dict[str, int] = {}
        for x in gaps:
            por_regra_gap[x["regra"]] = por_regra_gap.get(x["regra"], 0) + 1
        linhas += ["", "## Cobertura real por regra", "",
                   "Violações plausíveis que o verificador NÃO pegou. As regras são",
                   "expressões regulares com termos literais: elas acertam o que está na",
                   "lista e passam por cima de variação óbvia. Estão em `nao-pegos.jsonl`.",
                   "",
                   "| Regra | Pegou | Não pegou | Cobertura |",
                   "|---|---|---|---|"]
        for r in sorted(set(list(por_regra) + list(por_regra_gap))):
            ok = por_regra.get(r, 0)
            gap = por_regra_gap.get(r, 0)
            pct = round(100 * ok / (ok + gap)) if (ok + gap) else 0
            linhas.append(f"| `{r}` | {ok} | {gap} | {pct}% |")
        linhas += ["", "Exemplos que escaparam:", ""]
        for x in gaps[:12]:
            linhas.append(f"- `{x['regra']}` > {x['texto'][:100]}")

    if sujos:
        linhas += ["", "## Reescritas que ainda sujavam", "",
                   "A versão corrigida disparava outra regra. Ficam de fora porque um",
                   "exemplo de conserto não pode carregar defeito novo.", ""]
        for x in sujos:
            linhas.append(f"- `{x['regra']}` — {x['motivo']}")

    (saida / "RELATORIO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")

    print(f"  gerados: {n} · aceitos: {len(aceitos)} · descartados: {len(rejeitados)} · negativos: {len(negativos)}")
    for r, q in sorted(por_regra.items()):
        print(f"    {r:10s} {q}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
