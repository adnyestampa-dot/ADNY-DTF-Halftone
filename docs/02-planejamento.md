# Planejamento

A interface fica em PySide6. O processamento fica numa árvore chamada pelo motor central. Trocar um motor não exige reconstruir a janela.

```
Motor central
├── Imagem: abrir, 300 DPI, escala, recorte
├── Cor: matiz, saturação, luminosidade
├── Knockout: distância até a cor escolhida
├── Levels: entrada, gamma, saída
├── Retícula: 20–45 LPI, ângulo e forma
├── Limpeza: remove ilhas menores que o número exibido
├── Base branca: choke de 0, 1 ou 2 px
└── Exportação: PNG com alfa 0 ou 255 e RGB zerado no transparente
```

A cobertura vem da distância entre o pixel e a cor de knockout. O threshold zera o que está perto dessa cor. Levels molda a cobertura. Onde a cobertura é total, o ponto fecha e o texto permanece sólido. Onde é parcial, a retícula abre o degradê. Cleanup roda depois. O pincel devolve o pixel original opaco. A varinha força transparência.

A retícula recusa LPI fora de 20–45. Não há correção silenciosa. DPI de trabalho é 300. O PNG de saída leva essa marca. A base branca é a tinta encolhida pelo choke e exportada como layer RGBA, mask em cinza ou spot em PNG. O spot original não teve a codificação publicada; o arquivo avisa isso no metadado.

O .dtx deste clone é um zip com imagem, ajustes e máscaras, formato `dtx-clone-1`. Ele não abre o arquivo proprietário.

O preview ao vivo usa o mesmo motor da exportação. Export PNG só grava o resultado do Apply Seps. Se um controle muda, a exportação trava de novo.

Presets publicados: 30 LPI, 22,5° e Round. Black e White também pintam knockout e camiseta de preto ou branco. Color só mexe na retícula.
