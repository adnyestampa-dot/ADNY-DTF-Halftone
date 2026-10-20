# Falha do motor atual

A interface foi aceita. A lógica do motor não atende a finalidade do aplicativo.

O arquivo enviado pelo usuário para teste não ficou salvo na pasta do projeto. O último registro em `dados/ultimo_processamento.json` só confirma LPI 30, célula de 10 px, alfa binário e base branca desligada. A falha abaixo está no código e atinge arte colorida de camiseta, não depende de adivinhar o arquivo.

## O que o motor fazia

Até a correção desta etapa, `knockout_engine.cobertura` dividia a distância até o preto por 441,67. Quase toda cor viva caía entre 0,5 e 0,9 e a retícula furava o chapado inteiro. O fundo sumia e a estampa virava adesivo pontilhado, sem separar fumaça de cor contínua.

## O que o motor faz agora

A presença continua no limiar da cor de knockout. O tom está em `tone_engine`, pela pesquisa em `rag/base/pesquisa-publica-reticula.md`. Cor opaca e viva fica contínua. Alfa parcial vira ponto na proporção da opacidade. Cinza opaco em rampa vira ponto. Degradê opaco entre cores vivas permanece contínuo, porque a fonte pública de DTF não manda furar esse caso. A interface não mudou.

## O que não mexer

Painéis, menus, vistas, Apply Seps, Export PNG e o restante da interface permanecem. A correção é troca de lógica dentro dos motores, coordenada pelo motor central.
