# Finalidade da separação DTF têxtil

O aplicativo prepara arte para impressão DTF em camiseta. A saída é um PNG em que a cor da estampa fica nos pontos e o tecido aparece nos furos.

## Resultado que a finalidade exige

- Cor da camiseta removida, sem caixa preta e sem halo branco.
- Texto e chapado contínuos, legíveis, sem serem esfarelados.
- Fumaça, sombra, degradê e borda suave convertidos em retícula de 20 a 45 LPI.
- O LPI mostrado é o LPI processado. Fora dessa faixa o motor recusa.
- Alfa só 0 ou 255. Onde o alfa é 0, o RGB também é 0.
- Base branca opcional, acompanhando a tinta, com choke de 0, 1 ou 2 px para não vazar na borda.
- As cores da arte permanecem nos pixels que recebem tinta. O RIP da impressora converte para CMYK. O app não inventa separação em chapas CMYK.

## Duas decisões que o motor precisa separar

Presença: o pixel pertence à arte ou à camiseta.

Tom: dentro da arte, o pixel é chapado ou é uma transição que precisa de ponto.

A presença usa a cor de knockout e o limiar visível. O tom usa a opacidade e, no cinza opaco em rampa, a distância até a camiseta. Cor viva opaca não vira ponto só por estar longe do preto.
