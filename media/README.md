# Materiais visuais sintéticos

Todos os arquivos desta pasta foram criados especificamente para o portfólio. Eles não contêm imagens, nomes, respostas, relatórios nem metadados copiados do sistema original.

## Processamento efetivamente executado

| Arquivo | Conteúdo | Classificação |
|---|---|---|
| `synthetic-card-aligned.png` | Cartão fictício alinhado, com brancos, múltipla marcação e preenchimento fraco. | Entrada sintética gerada |
| `synthetic-card-tilted.png` | Mesmo cartão com rotação e fundo artificial. | Entrada sintética gerada |
| `synthetic-card-perspective.png` | Mesmo cartão com distorção projetiva. | Entrada sintética gerada |
| `synthetic-card-corrected.png` | Normalização para 1241 × 1754 pixels. | Saída real do núcleo isolado |
| `geometry-correction-before-after.png` | Comparação com as quatro marcas detectadas e o cartão normalizado. | Saída real apresentada |
| `mark-detection-overlay.png` | Bolhas classificadas como fortes, fracas, múltiplas ou vazias. | Saída real apresentada |
| `omr-correction-flow.png` | Sequência estática de entrada, detecção, homografia e classificação. | Saída real apresentada |
| `omr-demo.gif` | Sequência animada do mesmo processamento. | Saída real apresentada |
| `omr-demo-results.json` | Medições e resumo do cenário controlado. | Resultado real da execução |

“Saída real” significa que o algoritmo isolado processou a entrada sintética. Não significa execução da aplicação desktop completa, validação em cartões físicos ou benchmark de precisão.

## Ilustração conceitual

`omr-processing-flow.png` é um diagrama explicativo criado por `examples/create_conceptual_flow.py`. Ele não é uma saída do motor OMR.

## Resultado controlado

Na fixture de 20 questões, o classificador e o avaliador produziram:

- 13 respostas corretas;
- 3 incorretas;
- 3 em branco;
- 1 múltipla;
- 1 alerta de marca fraca, não contabilizado como resposta.

Esse resultado é determinístico para uma única imagem sintética e não deve ser apresentado como taxa de acerto. A proveniência e as diferenças do código isolado estão documentadas em [../docs/technical-overview.md](../docs/technical-overview.md).

## Material não produzido

`desktop-overview.png` permanece fora do escopo. Uma captura fiel exigiria executar ou reconstruir a interface, o que não é necessário para demonstrar o processamento OMR e poderia aumentar o risco de exposição.

## Regras para capturas

- Não usar capturas do banco ou dos relatórios atuais.
- Não usar nomes de arquivos que revelem estudantes ou turmas reais.
- Não mostrar URL, chave, código de acesso, licença ou identificador da máquina.
- Não mostrar nome, endereço, logo ou cores exclusivas de uma instituição sem autorização.
- Inspecionar metadados e propriedades dos arquivos antes da publicação.
- Preferir imagens recriadas com dados fictícios a borrar dados reais.
