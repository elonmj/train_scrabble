"""
Modules pour la génération de situations d'entraînement au Scrabble.

Migration vers CBIC (Construction Incrémentale par Contraintes):
- Les anciens modules initialization et connection sont obsolètes
- Le nouveau module cbic remplace le workflow en 3 phases
- optimization est simplifié en optimisation légère optionnelle
"""

from .cbic import (
    CBIC_generer_grille,
    Placement,
    generer_placements_connexes,
    est_placement_valide,
    score_unifie
)

from .optimization import optimisation_locale_legere

# Note: initialization et connection sont obsolètes avec CBIC
# Ils sont gardés temporairement pour compatibilité mais seront supprimés


