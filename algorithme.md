## Algorithme d'Initialisation (Explication Heuristique Mathématique)

**Objectif:** Placer un mot initial sur la grille et placer des mots supplémentaires *isolés* pour démarrer la partie de Scrabble avec une configuration initiale de mots non connectés.

**Approche Heuristique:**
1. Sélectionner aléatoirement un mot valide d'une longueur appropriée (entre 4 et 7 lettres) et le placer aléatoirement soit horizontalement soit verticalement en passant par la case centrale de la grille.
2. Immédiatement après, tenter de placer un ensemble de "mots à réviser" *sans les connecter* au mot central initialement placé. Ces mots sont placés de manière isolée sur la grille.

**Représentation Mathématique:**

1.  **Placement du Mot Central:** (Identique à la version précédente, intégrant le choix aléatoire de la direction)
    1.  **Ensemble des mots valides:** Soit $D$ l'ensemble de tous les mots valides dans le dictionnaire Scrabble.
    2.  **Ensemble des mots centraux valides:** Définissons $D_c$ comme le sous-ensemble de $D$ contenant les mots de longueur appropriée pour le mot central :
        $D_c = \{w \in D \mid 4 \leq \text{longueur}(w) \leq 7\}$
    3.  **Sélection du mot central:** Choisir aléatoirement un mot $w_c$ de l'ensemble $D_c$ :
        $w_c = \text{choix\_aléatoire}(D_c)$
    4.  **Direction de placement:** Choisir aléatoirement une direction parmi horizontale ou verticale pour le mot central :
        $\text{direction}_c = \text{choix\_aléatoire}(\{\text{HORIZONTALE}, \text{VERTICALE}\})$
    5.  **Position centrale:** Définir $pos_{centre}$ comme la coordonnée de la case centrale sur la grille.
    6.  **Position aléatoire de la lettre centrale sur le centre:** Choisir un indice aléatoire $i_c$ dans le mot $w_c$ pour positionner une de ses lettres sur la case centrale :
        $i_c = \text{entier\_aléatoire}(0, \text{longueur}(w_c) - 1)$
    7.  **Calcul de la position de départ du mot central:** Calculer la coordonnée de départ $(x_c, y_c)$ du mot central de sorte que la lettre à l'indice $i_c$ soit placée sur la case centrale, en ajustant selon la direction choisie :
        Si $\text{direction}_c = \text{VERTICALE}$:
            $x_c = pos_{centre} - i_c$
            $y_c = pos_{centre}$
        Sinon ($\text{direction}_c = \text{HORIZONTALE}$):
            $x_c = pos_{centre}$
            $y_c = pos_{centre} - i_c$
    8.  **Placement du mot central sur la grille et mise à jour du graphe:** Placer les lettres du mot $w_c$ sur la grille à partir de la position $(x_c, y_c)$ dans la direction $\text{direction}_c$, et mettre à jour le graphe de mots avec le mot central et ses informations de position.

2.  **Placement des Mots à Réviser (Isolés):**
    1.  **Entrée:** Grille $G$ contenant le mot central $w_c$, ensemble de mots à réviser $W_r$.
    2.  **Itération sur les mots à réviser:** Pour chaque mot $word_r \in W_r$ :
        a.  **Sélection aléatoire de la direction:** Choisir aléatoirement une direction $\text{direction}_r \in \{\text{HORIZONTALE}, \text{VERTICALE}\}$ pour le mot à réviser.
        b.  **Recherche aléatoire d'une position valide:** Tenter de trouver une position de départ $(x_r, y_r)$ aléatoire sur la grille pour placer $word_r$ dans la direction $\text{direction}_r$, en utilisant une fonction `trouver_position_aleatoire_valide(direction_r, word_r, grille)`. Cette fonction doit rechercher une position qui respecte les limites de la grille et n'entre pas en conflit avec des lettres déjà placées (mais *sans chercher à se connecter* à d'autres mots).
        c.  **Placement conditionnel (si position valide trouvée):** Si une position valide $(x_r, y_r)$ est trouvée :
            i.  Placer $word_r$ sur la grille $G$ à la position $(x_r, y_r)$ dans la direction $\text{direction}_r$.
            ii. Mettre à jour le graphe $Graph$ en ajoutant $word_r$ (mais *sans connexion* pour le moment).
            iii.Mettre à jour les orientations $O$ avec l'orientation de $word_r$.
            iv. Si aucune position valide n'est trouvée après plusieurs tentatives, passer au mot à réviser suivant.

**Justification Heuristique de l'Initialisation Complète:**

*   **Simplicité et Rapidité (Mot Central):** Le placement du mot central reste simple et rapide, assurant un démarrage efficace.
*   **Introduction de Mots Supplémentaires (Isolés):** Placer des mots à réviser de manière isolée permet de créer une configuration initiale plus riche en mots sur la grille, augmentant la complexité et l'intérêt du jeu dès le début.
*   **Éviter la Complexité Initiale de la Connexion:** En plaçant les mots à réviser isolément, on évite la complexité de l'algorithme de connexion lors de la phase d'initialisation. La connexion des mots est reportée à la phase de connexion dédiée, permettant de séparer clairement les responsabilités des algorithmes.

## Algorithme de Connexion (Explication Heuristique Mathématique)

**Objectif:** Connecter les mots isolés sur la grille de Scrabble en trouvant et en plaçant des "mots ponts" valides.

**Approche Heuristique:** Connecter itérativement les mots non connectés à la composante connexe principale (initialement formée autour du mot central), en priorisant les mots les plus proches de cette composante et en utilisant des mots ponts trouvés efficacement grâce à la structure de données GADDAG.

**Représentation Mathématique (Étape par Étape):**

**Entrées:**

*   $G$ : Grille de Scrabble (`Board`).
*   $W_r$ : Ensemble des mots à réviser (mots isolés à connecter).
*   $W_p$ : Ensemble des mots placés sur la grille (`mots_places`).
*   $Graph$ : Graphe de mots (`ScrabbleGraph`).
*   $O$ : Orientations des mots (dictionnaire mot -> (position, direction)).
*   $D$ : Dictionnaire de mots valides.
*   $L_s$ : Lettres d'appui (dictionnaire mot -> {lettre -> index}).
*   $L_a$ : Lettres disponibles pour former des mots ponts.
*   $GADDAG$ : Structure de données GADDAG pour la recherche efficace de mots.

**Algorithme:**

1.  **Initialisation du Graphe:** Créer des nœuds dans le graphe $Graph$ pour tous les mots dans $W_p \cup W_r$, en utilisant les orientations $O$ pour définir leur position et direction.

2.  **Identification des Mots Non Connectés:** Utiliser la fonction `Graph.get_unconnected_words()` pour identifier l'ensemble $U$ des mots non connectés à la composante connexe principale (déterminée via `UnionFind` dans le graphe). Cette fonction retourne également un dictionnaire de distances $Distances$ où $Distances[mot]$ représente la distance graphique de chaque mot non connecté au mot central.

    $U, Distances = Graph.get\_unconnected\_words()$

3.  **Priorisation des Mots Non Connectés:** Trier les mots non connectés $U$ en fonction de leur distance à la composante connexe principale (distance graphique), en utilisant les distances obtenues à l'étape précédente. Les mots les plus proches sont priorisés.

    $Sorted\_U = \text{sort}(U, \text{clé}=\lambda w: Distances.get(w, \infty))$

4.  **Itération et Connexion:** Pour chaque mot $mot_1$ dans l'ensemble trié $Sorted\_U$ :

    a.  **Recherche du Mot Connecté le Plus Proche:** Trouver un mot $mot_2$ qui est déjà connecté à la composante connexe principale et qui est le plus proche de $mot_1$ (dans le graphe ou géométriquement). Prioriser le mot central, puis les autres mots connectés.

    b.  **Vérification de la Validité Géométrique:** Calculer la séparation verticale et horizontale entre $mot_1$ et $mot_2$ en utilisant `calculate_separation()`. Vérifier avec `is_valid_word_placement()` si le placement des deux mots est géométriquement valide (distance minimale pour les mots parallèles, respect des limites du plateau). Si le placement n'est pas valide, passer au mot non connecté suivant.

    c.  **Tentative de Connexion par Mot Pont:** Si une connexion directe (intersection) n'existe pas entre $mot_1$ et $mot_2$, tenter de trouver des mots ponts en utilisant la structure GADDAG :

        $Bridge\_words = GADDAG.find\_bridge\_words(mot_1, pos_1, dir_1, mot_2, pos_2, dir_2, L_s, L_a)$

        Cette fonction recherche dans le GADDAG des mots qui peuvent servir de ponts en considérant :

        *   Les combinaisons de lettres possibles entre $mot_1$ et $mot_2$.
        *   La direction requise pour le mot pont (perpendiculaire à $mot_1$ et $mot_2$).
        *   Les lettres disponibles $L_a$.
        *   Elle génère des "squelettes" pour la méthode `gaddag.find_words_with_skeleton()`, représentant les positions des lettres de $mot_1$ et $mot_2$ dans le mot pont potentiel.

    d.  **Sélection du Meilleur Mot Pont:** Si des mots ponts sont trouvés, sélectionner le meilleur candidat $w_b$ parmi $Bridge\_words$ (par exemple, le mot le plus court).

    e.  **Placement du Mot Pont et Mise à Jour du Graphe:**

        *   Placer le mot pont $w_b$ sur la grille $G$ en utilisant `grille.placer_mot()`.
        *   Ajouter le mot pont $w_b$ au graphe $Graph$ avec `graphe.add_word()`.
        *   Déterminer le point d'intersection entre $w_b$ et $mot_1$ et entre $w_b$ et $mot_2$ (ou utiliser les lettres d'appui).
        *   Ajouter deux connexions au graphe : une entre $mot_1$ et $w_b$, et une autre entre $w_b$ et $mot_2$, en utilisant `graphe.add_connection()`.

5.  **Retour:** L'algorithme de connexion retourne `Vrai` si au moins une connexion a été établie, et `Faux` sinon.

**Justification Heuristique:**

*   **Priorisation des mots proches:** En priorisant la connexion des mots non connectés les plus proches de la composante connexe, l'algorithme cherche à étendre le réseau de mots de manière progressive et efficace.
*   **Utilisation du GADDAG:** L'emploi de la structure de données GADDAG permet de rechercher rapidement des mots ponts valides, optimisant le processus de connexion.
*   **Contraintes géométriques:** Les vérifications de validité géométrique assurent que les mots ponts placés respectent les règles du Scrabble et les contraintes spatiales du plateau.
*   **Approche itérative:** L'algorithme itératif permet de connecter progressivement plusieurs mots isolés, améliorant la connectivité globale du réseau de mots sur le plateau.

---

This explanation now correctly describes the initialization algorithm as placing the central word and then placing "mots à réviser" in isolation, and includes the connection algorithm description.
