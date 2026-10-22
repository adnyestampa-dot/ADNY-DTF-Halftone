Aplicativo desktop para Windows x64, empacotado com Python, PySide6 e dependências.

- Abra `ADNY-DTF-Halftone.exe` com dois cliques, sem instalar Python.
- O ZIP portátil inclui o executável e o atalho `ABRIR-ADNY.bat` na raiz.
- O mesmo atalho está na raiz do repositório e baixa a versão publicada no primeiro uso.
- Projetos internos são salvos em `%LOCALAPPDATA%\ADNY-DTF-Halftone`, fora da extração temporária do executável.
- O pacote só é publicado após os testes do motor e a execução do próprio `.exe`: interface, processamento, PNG, base branca, dimensões/DPI e projeto `.dtx` próprio.

Versão experimental. Não houve prova física de impressão nesta compilação. As versões das bibliotecas e a revisão de origem constam em `BUILD.json`. Confira os downloads com `SHA256SUMS.txt`.
