# Pesquisa pública da retícula DTF

Método do orquestrador, 20 de outubro de 2026. A pergunta foi: qual aplicativo público faz o mesmo papel, com melhor reputação, resultado e desempenho, dentro da nossa regra. A fórmula do ActionSeps não apareceu. Nada de código proprietário foi copiado.

## Onde se olhou

GitHub, fórum de camiseta, guias de oficina DTF e a página de um gerador DTF. Mastodon não devolveu discussão técnica utilizável nesta busca.

## O que cada um faz

- OpenRIP (`andar1216/RIP-Software`): DTF/DTG, base branca e retícula Floyd-Steinberg, estocástica ou ordenada. Zero estrelas. O autor marca como protótipo. A difusão de erro fura também o chapado. Não serve.
- Halftones (`schwanksta/Halftones`): serigrafia em chapas, cor chapada ou retícula por camada, base com redução. Zero estrelas. É outro produto, de telas, não um PNG único para o RIP.
- BWLabSP: retícula AM por luminância para serigrafia. Fotografia inteira vira ponto, inclusive o que precisaria ficar chapado.
- Monochromizer: cita Bayer 1973 e Holladay 1980 e testa a área do ponto. Zero estrelas e licença sem uso comercial. A retícula AM clássica também fura o texto.
- toPSD, gerador DTF: pixel opaco permanece com a mesma cor; pixel transparente permanece vazio; opacidade parcial vira ponto da própria cor, com a área acompanhando a opacidade. Há corte do que é claro demais e fechamento do que já é quase sólido.
- DTF Transfer Studio e DTF Direct: a fumaça, a sombra e o degradê que existem como transparência precisam virar ponto, porque o DTF não imprime translucidez. A cor opaca fica contínua.
- T-Shirt Forums: pixel semitransparente ganha base branca indesejada. O fade de preto ou cinza tem de ser refeito em retícula, com ponto sólido e furo, sem borda borrada.

## Escolha

O método aplicado é o do toPSD mais o fade neutro do fórum. Motivo: é o único descrito para DTF têxtil, no mesmo tipo de saída que a nossa (PNG RGB com transparência), e não esfarela o chapado. Os repositórios com retícula AM genérica têm a mesma reputação baixa e pior resultado para esta regra. Nenhum deles mostrou medida de desempenho reproduzível; a escolha não usou um número de velocidade.

## Regra que entrou no motor

- Perto da cor de knockout, até o limiar visível, não há tinta.
- Alfa zero não tem tinta.
- Alfa parcial vira cobertura igual à opacidade. O ponto guarda a cor do pixel.
- Cor opaca e viva fica contínua, mesmo longe do preto.
- Cinza opaco em rampa, fumaça ou sombra sem alfa, vira ponto. A cobertura é a distância até a camiseta dividida pelo diâmetro RGB, raiz de 3 vezes 255. Isso só vale para cor neutra. Cor viva não passa por esse divisor.
- Degradê opaco entre duas cores vivas permanece contínuo. A fonte pública não manda furar esse caso. Fica registrado, não vira ponto por suposição.
