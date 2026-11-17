# Humanizer Token Optimizer pt-BR

Skill para Claude que tira o jeito de IA de textos em Português do Brasil. Ela remove travessões usados como aparte, clichês ("vale ressaltar", "alavancar", "um verdadeiro marco"), fórmulas como "não é X, é Y" e enchimento em geral, e reescreve com voz natural sem mudar o conteúdo. Funciona no **Claude Code** e no **claude.ai**.

Criada e mantida por **Alex Camacho Castilho**.

## O que ela faz

- **Preserva o conteúdo.** Não inventa fato, número, fonte nem exemplo, e não muda a força das afirmações. Quando o texto se apoia em "especialistas afirmam" sem fonte, ela avisa em vez de inventar uma.
- **Protege o que não deve ser tocado.** Citações diretas, código, URLs, e-mails, @menções, #hashtags, nomes e marcas (P&D, Johnson & Johnson), números, datas, intervalos (10-20) e termos técnicos ou jurídicos são copiados sem alteração.
- **Corta marcas de IA com critério.** O vocabulário é tratado como lista de suspeitos, não como lista proibida: "otimizar a query" e "ecossistema" em biologia continuam onde estão.
- **Economiza tokens.** Entrega só o texto reescrito, sem preâmbulo nem lista de mudanças, e o texto final costuma sair mais curto que o original.
- **Ajusta ao canal.** LinkedIn, Instagram, X, e-mail corporativo, blog, WhatsApp e press release.

## Exemplo

| Antes | Depois |
|---|---|
| Não é só um app de notas — é um verdadeiro aliado que organiza suas ideias. | O app de notas organiza suas ideias. |
| O time — que já estava sobrecarregado — recusou. | O time, já sobrecarregado, recusou. |
| Vale ressaltar que os resultados foram positivos. | Os resultados foram positivos. |

## Instalação

### Claude Code (plugin)

Dentro de uma sessão do Claude Code:

```
/plugin marketplace add alexccastilho/humanizer-token-optimizer-pt-br
/plugin install humanizer-token-optimizer-pt-br@alexccastilho-skills
```

Ou pelo terminal:

```bash
claude plugin marketplace add alexccastilho/humanizer-token-optimizer-pt-br
claude plugin install humanizer-token-optimizer-pt-br@alexccastilho-skills
```

Para atualizar depois: `claude plugin marketplace update alexccastilho-skills`.

### Claude Code (manual)

Copie a pasta `skills/humanizer-token-optimizer-pt-br` para `~/.claude/skills/` (vale para todos os projetos) ou para `.claude/skills/` dentro de um projeto. A skill é carregada na próxima sessão.

```bash
git clone https://github.com/alexccastilho/humanizer-token-optimizer-pt-br.git
cp -r humanizer-token-optimizer-pt-br/skills/humanizer-token-optimizer-pt-br ~/.claude/skills/
```

### claude.ai

1. Baixe `humanizer-token-optimizer-pt-br.zip` na [última release](https://github.com/alexccastilho/humanizer-token-optimizer-pt-br/releases/latest).
2. Confira se a execução de código está ativada na sua conta (as skills dependem dela).
3. Em [Customize > Skills](https://claude.ai/customize/skills), envie o ZIP sem descompactar.

Se já houver uma versão anterior com o mesmo nome, substitua-a pela nova. As skills do claude.ai e do Claude Code não sincronizam entre si.

Para gerar o ZIP a partir do código: `python scripts/build_zip.py` (saída em `dist/`).

## Como usar

A skill é acionada sozinha quando você pede para humanizar um texto, tirar o jeito de IA, deixar mais natural ou adaptar para um canal. Também reconhece queixas como "parece ChatGPT", "tá muito formal" ou "não tá com a minha cara".

```
Humaniza esse post pro LinkedIn: <texto>
```

### Tags de controle

| Tag | Efeito |
|---|---|
| `[CASUAL]` | Tom amigável, frases curtas, leve informalidade |
| `[FORMAL]` | Profissional, sem opinião nem gíria |
| `[OPINION]` | Acrescenta reação ou avaliação sobre fatos já presentes, sem inventar experiência pessoal |
| `[CANAL: LinkedIn]` | Adapta ao canal indicado |
| `[DEBUG]` | Lista os padrões de IA encontrados antes do texto |
| `[ESTRUTURA]` | Mantém a estrutura original, sem converter listas em prosa |
| `[TRAVESSAO: OK]` | Mantém os travessões do original |

As tags podem ser combinadas. Um pedido em linguagem comum vale como a tag correspondente ("deixa mais informal" equivale a `[CASUAL]`).

## Limites

A skill reduz marcas de escrita de IA. Ela não garante nota em nenhum detector e não promete texto "indetectável". Também não serve para código, tradução, correção só gramatical nem remoção de marcas d'água ou metadados.

## Estrutura do repositório

```
.claude-plugin/
  marketplace.json      catálogo para /plugin marketplace add
  plugin.json           manifesto do plugin
skills/
  humanizer-token-optimizer-pt-br/
    SKILL.md            a skill
docs/
  ANALISE.md            análise que originou a v2.0.0
scripts/
  build_zip.py          gera o ZIP para o claude.ai
```

## Versões

Veja o [CHANGELOG](CHANGELOG.md).

## Autor

**Alex Camacho Castilho** ([@alexccastilho](https://github.com/alexccastilho))

## Licença

[MIT](LICENSE) © 2026 Alex Camacho Castilho
