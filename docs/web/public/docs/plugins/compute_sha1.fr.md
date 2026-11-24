
# SHA-1 hashes

Écrit le SHA-1 de chaque zip du dossier de build dans un seul fichier JSON, pour vérifier un téléchargement ou savoir quel pack a changé.

Il tourne dans le template `basic` sous le nom `stewbeet.plugins.compute_sha1` et dans le template `extensive` sous le nom `stewbeet.plugins.compute_sha1.silent`, qui masque sa sortie de log. Il a besoin de `output` dans `beet.yml`. [Source](https://github.com/Stoupy51/StewBeet/blob/main/python_package/stewbeet/plugins/compute_sha1/__init__.py)

## Ce que ce plugin écrit

- `sha1_hashes.json` dans le dossier `output` : une clé par zip, triées par nom, dont la valeur est le SHA-1 en hexadécimal.

```json
{
  "StardustFragment_datapack.zip": "...",
  "StardustFragment_resource_pack.zip": "..."
}
```

Chaque `.zip` du dossier est haché, ceux en `_with_libs.zip` compris.

## Limites

- Le plugin hache ce qui est dans le dossier au moment où il tourne. Placez-le après [Zip archives](archive.fr.md) et le [Smithed Weld merge](merge_smithed_weld.fr.md) dans le `pipeline`, sinon leurs zips manquent ou sont périmés.
- Un zip laissé dans `output` par un build précédent, comme un zip d'avant le renommage du projet, est haché lui aussi.

## Pour continuer

- [Publier les releases automatiquement](../6_continuous_delivery/fr.md) : publier le build.

