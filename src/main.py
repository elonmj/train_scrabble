from typing import Set, Dict
import random

from src.models.board import Board
from src.models.gaddag import GADDAG
from src.models.graph import ScrabbleGraph
from src.models.types import Direction
from src.modules.cbic import CBIC_generer_grille



def charger_dictionnaire(chemin_fichier: str) -> Set[str]:
    """Charge le dictionnaire depuis un fichier."""
    try:
        # Modifier le chemin pour qu'il soit relatif à la racine du projet
        with open(f"data/{chemin_fichier}", 'r', encoding='utf-8') as f:
            return {word.strip().upper() for word in f if word.strip()}
    except FileNotFoundError:
        print(f"Fichier data/{chemin_fichier} non trouvé, utilisation d'un dictionnaire de test")
        return {"CACABERA", "BACCARAS", "BACCARAT", "CHAT", "CHIEN", "MAISON", "JARDIN", 
                "LIVRE", "CRAYON", "PAPIER", "FENETRE", "PORTE", "LAMPE",
                "ARBRE", "FLEUR", "SOLEIL", "LUNE", "ETOILE", "NUAGE"}


def initialiser_sac_lettres() -> Dict[str, int]:
    """Initialises le sac de lettres avec la distribution du Scrabble français."""
    return {
        'A': 9, 'B': 2, 'C': 2, 'D': 3, 'E': 15, 'F': 2, 'G': 2, 'H': 2,
        'I': 8, 'J': 1, 'K': 1, 'L': 5, 'M': 3, 'N': 6, 'O': 6, 'P': 2,
        'Q': 1, 'R': 6, 'S': 6, 'T': 6, 'U': 6, 'V': 2, 'W': 1, 'X': 1,
        'Y': 1, 'Z': 1, '*': 2  # Jokers
    }


def generer_situation_entrainement(mots_a_reviser: Set[str], dico: Set[str],
                                  gaddag: GADDAG, sac_lettres: Dict[str, int],
                                  lettres_appui: Dict[str, Dict[str, int]],
                                  mot_central: str = "DATAIS") -> Board:
    """
    Génère une situation d'entraînement complète en utilisant l'algorithme CBIC.
    
    L'algorithme CBIC (Construction Incrémentale par Contraintes) garantit la connexité
    par construction en ne plaçant que des mots qui se connectent aux mots existants.
    
    Args:
        mots_a_reviser: Ensemble des mots à réviser
        dico: Dictionnaire des mots valides (non utilisé avec CBIC mais gardé pour compatibilité)
        gaddag: Structure GADDAG pour validation des mots
        sac_lettres: Dictionnaire des lettres disponibles (non utilisé mais gardé pour compatibilité)
        lettres_appui: Dictionnaire des lettres d'appui pour chaque mot
        mot_central: Mot central à placer (défaut: "DATAIS")
        
    Returns:
        Plateau de jeu généré avec tous les mots connectés
        
    Raises:
        ValueError: Si un mot à réviser n'a pas ses lettres d'appui définies
    """
    # Valider que tous les mots à réviser ont leurs lettres d'appui définies
    for mot in mots_a_reviser:
        if mot not in lettres_appui:
            raise ValueError(f"Le mot '{mot}' n'a pas ses lettres d'appui définies")

    # Utiliser l'algorithme CBIC pour générer la grille
    # CBIC garantit la connexité par construction en une seule phase
    grille, graphe, mots_places = CBIC_generer_grille(
        list(mots_a_reviser),
        gaddag,
        lettres_appui,
        mot_central
    )
    
    print("\n=== Résultat final ===")
    print(f"Mots placés: {len(mots_places)}/{len(mots_a_reviser)} "
          f"({len(mots_places) / len(mots_a_reviser) * 100:.1f}%)")
    print(f"Mots: {', '.join(sorted(mots_places))}")
    
    mots_non_places = set(mots_a_reviser) - mots_places
    if mots_non_places:
        print(f"Mots non placés: {', '.join(sorted(mots_non_places))}")
    
    print("\nÉtat de la grille finale:")
    grille.debug_print()
    print("\nÉtat du graphe final:")
    graphe.debug_print()
        
    return grille


def main():
    """Point d'entrée du programme."""
    # 1. Charger le dictionnaire - Modifier le chemin
    dico = charger_dictionnaire("ods8.txt")  # Changement ici
    print(f"\nDictionnaire chargé avec {len(dico)} mots")
    
    # 2. Créer le GADDAG
    gaddag = GADDAG()
    for mot in dico:
        gaddag.add_word(mot)
    print(f"GADDAG créé avec {gaddag.word_count} mots")
    
    # 3. Définir les mots à réviser et leurs lettres d'appui
    mots_a_reviser = {"CACABERA", "BACCARAS", "BACCARAT"}
    # Définir les lettres d'appui pour chaque mot avec leur position
    lettres_appui = {
        'CACABERA': {'E': 6},  # E en position 6
        'BACCARAS': {'S': 7},  # S en position 7
        'BACCARAT': {'T': 7}   # T en position 7
    }
    print(f"\nMots à réviser : {', '.join(mots_a_reviser)}")
    print("Lettres d'appui définies pour chaque mot :")
    for mot, appuis in lettres_appui.items():
        print(f"  {mot}: {', '.join(f'{lettre} en position {pos}' for lettre, pos in appuis.items())}")
    
    # 4. Initialiser le sac de lettres
    sac_lettres = initialiser_sac_lettres()
    
    # 5. Générer la situation d'entraînement
    grille = generer_situation_entrainement(mots_a_reviser, dico, gaddag, sac_lettres, lettres_appui)
    
    # 6. Afficher le résultat
    print("\nSituation d'entraînement générée :")
    print(grille)  # Utilise directement la méthode __str__ de Board
    
    # 7. Générer un tirage aléatoire de 7 lettres
    lettres_disponibles = list(sac_lettres.keys())
    tirage = ''.join(random.choice(lettres_disponibles) for _ in range(7))
    print(f"\nTirage : {tirage}")


if __name__ == "__main__":
    main()
