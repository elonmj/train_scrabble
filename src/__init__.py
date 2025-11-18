"""
Train Scrabble - Un générateur de situations d'entraînement au Scrabble.

Migration vers CBIC: L'algorithme CBIC (Construction Incrémentale par Contraintes)
remplace l'ancien workflow en 3 phases pour une génération de grilles plus efficace.
"""
from .models.board import Board
from .models.gaddag import GADDAG
from .models.types import Direction, Move
from .models.graph import ScrabbleGraph, Connection, WordNode

from .modules.cbic import (
    CBIC_generer_grille,
    Placement,
    generer_placements_connexes,
    score_unifie
)

from .modules.optimization import optimisation_locale_legere

from .services.word_validator import WordValidator

__all__ = [
    'Board',
    'GADDAG',
    'Direction',
    'Move',
    'ScrabbleGraph',
    'Connection',
    'WordNode',
    'CBIC_generer_grille',
    'Placement',
    'generer_placements_connexes',
    'score_unifie',
    'optimisation_locale_legere',
    'WordValidator'
]
