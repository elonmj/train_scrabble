from typing import Dict, Optional

class Node:
    """Représente un nœud dans le GADDAG."""
    
    def __init__(self):
        self.transitions: Dict[str, 'Node'] = {}  # transitions vers d'autres nœuds
        self.is_terminal: bool = False  # indique si le nœud est terminal
    
    def add_transition(self, char: str, node: Optional['Node'] = None) -> 'Node':
        """Ajoute une transition vers un nouveau nœud ou retourne le nœud existant."""
        if char not in self.transitions:
            self.transitions[char] = node if node else Node()
        return self.transitions[char]
    
    def get_transition(self, char: str) -> Optional['Node']:
        """Retourne le nœud cible pour une lettre donnée, ou None si inexistant."""
        return self.transitions.get(char)
    
    def has_transition(self, char: str) -> bool:
        """Vérifie si une transition existe pour une lettre donnée."""
        return char in self.transitions
