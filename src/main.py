from typing import Set, Dict
import random

from src.models.board import Board
from src.models.gaddag import GADDAG
from src.models.graph import ScrabbleGraph
from src.models.types import Direction
from src.modules.initialization import placer_mot_central, placer_mots_a_reviser
from src.modules.connection import phase_de_connexion
from src.modules.optimization import optimisation_finale


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
                                 d_max: int = 3) -> Board:
    """
    Génère une situation d'entraînement complète.
    
    Args:
        mots_a_reviser: Ensemble des mots à réviser
        dico: Dictionnaire des mots valides
        gaddag: Structure GADDAG
        sac_lettres: Dictionnaire des lettres disponibles
        d_max: Distance maximale entre les mots
        
    Returns:
        Plateau de jeu généré
    """
    # 1. Créer la grille
    grille = Board()
    
    # 2. Définir les lettres d'appui par mot
    lettres_appui = {
        'CACABERA': {'E': 6},  # E en position 6
        'BACCARAS': {'S': 7},  # S en position 7
        'BACCARAT': {'T': 7}   # T en position 7
    }
    
    # 3. Initialiser l'ensemble des mots placés
    mots_places = set()
    
    # Créer le graphe de Scrabble
    graphe = ScrabbleGraph(grille)
    
    # 4. Placer le mot central
    print("\nPlacement du mot central...")
    resultat = placer_mot_central(grille, dico, lettres_appui, graphe)
    if not resultat:
        raise ValueError("Impossible de placer le mot central")
    mot_central, x, y = resultat
    mots_places.add(mot_central)  # Important: ajouter le mot central aux mots placés
    print(f"Mot central placé : {mot_central} en ({x}, {y})")
    print("État du graphe après placement du mot central:")
    graphe.debug_print()
    grille.debug_print("Après placement du mot central")
    
    # 5. Placer les mots à réviser
    print("\nPlacement des mots à réviser...")
    mots_places_reviser, mots_non_places = placer_mots_a_reviser(
        grille, list(mots_a_reviser), dico, lettres_appui, d_max, sac_lettres, graphe
    )
    print(f"Mots placés : {', '.join(mots_places_reviser)}")
    print(f"Mots non placés : {', '.join(mots_non_places)}")
    grille.debug_print("Après placement des mots à réviser")
    
    # 6. Mettre à jour l'ensemble des mots placés
    mots_places.update(mots_places_reviser)
    
    # 7. Récupérer les orientations depuis le graphe
    orientations = {}
    for mot in mots_places:
        if mot in graphe.nodes:
            orientations[mot] = graphe.nodes[mot].direction
        else:
            print(f"Warning: Word '{mot}' in mots_places but not in graphe.nodes")
    
    # 8. Phase de connexion avec le graphe
    print("\nPhase de connexion...")
    connection_success = phase_de_connexion(
        grille, set(mots_non_places), mots_places, graphe,
        orientations, dico, lettres_appui, d_max,
        sac_lettres, gaddag
    )
    
    print(f"\nRésultat de la phase de connexion: {'Succès' if connection_success else 'Échec'}")
    print("\nÉtat de la grille après connexion:")
    grille.debug_print()
    print("\nÉtat du graphe après connexion:")
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
    
    # 3. Définir les mots à réviser
    mots_a_reviser = {"CACABERA", "BACCARAS", "BACCARAT"}
    print(f"\nMots à réviser : {', '.join(mots_a_reviser)}")
    
    # 4. Initialiser le sac de lettres
    sac_lettres = initialiser_sac_lettres()
    
    # 5. Générer la situation d'entraînement
    grille = generer_situation_entrainement(mots_a_reviser, dico, gaddag, sac_lettres)
    
    # 6. Afficher le résultat
    print("\nSituation d'entraînement générée :")
    print(grille)  # Utilise directement la méthode __str__ de Board
    
    # 7. Générer un tirage aléatoire de 7 lettres
    lettres_disponibles = list(sac_lettres.keys())
    tirage = ''.join(random.choice(lettres_disponibles) for _ in range(7))
    print(f"\nTirage : {tirage}")


if __name__ == "__main__":
    main()
