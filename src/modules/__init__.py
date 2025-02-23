"""
Modules pour la génération de situations d'entraînement au Scrabble.
"""

from .initialization import (
    placer_mot_central,
    placer_mots_a_reviser,
)

from .connection import (
    calculate_separation,
    is_valid_word_placement,
    get_letter_position,
    find_bridge_words,
    phase_de_connexion,
    ConnectionCandidate
)

from .optimization import optimisation_finale

from .utilities import (
    placer_mot,
    trouver_position,
    trouver_orientation,
    trouver_mots_courts_valides
)
