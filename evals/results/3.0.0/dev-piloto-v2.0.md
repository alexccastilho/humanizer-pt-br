# Resultado do benchmark (dev)

## Checagens determinísticas por braço

| Braço | Execuções | Acionou skill | Com alguma falha | Protegidos | Nº sumiu | Nº novo | Travessão | Preâmbulo | Falta fonte ausente | Tamanho (IA, mediana) | Similaridade texto bom | Tokens entrada (med.) | Tokens saída (med.) | Custo médio US$ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 41 | 0 | 24/41 | 6 | 1 | 6 | 2 | 13 | 1 | 1.171 | 0.541 | 7338 | 465 | 0.02793 |
| minimal | 41 | 0 | 5/41 | 2 | 1 | 1 | 0 | 0 | 1 | 0.849 | 0.776 | 7455 | 279 | 0.02699 |
| novocab | 41 | 40 | 2/41 | 0 | 0 | 1 | 0 | 1 | 0 | 0.718 | 0.905 | 18858 | 439 | 0.04417 |
| skill | 41 | 40 | 2/41 | 0 | 0 | 1 | 0 | 1 | 0 | 0.704 | 0.887 | 19442 | 454 | 0.04587 |

## Preferência do juiz cego

| Par | n | Vitórias 1º | Vitórias 2º | Empates | Taxa 1º (sem empates) | IC 95% | Venceu posição A/B |
|---|---|---|---|---|---|---|---|
| skill x baseline | 41 | 38 | 3 | 0 | 93% | 81% a 98% | 19/22 |
| skill x minimal | 41 | 27 | 14 | 0 | 66% | 50% a 78% | 21/20 |
| skill x novocab | 41 | 11 | 28 | 2 | 28% | 16% a 44% | 22/17 |

## Fidelidade e naturalidade (juiz)

| Braço | Erros de fidelidade por saída | Saídas com erro | Naturalidade média (1-10) |
|---|---|---|---|
| baseline | 1.951 | 76% | 6.93 |
| minimal | 0.756 | 44% | 6.76 |
| novocab | 0.585 | 42% | 7.49 |
| skill | 0.715 | 45% | 7.35 |

## Critérios de decisão

- PASSOU: G1 trechos protegidos intactos (skill)
- PASSOU: G2 números: skill não pior que baseline
- PASSOU: G3 fidelidade (juiz): skill não pior que baseline
- PASSOU: G4 preferência skill x baseline >= 60% e IC acima de 50%
- PASSOU: G5 skill não perde do prompt mínimo (IC superior >= 50%)
- FALHOU: T economia de tokens real (custo médio skill <= baseline)
