"""Trouve où télécharger la build courante d'un paquet Android, sans rien
télécharger. Imprime :  <source>\t<versionCode>\t<url>\t<nom de fichier>

C'est la moitié BON MARCHÉ du robot : connaître la version disponible coûte
~100 Ko, l'archive en coûte 100 à 200 Mo. On compare d'abord, on ne transfère
que si ça a bougé.

DEUX SOURCES, et c'est délibéré : une seule source qui tombe, c'est une panne à
surveiller ; deux sources indépendantes, c'est une dégradation silencieuse.
Mesuré le 11/08/2026, et c'est ce qui dicte l'ordre :

- pureapk (l'API que le launcher utilise déjà) répond pour les TROIS paquets,
  Vietnam compris, et prend le paquet en simple paramètre : rien à découvrir
  quand on ajoute une région. C'est la primaire.
- apkcombo sert le global et le PBE, mais PAS le vietnamien (302 vers la fiche :
  le miroir n'a pas le fichier). C'est le repli.

IDENTITÉ COMMUNE AUX DEUX SOURCES : le versionCode, l'entier que les deux
exposent (jeton `<paquet>_<versionCode>_<hash>` chez pureapk, chemin
`<versionCode>.<sha>.apk[s]` chez apkcombo). Comparer des chaînes de version
lisibles à la place ferait republier 190 Mo à chaque bascule de source, pour un
fichier identique.

LE PIÈGE de pureapk, déjà payé une fois : sans les deux en-têtes, l'API répond
200 avec un corps vide de 36 octets. Un paquet qui n'existe pas répond pareil.
Le succès se juge sur le CORPS, jamais sur le code HTTP.
"""
import re
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
TIMEOUT = 40


def _get(url: str, headers: dict) -> bytes:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def from_pureapk(package: str):
    """La source primaire. Renvoie (versionCode, url, nom) ou None."""
    url = ("https://api.pureapk.com/m/v3/cms/app_version?hl=en-US&package_name="
           + urllib.parse.quote(package))
    # La version du client mobile que l'API attend. Absente, corps vide.
    body = _get(url, {"x-cv": "3172501", "x-sv": "29", "User-Agent": UA})
    if len(body) < 1024:
        return None

    text = body.decode("latin-1")
    # Réponse protobuf : les entrées sont triées de la plus récente à la plus
    # ancienne et chaque lien suit un marqueur de format. DEUX marqueurs, pas
    # un : le PBE et le vietnamien arrivent en `XAPKJ` (bundle avec splits), le
    # TFT global en `APKJ` (build universelle). Ne connaître que `XAPKJ` — ce
    # que fait `Sideload.resolve` dans l'app, qui n'a jamais servi qu'au PBE —
    # rendrait la source primaire aveugle au paquet global. Le jeu de caractères
    # est restreint exprès, pour que la capture s'arrête au champ binaire suivant.
    match = re.search(r"X?APKJ..(https?://[A-Za-z0-9:/?&=._%~+-]+)", text)
    if not match:
        return None
    link = match.group(1)

    # Le jeton du chemin est un base64url de `<paquet>_<versionCode>_<hash>`.
    # Il sert à DEUX choses : lire le versionCode sans télécharger, et vérifier
    # que l'API répond bien pour le paquet demandé et pas pour un homonyme.
    bundle = "/XAPK/" in link
    token = re.split(r"/X?APK/", link)[-1].split("?")[0]
    try:
        import base64
        decoded = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4)).decode("utf-8")
    except Exception:
        return None
    parts = decoded.rsplit("_", 2)
    if len(parts) != 3 or parts[0] != package or not parts[1].isdigit():
        return None
    return int(parts[1]), link, package + (".xapk" if bundle else ".apk")


def from_apkcombo(package: str):
    """Le repli. Le slug de l'URL n'a pas d'importance : le site résout par
    paquet et redirige vers la bonne fiche. Renvoie (versionCode, url, nom)."""
    page_url = f"https://apkcombo.com/x/{package}/download/apk"
    page = _get(page_url, {"User-Agent": UA}).decode("utf-8", "replace")
    import html
    page = html.unescape(page)

    best = None
    for encoded in set(re.findall(r"/r2\?u=([^\"'\s<>]+)", page)):
        link = urllib.parse.unquote(encoded)
        # `.apk` (build universelle, cas du TFT global) autant que `.apks`
        # (bundle avec splits, cas du PBE) : le pipeline sait ouvrir les deux.
        match = re.search(r"/" + re.escape(package) + r"/[^/]+/(\d+)\.[0-9a-f]{40}\.(apks?|xapk)", link)
        if not match:
            continue
        code = int(match.group(1))
        if best is None or code > best[0]:
            best = (code, link, match.group(2))
    if best is None:
        return None

    code, link, extension = best
    query = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
    disposition = query.get("response-content-disposition", [""])[0]
    match = re.search(r'filename="?([^"]+)"?', disposition)
    return code, link, (match.group(1) if match else f"{package}.{extension}")


SOURCES = (("pureapk", from_pureapk), ("apkcombo", from_apkcombo))


def resolve(package: str):
    problems = []
    for name, lookup in SOURCES:
        try:
            found = lookup(package)
        except Exception as error:              # réseau, TLS, page illisible
            problems.append(f"{name}: {error}")
            continue
        if found:
            return (name,) + found
        problems.append(f"{name}: rien pour {package}")
    raise SystemExit("aucune source n'a la build : " + " | ".join(problems))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: title_source.py <nom.du.paquet>")
    source, code, link, name = resolve(sys.argv[1])
    print("\t".join((source, str(code), link, name)))
