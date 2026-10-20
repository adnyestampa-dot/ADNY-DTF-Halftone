# Estrutura de criação do próximo motor

Proposta nossa. Não é código do ActionSeps. A presença e o tom descritos abaixo estão no `knockout_engine`. A interface não muda.

## Árvore

O motor central continua coordenando. A ordem passa a ser:

1. Motor de imagem: abre, 300 DPI, escala e recorte.
2. Motor de cor: HSL, se os controles estiverem fora do neutro.
3. Motor de presença: decide o que é camiseta e o que é arte, usando a cor de knockout e o mask threshold visível.
4. Motor de tom: dentro da arte, mede chapado contra transição. Degradê, fumaça, sombra e borda suave produzem cobertura entre 0 e 1. Cor viva de chapado não vira sólido só por estar longe do preto.
5. Motor de levels: entrada, gamma e saída moldam essa cobertura, com o valor exibido.
6. Motor de retícula: 20 a 45 LPI, ângulo e forma. Ponto só onde o tom é parcial. Tinta contínua só onde o tom está cheio de verdade.
7. Motor de limpeza: remove ilha menor que o número de pixels exibido.
8. Motor de base branca: tinta com choke de 0, 1 ou 2 px.
9. Motor de exportação: PNG com alfa binário e sem resíduo.

## Troca sem reconstruir o app

Presença e tom substituem o papel atual de `knockout_engine.cobertura`. A retícula deixa de promover cobertura 0,999 vinda da distância crua. O motor central só muda a ordem das chamadas. A janela continua mandando os mesmos controles.

## Pendente até haver prova

A fórmula exata do aplicativo original não foi publicada. Qualquer curva nova fica marcada como proposta até um arquivo de teste processado nos dois lados. Sem esse arquivo, o RAG não autoriza copiar um resultado imaginado.
