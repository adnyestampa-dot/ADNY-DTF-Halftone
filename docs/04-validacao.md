# Validação

Conferido nesta sessão, sem o aplicativo original aberto.

## Automático

`tests/test_engines.py`: 10 testes. A retícula recusa 19 e 46 LPI, o quadrado acompanha a cobertura, 20 LPI gera menos pontos que 45, o preto de fundo sai e o branco sólido permanece, o choke reduz a base, a limpeza apaga o pixel isolado, o PNG e o .dtx próprio fazem o caminho de ida e volta, e 300 px equivalem a 1 polegada.

`tests/test_janela.py`: a janela abre, separa, mantém o Export PNG desligado até Apply Seps, troca para 25 LPI e o resultado usa 25.

## Janela

A captura `docs/validacao-tela.png` mostra a arte `amostras/teste_dtf.png` em Split View. O fundo preto vira xadrez. O texto DTF permanece sólido. O amarelo e o anel à direita entram em retícula. Cabeçalho, vistas, Halftone Screen, Levels, Apply Seps, Export PNG, zoom e Fit to View estão no lugar descrito pela miniatura pública.

## Não validado

Não houve o mesmo arquivo processado no ActionSeps. Não houve prova física da estampa. Gang sheet, AI upscaler e o .dtx original continuam bloqueados. As cores são aproximadas. A posição de Image Size, Crop e dos painéis abaixo de Levels segue o vídeo e a página, não um print completo da rolagem.
