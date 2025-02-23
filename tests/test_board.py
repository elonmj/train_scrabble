from src.models.board import Board

def test_plateau() -> Board:
    """
    Test des fonctionnalités basiques du plateau :
    1. Affichage du plateau vide
    2. Système de coordonnées (A1-O15)
    3. Règles de placement :
       - Premier coup au centre (H8)
       - Coups suivants adjacents
       - Une lettre par case
    Note: Ce test ne vérifie PAS la validité des mots,
    il teste uniquement la mécanique du plateau.
    """
    print("\n=== Test du plateau ===")
    board = Board()
    
    print("Plateau initial:")
    print(board)
    
    # Tests de placement de lettres (sans vérification de mots valides)
    test_moves = [
        ("H8", "S"),  # Test 1: Premier coup - doit être au centre (H8)
        ("H7", "C"),  # Test 2: Adjacent horizontal gauche
        ("H9", "R"),  # Test 3: Adjacent horizontal droit
        ("G8", "U"),  # Test 4: Adjacent vertical haut
        ("I8", "X"),  # Test 5: Adjacent vertical bas
        ("A1", "Z"),  # Test 6: Devrait échouer (non adjacent)
        ("H8", "A"),  # Test 7: Devrait échouer (case occupée)
    ]
    
    for coord, letter in test_moves:
        try:
            row, col = board.parse_coordinates(coord)
            if board.place_letter(row, col, letter):
                print(f"\nPlacement réussi: {letter} en {coord}")
            else:
                print(f"\nPlacement invalide: {letter} en {coord} (non adjacent ou case occupée)")
            print(board)
        except ValueError as e:
            print(f"Erreur de coordonnées: {e}")
    
    return board

def test_coordonnees(board: Board) -> None:
    """Test spécifique du système de coordonnées."""
    test_coords = [
        "H8",   # Valide
        "A1",   # Valide - coin supérieur gauche
        "O15",  # Valide - coin inférieur droit
        "P1",   # Invalid - lettre hors limites
        "A16",  # Invalid - nombre hors limites
        "AA",   # Invalid - format incorrect
        "11",   # Invalid - pas de lettre
        "",     # Invalid - vide
    ]
    
    print("\n=== Test des coordonnées ===")
    for coord in test_coords:
        try:
            row, col = board.parse_coordinates(coord)
            print(f"Coordonnées {coord} -> ({row}, {col})")
        except ValueError as e:
            print(f"Coordonnées {coord} invalides: {e}")
