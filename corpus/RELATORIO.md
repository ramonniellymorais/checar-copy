# Relatório de verificação do corpus

Gerado por `corpus/montar.py`. Todo exemplo abaixo passou pelo `checar-copy`
de verdade: o trecho reprovado dispara a própria regra, e a versão corrigida
sai limpa de todas as sete.

- Exemplos gerados: **121**
- Aceitos no corpus: **90**
- Descartados na verificação: **31**
- Casos negativos: **14**
- Buracos de cobertura registrados: **29**

## Por regra

| Regra | Nível | Exemplos |
|---|---|---|
| `anedota` | reprova | 8 |
| `binaria` | reprova | 12 |
| `emoji` | reprova | 18 |
| `generico` | aviso | 12 |
| `pra` | reprova | 18 |
| `preco` | reprova | 18 |
| `urgencia` | aviso | 4 |

## Cobertura real por regra

Violações plausíveis que o verificador NÃO pegou. As regras são
expressões regulares com termos literais: elas acertam o que está na
lista e passam por cima de variação óbvia. Estão em `nao-pegos.jsonl`.

| Regra | Pegou | Não pegou | Cobertura |
|---|---|---|---|
| `anedota` | 8 | 8 | 50% |
| `binaria` | 12 | 5 | 71% |
| `emoji` | 18 | 0 | 100% |
| `generico` | 12 | 3 | 80% |
| `pra` | 18 | 0 | 100% |
| `preco` | 18 | 0 | 100% |
| `urgencia` | 4 | 13 | 24% |

Exemplos que escaparam:

- `binaria` > O algoritmo não recompensa volume. É retenção.
- `binaria` > Você não está cansada de criar. É de criar sem direção.
- `binaria` > Feed não vende. É a conversa que vende.
- `binaria` > Você não tem problema de conteúdo. É de oferta.
- `binaria` > Você não precisa de mil pessoas. É de trinta que não te largam.
- `anedota` > Semana passada me procurou uma mentora faturando quarenta mil por mês que cobrava mil e duzentos num
- `anedota` > Outro dia uma seguidora me mandou uma DM chorando: doze mil seguidores, oito meses sem vender nada.
- `anedota` > Uma mentorada minha sumiu quatro meses do Instagram. Quando voltou, o alcance tinha caído setenta po
- `anedota` > Semana passada uma dermatologista me disse na call: eu não tenho história. Duas horas depois ela sai
- `anedota` > Ontem uma aluna me mandou a bio dela para eu olhar. Três emojis, uma frase de efeito e nenhuma pista
- `anedota` > Veio uma coach aqui semana retrasada com sessenta DMs não respondidas. Sabe quantas viraram venda? N
- `anedota` > Uma mentorada me mandou áudio dizendo que depois do ELO ela parou de ter vergonha de aparecer. Chore

## Reescritas que ainda sujavam

A versão corrigida disparava outra regra. Ficam de fora porque um
exemplo de conserto não pode carregar defeito novo.

- `generico` — a versão corrigida ainda dispara ['preco']
- `generico` — a versão corrigida ainda dispara ['generico']
