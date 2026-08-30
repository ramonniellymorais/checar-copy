# Corpus de tiques de escrita de IA em português brasileiro

Banco de exemplos de copy de marketing que **soa genérico** — cada um marcado com
a regra que o reprova, o motivo, e a mesma ideia reescrita.

Licença **CC BY 4.0**. Use, adapte, publique. Só cite a fonte.

---

## O que isto é

Uma rubrica com exemplos. Cada linha traz um trecho reprovado, a regra nomeada
que o pegou, uma frase dizendo o que está errado ali, e a versão corrigida.

Serve para três coisas:

- **treinar o olho** de quem revisa copy em português
- **testar verificador** próprio — um conjunto pronto de casos com veredito conhecido
- **avaliar saída de LLM** (*eval set*) quando você pede copy em pt-BR e quer medir
  quanto dela cai nos vícios de sempre

## O que isto **não** é

**Não é detector de IA.** Ele não responde "isso foi escrito por máquina?". Responde
outra pergunta: "isso soa genérico, por qual regra, e como conserta?".

A diferença importa. Texto escrito por humano apressado cai nas mesmas armadilhas;
texto de LLM bem conduzido escapa delas. O objeto aqui é o **vício de escrita**, não
a autoria.

**Não é regra de gramática.** Várias entradas são decisões de estilo de uma casa
específica — estão declaradas como tal e você deve discordar de algumas.

---

## Estrutura

`tiques-pt-br.jsonl` — um exemplo por linha:

```json
{
  "id": "binaria-001",
  "regra": "binaria",
  "nivel": "reprova",
  "formato": "carrossel",
  "texto": "Pitch não é talento. É estrutura.",
  "porque": "duas frases opostas em paralelo; cadência de slide, não de fala",
  "certo": "Pitch não é talento bonito — é a frase que o cliente repete em casa.",
  "verificado": true
}
```

| Campo | O que é |
|---|---|
| `regra` | id da regra: `binaria`, `pra`, `emoji`, `preco`, `anedota`, `generico`, `urgencia` |
| `nivel` | `reprova` ou `aviso` |
| `formato` | onde a peça apareceria: legenda, carrossel, reels, story, email, anúncio |
| `texto` | o trecho reprovado |
| `porque` | o que está errado naquele exemplo específico |
| `certo` | a mesma ideia, reescrita e limpa |
| `verificado` | passou pela verificação mecânica descrita abaixo |

## O que tem dentro

| Arquivo | Linhas | O que é |
|---|---|---|
| `tiques-pt-br.jsonl` | **90** | exemplos reprovados, verificados, com a reescrita |
| `negativos.jsonl` | **14** | contêm o padrão e devem passar |
| `nao-pegos.jsonl` | **29** | violações plausíveis que o verificador **não** pega |

De 121 exemplos gerados, 90 sobreviveram à verificação. Os 31 que caíram estão
registrados — 29 viraram buracos de cobertura documentados, 2 eram reescritas que
ainda sujavam.

`negativos.jsonl` — os casos que **contêm o padrão e mesmo assim devem passar**:

```json
{
  "id": "neg-001",
  "situacao": "fala citada",
  "texto": "Ela me olhou e disse: \"só você pra dizer isso\".",
  "regra_que_dispara": "pra",
  "gate_disparou": ["pra"],
  "por_que_passa": "é fala transcrita de outra pessoa, não a copy",
  "veredito_humano": "passa"
}
```

Esta é a parte que costuma faltar em corpus desse tipo. Um verificador por expressão
regular não enxerga contexto: ele não sabe distinguir fala citada, discussão sobre a
própria regra, ou número de resultado de cliente. Sem os negativos declarados, quem
roda o gate numa entrevista transcrita vê tudo reprovar e conclui que a ferramenta
está quebrada.

O campo `gate_disparou` registra **o que a ferramenta acusou de verdade** nesse caso.
É o limite honesto dela, medido, não prometido.

---

## Como foi construído

1. As sete regras vêm de `../REGRAS.md`, que traz o raciocínio de cada uma.
2. Os exemplos foram gerados a partir desse raciocínio, variando tema e formato.
3. **Cada exemplo passou pelo `checar-copy` de verdade** antes de entrar:
   - o trecho reprovado tem que disparar a própria regra
   - a versão corrigida tem que sair limpa das sete
   - o que não bateu ficou de fora, com o motivo registrado em `RELATORIO.md`

O passo 3 é o que separa isto de uma lista de opiniões. O script está no repositório;
qualquer pessoa refaz a verificação com `python3 corpus/montar.py`.

Os números da rodada — quantos foram gerados, quantos passaram, quantos caíram e por
quê — estão em [`RELATORIO.md`](RELATORIO.md).

## Regressão

O corpus é também a suíte de testes do verificador:

```bash
./testes/rodar.sh
```

Cada exemplo reprovado tem que continuar reprovando pela regra dele; cada versão
corrigida tem que continuar passando. As regras são expressões regulares — mexer numa
para pegar um caso novo quebra outro em silêncio, e é isso que o teste impede.

---

## A cobertura real do verificador

Isto é o que a verificação mecânica revelou, e é a parte mais útil do corpus:

| Regra | Pegou | Não pegou | Cobertura |
|---|---|---|---|
| `emoji` | 18 | 0 | **100%** |
| `pra` | 18 | 0 | **100%** |
| `preco` | 18 | 0 | **100%** |
| `generico` | 12 | 3 | 80% |
| `binaria` | 12 | 5 | 71% |
| `anedota` | 8 | 8 | 50% |
| `urgencia` | 4 | 13 | **24%** |

As regras são expressões regulares com termos literais. Elas acertam o que está na
lista e passam por cima de variação óbvia: `urgencia` procura "últimas vagas" e não
enxerga "últimas horas"; procura "corre que está acabando" e não enxerga "corre que
as vagas estão acabando".

Isso não é defeito escondido — é o alcance da ferramenta, medido. Os 29 casos que
escaparam estão em `nao-pegos.jsonl` para quem quiser fechar os buracos, seja
ampliando os padrões, seja usando um julgador de modelo por cima.

O contraste entre `emoji` a 100% e `urgencia` a 24% diz uma coisa só: padrão que é
uma **classe de caractere** se resolve com regex; padrão que é uma **ideia** não.

## Limites, sem rodeio

- **A cobertura varia muito por regra** — de 100% a 24%, medido acima. Trate o
  verificador como filtro grosso, não como garantia.
- **Sete regras cobrem a superfície.** O que decide se a peça vale alguma coisa
  continua sem script: tem ponto de vista? a história é sua? alguém mandaria para uma
  amiga? dá para saber quem escreveu? Essas quatro são o trabalho de verdade.
- **Duas regras são de casa, não de idioma.** "para" por extenso e ausência de emoji
  são decisões de estilo. Se a sua marca decidiu diferente, apague a regra — o que
  não pode é ser acidente.
- **Os exemplos são sintéticos.** Nenhum vem de material de cliente. São construídos
  para demonstrar o padrão, e são plausíveis por desenho, não por coleta.
- **Português do Brasil.** Nada disso foi testado em pt-PT.

---

## Quem fez

[Ramonnielly Morais](https://ramonniellymorais.com.br) — estrategista de conteúdo,
criadora do Método ELO Criativo.

As regras nasceram de revisar copy própria e de cliente até virar padrão repetido, e
de perceber que decisão de estilo que não vira regra escrita se perde toda vez que o
prazo aperta.

## Como citar

```
Corpus de tiques de escrita de IA em português brasileiro,
por Ramonnielly Silva Morais — CC BY 4.0
https://github.com/ramonniellymorais/checar-copy
```

---

<details>
<summary><b>English summary</b></summary>

### Brazilian Portuguese AI-writing-tics corpus

A labelled corpus of marketing copy that **reads as generic**, built as a rubric with
paired rewrites. Each entry: the rejected snippet, the named rule that caught it, why,
and the same idea rewritten.

Useful as an **eval set** for pt-BR copy generation, as **guardrail** test fixtures, or
as reference material for an **LLM-as-a-judge** rubric.

**This is not an AI detector.** It does not answer "was this machine-written?". It
answers "does this read as generic, by which named rule, and how do you fix it?" —
a different and more actionable question.

Seven rules, split into `reprova` (hard fail) and `aviso` (warning). Every example was
verified against the actual checker before inclusion: rejected snippets must trip their
own rule, rewrites must come out clean. `negativos.jsonl` holds the **true negatives** —
text that contains the pattern and should still pass (quoted speech, meta-discussion
about the rule itself, client result figures, deliberate irony). That file documents the
regex checker's honest limits, measured rather than claimed.

Corpus licensed **CC BY 4.0**; the checker itself is MIT.

</details>
