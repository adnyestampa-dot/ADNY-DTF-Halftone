# Site ADNY DTF Halftone

Site de apresentação do aplicativo desktop. Os arquivos HTML, CSS, JavaScript e imagens estão nesta pasta `site/`.

## Download Windows

O download principal oferece o executável Windows x64 e o ZIP portátil da seção Releases. O pacote inclui Python e bibliotecas; o visitante pode abrir o aplicativo sem instalar Python.

A release `windows-v0.1.3-1` foi compilada a partir de `865d7cb610c4bde79f37b5161f4afdbf29cd3bc7`. Foram aprovados os 13 testes do motor e a execução do próprio .exe no Windows: interface nativa, processamento, PNG, base branca, dimensões/DPI e ida e volta do projeto .dtx. A captura `assets/desktop-windows.webp` veio dessa execução real do .exe, com uma imagem sintética de validação.

O atalho `ABRIR-ADNY.bat` está na raiz do repositório e do ZIP portátil. No primeiro uso pela pasta do código, baixa o executável publicado e confere seu SHA256. Esse primeiro uso foi validado separadamente no Windows, incluindo a abertura e o processamento pelo .exe baixado.

As imagens da demonstração são pré-processadas. O site não processa os arquivos do visitante; a edição é feita no aplicativo desktop.

## Visualizar este site

Abra `site/index.html` ou, na raiz do repositório, execute:

```sh
python -m http.server 8000 --directory site
```

Acesse `http://localhost:8000` no computador.

## Executar o código do aplicativo

Para quem preferir trabalhar com o código-fonte, na raiz do repositório:

```sh
python -m pip install -r requirements.txt
python -m app.main
```

O empacotamento e a release são mantidos em `.github/workflows/windows.yml`. As evidências e limitações estão em [AUDITORIA.md](AUDITORIA.md). Os testes digitais não substituem prova física de impressão.
