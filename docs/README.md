# Documentation Sphinx

## 📖 Consulter la documentation

Ouvrez simplement le fichier **`build/index.html`** dans votre navigateur.

C'est tout ! Aucune installation ou compilation nécessaire.

## 🔧 Pour les développeurs : Regénérer la documentation

> **Note** : Cette section est uniquement pour ceux qui veulent modifier la documentation. Les utilisateurs peuvent ignorer cette partie.

Si vous modifiez les fichiers sources dans `source/` (fichiers `.rst`), regénérez la documentation HTML :

```bash
sphinx-build -b html source build
```

## Structure

```
docs/
├── build/          # 📄 Documentation HTML générée (LIRE ICI)
│   └── index.html  # Page d'accueil de la documentation
└── source/         # 🔧 Fichiers sources .rst (pour développeurs uniquement)
```
