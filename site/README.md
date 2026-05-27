# site/ — le précis Ocarina en site statique Hugo + hugo-book

Site statique généré à partir des 144 fichiers `.md` du précis.

## Stack

- **Hugo** extended (testé sur 0.161.1)
- **hugo-book** — thème book vendoré dans `themes/hugo-book/` (sans `.git`).
  Sidebar arborescente complète toujours visible sur desktop, TOC, prev/next.
- **Pagefind** — recherche plein-texte (le fuse.js de hugo-book est désactivé,
  `BookSearch = false`). Index généré après le build, UI injectée dans la sidebar.

## Lancer

```bash
cd site

# Édition rapide (live-reload, SANS recherche : Pagefind indexe public/) :
hugo server                       # http://localhost:1313

# Build complet AVEC recherche Pagefind :
./build.sh                        # -> public/
npx -y pagefind --site public --serve   # prévisualisation avec recherche
```

`hugo server` ne sert pas la recherche : Pagefind indexe le site *construit*
(`public/`), pas le serveur en mémoire. Pour tester la recherche, passer par
`./build.sh` puis servir `public/`.

## Structure

```
hugo.toml          configuration (hugo-book, langue fr, menu)
build.sh           build de production : hugo + indexation Pagefind
content/           les 144 chapitres + _index.md — source de vérité
layouts/_markup/render-link.html        résout les liens .md inter-fichiers
layouts/_partials/docs/inject/          injection de l'UI Pagefind (head/menu/body)
themes/hugo-book/  thème vendoré
migrate.py         migration initiale vers Hugo (historique, ne pas relancer)
restore-headings.py  restauration des `# H1` dans le corps (historique)
```

`content/` **est** le précis : éditer directement les `.md` ici. Chaque fichier
porte son frontmatter (`title`, `weight`, `tags`, `series`) et son `# H1` dans
le corps. La sidebar et son ordre sont pilotés par `weight`.

## Choix de migration

- **Frontmatter** : `title` (aussi gardé comme `# H1` dans le corps, attendu par
  hugo-book), `weight` du préfixe numéroté, `date` fixe.
- **`README.md` → `_index.md`** : pages d'atterrissage de section (= nœuds de la sidebar).
- **Liens `.md`** : non réécrits dans le contenu ; résolus au build par le render-hook.
- **`tags`** : tag de chapitre + tags par mots-clés (ROP, ISTQB, CI/CD, watcher…).
- **`series`** : nom du dossier parent (frontmatter conservé).
- **Schémas ASCII** : préservés tels quels en blocs de code.
- **Recherche Pagefind** : index limité à `article.book-article` (le contenu,
  pas la sidebar) via `--root-selector`.
