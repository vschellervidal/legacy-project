"""Tests pour l'écriture GWB minimale (Issues #22, #23)."""

from __future__ import annotations

import json
from datetime import date as date_type
from pathlib import Path

from geneweb.domain.models import Famille, Individu, Sexe
from geneweb.io.gwb import load_gwb_minimal, write_gwb_minimal


def test_write_gwb_minimal_basic(tmp_path: Path) -> None:
    """Test d'écriture basique avec quelques individus."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
        Individu(id="I003", nom="UNKNOWN", prenom="X", sexe=Sexe.X),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    index_path = tmp_path / "index.json"
    assert index_path.exists()

    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(data) == 3
    assert data[0]["id"] == "I001" and data[0]["nom"] == "DUPONT" and data[0]["prenom"] == "Jean"
    assert data[0]["sexe"] == "M"
    assert data[1]["sexe"] == "F"
    assert data[2]["sexe"] == "X"


def test_write_gwb_minimal_round_trip(tmp_path: Path) -> None:
    """Test round-trip : écriture puis lecture doit redonner les mêmes données."""
    individus_initiaux = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
        Individu(id="I003", nom="SMITH", prenom="Bob", sexe=Sexe.X),
    ]
    familles: list[Famille] = []

    # Écrire
    write_gwb_minimal(individus_initiaux, familles, tmp_path)

    # Relire
    individus_lus, _, _ = load_gwb_minimal(tmp_path)

    # Vérifier la parité
    assert len(individus_lus) == len(individus_initiaux)
    for ind_initial, ind_lu in zip(individus_initiaux, individus_lus, strict=True):
        assert ind_lu.id == ind_initial.id
        assert ind_lu.nom == ind_initial.nom
        assert ind_lu.prenom == ind_initial.prenom
        assert ind_lu.sexe == ind_initial.sexe


def test_write_gwb_minimal_partial_data(tmp_path: Path) -> None:
    """Test avec des données partielles (certains champs None)."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom=None, sexe=Sexe.M),
        Individu(id="I002", nom=None, prenom="Anne", sexe=None),
        Individu(id="I003", nom="SMITH", prenom="Bob", sexe=Sexe.F),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    individus_lus, _, _ = load_gwb_minimal(tmp_path)
    assert len(individus_lus) == 3
    assert individus_lus[0].id == "I001" and individus_lus[0].nom == "DUPONT"
    assert individus_lus[0].prenom is None
    assert individus_lus[0].sexe == Sexe.M
    assert individus_lus[1].id == "I002" and individus_lus[1].nom is None
    assert individus_lus[1].prenom == "Anne"
    assert individus_lus[1].sexe is None


def test_write_gwb_minimal_empty_id_ignored(tmp_path: Path) -> None:
    """Test que les individus sans ID valide sont ignorés."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="", nom="INVALID", prenom="X", sexe=Sexe.F),  # ID vide -> ignoré
        Individu(id="   ", nom="INVALID2", prenom="Y", sexe=Sexe.M),  # ID vide -> ignoré
        Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    individus_lus, _, _ = load_gwb_minimal(tmp_path)
    assert len(individus_lus) == 2
    assert individus_lus[0].id == "I001"
    assert individus_lus[1].id == "I002"


def test_write_gwb_minimal_creates_directory(tmp_path: Path) -> None:
    """Test que la fonction crée le répertoire s'il n'existe pas."""
    output_dir = tmp_path / "new_gwb"
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
    ]
    familles: list[Famille] = []

    assert not output_dir.exists()
    write_gwb_minimal(individus, familles, output_dir)

    assert output_dir.exists()
    assert (output_dir / "index.json").exists()


def test_write_gwb_minimal_with_familles_ignored(tmp_path: Path) -> None:
    """Test que les familles sont maintenant sérialisées (Issue #24)."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
    ]
    familles = [
        Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=["I003"]),
    ]

    write_gwb_minimal(individus, familles, tmp_path)

    # Vérifier que les familles sont maintenant sérialisées (Issue #24)
    data = json.loads((tmp_path / "index.json").read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert len(data["individus"]) == 1
    assert len(data["familles"]) == 1
    assert data["individus"][0]["id"] == "I001"
    assert data["familles"][0]["id"] == "F001"


def test_write_gwb_minimal_unicode(tmp_path: Path) -> None:
    """Test avec des caractères Unicode."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="I002", nom="MÜLLER", prenom="François", sexe=Sexe.M),
        Individu(id="I003", nom="O'CONNOR", prenom="Mary", sexe=Sexe.F),
        Individu(id="I004", nom="GARCÍA", prenom="José", sexe=Sexe.M),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    # Vérifier round-trip avec Unicode
    individus_lus, _, _ = load_gwb_minimal(tmp_path)
    assert len(individus_lus) == 4
    assert individus_lus[1].nom == "MÜLLER"
    assert individus_lus[2].nom == "O'CONNOR"
    assert individus_lus[3].nom == "GARCÍA"


def test_write_gwb_minimal_with_events(tmp_path: Path) -> None:
    """Test d'écriture avec événements vitaux (BIRT/DEAT) - Issue #23."""
    individus = [
        Individu(
            id="I001",
            nom="DUPONT",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date_type(1990, 1, 15),
            lieu_naissance="Paris, France",
            date_deces=date_type(2050, 12, 31),
            lieu_deces="Lyon, France",
        ),
        Individu(
            id="I002",
            nom="MARTIN",
            prenom="Anne",
            sexe=Sexe.F,
            date_naissance=date_type(1995, 6, 20),
            lieu_naissance="Marseille",
        ),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    index_path = tmp_path / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert len(data) == 2

    # Vérifier premier individu avec tous les événements
    assert data[0]["id"] == "I001"
    assert data[0]["date_naissance"] == "1990-01-15"
    assert data[0]["lieu_naissance"] == "Paris, France"
    assert data[0]["date_deces"] == "2050-12-31"
    assert data[0]["lieu_deces"] == "Lyon, France"

    # Vérifier deuxième individu avec seulement BIRT
    assert data[1]["id"] == "I002"
    assert data[1]["date_naissance"] == "1995-06-20"
    assert data[1]["lieu_naissance"] == "Marseille"
    assert "date_deces" not in data[1]
    assert "lieu_deces" not in data[1]


def test_write_gwb_minimal_round_trip_with_events(tmp_path: Path) -> None:
    """Test round-trip avec événements vitaux (Issue #23)."""
    individus_initiaux = [
        Individu(
            id="I001",
            nom="DUPONT",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date_type(1990, 1, 15),
            lieu_naissance="Paris, France",
            date_deces=date_type(2050, 12, 31),
            lieu_deces="Lyon, France",
        ),
        Individu(
            id="I002",
            nom="MARTIN",
            prenom="Anne",
            sexe=Sexe.F,
            date_naissance=date_type(1995, 6, 20),
            lieu_naissance="Marseille",
        ),
    ]
    familles: list[Famille] = []

    # Écrire
    write_gwb_minimal(individus_initiaux, familles, tmp_path)

    # Relire
    individus_lus, _, _ = load_gwb_minimal(tmp_path)

    # Vérifier la parité complète (y compris événements)
    assert len(individus_lus) == len(individus_initiaux)
    for ind_initial, ind_lu in zip(individus_initiaux, individus_lus, strict=True):
        assert ind_lu.id == ind_initial.id
        assert ind_lu.nom == ind_initial.nom
        assert ind_lu.prenom == ind_initial.prenom
        assert ind_lu.sexe == ind_initial.sexe
        assert ind_lu.date_naissance == ind_initial.date_naissance
        assert ind_lu.lieu_naissance == ind_initial.lieu_naissance
        assert ind_lu.date_deces == ind_initial.date_deces
        assert ind_lu.lieu_deces == ind_initial.lieu_deces


def test_write_gwb_minimal_partial_events(tmp_path: Path) -> None:
    """Test avec événements partiels (seulement date ou seulement lieu)."""
    individus = [
        Individu(
            id="I001",
            nom="DUPONT",
            prenom="Jean",
            sexe=Sexe.M,
            date_naissance=date_type(1990, 1, 15),
            lieu_naissance=None,
        ),
        Individu(
            id="I002",
            nom="MARTIN",
            prenom="Anne",
            sexe=Sexe.F,
            date_naissance=None,
            lieu_naissance="Lyon",
        ),
        Individu(
            id="I003",
            nom="SMITH",
            prenom="Bob",
            sexe=Sexe.M,
            date_deces=date_type(2020, 5, 10),
            lieu_deces=None,
        ),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    individus_lus, _, _ = load_gwb_minimal(tmp_path)
    assert len(individus_lus) == 3

    assert individus_lus[0].date_naissance == date_type(1990, 1, 15)
    assert individus_lus[0].lieu_naissance is None

    assert individus_lus[1].date_naissance is None
    assert individus_lus[1].lieu_naissance == "Lyon"

    assert individus_lus[2].date_deces == date_type(2020, 5, 10)
    assert individus_lus[2].lieu_deces is None


def test_load_gwb_minimal_with_events_retrocompat(tmp_path: Path) -> None:
    """Test que load_gwb_minimal reste rétrocompatible avec anciens fichiers sans événements."""
    # Format ancien (Issue #22) sans événements
    data = [
        {"id": "I001", "nom": "DUPONT", "prenom": "Jean", "sexe": "M"},
        {"id": "I002", "nom": "MARTIN", "prenom": "Anne", "sexe": "F"},
    ]
    (tmp_path / "index.json").write_text(json.dumps(data), encoding="utf-8")

    individus_lus, familles_lues, _ = load_gwb_minimal(tmp_path)

    assert len(individus_lus) == 2
    assert len(familles_lues) == 0
    assert individus_lus[0].id == "I001"
    assert individus_lus[0].nom == "DUPONT"
    assert individus_lus[0].date_naissance is None
    assert individus_lus[0].lieu_naissance is None


def test_write_gwb_minimal_with_familles(tmp_path: Path) -> None:
    """Test d'écriture avec familles (Issue #24)."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
        Individu(id="I003", nom="DUPONT", prenom="Pierre", sexe=Sexe.M),
    ]
    familles = [
        Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=["I003"]),
    ]

    write_gwb_minimal(individus, familles, tmp_path)

    index_path = tmp_path / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))

    # Vérifier que c'est le format complet (objet)
    assert isinstance(data, dict)
    assert "individus" in data
    assert "familles" in data

    assert len(data["individus"]) == 3
    assert len(data["familles"]) == 1

    # Vérifier la famille
    fam = data["familles"][0]
    assert fam["id"] == "F001"
    assert fam["pere_id"] == "I001"
    assert fam["mere_id"] == "I002"
    assert fam["enfants_ids"] == ["I003"]


def test_write_gwb_minimal_round_trip_with_familles(tmp_path: Path) -> None:
    """Test round-trip avec familles (Issue #24)."""
    individus_initiaux = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
        Individu(id="I003", nom="DUPONT", prenom="Pierre", sexe=Sexe.M),
    ]
    familles_initiales = [
        Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=["I003"]),
        Famille(id="F002", pere_id="I001", mere_id=None, enfants_ids=[]),
    ]

    # Écrire
    write_gwb_minimal(individus_initiaux, familles_initiales, tmp_path)

    # Relire
    individus_lus, familles_lues, _ = load_gwb_minimal(tmp_path)

    # Vérifier les individus
    assert len(individus_lus) == len(individus_initiaux)
    for ind_initial, ind_lu in zip(individus_initiaux, individus_lus, strict=True):
        assert ind_lu.id == ind_initial.id
        assert ind_lu.nom == ind_initial.nom

    # Vérifier les familles
    assert len(familles_lues) == len(familles_initiales)
    for fam_initial, fam_lu in zip(familles_initiales, familles_lues, strict=True):
        assert fam_lu.id == fam_initial.id
        assert fam_lu.pere_id == fam_initial.pere_id
        assert fam_lu.mere_id == fam_initial.mere_id
        assert fam_lu.enfants_ids == fam_initial.enfants_ids


def test_write_gwb_minimal_format_simple_sans_familles(tmp_path: Path) -> None:
    """Test que sans familles, on utilise le format simple (rétrocompatibilité)."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path)

    index_path = tmp_path / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))

    # Vérifier que c'est le format simple (liste)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "I001"


def test_load_gwb_minimal_format_complet(tmp_path: Path) -> None:
    """Test que load_gwb_minimal lit correctement le format complet."""
    data = {
        "individus": [
            {"id": "I001", "nom": "DUPONT", "prenom": "Jean", "sexe": "M"},
        ],
        "familles": [
            {"id": "F001", "pere_id": "I001", "mere_id": "I002", "enfants_ids": ["I003"]},
        ],
    }
    (tmp_path / "index.json").write_text(json.dumps(data), encoding="utf-8")

    individus_lus, familles_lues, _ = load_gwb_minimal(tmp_path)

    assert len(individus_lus) == 1
    assert len(familles_lues) == 1
    assert individus_lus[0].id == "I001"
    assert familles_lues[0].id == "F001"
    assert familles_lues[0].pere_id == "I001"
    assert familles_lues[0].mere_id == "I002"
    assert familles_lues[0].enfants_ids == ["I003"]


def test_write_gwb_minimal_famille_partielle(tmp_path: Path) -> None:
    """Test avec familles partielles (sans père, sans mère, sans enfants)."""
    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M),
        Individu(id="I002", nom="MARTIN", prenom="Anne", sexe=Sexe.F),
    ]
    familles = [
        Famille(id="F001", pere_id="I001", mere_id=None, enfants_ids=[]),
        Famille(id="F002", pere_id=None, mere_id="I002", enfants_ids=["I001"]),
        Famille(id="F003", pere_id=None, mere_id=None, enfants_ids=[]),
    ]

    write_gwb_minimal(individus, familles, tmp_path)

    _, familles_lues, _ = load_gwb_minimal(tmp_path)

    assert len(familles_lues) == 3
    assert familles_lues[0].pere_id == "I001"
    assert familles_lues[0].mere_id is None
    assert familles_lues[1].pere_id is None
    assert familles_lues[1].mere_id == "I002"
    assert familles_lues[1].enfants_ids == ["I001"]
    assert familles_lues[2].pere_id is None
    assert familles_lues[2].mere_id is None


def test_write_gwb_minimal_with_notes_sources(tmp_path: Path) -> None:
    """Test d'écriture avec notes et sources (Issue #25)."""
    from datetime import date as date_type
    from geneweb.domain.models import Source

    individus = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, note="Note sur Jean", sources=["S001"]),
    ]
    familles = [
        Famille(id="F001", pere_id="I001", mere_id="I002", enfants_ids=["I003"], note="Note famille", sources=["S001", "S002"]),
    ]
    sources = [
        Source(id="S001", titre="Acte de naissance", auteur="Mairie Paris", date_publication=date_type(1990, 1, 15)),
        Source(id="S002", titre="Recensement", auteur="INSEE", url="https://example.com"),
    ]

    write_gwb_minimal(individus, familles, tmp_path, sources)

    index_path = tmp_path / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))

    assert isinstance(data, dict)
    assert "individus" in data
    assert "familles" in data
    assert "sources" in data

    # Vérifier les notes et sources dans individus
    assert data["individus"][0]["note"] == "Note sur Jean"
    assert data["individus"][0]["sources"] == ["S001"]

    # Vérifier les notes et sources dans familles
    assert data["familles"][0]["note"] == "Note famille"
    assert data["familles"][0]["sources"] == ["S001", "S002"]

    # Vérifier les sources complètes
    assert len(data["sources"]) == 2
    assert data["sources"][0]["id"] == "S001"
    assert data["sources"][0]["titre"] == "Acte de naissance"
    assert data["sources"][0]["auteur"] == "Mairie Paris"
    assert data["sources"][0]["date_publication"] == "1990-01-15"
    assert data["sources"][1]["url"] == "https://example.com"


def test_write_gwb_minimal_round_trip_notes_sources(tmp_path: Path) -> None:
    """Test round-trip avec notes et sources (Issue #25)."""
    from datetime import date as date_type
    from geneweb.domain.models import Source

    individus_initiaux = [
        Individu(id="I001", nom="DUPONT", prenom="Jean", sexe=Sexe.M, note="Note individu", sources=["S001"]),
    ]
    familles_initiales = [
        Famille(id="F001", pere_id="I001", mere_id="I002", note="Note famille", sources=["S002"]),
    ]
    sources_initiales = [
        Source(id="S001", titre="Source 1", auteur="Auteur 1", note="Note source"),
        Source(id="S002", titre="Source 2", url="https://example.com"),
    ]

    # Écrire
    write_gwb_minimal(individus_initiaux, familles_initiales, tmp_path, sources_initiales)

    # Relire
    individus_lus, familles_lues, sources_lues = load_gwb_minimal(tmp_path)

    # Vérifier les individus
    assert len(individus_lus) == 1
    assert individus_lus[0].note == "Note individu"
    assert individus_lus[0].sources == ["S001"]

    # Vérifier les familles
    assert len(familles_lues) == 1
    assert familles_lues[0].note == "Note famille"
    assert familles_lues[0].sources == ["S002"]

    # Vérifier les sources
    assert len(sources_lues) == 2
    assert sources_lues[0].id == "S001"
    assert sources_lues[0].titre == "Source 1"
    assert sources_lues[0].auteur == "Auteur 1"
    assert sources_lues[0].note == "Note source"
    assert sources_lues[1].url == "https://example.com"


def test_write_gwb_minimal_unicode_nfc_normalization(tmp_path: Path) -> None:
    """Test que les chaînes Unicode sont normalisées en NFC (Issue #26)."""
    import unicodedata
    from geneweb.domain.models import Source

    # Créer un nom avec E accent aigu en forme décomposée (NFD)
    prenom_nfd = "E\u0301lise"  # É en NFD
    nom = "D'Hôtel"
    lieu = "Łódź – 😀"

    # Vérifier que l'entrée est bien en NFD
    assert unicodedata.normalize("NFD", "É") == "\u0045\u0301"
    assert unicodedata.normalize("NFC", prenom_nfd) == "Élise"

    individus = [
        Individu(id="I001", nom=nom, prenom=prenom_nfd, sexe=Sexe.F, lieu_naissance=lieu, note="Note avec émojis 😀"),
    ]
    sources = [
        Source(id="S001", titre="Źródło Étude", auteur="François", url="https://example.com/émoji"),
    ]
    familles: list[Famille] = []

    write_gwb_minimal(individus, familles, tmp_path, sources)

    # Relire et vérifier que tout est en NFC
    individus_lus, _, sources_lues = load_gwb_minimal(tmp_path)

    assert len(individus_lus) == 1
    # Le prénom doit être en NFC (composé)
    assert individus_lus[0].prenom == "Élise"
    assert individus_lus[0].nom == "D'Hôtel"
    assert individus_lus[0].lieu_naissance == "Łódź – 😀"
    assert individus_lus[0].note == "Note avec émojis 😀"

    assert len(sources_lues) == 1
    assert sources_lues[0].titre == "Źródło Étude"
    assert sources_lues[0].auteur == "François"
    assert sources_lues[0].url == "https://example.com/émoji"

    # Vérifier que les données dans le JSON sont bien en NFC
    index_path = tmp_path / "index.json"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    indi_data = data["individus"][0]
    assert indi_data["prenom"] == "Élise"  # NFC, pas NFD
    assert "É" in indi_data["prenom"]  # Caractère composé
    assert "\u0301" not in indi_data["prenom"]  # Pas d'accent décomposé


def test_write_gwb_minimal_unicode_round_trip_nfd(tmp_path: Path) -> None:
    """Test round-trip avec entrée en NFD convertie automatiquement en NFC (Issue #26)."""
    import unicodedata

    # Créer des données avec caractères en NFD (décomposés)
    prenom_nfd = "E\u0301lise"  # É en NFD
    nom_nfd = "Franc\u0327ois"  # ç en NFD

    individus_initiaux = [
        Individu(id="I001", nom=nom_nfd, prenom=prenom_nfd, sexe=Sexe.M),
    ]
    familles: list[Famille] = []

    # Écrire (doit normaliser en NFC)
    write_gwb_minimal(individus_initiaux, familles, tmp_path)

    # Relire
    individus_lus, _, _ = load_gwb_minimal(tmp_path)

    # Vérifier que les données sont en NFC (composé)
    assert len(individus_lus) == 1
    assert individus_lus[0].prenom == "Élise"  # NFC
    assert individus_lus[0].nom == "François"  # NFC

    # Vérifier que NFC == ce qu'on a lu (parité)
    assert individus_lus[0].prenom == unicodedata.normalize("NFC", prenom_nfd)
    assert individus_lus[0].nom == unicodedata.normalize("NFC", nom_nfd)


def test_write_gwb_minimal_unicode_special_characters(tmp_path: Path) -> None:
    """Test avec caractères spéciaux variés (Issue #26)."""
    from geneweb.domain.models import Source

    individus = [
        Individu(
            id="I001",
            nom="GARCÍA",
            prenom="José",
            sexe=Sexe.M,
            lieu_naissance="São Paulo",
            lieu_deces="Łódź",
            note="Note avec: émojis 😀, accents áéíóú, symboles ©®™",
        ),
    ]
    sources = [
        Source(
            id="S001",
            titre="Source avec émojis 😀",
            auteur="François Müeller",
            url="https://example.com/émoji?test=©",
            note="Note source avec accents: áéíóú",
        ),
    ]
    familles = [
        Famille(
            id="F001",
            pere_id="I001",
            note="Famille avec caractères spéciaux: ñ, ü, ç",
        ),
    ]

    write_gwb_minimal(individus, familles, tmp_path, sources)

    # Relire et vérifier que tous les caractères sont préservés
    individus_lus, familles_lues, sources_lues = load_gwb_minimal(tmp_path)

    assert individus_lus[0].nom == "GARCÍA"
    assert individus_lus[0].prenom == "José"
    assert individus_lus[0].lieu_naissance == "São Paulo"
    assert individus_lus[0].lieu_deces == "Łódź"
    assert "émojis 😀" in individus_lus[0].note
    assert "accents áéíóú" in individus_lus[0].note
    assert "symboles ©®™" in individus_lus[0].note

    assert sources_lues[0].titre == "Source avec émojis 😀"
    assert sources_lues[0].auteur == "François Müeller"
    assert sources_lues[0].url == "https://example.com/émoji?test=©"
    assert "accents: áéíóú" in sources_lues[0].note

    assert familles_lues[0].note == "Famille avec caractères spéciaux: ñ, ü, ç"


def test_load_gwb_minimal_unicode_nfd_input(tmp_path: Path) -> None:
    """Test que load_gwb_minimal normalise aussi les données en entrée NFD (Issue #26)."""
    import unicodedata

    # Créer un JSON avec des données en NFD (peut arriver si le fichier a été créé ailleurs)
    data = {
        "individus": [
            {
                "id": "I001",
                "nom": "Franc\u0327ois",  # ç en NFD
                "prenom": "E\u0301lise",  # É en NFD
            }
        ],
    }
    (tmp_path / "index.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    individus_lus, _, _ = load_gwb_minimal(tmp_path)

    # Les données doivent être normalisées en NFC lors de la lecture
    assert len(individus_lus) == 1
    assert individus_lus[0].nom == "François"  # NFC
    assert individus_lus[0].prenom == "Élise"  # NFC
