# Limitações e alegações permitidas

## Finalidade

Este documento evita que a apresentação pública atribua ao projeto maturidade, precisão ou validação que não estão demonstradas por evidências disponíveis.

## Limitações técnicas confirmadas

### Testes e precisão

- O projeto original não possui suíte de testes automatizados identificada.
- O demonstrador público possui testes unitários e de integração com dados sintéticos; eles não validam o sistema desktop privado.
- Não existe benchmark versionado de cartões físicos ou imagens reais de referência.
- Não há benchmark público de precisão das bolhas, OCR de nomes ou associação aos estudantes.
- Não há evidência reproduzível para anunciar uma porcentagem de acerto.
- O teste com cartões impressos e preenchidos em condições variadas permanece fora do escopo.

### Arquitetura

- O módulo principal combina interface, domínio, visão computacional, banco de dados, rede e relatórios.
- Grande parte da interface está dentro de uma única função com closures ligadas aos widgets.
- Configuração e diretórios são globais.
- Há capturas amplas de exceções, algumas silenciosas.
- Dependências não são declaradas em manifesto reprodutível no projeto original.

### Processamento de imagem

- Dimensões, regiões e tolerâncias foram definidas para o cartão desenvolvido no projeto.
- O algoritmo pode falhar quando marcas de alinhamento ou contornos das bolhas não estão preservados.
- Limiarização e densidade de tinta podem variar com scanner, compressão, iluminação, lápis e caneta.
- A rotação tratada explicitamente é de 180 graus; outras rotações dependem da correção pelas marcas.

### Identificação de estudantes

- OCR de escrita manual não é determinístico.
- O casamento nominal seleciona a melhor similaridade acima de um limiar, sem uma margem explícita para o segundo candidato.
- Número de chamada melhora a associação, mas erros de preenchimento ou duplicidades ainda exigem revisão.
- A interface permite prosseguir sem revisão em certos casos pendentes.

### Estatísticas e indicadores

- Médias, percentuais e distribuições são indicadores descritivos.
- Sinalizadores de defasagem, disparidade, abandono ou similaridade de erros são heurísticas internas.
- Esses sinalizadores não são diagnósticos pedagógicos, psicológicos ou disciplinares.
- Nenhuma decisão sobre um estudante deve ser automatizada a partir desses sinais.

### Persistência e privacidade

- O projeto original armazena identificação, notas e respostas em arquivos locais sem criptografia de aplicação.
- Backups e relatórios replicam parte dos dados.
- Imagens de depuração podem conter o cabeçalho do cartão.
- Esses artefatos não pertencem ao escopo público.

## Alegações adequadas para o portfólio

É adequado afirmar que o projeto:

- implementa um pipeline offline de OMR;
- usa OpenCV para detectar grade e marcas de alinhamento;
- trata respostas em branco, múltiplas e de preenchimento fraco;
- processa PDFs em lote e isola falhas por página ou cartão;
- suporta gabaritos por tipo de prova;
- produz estatísticas descritivas e documentos locais;
- demonstra integração entre visão computacional, processamento tabular e automação documental.

## Alegações que não devem ser feitas

Não afirmar, sem validação adicional, que o projeto:

- possui determinada taxa de precisão;
- elimina a necessidade de conferência humana;
- identifica estudantes sem risco de erro;
- detecta fraude ou cola;
- diagnostica ansiedade, desatenção ou defasagem;
- está pronto para produção em qualquer escola;
- é uma plataforma de inteligência artificial completa;
- possui portal online concluído e mantido;
- foi integralmente testado em cenários reais.

## Desenvolvimento assistido por IA

O projeto foi desenvolvido com apoio de ferramentas de IA. Isso não invalida o trabalho técnico, mas exige revisão humana explícita. A apresentação pública deve valorizar decisões verificáveis no código, não o volume produzido. Trechos adaptados devem ser testados e descritos como adaptações, preservando a distinção entre o sistema original e a amostra pública.
