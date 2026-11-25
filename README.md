# Humanizer pt-BR

Skill para Claude que tira o jeito de IA de textos em Português do Brasil. Ela remove travessões usados como aparte, clichês ("vale ressaltar", "alavancar", "um verdadeiro marco"), fórmulas como "não é X, é Y" e enchimento em geral, e reescreve com voz natural sem mudar o conteúdo. Funciona no **Claude Code** e no **claude.ai**.

Criada e mantida por **Alex Camacho Castilho**.

> Até a v2.0.0 este projeto se chamava `humanizer-token-optimizer-pt-br`. O nome mudou na v3.0.0 porque o benchmark mostrou que a skill não economiza tokens: ela custa cerca de 60% a mais por pedido do que o Claude sem skill. O ganho é de qualidade e de fidelidade, não de custo. Veja [como atualizar](#atualizando-da-v2).

## O que ela faz

- **Preserva o conteúdo.** Não inventa fato, número, fonte nem exemplo, e não muda a força das afirmações. Quando o texto se apoia em "especialistas afirmam" sem fonte, ela avisa em vez de inventar uma.
- **Protege o que não deve ser tocado.** Citações diretas, código, URLs, e-mails, @menções, #hashtags, nomes e marcas (P&D, Johnson & Johnson), números, datas, intervalos (10-20) e termos técnicos ou jurídicos são copiados sem alteração.
- **Corta marcas de IA com critério.** Remove fórmulas, aberturas e fechamentos prontos e enchimento, mas mantém o que é afirmação do original e o uso técnico das palavras ("otimizar a query" continua onde está).
- **Entrega só o texto.** Sem preâmbulo, sem "se quiser, posso ajustar" e sem lista de mudanças. O texto final costuma sair mais curto que o original.
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
/plugin marketplace add alexccastilho/humanizer-pt-br
/plugin install humanizer-pt-br@alexccastilho-humanizer
```

Ou pelo terminal:

```bash
claude plugin marketplace add alexccastilho/humanizer-pt-br
claude plugin install humanizer-pt-br@alexccastilho-humanizer
```

Para atualizar depois: `claude plugin marketplace update alexccastilho-humanizer`.

### Claude Code (manual)

Copie a pasta `skills/humanizer-pt-br` para `~/.claude/skills/` (vale para todos os projetos) ou para `.claude/skills/` dentro de um projeto. A skill é carregada na próxima sessão.

```bash
git clone https://github.com/alexccastilho/humanizer-pt-br.git
cp -r humanizer-pt-br/skills/humanizer-pt-br ~/.claude/skills/
```

### claude.ai

1. Baixe `humanizer-pt-br.zip` na [última release](https://github.com/alexccastilho/humanizer-pt-br/releases/latest).
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
| `[TRAVESSAO: OK]` | Mantém os travessões que já estavam no original, sem criar nenhum novo |

As tags podem ser combinadas. Um pedido em linguagem comum vale como a tag correspondente ("deixa mais informal" equivale a `[CASUAL]`).

## Resultado medido

Benchmark da v3.0.0 no conjunto de reserva: 68 casos (textos gerados por Claude Haiku, Sonnet e Opus, mais casos difíceis feitos à mão), 2 rodadas, Claude Sonnet como modelo testado e Claude Opus como juiz cego. Detalhes em [`evals/`](evals/README.md) e números completos em [`evals/results/3.0.0/holdout.md`](evals/results/3.0.0/holdout.md).

| | Sem skill | Prompt de 2 linhas | Skill v3.0.0 |
|---|---|---|---|
| Vezes em que o juiz preferiu a alternativa à skill | 9% | 38% | - |
| Respostas com comentário antes ou depois do texto | 38 de 134 | 0 | 0 |
| Trechos protegidos alterados (citação, código, URL, marca) | 6 | 2 | 0 |
| Erros de fidelidade por resposta (juiz) | 2,19 | 1,00 | 0,78 |
| Tamanho da saída em relação ao original (mediana) | 116% | 86% | 74% |
| Custo médio por pedido (US$) | 0,028 | 0,027 | 0,046 |

A skill foi acionada sozinha em 130 de 136 pedidos. Ela custa mais porque o Claude precisa carregá-la antes de responder.

## Atualizando da v2

O nome do plugin, da skill e do marketplace mudou. No Claude Code:

```
/plugin uninstall humanizer-token-optimizer-pt-br@alexccastilho-skills
/plugin marketplace add alexccastilho/humanizer-pt-br
/plugin install humanizer-pt-br@alexccastilho-humanizer
```

O marketplace antigo, `alexccastilho-skills`, pode estar sendo usado por outro plugin do mesmo autor; só remova se não estiver. No claude.ai, apague a skill antiga em Customize > Skills e envie o ZIP novo.

## Limites

A skill reduz marcas de escrita de IA. Ela não garante nota em nenhum detector e não promete texto "indetectável". Também não serve para código, tradução, correção só gramatical nem remoção de marcas d'água ou metadados.

## Estrutura do repositório

```
.claude-plugin/
  marketplace.json      catálogo para /plugin marketplace add
  plugin.json           manifesto do plugin
skills/
  humanizer-pt-br/
    SKILL.md            a skill
docs/
  ANALISE.md            análise que originou a v2.0.0
evals/                  benchmark, checador determinístico e resultados por versão
tests/                  testes rodados no CI
scripts/
  build_zip.py          gera o ZIP para o claude.ai
```

## Versões

Veja o [CHANGELOG](CHANGELOG.md).

## Autor

**Alex Camacho Castilho** ([@alexccastilho](https://github.com/alexccastilho))

## Licença

[MIT](LICENSE) © 2026 Alex Camacho Castilho
