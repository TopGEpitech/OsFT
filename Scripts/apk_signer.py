"""Imprime l'empreinte SHA-256 du certificat qui a SIGNÉ un APK.

Pourquoi ce fichier existe : le robot de rafraîchissement republie des APK
récupérés chez un miroir tiers. Le seul contrôle qui rende ce montage sûr sans
surveillance humaine est de vérifier que le fichier est bien signé par l'éditeur
attendu — un miroir compromis, une redirection détournée ou un simple homonyme de
paquet produisent un certificat DIFFÉRENT, et la publication s'arrête là.

Pourquoi pas `apksigner` : il vient des build-tools du SDK Android, absent de ce
Mac et pas garanti sur un runner. Un contrôle de sécurité qui « se saute quand
l'outil manque » ne protège de rien. Ce lecteur est donc autonome : Python
standard, aucune dépendance.

Ce qui est lu : le bloc de signature APK (schémas v2 et v3), placé entre les
entrées et le répertoire central du ZIP. Les APK modernes de Riot n'ont PLUS de
signature v1 (aucun META-INF/*.RSA, mesuré sur le client VN), donc lire le ZIP
comme un JAR ne donne rien : il faut ce bloc.

Usage : python3 apk_signer.py base.apk   ->   "a1b2c3…" (64 caractères hex)
"""
import hashlib
import struct
import sys

APK_SIG_BLOCK_MAGIC = b"APK Sig Block 42"
SCHEME_V2 = 0x7109871A
SCHEME_V3 = 0xF05368C0


def _eocd_central_dir_offset(data: bytes) -> int:
    """Offset du répertoire central, lu depuis l'End Of Central Directory."""
    # L'EOCD fait 22 octets plus un commentaire d'au plus 65535 : on le cherche
    # depuis la fin, sans jamais scanner tout le fichier.
    tail = data[-(22 + 65535):]
    index = tail.rfind(b"PK\x05\x06")
    if index < 0:
        raise SystemExit("pas un ZIP : End Of Central Directory introuvable")
    return struct.unpack_from("<I", tail, index + 16)[0]


def _signing_block(data: bytes) -> bytes:
    central = _eocd_central_dir_offset(data)
    if data[central - 16:central] != APK_SIG_BLOCK_MAGIC:
        raise SystemExit("APK sans bloc de signature v2/v3")
    size = struct.unpack_from("<Q", data, central - 24)[0]
    start = central - 8 - size
    if start < 0 or struct.unpack_from("<Q", data, start)[0] != size:
        raise SystemExit("bloc de signature incohérent (fichier tronqué ?)")
    return data[start + 8:central - 24]


def _pairs(block: bytes):
    """Les paires (identifiant, valeur) du bloc, dans l'ordre."""
    offset = 0
    while offset + 12 <= len(block):
        length = struct.unpack_from("<Q", block, offset)[0]
        ident = struct.unpack_from("<I", block, offset + 8)[0]
        yield ident, block[offset + 12:offset + 8 + length]
        offset += 8 + length


def _first_certificate(value: bytes) -> bytes:
    """Le certificat du premier signataire d'un bloc v2/v3.

    Emboîtement, chaque niveau préfixé de sa longueur sur 4 octets :
    signataires -> signataire -> données signées -> [empreintes][certificats].
    """
    def chunk(buffer: bytes, offset: int):
        length = struct.unpack_from("<I", buffer, offset)[0]
        return buffer[offset + 4:offset + 4 + length], offset + 4 + length

    signers, _ = chunk(value, 0)
    signer, _ = chunk(signers, 0)
    signed_data, _ = chunk(signer, 0)
    _digests, after_digests = chunk(signed_data, 0)      # empreintes : ignorées
    certificates, _ = chunk(signed_data, after_digests)
    certificate, _ = chunk(certificates, 0)
    return certificate


def fingerprint(path: str) -> str:
    with open(path, "rb") as handle:
        data = handle.read()
    block = _signing_block(data)
    # v3 d'abord : c'est le schéma courant, et il porte le certificat en vigueur
    # après une éventuelle rotation de clé.
    for wanted in (SCHEME_V3, SCHEME_V2):
        for ident, value in _pairs(block):
            if ident == wanted:
                return hashlib.sha256(_first_certificate(value)).hexdigest()
    raise SystemExit("aucun bloc v2/v3 dans la signature")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: apk_signer.py <fichier.apk>")
    print(fingerprint(sys.argv[1]))
