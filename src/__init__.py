"""
Train Scrabble - Un générateur de situations d'entraînement au Scrabble.
"""
from .models.board import Board
from .models.gaddag import GADDAG
from .models.types import Direction, Move
from .models.graph import ScrabbleGraph, Connection, WordNode

from .modules.initialization import (
    placer_mot_central,
    placer_mots_a_reviser,
)

from .modules.connection import (
    phase_de_connexion,
    calculate_separation
)

from .modules.optimization import optimisation_finale

from .services.word_validator import WordValidator
from .services.game_stats import GameStats

__all__ = [
    'Board',
    'GADDAG',
    'Direction',
    'Move',
    'ScrabbleGraph',
    'Connection',
    'WordNode',
    'placer_mot_central',
    'placer_mots_a_reviser',
    'phase_de_connexion',
    'calculate_separation',
    'optimisation_finale',
    'placer_mot',
    'WordValidator',
    'GameStats'
]
