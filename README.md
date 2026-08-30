# checar-copy

Um verificador que reprova as construções que denunciam copy de fórmula — antes de a peça ir ao ar.

```bash
checar-copy peca.md
```

```
[REPROVA] linha 1 — Construcao binaria "X nao e A. E B."
          Pitch não é talento. É estrutura.
          Por que: Paralelismo curto em duas frases opostas e cara de copywriter,
                   nao de gente falando. Desenrole a virada dentro de uma frase so.
          Saida:   "Pitch nao e talento bonito — e a frase que o cliente repete
                   em casa, na hora do jantar."
```

Sem instalação de nada, sem conta, sem mensalidade. É um arquivo só, e o Perl que ele usa já vem no seu Mac.

---

## Por que isto existe

Todo mercado desenvolve tiques. O de conteúdo digital tem os dele, e eles são fáceis de listar porque aparecem em todo lugar ao mesmo tempo.

O mais teimoso é a construção binária: *"X não é A. É B."* Duas frases curtas, opostas, uma atrás da outra. Ela parece afiada porque tem ritmo. O problema aparece quando você lê em voz alta e percebe que ninguém fala assim — é ritmo de slide, não de conversa. E quando cinquenta perfis do mesmo nicho escrevem no mesmo ritmo, o ritmo deixa de assinar qualquer um deles.

Eu cansei de pegar isso na revisão manual e transformei em script. Hoje toda peça passa por aqui antes de virar arte.

**O que ele não faz:** dizer se o texto é bom. Ele pega o que dá para pegar com regra. A voz, o ponto de vista e a história continuam sendo trabalho seu — e continuam sendo a única parte que ninguém consegue copiar.

---

## Instalar

```bash
git clone https://github.com/ramonniellymorais/checar-copy.git
cd checar-copy
chmod +x checar-copy
cp checar-copy ~/.local/bin/
```

Se `~/.local/bin` não estiver no seu caminho:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

Conferir:

```bash
checar-copy --lista
```

---

## Usar

```bash
# um arquivo
checar-copy carrossel.md

# vários de uma vez
checar-copy slides/*.txt legenda.txt

# direto do que você acabou de escrever
pbpaste | checar-copy

# ver todas as regras e por que cada uma existe
checar-copy --lista
```

Códigos de saída: `0` passou · `1` tem reprovação · `2` erro de uso. Serve para plugar em automação.

---

## As 7 regras

Cinco reprovam, duas avisam. Reprovação pede reescrita; aviso pede uma segunda leitura, porque às vezes é escolha consciente.

| | Regra | O que pega |
|---|---|---|
| REPROVA | **Construção binária** | *"X não é A. É B."* — a virada quebrada em duas frases opostas |
| REPROVA | **"pra" em vez de "para"** | a forma curta em copy publicada |
| REPROVA | **Emoji** | qualquer emoji no corpo do texto |
| REPROVA | **Preço em peça orgânica** | `R$` seguido de número, dentro de post ou legenda |
| REPROVA | **Anedota provavelmente inventada** | *"Conheci um mentor que..."*, *"Tive uma aluna que..."* |
| AVISO | **Palavra-marca de copy genérica** | descubra, segredo revelado, fórmula mágica, liberdade financeira |
| AVISO | **Urgência sem data** | *"corre que está acabando"*, *"últimas vagas"* |

O raciocínio completo de cada uma, com o antes e o depois, está em **[REGRAS.md](REGRAS.md)**.

---

## Como encaixar no seu fluxo

**Na revisão manual.** Escreveu, rodou, corrigiu o que ele apontou, e só então mandou para arte. Este é o uso mais simples e já resolve a maior parte.

**Como último passo do assistente.** Se você escreve com Claude, Cursor ou parecido, peça para ele rodar o script antes de te entregar a peça. Assistente de IA é justamente quem mais cai na construção binária, porque ela é o padrão mais frequente em texto de marketing na internet — e é disso que ele aprendeu.

Num arquivo `CLAUDE.md` na raiz do projeto:

```markdown
Antes de me entregar qualquer copy, rode `checar-copy` no texto
e corrija o que ele reprovar.
```

**Em automação.** O código de saída `1` deixa você travar a publicação de peça reprovada dentro de um script ou de um passo de CI.

---

## Ajustar às suas regras

As regras vivem numa lista no topo do arquivo, cada uma com nome, expressão, nível e a explicação que aparece no relatório. Editar é acrescentar ou tirar item dessa lista.

```perl
{
  id      => 'jargao_da_casa',
  nome    => 'Palavra que a marca nao usa',
  nivel   => 'reprova',
  regex   => qr/\b(?:curadoria|protagonismo)\b/iu,
  porque  => 'Sao palavras que essa marca decidiu nao usar.',
  exemplo => 'curadoria vira "composicao" ou "escolhas estrategicas".',
},
```

A lista de palavras que uma marca não usa é um dos ativos mais subestimados de identidade verbal. Vale mais do que a lista de palavras que ela usa, porque é ela que impede o texto de escorregar para o genérico quando o prazo aperta.

---

## O que fica de fora, de propósito

Este script pega padrão de superfície. Ele nunca vai saber:

- se a peça tem ponto de vista ou só informação que qualquer concorrente daria
- se a história contada é sua de verdade
- se a primeira frase poderia ser dita por outras cinco pessoas do seu nicho
- se alguém mandaria isso para uma amiga

Essas quatro perguntas são o trabalho. O script existe para você parar de gastar atenção com o que é mecânico e sobrar atenção para elas.

---

## O corpus

Junto com o verificador vai um **banco de exemplos** em [`corpus/`](corpus/): trechos
reprovados, a regra que pegou cada um, o motivo, e a mesma ideia reescrita.

```
corpus/tiques-pt-br.jsonl   os exemplos, um por linha
corpus/negativos.jsonl      o que contém o padrão e mesmo assim deve passar
corpus/RELATORIO.md         quantos foram gerados, quantos passaram, o que caiu
```

Serve para treinar o olho de quem revisa, para testar verificador próprio, e como
conjunto de avaliação quando você pede copy em português a um modelo e quer medir
quanto dela cai nos vícios de sempre.

**Todo exemplo foi verificado rodando este script.** O trecho reprovado tem que
disparar a própria regra; a versão corrigida tem que sair limpa das sete. O que não
bateu ficou de fora, com o motivo registrado. Refaça com `python3 corpus/montar.py`.

O `negativos.jsonl` é a parte que costuma faltar: fala citada, discussão sobre a
própria regra, número de resultado de cliente. Regex não vê contexto, e o arquivo
documenta esse limite medindo em vez de prometer.

O corpus é também a suíte de regressão — `./testes/rodar.sh` roda o verificador contra
ele inteiro, porque mexer numa expressão regular para pegar um caso novo quebra outro
em silêncio.

Corpus em **CC BY 4.0**; o verificador continua **MIT**.

---

## Continua

- **[stack-marketing-com-ia](https://github.com/ramonniellymorais/stack-marketing-com-ia)** — o que está instalado aqui e para que serve
- **[radar-de-plataformas](https://github.com/ramonniellymorais/radar-de-plataformas)** — o que as plataformas confirmaram oficialmente, com fonte e data
- **[transcrever](https://github.com/ramonniellymorais/transcrever)** — reunião virando roteiro com identificação de quem fala

Se você quiser o passo seguinte — o método completo trabalhando dentro do seu assistente, com a sua voz — ele vive em [ramonniellymorais.com.br](https://ramonniellymorais.com.br).

---

Feito por **[Ramonnielly Morais](https://ramonniellymorais.com.br)**, criadora do Método ELO Criativo.

Licença [MIT](LICENSE).
