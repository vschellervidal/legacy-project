#!/usr/bin/env python3
"""Script de test pour les routes gwd (Issue #34).

Usage:
    python scripts/test_gwd_routes.py
    python scripts/test_gwd_routes.py --base /tmp/gwb_test --port 8000
"""

import argparse
import json
from pathlib import Path

import requests


def create_test_base(base_dir: Path) -> None:
    """Crée une base GWB de test si elle n'existe pas."""
    if (base_dir / "index.json").exists():
        print(f"✅ Base existe déjà : {base_dir}")
        return
    
    print(f"📦 Création de la base de test dans {base_dir}...")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    from geneweb.domain.models import Famille, Individu, Sexe
    from geneweb.io.gwb import write_gwb_minimal
    
    individus = [
        Individu(
            id="I001",
            nom="DUPONT",
            prenom="Jean",
            sexe=Sexe.M,
            lieu_naissance="Paris",
            note="Test individu 1",
        ),
        Individu(
            id="I002",
            nom="MARTIN",
            prenom="Marie",
            sexe=Sexe.F,
            lieu_naissance="Lyon",
            note="Test individu 2",
        ),
        Individu(
            id="I003",
            nom="DUPONT",
            prenom="Pierre",
            sexe=Sexe.M,
            famille_enfance_id="F001",
            note="Enfant de Jean et Marie",
        ),
    ]
    
    familles = [
        Famille(
            id="F001",
            pere_id="I001",
            mere_id="I002",
            enfants_ids=["I003"],
            note="Famille test",
        ),
    ]
    
    write_gwb_minimal(individus, familles, base_dir)
    print(f"✅ Base créée : {len(individus)} individus, {len(familles)} familles")


def test_route(base_url: str, base: str, mode: str = "", **params) -> dict:
    """Teste une route et affiche le résultat."""
    params["base"] = base
    params["mode"] = mode
    params["use_python"] = "true"
    
    url = f"{base_url}/gwd"
    
    print(f"\n🔍 Test : {url}")
    print(f"   Params : {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()
        print(f"   ✅ Status : {response.status_code}")
        print(f"   📄 Résultat :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur : {e}")
        if hasattr(e.response, "text"):
            print(f"   Détail : {e.response.text}")
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Tester les routes gwd")
    parser.add_argument(
        "--base",
        default="/tmp/gwb_test",
        help="Chemin de la base GWB (défaut: /tmp/gwb_test)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port du serveur (défaut: 8000)",
    )
    parser.add_argument(
        "--create-base",
        action="store_true",
        help="Créer une base de test si elle n'existe pas",
    )
    args = parser.parse_args()
    
    base_dir = Path(args.base)
    base_url = f"http://localhost:{args.port}"
    
    # Créer la base si demandé
    if args.create_base:
        create_test_base(base_dir)
    
    # Vérifier que le serveur est accessible
    try:
        response = requests.get(f"{base_url}/healthz", timeout=2)
        response.raise_for_status()
        print("✅ Serveur accessible")
    except requests.exceptions.RequestException:
        print("❌ Erreur : Serveur non accessible")
        print(f"   Assurez-vous que le serveur tourne sur {base_url}")
        print("   Commande : uvicorn geneweb.adapters.http.app:app --reload --port {args.port}")
        return
    
    # Utiliser le chemin absolu pour la base
    base_param = str(base_dir.absolute())
    
    print("\n" + "=" * 60)
    print("🧪 TESTS DES ROUTES GWD (Issue #34)")
    print("=" * 60)
    
    # Test 1 : Page d'accueil
    test_route(base_url, base_param)
    
    # Test 2 : Fiche individu
    test_route(base_url, base_param, i="I001")
    
    # Test 3 : Recherche (mode S)
    test_route(base_url, base_param, mode="S")
    
    # Test 4 : Recherche avec query (mode NG)
    test_route(base_url, base_param, mode="NG", v="DUPONT")
    
    # Test 5 : Fiche famille
    test_route(base_url, base_param, mode="F", f="F001")
    
    # Test 6 : Ascendance
    test_route(base_url, base_param, mode="A", i="I003")
    
    # Test 7 : Descendance
    test_route(base_url, base_param, mode="D", i="I001")
    
    # Test 8 : Notes
    test_route(base_url, base_param, mode="NOTES")
    
    # Test 9 : Erreur (individu introuvable)
    print("\n🧪 Test d'erreur : individu introuvable")
    test_route(base_url, base_param, i="I999")
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés")
    print("=" * 60)


if __name__ == "__main__":
    main()

