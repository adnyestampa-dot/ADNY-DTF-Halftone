# Plano de suavização — LOCALIZAR, CORRIGIR, TESTAR, VALIDAR

Orquestrador, 20 de outubro de 2026. Consulta RAG: `rag/consultas/20261020-142916.json`.

A base não descreve um jeito mais rápido de calcular a retícula. Por isso este plano não troca fórmula, não reamostra a arte e não mexe no desenho da janela. A trava está no código nosso: o botão espera um cálculo da imagem inteira na mesma linha que desenha a tela.

O motor de chapado e ponto continua aberto até o julgamento da arte do usuário. Esta fila não fecha essa tarefa.

## Limite para todos os agentes

- LPI continua 20–45, e o número na tela é o número processado.
- Alfa binário, cor, texto, fumaça, sombra, degradê e geometria do ponto permanecem.
- Largura, altura, proporção e DPI do arquivo permanecem. Arquivo sem DPI não ganha 300 na exportação.
- Menus, painéis, vistas e o fluxo Aplicar separação / Exportar PNG ficam no lugar.
- Checkpoint em `checkpoints/` antes da primeira alteração de código.
- Nenhum agente marca a suavização como concluída sem o teste e a validação abaixo.

## 1. LOCALIZAR

O Orquestrador já leu o caminho do clique. O Pesquisador não busca fórmula nova. O Executor mede, no arquivo real, qual destes pontos segura o clique por mais tempo. Sem essa medida, ninguém escolhe um culpado no escuro.

Pontos já vistos no código:

1. Vista e fundo da camisa. `_mostrar` e `_sobrepor` em `app/ui/main_window.py` montam a imagem inteira em ponto flutuante na thread da janela. Original, Separação, Lado a lado, Máscara e o fundo da camisa passam por aí. O Lado a lado faz isso duas vezes. `para_pixmap` em `app/ui/canvas.py` copia de novo para o Qt.
2. Controles contínuos. Lineatura, ângulo, limiar, matiz, saturação, luminosidade e limpeza chamam `_marcar` a cada passo. O timer espera 80 ms e dispara o motor inteiro. Se o motor ainda está rodando, `repetir` começa outro assim que o anterior termina.
3. Cópia antes do motor. `_disparar` copia a arte e as máscaras na thread da janela, antes de a thread de trabalho começar.
4. Volta do motor. `_resultado` grava JSON e chama `_mostrar` na thread da janela. O clique que chega nesse instante espera a montagem da vista.
5. Pincel. Cada movimento do mouse chama `_marcar`, então um traço pede uma separação completa por ponto.
6. Varinha. A distância de cor da imagem inteira é calculada na thread da janela e em seguida chama `_marcar`.
7. Abertura. O histograma percorre a arte na thread da janela.
8. Salvar e Exportar PNG. A gravação do arquivo acontece na thread da janela depois do diálogo.
9. Tema Claro/Escuro. Troca o estilo da janela inteira de uma vez. É um soluço curto, atrás dos itens acima.
10. Fechar. A janela pode esperar até 8 s o motor terminar. Só aparece ao sair.

O que o Executor mede, sem mudar código de motor:

- Tempo de um clique em Original, Separação, Lado a lado, Máscara e no fundo da camisa, com a mesma arte já carregada.
- Tempo de um arraste de limiar ou ângulo até o estado voltar a Pronto.
- Tempo de um traço curto de pincel e de um clique da varinha.
- Tempo de Salvar e de Exportar PNG depois que a separação já está pronta.
- Tamanho em pixels e DPI da arte usada na medida, anotados no registro. Sem porcentagem inventada.

## 2. CORRIGIR

O Construtor desenha a troca. O Executor aplica depois do checkpoint. A ordem é a da medida: o ponto mais lento entra primeiro. Se dois empatam, a vista e o fundo da camisa vêm antes do motor, porque seguram o botão mesmo quando a separação já existe.

Correções permitidas, todas com o mesmo resultado visual do motor atual:

- Guardar a montagem da vista enquanto a arte, a separação, a cor da camisa e o interruptor do fundo não mudarem. O xadrez nasce uma vez para aquele tamanho.
- Converter para pixmap fora da resposta do clique, ou reaproveitar o pixmap se a vista não mudou.
- Enquanto o controle estiver sendo arrastado, esperar o soltar para rodar o motor uma vez. O valor solto é o valor processado.
- Se um cálculo já está andando, o próximo usa só o último pedido. Pedidos intermediários não entram na fila.
- A cópia da arte e a montagem da vista saem da thread da janela. A janela só recebe a imagem pronta e troca o estado.
- O pincel atualiza a máscara na hora e pede uma separação só ao soltar o mouse.
- A varinha calcula a distância fora da thread da janela.
- Salvar e Exportar PNG gravam fora da thread da janela. O estado mostra que está gravando e depois confirma ou mostra a falha.
- O tema só entra se a medida mostrar que ele segura o clique. Não é desculpa para redesenhar a janela.

Correções proibidas:

- Retícula em resolução menor que a arte.
- Fórmula nova de ponto, ângulo ou cobertura.
- Mudar o que o PNG exporta, inclusive gravar a cor da camisa dentro do arquivo.
- Mover botão, menu ou painel.

## 3. TESTAR

O Validador escreve o teste antes de aceitar a correção. O Executor roda o que já existe e o que for novo.

- `tests/test_engines.py` permanece verde. Um arquivo fixo, com DPI informado e outro sem DPI, sai com os mesmos pixels, o mesmo tamanho e o mesmo DPI de antes desta fila.
- A montagem da vista com fundo de camisa e com xadrez produz os mesmos pixels da função atual. A segunda chamada, sem mudança de arte nem de cor, não refaz a imagem.
- Vários avisos de controle seguidos geram um único processamento, com o último valor.
- O pincel em movimento não dispara um motor por coordenada. O soltar dispara um.
- A varinha e a gravação não travam a chamada que só pede o trabalho: a janela segue capaz de processar eventos enquanto o arquivo está sendo escrito.
- Teste de janela existente de vista, fundo da camisa, salvar e exportar continua verde.

Queda do Qt ao encerrar um teste offscreen, depois do OK impresso, não conta como falha. Já é conhecida.

## 4. VALIDAR

O Validador só aceita quando os três itens abaixo estão juntos.

- Os testes novos e os antigos passaram no mesmo arquivo de prova.
- Na arte do usuário, trocar de vista, marcar o fundo da camisa, arrastar um controle e soltar, usar pincel e varinha, salvar e exportar não deixam a janela muda. O estado pode dizer Separando ou Gravando. O botão de vista não espera o motor.
- A separação final do arquivo de prova é a mesma de antes da fila. O usuário continua sendo quem diz se o chapado e o ponto servem na arte dele.

Se a medida mostrar que um ponto da lista não segura o clique, ele sai da correção e fica anotado. Não se corrige o que a medida não acusou.
