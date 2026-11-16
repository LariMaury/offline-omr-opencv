# Visão técnica e seleção de código

## Objetivo deste documento

Este documento registra quais partes do projeto original têm maior valor para uma eventual publicação seletiva. Após autorização explícita, um subconjunto do núcleo OMR foi isolado em `examples/visual_demo/omr_demo_core.py` exclusivamente para a demonstração sintética. A autorização de isolamento e execução não autoriza publicação.

A seleção prioriza componentes que:

- demonstram raciocínio algorítmico;
- podem ser compreendidos sem a aplicação completa;
- aceitam entradas sintéticas;
- não dependem de credenciais ou dados escolares;
- podem ser apresentados honestamente como adaptações do código existente.

## Avaliação dos candidatos

### `calibrar_grade`

**Finalidade:** localizar os contornos das bolhas, agrupar candidatos em linhas, inferir o layout e reconstruir a posição A–E de cada coluna.

**Competências demonstradas:** OpenCV, limiarização adaptativa, análise de contornos, agrupamento geométrico, estatística robusta por mediana e tratamento de detecções parciais.

**Dependências:** OpenCV e NumPy.

**Qualidade observada:** alta legibilidade local e boa explicação do algoritmo. As validações de quantidade de linhas e candidatos tornam falhas explícitas.

**Adaptação implementada:** o algoritmo preserva os layouts fixos do original — três colunas com 8 a 15 linhas ou quatro colunas com 25 linhas — e retorna uma `GridGeometry` tipada. Os limites geométricos não foram parametrizados. A detecção da faixa divisória foi isolada e mantém a rejeição original de linhas abaixo de 80% da altura. Há testes para a grade sintética e para entradas inválidas.

**Risco de exposição:** baixo se forem utilizadas somente imagens sintéticas. A função não precisa conhecer nomes ou notas.

**Recomendação:** prioridade máxima.

### `corrigir_perspectiva_por_marcas`

**Finalidade:** detectar quatro quadrados de alinhamento, validar isolamento e coerência geométrica e normalizar o cartão para uma dimensão de referência.

**Competências demonstradas:** visão computacional, filtragem de contornos, geometria projetiva, validação defensiva e transformação de perspectiva.

**Dependências:** OpenCV e NumPy.

**Qualidade observada:** algoritmo demonstrativo forte. As verificações de quadrante, tamanho e proporção reduzem falsos candidatos.

**Adaptação implementada:** a detecção das marcas foi separada da homografia, a captura genérica silenciosa foi removida e o retorno inclui os pontos localizados. A conversão usa `BGR2GRAY`, pois o demonstrador recebe imagens no formato nativo do OpenCV; o original recebe imagens RGB. Dimensões e tolerâncias continuam fixas e específicas do cartão. A função aceita qualquer matriz compatível, embora os scripts públicos forneçam somente entradas sintéticas.

**Risco de exposição:** baixo com cartões fictícios e sem cabeçalho institucional.

**Recomendação:** prioridade máxima.

### Classificação de marcações em `_corrigir_folha_interna`

**Finalidade:** medir a quantidade de tinta dentro de uma máscara circular e classificar a bolha como marcada, fraca ou vazia.

**Competências demonstradas:** processamento binário, máscaras, medição de densidade, configuração por limiares e visualização de depuração.

**Dependências:** OpenCV e NumPy; a função completa também depende de OCR, configuração global, sistema de arquivos e identificação de estudantes.

**Qualidade observada:** a parte matemática é clara, mas está incorporada a uma função de 133 linhas que mistura reconhecimento, dados pessoais e gravação de imagens.

**Adaptação realizada na demonstração:** foi extraído apenas um classificador independente, identificado como adaptação do algoritmo original. OCR, identificação, caminhos e gravações de depuração foram excluídos. Os limiares de marca forte e fraca passaram de configuração global para argumentos com os mesmos padrões `0.40` e `0.22`.

**Risco de exposição:** alto se a função completa for copiada, porque ela manipula nome, número e recortes do cabeçalho. Baixo para o classificador isolado.

**Recomendação:** prioridade máxima. O desacoplamento mínimo foi realizado para a demonstração sintética; uma publicação ainda exige revisão própria.

### `avaliar_respostas`

**Finalidade:** comparar as alternativas de uma ficha com o gabarito e produzir nota total, notas por disciplina e detalhe questão a questão.

**Competências demonstradas:** modelagem de regras, estruturas de dados, separação entre leitura e avaliação e tratamento de branco ou múltipla marcação.

**Dependências:** apenas estruturas padrão do Python.

**Qualidade observada:** função curta, legível e praticamente pura. É o componente mais fácil de testar e explicar.

**Adaptação implementada:** o demonstrador preserva somente a regra de acerto por questão. O retorno original com nota total, notas por disciplina e detalhes textuais foi substituído por `GradeResult`, que contabiliza correta, incorreta, branca e múltipla. O estado original `ANULADA` foi renomeado para `MULTIPLE` para evitar confusão com questão cancelada. Notas por disciplina não fazem parte da amostra pública. Há testes de todos os estados e de entradas vazias.

**Risco de exposição:** baixo, desde que exemplos e identificadores sejam fictícios.

**Recomendação:** prioridade máxima.

### `ler_lote`

**Finalidade:** percorrer páginas de um PDF, renderizar imagens, dividir cartões, processar cada unidade e preservar erros localizados.

**Competências demonstradas:** pipeline em lote, integração com PDF, tolerância a falhas, callbacks de progresso e gerenciamento de recursos.

**Dependências:** PyMuPDF, OpenCV, NumPy e funções internas de leitura.

**Qualidade observada:** fluxo compreensível e útil como exemplo de robustez operacional. A dependência do restante do monólito impede publicação isolada direta.

**Adaptação necessária:** receber um processador injetável; usar tipos de resultado sem nomes; garantir fechamento por gerenciador de contexto; testar página inválida e cartão duplo.

**Risco de exposição:** médio. Os resultados originais contêm identificação de estudantes e mensagens potencialmente derivadas de arquivos reais.

**Recomendação:** publicar somente uma adaptação sanitizada e explicitamente documentada.

### `montar_estatisticas`

**Finalidade:** produzir resumo da turma, médias por disciplina, distribuição de aproveitamento e análise por questão.

**Competências demonstradas:** Pandas, NumPy, agregação tabular e transformação de resultados de domínio em indicadores.

**Dependências:** Pandas, NumPy e funções de seleção de gabarito.

**Qualidade observada:** boa cobertura funcional, porém combina cálculo de DataFrames com construção de registros detalhados por estudante.

**Adaptação necessária:** usar identificadores sintéticos; separar agregações coletivas do detalhe individual; documentar denominadores e regras para brancos e múltiplas marcações.

**Risco de exposição:** alto com os dados atuais; baixo com fixtures inteiramente sintéticas.

**Recomendação:** alta, após sanitização.

### `detectar_tipo`, `normalizar_gabaritos` e `gabarito_do_resultado`

**Finalidade:** reconhecer o tipo A–D e selecionar a chave correta.

**Competências demonstradas:** integração entre visão computacional e regras de correção, compatibilidade entre gabarito único e múltiplos modelos.

**Dependências:** OpenCV e NumPy para a detecção; Python padrão para a seleção.

**Qualidade observada:** funções curtas e úteis, mas a detecção usa coordenadas e um limiar vinculados ao cartão original.

**Estado no demonstrador:** não incluído. A fixture declara explicitamente o tipo A; o repositório não demonstra reconhecimento nem seleção de tipos A–D.

**Risco de exposição:** baixo com imagens sintéticas.

**Recomendação:** incluir como apoio ao núcleo OMR.

## Componentes não recomendados

- Interface completa de `leitor.py`: alto acoplamento e presença de elementos confidenciais.
- OCR e casamento nominal completos: risco de dados pessoais e ausência de benchmark.
- Histórico SQLite original: contém registros individuais.
- Heurísticas de defasagem, ansiedade, abandono e similaridade de erros: não validadas para exposição como diagnóstico.
- Geração e validação de licenças: material confidencial.
- Integração com o portal: depende de configuração e infraestrutura privadas.
- Relatórios existentes com dados reais: risco direto de exposição.
- Gerador de caderno completo: protótipo com referências institucionais.

## Ordem recomendada para uma eventual publicação seletiva

1. Motor puro de correção de respostas.
2. Correção de perspectiva e calibração da grade.
3. Classificador isolado de bolhas.
4. Seleção de gabarito por tipo.
5. Pipeline de lote sanitizado.
6. Estatísticas coletivas sobre fixtures sintéticas.

O núcleo OMR visual registra neste documento sua origem, as alterações de desacoplamento e os limites demonstráveis. Qualquer componente adicional deve passar por nova revisão técnica, de privacidade e de titularidade.

## Competências evidenciadas

- Python aplicado a um fluxo real de automação.
- Visão computacional clássica e geometria de imagens.
- Integração de bibliotecas científicas e documentais.
- Processamento em lote tolerante a falhas.
- Modelagem de regras de correção.
- Análise tabular e geração de indicadores.
- Geração automatizada de Excel e PDF.
- Persistência local e empacotamento para desktop.
- Capacidade de reconhecer limites de confiabilidade e privacidade.
