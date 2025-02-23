L'algorithme GADDAG (Generalized Directed Acyclic Word Graph) est une structure de données et un algorithme conçus pour générer rapidement tous les mouvements possibles dans le jeu de Scrabble. Il est basé sur une représentation du lexique qui permet une exploration bidirectionnelle des mots, contrairement à l'algorithme DAWG (Directed Acyclic Word Graph) qui fonctionne de manière linéaire, de gauche à droite. Voici une description détaillée de son implémentation dans le contexte du Scrabble :

**1. Représentation du Lexique avec un GADDAG**
*   Le GADDAG est construit à partir d'un lexique de mots, et contrairement au DAWG, il encode un chemin bidirectionnel à partir de chaque lettre de chaque mot.
*   Chaque mot du lexique est représenté plusieurs fois dans le GADDAG, une fois pour chaque lettre du mot. Par exemple, le mot "CARE" aura quatre représentations : "CeARE", "ACeRE", "RACeE" et "ERAC". Le caractère "e" est un délimiteur.
*   Le GADDAG est un graphe acyclique dirigé où les arcs sont étiquetés par des lettres et des ensembles de lettres. Les ensembles de lettres indiquent les lettres qui, si elles sont rencontrées ensuite, forment un mot.
*   Les états du GADDAG ne sont pas explicitement marqués comme finaux ou non finaux. Au lieu de cela, les ensembles de lettres sur les arcs indiquent si un chemin donné forme un mot.

**2. Construction du GADDAG**
*   Pour chaque mot du lexique, le GADDAG crée des chemins en insérant un caractère délimiteur « e » à chaque position possible dans le mot. Cela crée une représentation bidirectionnelle qui facilite la génération de mots à partir de n'importe quelle lettre.
*   Le GADDAG est semi-minimisé lors de sa construction en fusionnant les nœuds qui mènent aux mêmes ensembles de mots possibles. Cela réduit la taille du graphe sans nécessiter une étape de minimisation complète, ce qui accélère la construction du graphe.
*  Dans la semi-minimisation, si `xy = vw`, alors `{z | REV(x)eyz is a path} = {z | REV(v)ewz is a path}`. Cela signifie que le nœud que `REV(x)ey` mène fusionne avec le nœud que `REV(v)ew` mène à.
*   L'algorithme de construction fusionne tous les états menant à des ensembles de mots équivalents, ce qui réduit considérablement la taille du graphe.

**3. Génération des Mouvements**
*   La génération de mouvements est effectuée par une recherche en profondeur avec retour arrière à travers le GADDAG. L'algorithme parcourt le graphe en utilisant les lettres disponibles du chevalet du joueur et en respectant les contraintes du plateau.
*   L'algorithme `Gen(0,NULL,RACK,INIT)` est appelé, où `INIT` est un arc vers l'état initial du GADDAG avec un ensemble de lettres null. La procédure `Gen` est indépendante de la direction.
*   Les tuiles sont placées vers la gauche ou la droite à partir de la case d'ancrage. Une fois le délimiteur « e » rencontré, la direction change de gauche à droite.
*   Une case d'ancrage est une case où un nouveau mot peut être relié à des lettres déjà présentes sur le plateau. L'algorithme GADDAG réduit le nombre de cases d'ancrage nécessaires, car il n'est pas nécessaire de générer des mouvements à partir de toutes les cases d'ancrage internes d'une séquence contiguë de cases d'ancrage.
*   L'algorithme de génération de mouvement explore toutes les manières possibles de jouer un mot sur le plateau en « accrochant » des lettres du chevalet à des lettres existantes, en respectant la structure du GADDAG et les contraintes du plateau.
*   L'algorithme vérifie si la lettre à placer est autorisée sur la case et si la combinaison de lettres forme un mot valide du lexique.

**4. Avantages du GADDAG**
*   **Vitesse** : L'algorithme GADDAG génère des mouvements plus de deux fois plus vite que l'algorithme DAWG. Cela est dû à sa capacité à traiter les préfixes comme des suffixes et à éliminer les préfixes qui ne mènent pas à des mots valides.
*   **Déterminisme** : Le GADDAG réduit le non-déterminisme dans la génération de préfixes présent dans l'algorithme DAWG. Les préfixes sont joués de la même manière que les suffixes, ce qui permet d'appliquer les contraintes du plateau plus tôt.
*   **Ensembles Croisés** : L'algorithme GADDAG permet de calculer les ensembles croisés gauche et droite de manière déterministe et simultanée, ce qui n'est pas le cas avec le DAWG.
*   **Nombre réduit de cases d'ancrage** : Le GADDAG réduit le nombre de cases d'ancrage nécessaires, ce qui diminue le nombre de calculs requis pour la génération des mouvements.

**5. Optimisations**
*   **Minimisation** : Le GADDAG est minimisé pendant sa construction pour réduire la taille de la structure.
*   **Représentation Compressée** : Le GADDAG peut être représenté sous forme compressée pour réduire l'utilisation de la mémoire. Cependant, la représentation compressée peut ralentir légèrement le temps de recherche des arcs par rapport à une représentation non compressée.
*   **Ensembles de lettres** : L'utilisation d'ensembles de lettres au lieu d'états finaux explicites permet de fusionner plus d'états lors de la minimisation.

**6. Gestion des Blanks**
*   L'algorithme GADDAG prend en compte les tuiles blanches (blanks) qui peuvent représenter n'importe quelle lettre.
*   La présence de blancs augmente le nombre de mouvements possibles, mais le GADDAG est plus rapide que le DAWG pour traiter les mouvements avec des blancs.

**7. Performances**
*   L'algorithme GADDAG est plus rapide que l'algorithme DAWG. Il traverse moins d'arcs et atteint moins d'impasses avant de détecter les impasses.
*   Les temps CPU sont plus rapides avec le GADDAG qu'avec le DAWG pour la génération de mouvements. L'algorithme GADDAG traverse environ 22 000 arcs par seconde. Cependant, le GADDAG traverse le même nombre d'arcs pour générer cinq mouvements que le DAWG pour générer deux mouvements.

En résumé, l'algorithme GADDAG est une approche efficace pour générer rapidement tous les mouvements possibles au Scrabble grâce à sa structure bidirectionnelle, sa minimisation lors de la construction et sa gestion efficace des ensembles de lettres et des contraintes du plateau. Il est préférable au DAWG en termes de vitesse, bien qu'il nécessite plus de mémoire.
