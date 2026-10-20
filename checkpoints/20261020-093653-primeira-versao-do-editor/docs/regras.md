# Regras do projeto

Versão 1.0 mais a regra 13. O Orquestrador consulta este arquivo.

1. O ActionSeps DTX Live é a referência. A meta é 90% a 95% de fidelidade de interface, fluxo e resultado, com código nosso. 100% seria copiar o fonte linha a linha, e isso está fora do projeto.
2. Tudo é Python: interface, motores e ferramentas. Sem plugin do Photoshop.
3. Mudança que descaracterize o clone para e pede autorização. Melhoria compatível com o objetivo ganha checkpoint, motivo e aviso.
4. Um motor central coordena motores especializados, substituíveis sem reconstruir o app.
5. Pesquisador, construtor, executor e validador se falam pelo orquestrador.
6. Função não confirmada em fonte pública não vira comportamento. Fica pendente.
7. É permitido estudar o comportamento público. É proibido copiar código proprietário.
8. O alvo é DTF têxtil para camiseta: CMYK entregue ao RIP em PNG RGB, base branca, retícula só de 20 a 45 LPI. O valor na tela é o valor do motor. DTF UV fica de fora.
9. A saída reticulada tem alfa binário, sem resíduo no transparente. Cor, texto, fumaça, sombra, degradê e geometria do ponto entram no critério. Teste digital não substitui a prova física.
10. Ferramenta sem teste não está validada.
11. Correção retesta o que mudou e o que pode ter sido afetado.
12. Checkpoint em pasta `checkpoints/` guarda o código para restauração.
13. O monitor Python lê `monitor/status.json` e abre um aviso real a cada 15 minutos. Sem registro confiável, o aviso fica vermelho. Ele encerra se o Cursor fechar ou se existir `monitor/STOP`, escrito quando o usuário disser: Vamos parar o projeto por aqui.
