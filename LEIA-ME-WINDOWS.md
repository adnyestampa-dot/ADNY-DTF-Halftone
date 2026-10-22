# ADNY DTF Halftone — Windows x64

Baixe o executável ou o ZIP na seção Releases deste repositório.

- Executável: abra `ADNY-DTF-Halftone.exe` com dois cliques. Python e bibliotecas já acompanham o arquivo.
- ZIP portátil: extraia a pasta e abra `ABRIR-ADNY.bat` ou o executável, ambos na raiz da pasta extraída.
- Código do GitHub: o atalho `ABRIR-ADNY.bat` na raiz baixa o executável publicado no primeiro uso, confere seu SHA256 e abre o aplicativo. Esse primeiro download exige internet. Nas próximas aberturas, usa o executável já baixado.

O aplicativo não precisa de internet para processar e exportar imagens. Para atualizar, feche o aplicativo e substitua o executável pela nova versão em Releases.

Os projetos salvos pelo menu Salvar ficam em `%LOCALAPPDATA%\ADNY-DTF-Halftone\dados\projetos`. Os diálogos de exportação permitem escolher outra pasta.

Este pacote abre diretamente o editor, sem o monitor de desenvolvimento. A versão é experimental e deve ser conferida no seu processo antes da produção. Os testes digitais do pacote não substituem prova de impressão.

O arquivo `BUILD.json` registra a revisão, versões das dependências e testes do pacote. `SHA256SUMS.txt` permite conferir os downloads da release.
