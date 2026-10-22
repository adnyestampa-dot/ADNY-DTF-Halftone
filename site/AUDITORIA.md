# Auditoria do site ADNY DTF Halftone

Data: 22/10/2026. Repositório conferido: https://github.com/adnyestampa-dot/ADNY-DTF-Halftone

Revisão exata: `0af02d462ec07f39bf2856493b384c0a6621fb19` (commit de 20/10/2026). As conclusões se referem a essa revisão. Links gerais do GitHub podem mostrar alterações posteriores; o download do site está fixado na revisão conferida.

## Resultado e correções

A apresentação foi comparada com os arquivos Python atuais, e não apenas com a documentação, que contém registros históricos desatualizados. Foram corrigidos os pontos abaixo.

| Ponto | Evidência / correção |
| --- | --- |
| Captura antiga apresentada como interface atual | `docs/validacao-tela.png` ainda mostrava DTX Live. Substituída por uma captura da janela realmente executada a partir de `app/ui/main_window.py`, em português, com a arte de teste do repositório. Legenda identifica a revisão. |
| Abertura do aplicativo | `iniciar.py` também chama o monitor de desenvolvimento. O site agora indica `python -m app.main`, que abre diretamente o editor, conforme a entrada de `app/main.py`. |
| Preservação de tamanho | A separação preserva a imagem de trabalho; os comandos de tamanho e recorte mudam as dimensões. Corrigidos fluxo e FAQ, conforme `main_window.py` e `image_engine.py`. |
| DPI ausente | O editor usa 300 internamente para cálculos quando não há DPI informado; a exportação não grava esse valor como metadado de origem. FAQ esclarecido, conforme `_aplicar_origem` e `_eixos_dpi`. |
| Demonstração confundida com editor online | CTA alterado para “Ver demonstração” e explicação visível no início: são exemplos pré-processados; arquivos próprios exigem o aplicativo desktop. |
| Alfa binário atribuído também ao original | Indicador agora distingue “Original: alfa variável” de “Saída: alfa 0 ou 255”. |
| Download sujeito a mudanças futuras | Botão fixado no ZIP da revisão conferida, com identificação visível. Continua claramente identificado como código Python, que exige dependências. |
| Promessa implícita de resultado de impressão | Site informa que o projeto está em desenvolvimento e que o repositório não comprova prova física da estampa. |

## Afirmações confirmadas

| Informação no site | Fonte na revisão conferida |
| --- | --- |
| Aplicativo desktop Python / PySide6 | `app/main.py`, `app/ui/main_window.py`, `requirements.txt` |
| Retícula de 20–45 LPI | `app/model/settings.py`, `app/engines/halftone_engine.py`; interface oferece valores inteiros de 20 a 45 |
| Ângulo de 0° a 90° | `Settings.validate` e controle da interface |
| Cinco formas: redondo, elipse, losango, quadrado, linha | `SHAPES`, `SHAPE_LABELS`, `halftone_engine.renderizar` |
| Knockout por cor e limiar; transparência binária; RGB limpo em pixels transparentes | `knockout_engine.py`, `central.py`, `export_engine.py` |
| Base branca opcional e choke 0/1/2 px | `settings.py`, `underbase_engine.py`, `main_window.py` |
| Ajustes de tons, níveis e limpeza | `levels_engine.py`, `color_engine.py`, `tone_engine.py`, `cleanup_engine.py` e painéis da interface |
| Original, separação, máscara e comparação | `main_window.py`, `canvas.py` |
| Entrada PNG/JPG e .dtx próprio | Carregamento na interface, `image_engine.py`, `dtx_store.py` |
| .dtx próprio não compatível com formatos proprietários | `dtx_store.py`, identificador `dtx-clone-1` |
| Saída PNG RGB com alfa; base branca em arquivo separado quando habilitada | `export_engine.py`, `JanelaPrincipal.exportar_para` |
| DTF têxtil; conversão de cor pelo RIP; sem garantia de prova física | `docs/regras.md`, `rag/base/finalidade-dtf.md`, `docs/04-validacao.md` |
| Dependências PySide6, NumPy, Pillow e OpenCV | `requirements.txt` |

Não foram anunciados executável pronto, processamento web de arquivos próprios, gang sheet, upscaler, compatibilidade com .dtx de terceiros, canais spot proprietários ou qualidade de impressão garantida. A consulta de releases retornou lista vazia.

## Verificações executadas

- **Motor:** 13 testes de `tests/test_engines.py`, todos aprovados, incluindo limites de LPI, knockout, branco sólido, choke, limpeza, exportação, projeto próprio, dimensões e DPI presente/ausente.
- **Conferência independente:** 15 combinações de cinco formas × três frequências (20/30/45), preservando dimensões e alfa binário. Para as nove imagens de retícula exibidas no site, as três bases brancas e o exemplo de knockout, os pixels coincidiram exatamente com resultados recém-calculados pelo motor da revisão conferida: **13 saídas idênticas**.
- **Arte original:** o SHA Git da amostra usada coincide com `amostras/teste_dtf.png` do repositório.
- **Captura:** interface executada com Qt em modo offscreen, 1440 × 960; carregamento da amostra e conclusão do processamento antes da captura. Não é uma reconstrução gráfica nem a captura histórica dos documentos.
- **Entrada direta:** `python -m app.main` iniciou e permaneceu no laço gráfico durante a janela de teste; foi interrompido pelo limite de 3 segundos do teste.
- **Navegador desktop:** navegação por âncoras, nove combinações LPI/forma, três modos de visualização, slider por teclado, alternância de knockout, choke 0/1/2, modal de captura, perguntas expansíveis e tema. Imagens conferidas sem falhas de carregamento.
- **Comandos:** texto de instalação e execução conferido. Neste navegador, a permissão de clipboard não estava disponível; o fallback selecionou o comando e orientou a cópia manual.
- **Responsividade:** desktop de 1363 px e quadros de celular de 390 e 360 px. Nenhum transbordamento horizontal nos documentos. Menu móvel abriu, navegou e fechou; seletores, slider e tema responderam em largura móvel. São testes em navegador, não em aparelhos físicos.
- **Download real:** a URL exata do botão entregou ZIP de 11.839.105 bytes, com 119 entradas, pasta da revisão correta e arquivos essenciais presentes. A checagem CRC não encontrou arquivo corrompido. O rastreamento de conclusão de download do navegador gerenciado excedeu o tempo; a transferência e a integridade foram verificadas separadamente por HTTP.
- **JavaScript:** `node --check dist/app.js` aprovado.

## Pendências encontradas no aplicativo

A auditoria não permite dizer que o aplicativo inteiro está livre de falhas:

1. `tests/test_rag.py::test_encontra_a_falha_do_motor` falha porque a busca não retorna `rag/base/falha-do-motor-atual.md` entre os três primeiros resultados esperados. Reproduzido também no ZIP completo baixado, com os arquivos presentes. Os outros dois testes documentais passaram. O site não anuncia essa busca como recurso.
2. As três verificações de `tests/test_janela.py` chegaram a `OK`, incluindo separação e exportação. Porém, o processo terminou com código 139 no encerramento do ambiente Qt offscreen. Isso impede classificar essa execução gráfica como aprovação integral; não foi demonstrado que o encerramento se comporta da mesma forma no computador do usuário. A captura isolada terminou normalmente. Nenhum motor ou arquivo do aplicativo foi alterado nesta auditoria.
3. Não foi realizada prova física de impressão, instalação limpa completa em Windows/macOS, nem conferência de cores com RIP/impressora.

A navegação foi feita na prévia do mesmo código do site, em ambiente de teste.
