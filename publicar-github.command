#!/bin/bash
# Duplo-clique para publicar/atualizar o site no GitHub (Pages).
# Pré-requisitos (feitos UMA vez): (1) adicionar a chave SSH ao GitHub,
# (2) criar um repositório vazio no GitHub. Veja o README/instruções.
cd "$(dirname "$0")"
echo "Publicar Apostila China no GitHub Pages"
echo "----------------------------------------"

# garante que o agente SSH conheça a chave
ssh-add ~/.ssh/id_ed25519 >/dev/null 2>&1

if ! git remote | grep -q origin; then
  echo "Qual é o seu usuário do GitHub? (ex: brunainfurna)"
  read -r GHUSER
  echo "Qual o nome do repositório que você criou? (ex: apostila-china)"
  read -r GHREPO
  git remote add origin "git@github.com:${GHUSER}/${GHREPO}.git"
  echo "Remote: git@github.com:${GHUSER}/${GHREPO}.git"
fi

git add -A
git commit -m "Atualiza site" >/dev/null 2>&1
echo "Enviando para o GitHub..."
if git push -u origin main; then
  ORIGIN=$(git remote get-url origin)
  USER=$(echo "$ORIGIN" | sed -E 's#.*:([^/]+)/.*#\1#')
  REPO=$(echo "$ORIGIN" | sed -E 's#.*/([^/.]+)(\.git)?#\1#')
  echo ""
  echo "✅ Enviado!"
  echo "Agora ative o GitHub Pages (uma vez só):"
  echo "  https://github.com/${USER}/${REPO}/settings/pages"
  echo "  Em 'Branch', escolha: main  /  (root)  → Save"
  echo ""
  echo "Em ~1 minuto o site estará em:"
  echo "  https://${USER}.github.io/${REPO}/"
else
  echo "❌ Push falhou. Confira se a chave SSH foi adicionada ao GitHub"
  echo "   e se o repositório existe e está vazio."
fi
echo ""
echo "Pressione Enter para fechar."
read -r _
