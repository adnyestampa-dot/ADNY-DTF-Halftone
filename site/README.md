# Site ADNY DTF Halftone

Código do site de apresentação do aplicativo ADNY DTF Halftone. HTML, CSS, JavaScript e imagens estão nesta pasta `site/`.

Para visualizar, abra `site/index.html` no navegador. Para usar um servidor local, execute na raiz do repositório:

```sh
python -m http.server 8000 --directory site
```

Acesse `http://localhost:8000` no seu computador.

Os controles do site exibem exemplos pré-processados. Para editar seus próprios arquivos no aplicativo desktop, instale as dependências a partir da raiz deste repositório:

```sh
python -m pip install -r requirements.txt
python -m app.main
```

O conteúdo e os exemplos foram conferidos contra a revisão `0af02d462ec07f39bf2856493b384c0a6621fb19`. O download do aplicativo aponta para essa revisão.

Leia [AUDITORIA.md](AUDITORIA.md) para as correções, testes e limitações encontrados. Os testes digitais não substituem uma prova de impressão.

Para regenerar as imagens de demonstração, com as dependências do aplicativo instaladas, execute da raiz do repositório:

```sh
python site/tools/render-previews.py --app-root . --output site/assets
```

A imagem `desktop.webp` foi capturada executando a interface da revisão conferida. O script de estudos não a substitui.
