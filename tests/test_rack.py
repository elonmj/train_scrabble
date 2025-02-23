from src.models.rack import Rack

def test_rack():
    """Tests des fonctionnalités du rack."""
    print("\n=== Test du Rack ===")
    
    # Test de base
    rack = Rack("AEILRST_")  # Un rack avec un blank
    print(f"Rack initial: {rack}")
    
    # Test des lettres disponibles
    possible_letters = rack.get_possible_letters()
    print(f"Lettres possibles: {sorted(possible_letters)}")
    
    # Test avec des blanks
    test_words = ["STAR", "TALES", "SALI", "RAILS"]
    print("\nTest de disponibilité des lettres:")
    for word in test_words:
        available = rack.has_letters(word)
        print(f"'{word}': {'disponible' if available else 'non disponible'}")
    
    # Test de retrait de lettres
    if rack.remove_letters("STAR"):
        print(f"\nAprès retrait de 'STAR': {rack}")
    
    return rack
