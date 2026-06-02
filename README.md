# 中国 · Apostila de Estudo — site de estudo vivo

Site de leitura e estudo da sua apostila sobre a China, para a viagem de
**5 a 27 de setembro de 2026** (Hong Kong → Pequim → Shenzhen → Xangai).

É **autocontido e funciona offline** — essencial dentro da China continental,
onde muitos serviços ocidentais são bloqueados.

## Como abrir

**Mais fácil:** duplo-clique em **`abrir.command`** — sobe um servidor local e
abre no navegador. (Na primeira vez, o macOS pode pedir confirmação:
clique com o botão direito → *Abrir*.)

**Alternativa offline pura:** duplo-clique em **`index.html`**. Abre direto no
navegador via `file://`, sem servidor. Tudo funciona; só a *atualização
automática* das Atualidades fica desligada (mas o conteúdo embutido aparece).

## O que tem dentro

- **Início** — capa, contagem regressiva para a viagem, atalhos.
- **8 capítulos** + Apresentação, Introdução e Conclusão, com a tipografia
  editorial da apostila, navegação lateral e "Nesta seção".
- **Busca** (tecla `/`) em todo o texto, com destaque.
- **Glossário** — 120 termos, filtro por letra e por busca; e *tooltips*: passe
  o mouse sobre um termo em chinês no texto para ver a definição.
- **Cronologia** — linha do tempo visual, do Século da Humilhação a 2026.
- **Atualidades** — camada viva: panorama atual da China, com fontes.
- **Adendo HSM Management** (Apêndice C).
- Tema claro/escuro (botão ◐ no topo).

## Atualizar as "Atualidades"

A camada viva é um retrato datado (veja a data no topo da seção). Para
atualizar, peça ao Claude: **"atualize as Atualidades da apostila"**. Ele
refaz a pesquisa, reescreve `data/live.json` e roda `python3 build.py`.

Para editar à mão: altere `data/live.json` e rode:

```bash
cd ~/apostila-china
python3 build.py
```

## Estrutura dos arquivos

```
apostila-china/
├── index.html          ← o site (autocontido — é só este arquivo p/ abrir offline)
├── abrir.command       ← launcher (duplo-clique)
├── template.html       ← molde (HTML/CSS/JS) sem os dados
├── build.py            ← injeta os dados no template → gera index.html
├── data/
│   ├── apostila.json   ← conteúdo da apostila (extraído do .docx)
│   └── live.json       ← camada de Atualidades (editável)
└── README.md
```

## Publicar online (versão com URL)

O site é estático — qualquer hospedagem de arquivos serve. Sem ferramentas
extras instaladas, o caminho mais simples é **arrastar a pasta** para um host:

- **Netlify Drop** — acesse https://app.netlify.com/drop e arraste a pasta
  `apostila-china`. Gera uma URL na hora (crie uma conta grátis para mantê-la).
- **Vercel** ou **Cloudflare Pages** — mesma ideia, conta grátis.
- **GitHub Pages** — se você usa GitHub: crie um repositório, suba os arquivos
  e ative Pages nas configurações.

Observação para a China: hosts ocidentais podem ser lentos/bloqueados no
continente. Por isso a versão **offline (`index.html`) é a principal** para a
viagem; a URL é útil para acessar de outros aparelhos e compartilhar.
