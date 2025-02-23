from typing import Dict, List, Set
from collections import Counter

class Rack:
    """Gestion des lettres disponibles pour un joueur."""
    
    # Constantes pour les jetons blanks
    BLANK = '_'
    BLANK_POINTS = 0
    
    # Points pour chaque lettre (français)
    LETTER_POINTS = {
        'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
        'I': 1, 'J': 8, 'K': 10, 'L': 1, 'M': 2, 'N': 1, 'O': 1, 'P': 3,
        'Q': 8, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 10, 'X': 10,
        'Y': 10, 'Z': 10, BLANK: 0
    }

    # Distribution des lettres en français
    LETTER_DISTRIBUTION = {
        'A': 9, 'B': 2, 'C': 2, 'D': 3, 'E': 15, 'F': 2, 'G': 2, 'H': 2,
        'I': 8, 'J': 1, 'K': 1, 'L': 5, 'M': 3, 'N': 6, 'O': 6, 'P': 2,
        'Q': 1, 'R': 6, 'S': 6, 'T': 6, 'U': 6, 'V': 2, 'W': 1, 'X': 1,
        'Y': 1, 'Z': 1, BLANK: 2
    }
    
    def __init__(self, letters: str = ""):
        self.letters = Counter()  # Compteur de lettres
        self.add_letters(letters.upper())
    
    def add_letters(self, letters: str) -> None:
        """Ajoute des lettres au rack."""
        for letter in letters.upper():
            if letter in self.LETTER_POINTS or letter == self.BLANK:
                self.letters[letter] += 1
    
    def remove_letters(self, letters: str) -> bool:
        """
        Retire des lettres du rack.
        Retourne False si certaines lettres ne sont pas disponibles.
        """
        temp_letters = self.letters.copy()
        for letter in letters.upper():
            if temp_letters[letter] <= 0:
                return False
            temp_letters[letter] -= 1
        
        self.letters = temp_letters
        return True
    
    def has_letters(self, letters: str) -> bool:
        """Vérifie si toutes les lettres sont disponibles dans le rack."""
        temp = self.letters.copy()
        blanks_needed = 0
        
        for letter in letters.upper():
            if temp[letter] > 0:
                temp[letter] -= 1
            elif temp[self.BLANK] > 0:
                temp[self.BLANK] -= 1
                blanks_needed += 1
            else:
                return False
        
        return True
    
    def get_possible_letters(self) -> Set[str]:
        """Retourne l'ensemble des lettres disponibles, y compris les substitutions de blanks."""
        result = set()
        
        # Ajoute toutes les lettres normales
        for letter, count in self.letters.items():
            if count > 0 and letter != self.BLANK:
                result.add(letter)
        
        # Si on a des blanks, ajoute toutes les lettres possibles
        if self.letters[self.BLANK] > 0:
            result.update(self.LETTER_POINTS.keys())
            result.remove(self.BLANK)
        
        return result
    
    def get_letter_points(self, letter: str) -> int:
        """Retourne les points pour une lettre donnée."""
        return self.LETTER_POINTS.get(letter.upper(), 0)
    
    def is_empty(self) -> bool:
        """Vérifie si le rack est vide."""
        return sum(self.letters.values()) == 0
    
    def __len__(self) -> int:
        """Retourne le nombre total de lettres dans le rack."""
        return sum(self.letters.values())
    
    def __str__(self) -> str:
        """Représentation string du rack."""
        return ''.join(letter * count for letter, count in self.letters.items())
