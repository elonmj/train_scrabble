from typing import Dict, List, Set, Tuple, Optional
from ..models.board import Board
from ..models.types import Direction, Move
from ..models.gaddag import GADDAG

from .connection import calculate_separation

# Constants for scoring adjustments
MIN_PARALLEL_DIST = 2      # Minimum distance between parallel words
CROSSWORD_BONUS = 1.5      # Bonus for crossword formations
ISOLATION_PENALTY = 0.7    # Penalty for isolated words
CENTER_WEIGHT = 0.15       # Weight for center proximity scoring
DENSITY_THRESHOLD = 0.3    # Threshold for zone density

def optimisation_finale(grille: Board, mots_a_reviser: Set[str], mots_places: Set[str],
                       graphe_connexite: Dict[str, Tuple[List[str], Direction]],
                       orientations: Dict[str, Direction], dico: Set[str],
                       lettres_appui: Set[str], d_max: int, sac_lettres: Dict[str, int],
                       gaddag: GADDAG, max_connexions: int = 3,
                       max_iterations: int = 50) -> None:
    """
    Optimise la grille finale.
    
    Args:
        grille: Plateau de jeu
        mots_a_reviser: Ensemble des mots à réviser
        mots_places: Ensemble des mots placés
        graphe_connexite: Graphe de connexité
        orientations: Dictionnaire des orientations
        dico: Dictionnaire des mots valides
        lettres_appui: Ensemble des lettres d'appui
        d_max: Distance maximale entre les mots
        sac_lettres: Dictionnaire des lettres disponibles
        gaddag: Structure GADDAG
        max_connexions: Nombre maximum de connexions par mot
        max_iterations: Nombre maximum d'itérations
    """
    iterations = 0
    while iterations < max_iterations:
        amelioration = False
        
        # 1. Identifier les mots sous-optimaux
        for mot in mots_places:
            if peut_ameliorer(mot, grille, mots_places, graphe_connexite):
                # 2. Chercher une meilleure position
                nouvelle_pos = trouver_meilleure_position(mot, grille, mots_places, d_max)
                
                if nouvelle_pos:
                    # 3. Tenter le déplacement
                    if deplacer_mot(mot, nouvelle_pos, grille, mots_places,
                                  graphe_connexite, orientations, dico,
                                  lettres_appui, d_max, sac_lettres, gaddag):
                        amelioration = True
                        
        if not amelioration:
            break
            
        iterations += 1
        
    # 4. Équilibrer la grille
    equilibrer_grille(grille, dico, sac_lettres)

def peut_ameliorer(mot: str, grille: Board, mots_places: Set[str],
                  graphe_connexite: Dict[str, Tuple[List[str], Direction]]) -> bool:
    """
    Détermine si un mot peut être amélioré selon des critères étendus.
    """
    # 1. Vérifier le nombre de connexions
    connexions = graphe_connexite.get(mot)
    if not connexions or not connexions[0]:
        return True
        
    # 2. Vérifier la position et l'isolement
    pos = trouver_position(mot, grille)
    if pos:
        row, col = pos
        # Vérifier la distance au centre
        centre = grille.size // 2
        if abs(row - centre) + abs(col - centre) > centre:
            return True
            
        # Vérifier les distances minimales aux mots parallèles
        direction = trouver_orientation(mot, grille)
        if direction:
            for r in range(max(0, row - MIN_PARALLEL_DIST),
                         min(grille.size, row + len(mot) + MIN_PARALLEL_DIST)):
                for c in range(max(0, col - MIN_PARALLEL_DIST),
                             min(grille.size, col + len(mot) + MIN_PARALLEL_DIST)):
                    if grille.get_letter(r, c):
                        if direction == Direction.HORIZONTAL and r != row:
                            if abs(r - row) < MIN_PARALLEL_DIST:
                                return True
                        elif direction == Direction.VERTICAL and c != col:
                            if abs(c - col) < MIN_PARALLEL_DIST:
                                return True
    
    # 3. Vérifier la formation de mots croisés
    if pos and not detecter_mots_croises(mot, grille):
        return True
    
    return False

def detecter_mots_croises(mot: str, grille: Board) -> bool:
    """
    Vérifie si un mot participe à des formations de mots croisés.
    """
    pos = trouver_position(mot, grille)
    if not pos:
        return False
        
    row, col = pos
    direction = trouver_orientation(mot, grille)
    if not direction:
        return False
        
    intersections = 0
    for i in range(len(mot)):
        r = row + (i if direction == Direction.VERTICAL else 0)
        c = col + (i if direction == Direction.HORIZONTAL else 0)
        
        # Vérifier les intersections perpendiculaires
        if direction == Direction.HORIZONTAL:
            if (r > 0 and grille.get_letter(r - 1, c)) or \
               (r < grille.size - 1 and grille.get_letter(r + 1, c)):
                intersections += 1
        else:  # VERTICAL
            if (c > 0 and grille.get_letter(r, c - 1)) or \
               (c < grille.size - 1 and grille.get_letter(r, c + 1)):
                intersections += 1
                
    return intersections > 0

def trouver_meilleure_position(mot: str, grille: Board, mots_places: Set[str],
                             d_max: int) -> Optional[Tuple[int, int, Direction]]:
    """Trouve une meilleure position stratégique pour un mot."""
    meilleur_score = -1
    meilleure_pos = None
    
    # Copie temporaire pour les tests
    grille_temp = grille.copy()
    
    # Supprimer temporairement le mot
    pos_actuelle = trouver_position(mot, grille)
    if pos_actuelle:
        supprimer_mot(mot, grille_temp)
    
    # Chercher la meilleure position
    for row in range(grille.size):
        for col in range(grille.size):
            for direction in Direction:
                if peut_placer_mot(mot, row, col, direction, grille_temp):
                    score = evaluer_position_strategique(
                        mot, row, col, direction,
                        grille_temp, mots_places, d_max
                    )
                    if score > meilleur_score:
                        meilleur_score = score
                        meilleure_pos = (row, col, direction)
                        
    return meilleure_pos

def peut_placer_mot(mot: str, row: int, col: int, direction: Direction, grille: Board) -> bool:
    """
    Vérifie si un mot peut être placé à une position donnée.
    
    Args:
        mot: Mot à placer
        row, col: Position
        direction: Direction du placement
        grille: Plateau de jeu
        
    Returns:
        True si le placement est possible
    """
    # 1. Vérifier les limites de la grille
    if direction == Direction.HORIZONTAL:
        if col + len(mot) > grille.size:
            return False
    else:
        if row + len(mot) > grille.size:
            return False
            
    # 2. Vérifier les chevauchements
    for i in range(len(mot)):
        current_row = row + (i if direction == Direction.VERTICAL else 0)
        current_col = col + (i if direction == Direction.HORIZONTAL else 0)
        
        # Case déjà occupée ?
        if grille.get_letter(current_row, current_col):
            return False
            
    return True

def evaluer_position_strategique(mot: str, row: int, col: int, direction: Direction,
                               grille: Board, mots_places: Set[str], d_max: int) -> float:
    """
    Évalue la qualité stratégique d'une position pour un mot.
    Incorpore des critères avancés comme les formations de mots croisés
    et les distances minimales.
    
    Args:
        mot: Mot à évaluer
        row, col: Position proposée
        direction: Direction du placement
        grille: Plateau de jeu
        mots_places: Ensemble des mots placés
        d_max: Distance maximale autorisée
    """
    score = 0.0
    
    # 1. Évaluation de la centralité
    centre = grille.size // 2
    dist_centre = abs(row - centre) + abs(col - centre)
    score -= dist_centre * CENTER_WEIGHT
    
    # 2. Vérification des distances minimales et parallélisme
    parallel_penalty = 0.0
    for r in range(max(0, row - MIN_PARALLEL_DIST), min(grille.size, row + len(mot) + MIN_PARALLEL_DIST)):
        for c in range(max(0, col - MIN_PARALLEL_DIST), min(grille.size, col + len(mot) + MIN_PARALLEL_DIST)):
            if grille.get_letter(r, c):
                # Vérifier le parallélisme
                if direction == Direction.HORIZONTAL:
                    if r != row and abs(r - row) < MIN_PARALLEL_DIST:
                        parallel_penalty -= ISOLATION_PENALTY
                else:  # VERTICAL
                    if c != col and abs(c - col) < MIN_PARALLEL_DIST:
                        parallel_penalty -= ISOLATION_PENALTY
    
    score += parallel_penalty
    
    # 3. Bonus pour formations de mots croisés
    crossword_bonus = 0.0
    intersections = 0
    for i, lettre in enumerate(mot):
        r = row + (i if direction == Direction.VERTICAL else 0)
        c = col + (i if direction == Direction.HORIZONTAL else 0)
        
        # Vérifier les intersections perpendiculaires
        if direction == Direction.HORIZONTAL:
            if (r > 0 and grille.get_letter(r - 1, c)) or \
               (r < grille.size - 1 and grille.get_letter(r + 1, c)):
                intersections += 1
                crossword_bonus += CROSSWORD_BONUS
        else:  # VERTICAL
            if (c > 0 and grille.get_letter(r, c - 1)) or \
               (c < grille.size - 1 and grille.get_letter(r, c + 1)):
                intersections += 1
                crossword_bonus += CROSSWORD_BONUS
    
    score += crossword_bonus
    
    # 4. Bonus pour utilisation des cases spéciales
    for i in range(len(mot)):
        r = row + (i if direction == Direction.VERTICAL else 0)
        c = col + (i if direction == Direction.HORIZONTAL else 0)
        letter_mult, word_mult = grille.get_multiplier(r, c)
        score += (letter_mult - 1) * 0.5 + (word_mult - 1) * 1.0
    
    # 5. Pénalité pour isolement
    isolation_penalty = 0.0
    voisins = 0
    for r in range(max(0, row - 2), min(grille.size, row + len(mot) + 2)):
        for c in range(max(0, col - 2), min(grille.size, col + len(mot) + 2)):
            if grille.get_letter(r, c):
                voisins += 1
    
    if voisins <= 2:  # Seuil d'isolement
        isolation_penalty = -ISOLATION_PENALTY
    score += isolation_penalty
    
    return max(0.0, score)

def deplacer_mot(mot: str, nouvelle_pos: Tuple[int, int, Direction],
                grille: Board, mots_places: Set[str],
                graphe_connexite: Dict[str, Tuple[List[str], Direction]],
                orientations: Dict[str, Direction], dico: Set[str],
                lettres_appui: Set[str], d_max: int,
                sac_lettres: Dict[str, int], gaddag: GADDAG) -> bool:
    """
    Déplace un mot vers une nouvelle position avec vérifications stratégiques.
    """
    # 1. Sauvegarder l'état actuel
    grille_backup = grille.copy()
    graphe_backup = graphe_connexite.copy()
    
    # 2. Supprimer le mot
    supprimer_mot(mot, grille)
    
    row, col, direction = nouvelle_pos
    
    # 3. Vérifier les distances minimales avant placement
    for r in range(max(0, row - MIN_PARALLEL_DIST),
                  min(grille.size, row + len(mot) + MIN_PARALLEL_DIST)):
        for c in range(max(0, col - MIN_PARALLEL_DIST),
                      min(grille.size, col + len(mot) + MIN_PARALLEL_DIST)):
            if grille.get_letter(r, c):
                if direction == Direction.HORIZONTAL and r != row:
                    if abs(r - row) < MIN_PARALLEL_DIST:
                        grille = grille_backup
                        graphe_connexite = graphe_backup
                        return False
                elif direction == Direction.VERTICAL and c != col:
                    if abs(c - col) < MIN_PARALLEL_DIST:
                        grille = grille_backup
                        graphe_connexite = graphe_backup
                        return False
    
    # 4. Placer le mot
    if not placer_mot(mot, (row, col), direction, grille):
        grille = grille_backup
        graphe_connexite = graphe_backup
        return False
    
    # 5. Évaluer la qualité stratégique du placement
    score_strategique = evaluer_position_strategique(
        mot, row, col, direction, grille, mots_places, d_max
    )
    if score_strategique <= 0:  # Position stratégiquement mauvaise
        grille = grille_backup
        graphe_connexite = graphe_backup
        return False
    
    # 6. Mettre à jour le graphe et vérifier la validité
    if not (mettre_a_jour_connexite(mot, grille, mots_places, graphe_connexite, d_max) and
            verifier_validite_globale(grille, mots_places, graphe_connexite, dico)):
        grille = grille_backup
        graphe_connexite = graphe_backup
        return False
    
    # 7. Mettre à jour l'orientation
    orientations[mot] = direction
    return True

def equilibrer_grille(grille: Board, dico: Set[str],
                     sac_lettres: Dict[str, int]) -> None:
    """
    Équilibre la grille en utilisant une stratégie améliorée de placement
    des mots courts dans les zones peu denses.
    """
    # 1. Identifier les zones peu denses
    zones = analyser_densite_grille(grille)
    mots_places = set()  # Pour suivre les mots déjà placés
    
    # 2. Pour chaque zone peu dense
    for zone in zones:
        row_start, col_start, row_end, col_end = zone
        if calculer_densite(zone, grille) < DENSITY_THRESHOLD:
            # 3. Chercher des mots courts à placer
            mots_courts = trouver_mots_courts_valides(zone, sac_lettres, dico)
            
            # 4. Évaluer chaque mot dans différentes positions
            for mot in mots_courts:
                meilleur_score = -1
                meilleur_placement = None
                
                # Essayer les deux directions
                for direction in Direction:
                    # Parcourir la zone
                    for row in range(row_start, row_end):
                        for col in range(col_start, col_end):
                            if peut_placer_mot(mot, row, col, direction, grille):
                                # Évaluer la position stratégiquement
                                score = evaluer_position_strategique(
                                    mot, row, col, direction,
                                    grille, mots_places, d_max=2
                                )
                                
                                if score > meilleur_score:
                                    meilleur_score = score
                                    meilleur_placement = (row, col, direction)
                
                # Si on a trouvé un bon placement, l'appliquer
                if meilleur_placement and meilleur_score > 0:
                    row, col, direction = meilleur_placement
                    if placer_mot(mot, (row, col), direction, grille):
                        mots_places.add(mot)
                        # Mettre à jour les lettres disponibles
                        for lettre in mot:
                            if lettre in sac_lettres:
                                sac_lettres[lettre] -= 1
                        break  # Passer à la zone suivante

def mettre_a_jour_connexite(mot: str, grille: Board, mots_places: Set[str],
                          graphe_connexite: Dict[str, Tuple[List[str], Direction]],
                          d_max: int) -> bool:
    """
    Met à jour le graphe de connexité après le déplacement d'un mot.
    
    Args:
        mot: Mot déplacé
        grille: Plateau de jeu
        mots_places: Ensemble des mots placés
        graphe_connexite: Graphe de connexité
        d_max: Distance maximale entre les mots
        
    Returns:
        True si la mise à jour est valide
    """
    # 1. Trouver les connexions potentielles
    connexions = []
    pos_mot = trouver_position(mot, grille)
    if not pos_mot:
        return False
        
    # 2. Parcourir les autres mots
    for autre_mot in mots_places:
        if autre_mot != mot:
            autre_pos = trouver_position(autre_mot, grille)
            if autre_pos:
                # Calculer la distance entre les mots
                direction_mot = trouver_orientation(mot, grille)
                direction_autre = trouver_orientation(autre_mot, grille)
                if not direction_mot or not direction_autre:
                    continue
                v_sep, h_sep = calculate_separation(pos_mot, direction_mot, len(mot), autre_pos, direction_autre, len(autre_mot))
                if v_sep <= d_max and h_sep <= d_max:
                    connexions.append(autre_mot)
                    
    # 3. Mettre à jour le graphe
    if mot in graphe_connexite:
        graphe_connexite[mot][0].extend(connexions)
    else:
        orientation = trouver_orientation(mot, grille)
        if not orientation:
            return False
        graphe_connexite[mot] = (connexions, orientation)
        
    # 4. Vérifier la validité des connexions
    for autre_mot in connexions:
        if autre_mot not in graphe_connexite:
            orientation = trouver_orientation(autre_mot, grille)
            if not orientation:
                return False
            graphe_connexite[autre_mot] = ([mot], orientation)
        else:
            graphe_connexite[autre_mot][0].append(mot)
            
    return True

def verifier_validite_globale(grille: Board, mots_places: Set[str],
                            graphe_connexite: Dict[str, Tuple[List[str], Direction]],
                            dico: Set[str]) -> bool:
    """
    Vérifie que la configuration globale est valide après un déplacement.
    
    Args:
        grille: Plateau de jeu
        mots_places: Ensemble des mots placés
        graphe_connexite: Graphe de connexité
        dico: Dictionnaire des mots valides
        
    Returns:
        True si la configuration est valide
    """
    # 1. Vérifier que tous les mots sont connectés
    for mot in mots_places:
        connexions = graphe_connexite.get(mot)
        if not connexions:
            return False
        mots_connectes, _ = connexions
        if not mots_connectes:
            return False
            
    # 2. Vérifier que tous les mots formés sont valides
    # Pour chaque mot placé
    for mot in mots_places:
        pos = trouver_position(mot, grille)
        if not pos:
            return False
        row, col = pos
        orientation = trouver_orientation(mot, grille)
        if not orientation:
            return False
            
        # Vérifier les mots formés perpendiculairement
        for i in range(len(mot)):
            current_row = row + (i if orientation == Direction.VERTICAL else 0)
            current_col = col + (i if orientation == Direction.HORIZONTAL else 0)
            
            # Chercher le début du mot perpendiculaire
            if orientation == Direction.HORIZONTAL:
                # Chercher vers le haut
                start_row = current_row
                while start_row > 0 and grille.get_letter(start_row - 1, current_col):
                    start_row -= 1
                    
                # Lire le mot vertical
                mot_vertical = ""
                r = start_row
                while r < grille.size and grille.get_letter(r, current_col):
                    mot_vertical += grille.get_letter(r, current_col)
                    r += 1
                    
                if len(mot_vertical) > 1 and mot_vertical not in dico:
                    return False
                    
            else:  # VERTICAL
                # Chercher vers la gauche
                start_col = current_col
                while start_col > 0 and grille.get_letter(current_row, start_col - 1):
                    start_col -= 1
                    
                # Lire le mot horizontal
                mot_horizontal = ""
                c = start_col
                while c < grille.size and grille.get_letter(current_row, c):
                    mot_horizontal += grille.get_letter(current_row, c)
                    c += 1
                    
                if len(mot_horizontal) > 1 and mot_horizontal not in dico:
                    return False
                    
    return True

def trouver_position(mot: str, grille: Board) -> Optional[Tuple[int, int]]:
    """Trouve la position d'un mot sur la grille."""
    for row in range(grille.size):
        for col in range(grille.size):
            if grille.get_letter(row, col) == mot[0]:
                # Vérifie horizontalement
                if all(col + i < grille.size and grille.get_letter(row, col + i) == mot[i] 
                      for i in range(len(mot))):
                    return row, col
                # Vérifie verticalement
                if all(row + i < grille.size and grille.get_letter(row + i, col) == mot[i] 
                      for i in range(len(mot))):
                    return row, col
    return None

def supprimer_mot(mot: str, grille: Board) -> None:
    """Supprime un mot de la grille."""
    pos = trouver_position(mot, grille)
    if pos:
        row, col = pos
        for i in range(len(mot)):
            if col + i < grille.size and grille.get_letter(row, col + i) == mot[i]:
                grille.grid[row][col + i] = None
            if row + i < grille.size and grille.get_letter(row + i, col) == mot[i]:
                grille.grid[row + i][col] = None

def detecter_zone_isolee(mot: str, grille: Board) -> bool:
    """Détecte si un mot est dans une zone isolée."""
    pos = trouver_position(mot, grille)
    if not pos:
        return False
        
    row, col = pos
    connexions = 0
    
    # Compte les connexions dans un rayon de 2 cases
    for r in range(max(0, row - 2), min(grille.size, row + 3)):
        for c in range(max(0, col - 2), min(grille.size, col + 3)):
            if grille.get_letter(r, c):
                connexions += 1
                
    # Soustrait les lettres du mot lui-même
    connexions -= len(mot)
    
    return connexions < 3  # Seuil arbitraire

def analyser_densite_grille(grille: Board) -> List[Tuple[int, int, int, int]]:
    """
    Analyse la densité de la grille et retourne les zones peu denses.
    Retourne une liste de tuples (row_start, col_start, row_end, col_end).
    """
    zones = []
    taille_zone = 4  # Taille arbitraire des zones
    
    for row in range(0, grille.size, taille_zone):
        for col in range(0, grille.size, taille_zone):
            row_end = min(row + taille_zone, grille.size)
            col_end = min(col + taille_zone, grille.size)
            
            densite = calculer_densite((row, col, row_end, col_end), grille)
            if densite < 0.3:  # Seuil arbitraire
                zones.append((row, col, row_end, col_end))
                
    return zones

def calculer_densite(zone: Tuple[int, int, int, int], grille: Board) -> float:
    """Calcule la densité de lettres dans une zone."""
    row_start, col_start, row_end, col_end = zone
    cases_occupees = 0
    total_cases = (row_end - row_start) * (col_end - col_start)
    
    for row in range(row_start, row_end):
        for col in range(col_start, col_end):
            if grille.get_letter(row, col):
                cases_occupees += 1
                
    return cases_occupees / total_cases if total_cases > 0 else 0
