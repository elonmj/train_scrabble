
---

### Plan final très détaillé

#### **1. Objectif**
Créer une grille de mots croisés 15x15 où :
- **DATAIS** par exemple est le mot central, passant par (7,7).
- Les mots à réviser  (par exemple **BACCARAS**, **BACCARAT**, **CACABERA**) sont placés autour, respectant :
  - `PARALLEL_MIN_DISTANCE = 4` pour les mots parallèles (distance axiale avec chevauchement d’intervalles).
  - `PERPENDICULAR_MIN_DISTANCE = 3` pour les mots perpendiculaires (distance de Manhattan).

#### **2. Constantes**
- **`PARALLEL_MIN_DISTANCE = 4`** : Distance minimale entre mots parallèles (en carrés de grille).
- **`PERPENDICULAR_MIN_DISTANCE = 3`** : Distance minimale entre mots perpendiculaires (en carrés de grille).
- **`MAX_TENTATIVES = 30`** : Nombre maximum de tentatives pour placer un mot.
- **`GRID_SIZE = 15`** : Taille de la grille (15x15).
- **`CENTER = (7, 7)`** : Position centrale de la grille.
- **Commentaires** :
  - `# Distance minimale entre mots parallèles (carrés de grille)` pour `PARALLEL_MIN_DISTANCE`.
  - `# Distance minimale entre mots perpendiculaires (carrés de grille)` pour `PERPENDICULAR_MIN_DISTANCE`.

#### **3. Structure des données**
- **`grid`** : Matrice 15x15 initialisée avec `'.'`.
- **`placed_words_info`** : Liste de tuples `(mot, (row, col), direction)` pour suivre les placements.
- **`Direction`** : Enum avec `HORIZONTAL` et `VERTICAL`.


#### **5. Fonction `placer_mots_a_reviser`**
- **Paramètres** :
  - `grid` : Grille actuelle.
  - `words_to_place` : Liste des mots à réviser (`["BACCARAS", "BACCARAT", "CACABERA"]`).
- **Logique** :
  1. **Placement du mot central** :
     - Placer **DATAIS** à (5, 7) vertical (colonne 7, rangées 5 à 10).
     - Ajouter à `placed_words_info` : `("DATAIS", (5, 7), VERTICAL)`.
     - Mettre à jour `grid`.
  2. **Division en zones** :
     - Quadrants : (0-7, 0-7), (0-7, 8-14), (8-14, 0-7), (8-14, 8-14).
  3. **Stratégie de placement** :
     - Trier `words_to_place` par longueur décroissante : `["BACCARAS", "BACCARAT", "CACABERA"]` (tous 8 lettres, ordre conservé).
     - Pour chaque mot :
       - Initialiser `tentatives = 0`.
       - Choisir une zone dans un ordre rotatif (0, 1, 2, 3).
       - Générer aléatoirement `(row, col)` dans la zone et `direction` (H/V).
       - Tester avec `est_position_valide`.
       - Si valide :
         - Placer le mot dans `grid`.
         - Ajouter à `placed_words_info`.
       - Sinon, incrémenter `tentatives` et recommencer jusqu’à `MAX_TENTATIVES`.
       - Si échec, signaler un problème (ou passer au suivant).

#### **6. Gestion des collisions**
- **Zone d’influence** : Vérifiée via distances minimales dans `est_position_valide`.
- **Distances** :
  - Parallèles : 4 (axial).
  - Perpendiculaires : 3 (Manhattan).
- **Diagonales** : Vérifiées pour éviter les proximités ambiguës.

#### **7. Résultat attendu**
La grille ci-dessus est un exemple valide avec :
- **DATAIS** au centre.
- Espacements respectés pour **BACCARAS**, **BACCARAT**, **CACABERA**.

---

=