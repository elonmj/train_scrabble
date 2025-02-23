from src.models.board import Board, SquareType
from src.services.move_generator import MoveGenerator, Direction, Move
from src.models.gaddag import GADDAG
from src.models.rack import Rack
from src.services.score_calculator import ScoreCalculator

def test_scores() -> None:
    """Test du système complet de calcul des scores."""
    print("\n=== Test du système de scores ===")
    
    # Premier test : multiplicateurs simples
    test_multiplicateurs()
    
    # Test des mots croisés et bonus
    board = Board()
    gaddag = GADDAG()
    test_words = ["VERTICALEMENT", "HORIZONTAL"]
    for word in test_words:
        gaddag.add_word(word)
    
    # Place un mot vertical puis un mot horizontal qui le croise
    board.reset_multipliers()
    print("\nTest des mots croisés:")
    
    # Place "VERTICALEMENT" en colonne 8
    for i, letter in enumerate("VERTICALEMENT"):
        board.place_letter(i+1, 8, letter)
        board.use_multiplier(i+1, 8)
    
    print("Après placement vertical:")
    print(board)
    
    # Place "HORIZONTAL" en ligne 8 - Correction du placement
    move = Move(
        word="HORIZONTAL",
        row=8,  # Ligne I
        col=5,  # Pour que le I croise avec VERTICALEMENT
        direction=Direction.HORIZONTAL
    )
    
    # Utiliser ScoreCalculator pour placer le mot correctement
    calculator = ScoreCalculator(board)
    score = calculator.calculate_move_score(move)
    
    print(f"\nScore du mot horizontal: {score}")
    print("Plateau final:")
    print(board)

def test_placement_score(word: str, coord: str, direction: Direction, 
                        board: Board, generator: MoveGenerator) -> None:
    """Test le score d'un placement spécifique."""
    print(f"\nTest du placement de '{word}' en {coord} {direction.name}")
    
    # Nettoyer le plateau avant chaque test
    board.grid = [['' for _ in range(board.SIZE)] for _ in range(board.SIZE)]
    board.first_move = True
    
    # Convertit les coordonnées
    row, col = board.parse_coordinates(coord)
    
    # Place le mot et collecte les informations
    letters_used = []
    blanks_used = []
    
    for i, letter in enumerate(word):
        current_row = row + (i if direction == Direction.VERTICAL else 0)
        current_col = col + (i if direction == Direction.HORIZONTAL else 0)
        
        if letter == '_':
            blanks_used.append(i)
            letter = 'E'  # Utilise E comme exemple pour le blank
            
        board.place_letter(current_row, current_col, letter)
        letters_used.append((letter, (current_row, current_col)))
    
    print(f"Plateau après placement:")
    print(board)
    
    # Calcule les différents composants du score
    main_score = generator._calculate_word_score(letters_used, blanks_used)
    cross_score = generator._calculate_cross_words_score(letters_used, blanks_used)
    bingo_bonus = generator.BINGO_BONUS if len(word) >= 7 else 0
    
    print(f"Score du mot principal: {main_score}")
    print(f"Score des mots croisés: {cross_score}")
    if bingo_bonus:
        print(f"Bonus pour 7 lettres: {bingo_bonus}")
    print(f"Score total: {main_score + cross_score + bingo_bonus}")

def test_multiplicateurs() -> None:
    """Test des multiplicateurs du plateau."""
    print("\n=== Test des multiplicateurs ===")
    
    test_cases = [
        ("ZOO", "H8", "H", "Mot normal au centre (Z=10, O=1)"),
        ("QUIZ", "A1", "H", "Triple mot avec Q=10, U=1, I=1, Z=10x2 -> 32*3"),
        ("AXE", "H1", "H", "A=1, X=10 double lettre, E=1"),
        ("JEUX", "A8", "V", "J=8, E=1, U=1, X=10x2 + triple mot"),
    ]
    
    for word, pos, direction, desc in test_cases:
        print(f"\nTest: {desc}")
        board = Board()
        calculator = ScoreCalculator(board)
        
        # Crée et calcule le mouvement
        move = Move(
            word=word,
            row=board.parse_coordinates(pos)[0],
            col=board.parse_coordinates(pos)[1],
            direction=Direction.HORIZONTAL if direction == "H" else Direction.VERTICAL
        )
        
        score = calculator.calculate_move_score(move)
        print(f"Mot: {word}")
        print(f"Score: {score}")
        print(board)

def test_multiplicateurs_mots_croises() -> None:
    """Test des scores avec des mots qui se croisent."""
    print("\n=== Test des mots croisés ===")
    
    test_cases = [
        # Format: (premier mot, pos1, dir1, score1, deuxième mot, pos2, dir2, score2, desc)
        (
            "PAR", "H8", "H", 5,           # Premier mot: PAR -> 5 pts
            "ART", "H8", "V", 4,           # Deuxième mot: ART -> 4 pts (A déjà posé)
            "Test simple croisement PAR/ART"
        ),
        (
            "THE", "H8", "H", 6,           # Premier mot
            "CHAT", "G9", "V", 12,         # Deuxième mot avec H déjà posé + lettre double
            "THE croisé par CHAT avec bonus"
        ),
    ]
    
    for (word1, pos1, dir1, score1, 
         word2, pos2, dir2, score2, desc) in test_cases:
        board = Board()
        calculator = ScoreCalculator(board)
        
        # Premier mot
        move1 = Move(word1, *board.parse_coordinates(pos1), Direction.HORIZONTAL if dir1 == "H" else Direction.VERTICAL)
        actual_score1 = calculator.calculate_move_score(move1)
        
        # Deuxième mot
        move2 = Move(word2, *board.parse_coordinates(pos2), Direction.HORIZONTAL if dir2 == "H" else Direction.VERTICAL)
        actual_score2 = calculator.calculate_move_score(move2)
        
        # Vérifications
        assert actual_score1 == score1, f"Score incorrect pour {word1}"
        assert actual_score2 == score2, f"Score incorrect pour {word2}"
        assert board.get_total_score() == score1 + score2, "Score total incorrect"

def test_score_simulation():
    """Test that score simulation doesn't modify board state."""
    board = Board()
    calculator = ScoreCalculator(board)
    
    # Place first word
    move1 = Move("PAR", 7, 7, Direction.HORIZONTAL)
    actual_score1 = calculator.calculate_move_score(move1)
    
    # Simulate second word
    move2 = Move("ART", 7, 7, Direction.VERTICAL)
    simulated_score = calculator.simulate_move_score(move2)
    
    # Board should be unchanged after simulation
    assert len(board.grid) == 3, "Board was modified during simulation"
    assert board.total_score == actual_score1, "Score was modified during simulation"
    
    # Actually place second word
    actual_score2 = calculator.calculate_move_score(move2)
    assert simulated_score == actual_score2, "Simulated score differs from actual"

if __name__ == "__main__":
    print("=== Tests des scores ===")
    test_multiplicateurs()
    test_multiplicateurs_mots_croises()
