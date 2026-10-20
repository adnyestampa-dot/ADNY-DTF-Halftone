# Uso do RAG pelos agentes

O RAG recupera trechos da base e dos documentos do projeto. Ele não desenha a tela e não grava código sozinho.

## Ordem

1. O Orquestrador formula a pergunta da etapa.
2. A consulta roda com `python -m rag.consultar` ou `rag.consultar.consultar`.
3. O resultado é gravado em `rag/consultas`, com pergunta, pontuação e fonte de cada trecho.
4. Pesquisador, construtor, executor e validador usam só o que voltou, mais o que estiver marcado como proposta.
5. Se a pontuação vier zerada, a etapa para e registra que não houve trecho. Não se completa a lacuna com suposição.

## O que consultar antes de mudar motor

- Falha do motor atual.
- Finalidade DTF têxtil.
- Estrutura de criação do próximo motor.
- Regras do projeto, em especial LPI 20–45, alfa binário e interface já aceita.

## O que não fazer

Não alterar menus, painéis nem o fluxo Apply Seps / Export PNG por causa de uma consulta de motor. Não tratar texto ausente da base como comportamento do ActionSeps.
