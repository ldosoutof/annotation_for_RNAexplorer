#!/bin/bash

# Script de Configuration Git Complet pour annotation_for_RNAexplorer
# Utilise SSH pour l'authentification

set -e

echo "============================================"
echo "Configuration Git - annotation_for_RNAexplorer"
echo "============================================"
echo ""

# Vérifier qu'on est dans le bon répertoire
if [ ! -f "rnaseq_analysis.py" ]; then
    echo "❌ Erreur: Vous devez être dans le répertoire annotation_for_RNAexplorer"
    echo "Allez dans le bon répertoire avec: cd annotation_for_RNAexplorer"
    exit 1
fi

# Vérifier Git
if ! command -v git &> /dev/null; then
    echo "❌ Git n'est pas installé"
    echo "Installez-le avec: sudo apt install git"
    exit 1
fi

echo "✅ Vous êtes dans le bon répertoire"
echo ""

# Nettoyer un éventuel .git existant
if [ -d .git ]; then
    echo "⚠️  Un repository Git existe déjà. Suppression..."
    rm -rf .git
fi

# Configuration Git utilisateur
echo "📝 Configuration Git utilisateur"
GIT_USER=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
    echo "Configuration nécessaire..."
    read -p "Nom complet: " USER_NAME
    read -p "Email: " USER_EMAIL
    git config --global user.name "$USER_NAME"
    git config --global user.email "$USER_EMAIL"
    echo "✅ Configuration sauvegardée"
else
    echo "Utilisateur: $GIT_USER <$GIT_EMAIL>"
fi

echo ""

# Vérifier SSH
echo "🔐 Vérification de la configuration SSH"

if [ ! -f ~/.ssh/id_ed25519.pub ] && [ ! -f ~/.ssh/id_rsa.pub ]; then
    echo ""
    echo "❌ Aucune clé SSH trouvée"
    echo ""
    echo "Vous devez configurer SSH pour GitHub. Voici comment:"
    echo ""
    echo "1️⃣  Générer une clé SSH:"
    echo "   ssh-keygen -t ed25519 -C \"votre-email@example.com\""
    echo "   (Appuyez sur Entrée pour accepter les valeurs par défaut)"
    echo ""
    echo "2️⃣  Démarrer l'agent SSH:"
    echo "   eval \"\$(ssh-agent -s)\""
    echo "   ssh-add ~/.ssh/id_ed25519"
    echo ""
    echo "3️⃣  Copier votre clé publique:"
    echo "   cat ~/.ssh/id_ed25519.pub"
    echo ""
    echo "4️⃣  Ajouter la clé sur GitHub:"
    echo "   - Allez sur https://github.com/settings/keys"
    echo "   - Cliquez sur 'New SSH key'"
    echo "   - Collez votre clé publique"
    echo "   - Cliquez sur 'Add SSH key'"
    echo ""
    echo "5️⃣  Tester la connexion:"
    echo "   ssh -T git@github.com"
    echo ""
    echo "Puis relancez ce script."
    exit 1
fi

# Tester la connexion SSH
echo "Test de connexion à GitHub..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ Connexion SSH à GitHub réussie!"
else
    echo ""
    echo "⚠️  La connexion SSH à GitHub a échoué"
    echo ""
    echo "Vérifiez que vous avez bien ajouté votre clé SSH sur GitHub:"
    echo "1. Affichez votre clé: cat ~/.ssh/id_ed25519.pub"
    echo "2. Allez sur: https://github.com/settings/keys"
    echo "3. Ajoutez votre clé"
    echo "4. Testez: ssh -T git@github.com"
    echo ""
    read -p "Voulez-vous continuer quand même? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Vérifier que le repo existe sur GitHub
echo "📦 Vérification du repository GitHub"
echo ""
echo "Assurez-vous que le repository existe sur GitHub:"
echo "   https://github.com/ldosoutof/annotation_for_RNAexplorer"
echo ""
echo "Si ce n'est pas le cas:"
echo "1. Allez sur https://github.com/new"
echo "2. Nom: annotation_for_RNAexplorer"
echo "3. Description: Pipeline d'annotation pour FRASER2 et OUTRIDER"
echo "4. NE PAS cocher 'Initialize with README'"
echo "5. Cliquez sur 'Create repository'"
echo ""
read -p "Le repository existe-t-il sur GitHub? [y/N] " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Créez d'abord le repository sur GitHub, puis relancez ce script."
    exit 0
fi

echo ""
echo "🚀 Initialisation du repository Git local"

# Initialiser Git
git init
echo "✅ Repository Git initialisé"

# Créer .gitattributes
cat > .gitattributes << 'EOF'
* text=auto
*.py text eol=lf
*.sh text eol=lf
*.md text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.tsv binary
*.tab binary
*.gtf binary
EOF
echo "✅ .gitattributes créé"

# Ajouter tous les fichiers
git add .
echo "✅ Fichiers ajoutés"

# Créer le commit initial
git commit -m "Initial commit: Annotation for RNAexplorer

Pipeline d'annotation pour FRASER2 et OUTRIDER avec support RNAexplorer.

Features:
- FRASER2 and OUTRIDER annotation
- GTF annotation integration
- PanelApp and gnomAD support
- ZIP file auto-detection with interactive mode
- Variant filtering and prioritization
- TSV export
- Comprehensive documentation"

echo "✅ Commit initial créé"

# Ajouter le remote
git remote add origin git@github.com:ldosoutof/annotation_for_RNAexplorer.git
echo "✅ Remote ajouté (SSH)"

# Renommer la branche en main
git branch -M main
echo "✅ Branche renommée en 'main'"

# Push
echo ""
echo "📤 Push vers GitHub..."
if git push -u origin main; then
    echo ""
    echo "============================================"
    echo "✅ SUCCESS! Repository poussé sur GitHub"
    echo "============================================"
    echo ""
    echo "Votre repository est maintenant disponible:"
    echo "   https://github.com/ldosoutof/annotation_for_RNAexplorer"
    echo ""
    echo "Prochaines étapes:"
    echo "1. Visitez votre repository sur GitHub"
    echo "2. Ajoutez une description"
    echo "3. Ajoutez des topics (ex: bioinformatics, rnaseq, fraser)"
    echo "4. Renommez README_GITHUB.md en README.md pour avoir les badges"
    echo ""
else
    echo ""
    echo "❌ Le push a échoué"
    echo ""
    echo "Vérifications:"
    echo "1. Le repository existe-t-il? https://github.com/ldosoutof/annotation_for_RNAexplorer"
    echo "2. SSH fonctionne-t-il? Testez: ssh -T git@github.com"
    echo "3. Avez-vous les droits d'écriture?"
    echo ""
    exit 1
fi

# Proposer de créer un tag
echo ""
read -p "Créer un tag v1.0.0? [Y/n] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    git tag -a v1.0.0 -m "First stable release

Features:
- Complete FRASER2/OUTRIDER annotation pipeline
- ZIP auto-detection
- Comprehensive annotation support
- Full documentation"
    
    git push origin v1.0.0
    echo "✅ Tag v1.0.0 créé et poussé"
    echo ""
    echo "Créez une release sur GitHub:"
    echo "   https://github.com/ldosoutof/annotation_for_RNAexplorer/releases/new?tag=v1.0.0"
fi

echo ""
echo "🎉 Configuration Git terminée!"
echo ""
echo "Commandes Git utiles:"
echo "  git status          - Voir l'état du repository"
echo "  git add <fichier>   - Ajouter des fichiers"
echo "  git commit -m 'msg' - Créer un commit"
echo "  git push            - Pousser vers GitHub"
echo "  git pull            - Récupérer depuis GitHub"
echo ""
