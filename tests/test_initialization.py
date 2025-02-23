import unittest
from src.models.board import Board
from src.models.types import Direction
from src.models.graph import ScrabbleGraph
from src.modules.initialization import placer_mot_central, placer_mots_a_reviser

class TestInitialization(unittest.TestCase):
    def setUp(self):
        self.board = Board()  # Standard 15x15 Scrabble board
        self.graph = ScrabbleGraph(self.board)
        self.dico = {'VIROSE', 'BACCARAT', 'CACABERA', 'BACCARAS'}
        
    def test_placement_mot_central(self):
        """Test le placement du mot central VIROSE."""
        lettres_appui = {
            'CACABERA': {'E': 5},
            'BACCARAS': {'S': 7},
            'BACCARAT': {'T': 7}
        }
        
        # Force VIROSE as central word for testing
        mot, x, y = placer_mot_central(self.board, {'VIROSE'}, lettres_appui, self.graph)
        direction = self.graph.nodes[mot].direction

        # Verify central word placement
        self.assertEqual(mot, 'VIROSE')
        self.assertEqual(self.graph.central_word, 'VIROSE')

        # Verify letters are placed correctly
        for i, lettre in enumerate('VIROSE'):
            if direction == Direction.VERTICAL:
                self.assertEqual(self.board.get_letter(x + i, y), lettre)
            else:
                self.assertEqual(self.board.get_letter(x, y + i), lettre)
        self.board.debug_print("Board after central word placement in test_placement_mot_central")

    def test_placement_mots_revision(self):
        """Test le placement des mots à réviser."""
        # Place central word first
        lettres_appui = {
            'CACABERA': {'E': 5},
            'BACCARAS': {'S': 7},
            'BACCARAT': {'T': 7}
        }
        mots = ['BACCARAT', 'CACABERA', 'BACCARAS']

        # Place VIROSE using placer_mot_central
        placer_mot_central(self.board, {'VIROSE'}, lettres_appui, self.graph)

        # Try placing revision words
        mots_places, mots_non_places = placer_mots_a_reviser(
            self.board, mots, self.dico, lettres_appui,
            d_max=2, sac_lettres={}, graphe=self.graph
        )
        
        # Verify words were placed
        self.assertIn('CACABERA', mots_places)
        self.assertIn('BACCARAS', mots_places)
        # Verify words are in the graph
        for mot in ['CACABERA', 'BACCARAS']:
            self.assertIn(mot, self.graph.nodes)
            node = self.graph.nodes[mot]
            self.assertIsNotNone(node.position)
            # Verify word is actually on the board at the reported position
            x, y = node.position
            for i, letter in enumerate(mot):
                if node.direction == Direction.HORIZONTAL:
                    self.assertEqual(self.board.get_letter(x, y + i), letter)
                else:
                    self.assertEqual(self.board.get_letter(x + i, y), letter)
        
        self.board.debug_print("Board after revision words placement in test_placement_mots_revision")

    def test_direction_balance(self):
        """Test that words are placed in both horizontal and vertical directions."""
        # Setup similar to previous test
        lettres_appui = {
            'CACABERA': {'E': 5},
            'BACCARAS': {'S': 7},
            'BACCARAT': {'T': 7}
        }
        mots = ['BACCARAT', 'CACABERA', 'BACCARAS']
        
        # Place VIROSE using placer_mot_central
        placer_mot_central(self.board, {'VIROSE'}, lettres_appui, self.graph)

        # Place revision words
        placer_mots_a_reviser(self.board, mots, self.dico, lettres_appui,
                             d_max=2, sac_lettres={}, graphe=self.graph)
        
        # Count horizontal and vertical placements
        horizontal = 0
        vertical = 0
        for node in self.graph.nodes.values():
            if node.direction == Direction.HORIZONTAL:
                horizontal += 1
            else:
                vertical += 1
                
        # Verify we have both horizontal and vertical placements
        self.assertGreater(horizontal, 0)
        self.assertGreater(vertical, 0)

        self.board.debug_print("Board after revision words placement in test_direction_balance")

if __name__ == '__main__':
    unittest.main()