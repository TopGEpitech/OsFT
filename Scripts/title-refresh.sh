#!/bin/sh
# Prépare l'archive installable d'UN paquet Android, au format exact que le
# launcher sait ouvrir. Ne publie RIEN : écrit trois fichiers et s'arrête.
#
# Usage : ./Scripts/title-refresh.sh <paquet> <slug> [dossier_sortie] [empreinte_attendue]
# Sortie : <out>/<slug>-splits.zip     archive base + splits
#          <out>/<slug>-version.txt    versionCode (entier, l'identité comparable)
#          <out>/<slug>-cert.txt       empreinte SHA-256 du certificat signataire
#
# Ce script remplace `pbe-refresh.sh`, qui ne savait faire qu'un seul paquet.
# Trois choses ont changé, chacune mesurée le 11/08/2026 :
#
# 1. AUCUN SPLIT N'EST FILTRÉ. L'ancien script gardait `en` + `mdpi` en disant
#    que jeter les autres langues divisait la taille. C'est faux : sur le XAPK
#    du PBE, 20 splits pèsent 192,7 Mo dont 192,0 pour base + arm64_v8a. Les 18
#    autres (17 langues + la densité) font 618 Ko, soit 0,3 %. Filtrer ne
#    gagnait rien et coûtait deux noms de fichiers en dur.
# 2. ET CES NOMS EN DUR ÉTAIENT DÉJÀ UNE PANNE. Le XAPK du PBE servi
#    aujourd'hui contient `config.xxhdpi.apk`, pas `config.mdpi.apk` : l'ancien
#    script échouait sur son `unzip` à la prochaine build publiée par Riot, donc
#    le robot serait tombé tout seul sans que rien n'ait changé chez nous. Ici
#    on prend ce qui est là, quel que soit son nom.
# 3. LA SIGNATURE EST VÉRIFIÉE. C'est ce qui permet de ne plus surveiller : on
#    republie un binaire pris chez un tiers, donc la seule question qui compte
#    est « est-il signé par l'éditeur attendu ? ». Empreinte différente =
#    on ne publie pas, la version précédente reste en ligne.
set -eu

PKG="${1:?usage: title-refresh.sh <paquet> <slug> [sortie] [empreinte]}"
SLUG="${2:?slug manquant}"
OUT="${3:-dist/titles}"
EXPECT="${4:-}"

HERE=$(dirname "$0")
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"

UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
# Plancher de taille. Le piège documenté est l'installeur maison du miroir,
# ~15 Mo, servi à la place du jeu ; les vrais clients font 100 à 200 Mo.
FLOOR=${FLOOR:-40000000}

line=$(python3 "$HERE/title_source.py" "$PKG")
source=$(printf '%s' "$line" | cut -f1)
code=$(printf '%s' "$line" | cut -f2)
url=$(printf '%s' "$line" | cut -f3)
name=$(printf '%s' "$line" | cut -f4)
echo "paquet  : $PKG"
echo "source  : $source"
echo "version : $code"

archive="$WORK/$name"
curl -sfL --max-time 1800 -A "$UA" -o "$archive" "$url"

size=$(wc -c < "$archive" | tr -d ' ')
echo "taille  : $size octets"
[ "$size" -ge "$FLOOR" ] || {
  echo "ABANDON : $size octets, sous le plancher de $FLOOR (ce n'est pas le jeu)." >&2
  exit 1
}

# --- Étaler le contenu : conteneur multi-APK, ou APK simple ---------------
staging="$WORK/staging"
mkdir -p "$staging"
case "$name" in
  *.apk)
    cp "$archive" "$staging/base.apk"
    ;;
  *)
    unzip -q "$archive" -d "$staging"
    # Le paquet annoncé par le conteneur doit être celui qu'on a demandé : un
    # miroir qui range un autre jeu sous ce nom est arrêté ici, avant la
    # signature, avec un message qui dit lequel.
    if [ -f "$staging/manifest.json" ]; then
      declared=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["package_name"])' \
        "$staging/manifest.json")
      [ "$declared" = "$PKG" ] || {
        echo "ABANDON : l'archive déclare $declared, pas $PKG." >&2
        exit 1
      }
    fi
    # L'APK de base porte le nom du paquet ; tout le reste est un split, gardé
    # tel quel. `ADB.install(splits:)` choisit sa base sur la sous-chaîne
    # « base », d'où le renommage : sans lui l'ordre serait celui, arbitraire,
    # de l'énumérateur de fichiers.
    [ -f "$staging/$PKG.apk" ] || {
      echo "ABANDON : pas de $PKG.apk dans l'archive." >&2
      exit 1
    }
    mv "$staging/$PKG.apk" "$staging/base.apk"
    for split in "$staging"/config.*.apk; do
      [ -f "$split" ] || continue
      mv "$split" "$staging/split_$(basename "$split")"
    done
    ;;
esac

# --- Le contrôle qui rend l'automatisation sûre ---------------------------
cert=$(python3 "$HERE/apk_signer.py" "$staging/base.apk")
echo "signé   : $cert"
if [ -n "$EXPECT" ] && [ "$cert" != "$EXPECT" ]; then
  echo "ABANDON : signataire inattendu." >&2
  echo "  attendu : $EXPECT" >&2
  echo "  obtenu  : $cert" >&2
  exit 1
fi
[ -n "$EXPECT" ] || echo "ATTENTION : aucune empreinte de référence fournie, celle-ci est prise pour référence."

# Stocké sans compression (-0) : des APK sont déjà des ZIP compressés, les
# recompresser coûte du temps de robot pour zéro octet gagné.
rm -f "$OUT/$SLUG-splits.zip"
find "$staging" -name '*.apk' -print0 | xargs -0 zip -q -X -0 -j "$OUT/$SLUG-splits.zip"
printf '%s\n' "$code" > "$OUT/$SLUG-version.txt"
printf '%s\n' "$cert" > "$OUT/$SLUG-cert.txt"

# Garde-fou de sortie : une archive sans APK de base installerait un paquet vide.
unzip -l "$OUT/$SLUG-splits.zip" | grep -q 'base.apk' || {
  echo "ABANDON : pas d'APK de base dans l'archive produite." >&2
  exit 1
}

echo "archive : $OUT/$SLUG-splits.zip ($(wc -c < "$OUT/$SLUG-splits.zip") octets, $(unzip -l "$OUT/$SLUG-splits.zip" | grep -c '\.apk$') APK)"
