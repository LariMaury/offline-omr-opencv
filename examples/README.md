# Exemplos sintéticos

Esta pasta não contém dados ou saídas do sistema original. O demonstrador autorizado está em [visual_demo](visual_demo/README.md) e opera somente sobre uma fixture fictícia de 20 questões.

## Estrutura implementada

```text
examples/
├── create_conceptual_flow.py
└── visual_demo/
    ├── README.md
    ├── omr_demo_core.py
    ├── generate_synthetic_cards.py
    ├── render_real_demo.py
    └── synthetic-fixture.json
```

## Requisitos dos dados fictícios

- Utilizar nomes claramente artificiais, sem correspondência com pessoas do projeto original.
- Não reutilizar números de chamada, turmas, títulos de provas ou questões existentes.
- Não utilizar logo ou nome institucional.
- Não derivar a lista fictícia por anonimização reversível de dados reais.
- Criar gabaritos e respostas do zero.
- Documentar o resultado esperado de cada exemplo.

## Cenários implementados

1. Cartão alinhado.
2. Cartão fotografado com inclinação.
3. Cartão com distorção de perspectiva.
4. Respostas corretamente preenchidas.
5. Três respostas em branco no resultado avaliado.
6. Uma questão com duas alternativas fortes.
7. Uma bolha fraca, acima do limiar de alerta e abaixo do limiar de contagem.

Rotação de 180 graus, lote com página inválida e múltiplos tipos de prova não foram incluídos nesta etapa visual.
