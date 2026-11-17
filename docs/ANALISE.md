# Análise da skill humanizer-token-optimizer-pt-br

Original analisado: `SKILL.md` de 9.472 bytes, 144 linhas (L = linha do original).
Versão nova: `skills/humanizer-token-optimizer-pt-br/SKILL.md`, 9.531 bytes, 120 linhas (9.457 bytes antes de receber `license` e `metadata` no frontmatter). Os dois arquivos usam quebra de linha LF, então os tamanhos são comparáveis.
A descrição (sempre carregada no contexto) caiu de 778 para 768 caracteres; o limite é 1.024.

As regras de formato foram conferidas na skill `skill-creator` e no validador dela (`quick_validate.py`): descrição de até 1.024 caracteres e sem `<` ou `>`, um único `SKILL.md`, e seis chaves permitidas no frontmatter (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`). A skill usa `name`, `description`, `license` (MIT) e `metadata` (autor e versão).

## Resumo

O original tem boa cobertura e bons exemplos, mas trata como proibição absoluta o que precisa de julgamento. O resultado são regras que se contradizem e uma checagem final (L125-131) que manda reescrever textos corretos. A correção central foi estrutural: uma linha de prioridade entre regras, uma lista única de trechos protegidos e a troca de "lista proibida" por "lista de suspeitos". O espaço para isso veio de cortes em redundância, então o arquivo não cresceu.

## Problemas por severidade

### Crítica

**C1. "Nunca inventar fatos" contra "troque por exemplo concreto ou número" (L25 x L97). Suspeita confirmada.**
Sem dado no original, a única forma de cumprir L97 é fabricar o exemplo ou o número. É o pior erro que um humanizador pode cometer, porque o usuário publica o texto.
Correção: §1 proíbe inventar fonte, exemplo ou número. A atribuição vaga fica como está (tirá-la transformaria um relato em afirmação do autor) e, se a afirmação depender dela, a saída ganha uma linha `Falta fonte: <trecho>`.

**C2. Exemplos da própria skill violam a fidelidade (L90 e L81).**
L90 transforma "é uma revolução" em "resolve o problema X", um fato que não existia. L81 transforma "um marco fundamental para o setor" em "Mudou o setor", afirmação mais forte que a original. Exemplo pesa mais que regra, então o modelo aprende a inventar.
Correção: os pares foram trocados por outros que só removem enchimento ("foi importante para o setor"; "O app de notas organiza suas ideias."). A regra de inflação agora diz "mesma força".

**C3. Hard fail proíbe toda palavra da lista de vocabulário (L127). Suspeita confirmada.**
A lista inclui "portanto", "no entanto", "por outro lado", "por fim", "otimizar", "essencial", "cenário", "ecossistema", "pilar", "estratégico". Proibir todas quebra texto técnico ("otimizar a query"), científico ("ecossistema") e jurídico, e contradiz a tag `[FORMAL]`, que manda preservar termos técnicos (L138). Sem conectivos, o texto fica picotado, o que a própria L101 condena.
Correção: §4 declara a lista como suspeitos. Troca-se a palavra quando ela infla ou enfeita e existe outra mais simples; mantém-se quando o uso é literal ou técnico. Os conectivos comuns saíram da lista e viraram regra de frequência: só se corrige quando abrem frase após frase ou não ligam nada.

**C4. Proibição de traço "sem exceções" (L35-38 e L126). Suspeita confirmada.**
A regra pega intervalos e datas (10-20, 2020-2024), citações literais, código, URLs, nomes próprios, palavras compostas, marcadores de lista e rótulos do tipo "Nome - Cargo". O hard fail L126 também ignora a tag `[TRAVESSAO: OK]` definida em L57.
Correção: a regra de §3 vale para o traço usado como aparte, pausa ou ênfase em prosa. Há uma lista do que se mantém, e a checagem final cita a tag.

**C5. Não existe lista do que não pode ser tocado.**
Citações diretas, código, links, menções, hashtags, placeholders, marcas e números ficam expostos a todas as regras de reescrita. Um caso concreto: L62 manda tirar "&", o que quebra "P&D" e "Johnson & Johnson".
Correção: §1 traz uma lista única de trechos protegidos, copiados sem alteração e isentos de todas as regras seguintes.

### Alta

**A1. "Nunca perder informação" contra "regra de três: escolha a que importa" (L25 x L75). Suspeita confirmada.**
Se os três itens são reais (três produtos, três etapas), escolher um apaga conteúdo.
Correção: a regra vale só para a tríade decorativa. "Three real items stay three."

**A2. "Saída ≤ original" como regra dura (L26 e L130). Suspeita confirmada.**
Conflita com expansão pedida pelo usuário, com `[OPINION]` (que acrescenta texto), com `[DEBUG]` (que acrescenta a lista), com texto já enxuto e com L83, que pede um parágrafo "com cinco frases".
Correção: virou meta com exceções explícitas em §2 e saiu da checagem final. A variação de ritmo se faz juntando ou dividindo o que existe, nunca acrescentando.

**A3. Não há prioridade entre regras.**
Só a estrutura tinha precedência (L105). Nos demais conflitos o modelo decide sozinho.
Correção: uma linha no topo: instrução do usuário e tags, depois fidelidade e trechos protegidos, pontuação, marcas de IA, tamanho e voz.

**A4. Gatilho amplo demais na descrição (L5-13).**
"Reescrever", "melhorar redação" e "revisar tom" sem qualificador disparam em código, tradução e revisão gramatical. A cláusula "sempre que um texto parecer artificial" dispara sem pedido do usuário. Há ainda vizinhança com a skill `remove-ai-marks` (marca d'água e metadados), que usa termos parecidos.
Correção: a descrição mantém as queixas coloquiais ("parece ChatGPT" etc.), restringe "reescrever" e "melhorar a redação" a prosa em pt-BR, remove o gatilho sem pedido e ganha uma frase "Não use para". Saíram "revisar tom" e "adaptar para redes sociais" como gatilhos soltos; os canais continuam citados pelo nome.

**A5. "Ponto final em cerca de 70% dos casos" (L41) contra "não picote frases" (L101).**
O número não tem base e empurra para a sequência de frases curtas, que é outra marca de IA.
Correção: a escada de preferência virou escolha pelo sentido da frase, com aviso explícito contra o ponto final como padrão.

**A6. Fórmula de contraste proibida sem exceção (L74 e L128).**
"Não é X, é Y" é legítimo quando X é um equívoco real que o texto corrige. Apagar X perde informação.
Correção: mantém-se nesse caso.

### Média

**M1. Fluxo de trabalho incompleto.** Não havia orientação para texto longo, texto em outro idioma, pt-PT na entrada, pedido só de diagnóstico, texto que já está bom, edição de arquivo no Claude Code, combinação e conflito de tags, nem formato do `[DEBUG]`.
Correção: §1 (outro idioma e pt-PT), §2 e §7 cobrem cada caso em uma linha.

**M2. "Mencione as tags ao final" (L28) contra "zero filler" e "só o texto final" (L23-24).**
Correção: a linha saiu. Pedido em linguagem comum agora vale como tag, o que dispensa anunciá-las.

**M3. "Confira se a abertura prende" (L133) e "gancho na 1ª linha" (L117) convidam a inventar gancho.**
Correção: "Do not invent a hook". A coluna de tom do Instagram perdeu a exigência de gancho.

**M4. Pergunta de contexto com critério vago (L27).**
Correção: o padrão é inferir canal e registro pelo próprio texto. Pergunta-se só quando o canal é desconhecido e muda o resultado.

**M5. Marcas de IA em pt-BR que faltavam.**
Acrescentadas, com custo baixo: aberturas "Neste artigo, vamos", "Imagine", "Seja X ou Y", "Quando o assunto é"; fechamentos "Em suma", "Confira", "Bora?", "Comente aqui" (CTA específico é conteúdo e fica); resíduo de chatbot ("Claro!", "Espero ter ajudado"); "é fundamental que", "quando se trata de"; intensificadores (realmente, verdadeiramente, extremamente); "navegar (desafios)", "universo", "poderoso"; lista com "**Título:** texto" em todo item; emoji como marcador ou título; passiva com nominalização; "Mais do que X, é Y".

**M6. `[OPINION]` podia gerar experiência pessoal inventada.**
Correção: a tag passa a acrescentar reação ou avaliação sobre fatos já presentes.

**M7. `[TRAVESSAO: OK]` falava em "restaurar" pontuação editorial (L57).**
Correção: mantém os travessões do original e não acrescenta novos. Dúvida em aberto: se a intenção era permitir que a skill também crie travessões editoriais, a linha da tag precisa voltar a dizer isso.

**M8. Opinião por padrão em blog e LinkedIn (L96) e "varie o ritmo" como instrução solta (L95).**
Acrescentar opinião que não está no original é acrescentar conteúdo, o que a fidelidade proíbe. A instrução de ritmo solta incentivava frases picotadas.
Correção: opinião e primeira pessoa só quando o original já tem ou com `[OPINION]`. O ritmo ficou na regra de "ritmo uniforme" de §4, limitada a juntar ou dividir o que existe. É mudança de comportamento: quem contava com opinião automática no LinkedIn precisa usar a tag.

### Baixa

**B1.** Erro de digitação "pontuation" (L57). Suspeita confirmada. A frase foi reescrita.
**B2.** Aspas curvas sem regra para canal desconhecido (L60-61). Agora ficam como o usuário digitou. A justificativa do teclado ABNT2 foi cortada.
**B3.** Cortes para pagar as adições: cabeçalho "Role" e "Goal", meta-linha L22, a checagem final repetindo as seções 2 e 3, dois pares de exemplo que mostravam o mesmo caso e a coluna "Informal" da tabela de canais. Essa coluna duplicava o tom em quatro canais; perderam-se as nuances "Moderado" (LinkedIn) e "Leve" (blog).
**B4.** "Um ponto de exclamação por bloco" e "!!" ficaram, mas agora também cedem aos trechos protegidos (citação literal).

## Não alterado, e por quê

- **`name` e formato do frontmatter.** `description` em bloco dobrado, que já carrega no claude.ai e no Claude Code. Autor, versão e licença foram acrescentados em `license` e `metadata`, chaves aceitas pelo validador.
- **Arquivo único, sem `references/`.** Com 116 linhas, quase tudo é usado em toda execução. Um arquivo de referência custaria uma leitura extra por uso e economizaria pouco. O limite sugerido pela `skill-creator` é de 500 linhas.
- **Convenção de idioma.** Lógica em inglês, exemplos e mensagens ao usuário em pt-BR.
- **As sete tags, com os mesmos nomes.** Quem já usa a skill não precisa reaprender.
- **Regra do traço como a mais forte de forma.** Continua logo abaixo da fidelidade. É a marca visual mais confiável e o usuário a cita no gatilho ("tirar travessão").
- **Listas de vocabulário quase inteiras.** O conteúdo é bom. Mudou o estatuto (suspeito, não proibido) e saíram poucos itens: os conectivos comuns e "reino", "escalável", "explorar" isolado, "com toda certeza", "primeiramente". "Paisagem" deu lugar a "panorama", mais frequente em texto de IA em pt-BR.
- **Tabela de canais.** Mantida com os seis canais, em três colunas.
- **Aviso contra supercorreção e contra prometer "indetectável".** Mantidos, pois evitam os dois abusos mais prováveis.
- **Saudação de e-mail ("Espero que esteja bem").** Não entrou como marca de IA: é convenção humana corrente em e-mail corporativo no Brasil e geraria falso positivo.
- **Avaliações automatizadas (evals).** Não foram criadas, porque a tarefa pede só os dois arquivos.

## Teste comparativo

Três casos rodados às cegas: cada versão foi aplicada por um agente que não sabia qual era.

| Caso | v1.0.0 | v2.0.0 |
|---|---|---|
| Post de LinkedIn com travessões, "não é X, é Y" e "especialistas afirmam" | Limpou bem; manteve a atribuição vaga sem aviso | Limpou bem; manteve a atribuição e acrescentou `Falta fonte:` |
| Texto técnico com "otimizar a query", intervalo 10-20, citação literal e código | Alterou a citação literal, trocou "otimizar" por "acelerar" e "10-20" por "10 a 20" | Citação, intervalo, código e termo técnico intactos; cortou só o enchimento |
| E-mail já bem escrito | Devolveu o texto igual | Respondeu em uma linha que não havia o que mudar |

A v2.0.0 passou nos três casos. O teste é pequeno e serve como verificação de regressão, não como avaliação estatística.
