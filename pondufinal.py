import random  
import os  # Pour vérifier et manipuler les fichiers
import time 
import subprocess  # Pour ouvrir de nouvelles fenêtres de terminal
import sys  # Pour accéder aux arguments de la ligne de commande


def initialiser_fichier_mots():
    
    # Vérifier si le fichier mots.txt existe déjà
    if not os.path.exists("mots.txt"):
        # Liste de 20 mots par défaut pour commencer le jeu
        mots_defaut = [
            "python", "ordinateur", "programmation", "clavier", "souris",
            "ecran", "internet", "fichier", "algorithme", "fonction",
            "variable", "boucle", "condition", "tableau", "dictionnaire",
            "chaine", "nombre", "liste", "classe", "objet"
        ]
        # Ouvrir le fichier en mode écriture avec encodage UTF-8
        with open("mots.txt", "w", encoding="utf-8") as f:
            # Écrire chaque mot sur une nouvelle ligne
            for mot in mots_defaut:
                f.write(mot + "\n")
        print("Fichier mots.txt créé avec 20 mots par défaut\n")


def initialiser_fichier_scores():
    
    # Vérifier si le fichier scores.txt existe déjà
    if not os.path.exists("scores.txt"):
        # Créer un fichier vide pour stocker les scores
        with open("scores.txt", "w", encoding="utf-8") as f:
            f.write("")
        print("Fichier scores.txt créé\n")


def charger_mots():
   
    # Ouvrir le fichier en mode lecture
    with open("mots.txt", "r", encoding="utf-8") as f:
        # Lire chaque ligne, enlever les espaces, convertir en minuscule
        # Ignorer les lignes vides avec "if ligne.strip()"
        mots = [ligne.strip().lower() for ligne in f if ligne.strip()]
    return mots


def ajouter_mot():
    
    print("\n=== AJOUTER UN MOT ===")
    # Demander à l'utilisateur d'entrer un mot
    nouveau_mot = input("Entrez le nouveau mot : ").strip().lower()
    
    # Vérifier que le mot contient uniquement des lettres (pas de chiffres ou symboles)
    if not nouveau_mot.isalpha():
        print("Le mot doit contenir uniquement des lettres!")
        return
    
    # Vérifier que le mot a au moins 4 lettres
    if len(nouveau_mot) < 4:
        print("Le mot doit contenir au moins 4 lettres!")
        return
    
    # Charger tous les mots existants
    mots_existants = charger_mots()
    # Vérifier si le mot existe déjà pour éviter les doublons
    if nouveau_mot in mots_existants:
        print("Ce mot existe déjà!")
        return
    
    # Ouvrir le fichier en mode ajout (append) pour ne pas écraser les mots existants
    with open("mots.txt", "a", encoding="utf-8") as f:
        f.write(nouveau_mot + "\n")
    print(f"Le mot '{nouveau_mot}' a été ajouté!")


def sauvegarder_score(nom, score, difficulte, temps=None):
    # Ouvrir le fichier en mode ajout
    with open("scores.txt", "a", encoding="utf-8") as f:
        # Si un temps est fourni, l'inclure dans le fichier
        if temps:
            # Format: nom,score,difficulté,temps
            f.write(f"{nom},{score},{difficulte},{temps:.1f}\n")
        else:
            # Format sans temps: nom,score,difficulté
            f.write(f"{nom},{score},{difficulte}\n")


def afficher_tableau_scores():
    # Afficher l'en-tête du tableau
    print("\n" + "="*70)
    print("TABLEAU DES SCORES ".center(70))
    print("="*70)
    
    # Vérifier si le fichier existe et n'est pas vide
    if not os.path.exists("scores.txt") or os.path.getsize("scores.txt") == 0:
        print("Aucun score enregistré pour le moment.")
        print("="*70 + "\n")
        return
    
    # Liste pour stocker tous les scores
    scores = []
    # Lire le fichier scores.txt
    with open("scores.txt", "r", encoding="utf-8") as f:
        # Parcourir chaque ligne du fichier
        for ligne in f:
            if ligne.strip():  # Ignorer les lignes vides
                # Séparer les éléments par la virgule
                parties = ligne.strip().split(",")
                # Vérifier qu'il y a au moins 3 éléments (nom, score, difficulté)
                if len(parties) >= 3:
                    nom = parties[0]
                    score = int(parties[1])  # Convertir le score en entier
                    difficulte = parties[2]
                    # Le temps est optionnel (4ème élément)
                    temps = float(parties[3]) if len(parties) >= 4 else None
                    # Ajouter un tuple à la liste des scores
                    scores.append((nom, score, difficulte, temps))
    
    # Trier les scores par ordre décroissant (du plus grand au plus petit)
    # key=lambda x: x[1] signifie trier par le 2ème élément (le score)
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # Afficher l'en-tête des colonnes
    print(f"{'Rang':<6}{'Joueur':<20}{'Score':>10}{'Difficulté':<15}{'Temps':>12}")
    print("-"*70)
    
    # Afficher les 10 meilleurs scores
    # enumerate(scores[:10], 1) commence la numérotation à 1
    for i, (nom, score, diff, temps) in enumerate(scores[:10], 1):
        # Formater le temps ou afficher "---" s'il n'existe pas
        temps_str = f"{temps:.1f}s" if temps else "---"
        # Afficher une ligne du tableau avec formatage
        print(f"{i:<6}{nom:<20}{score:>10}{diff:<15}{temps_str:>12}")
    
    print("="*70 + "\n")


def dessiner_pendu(erreurs):
    
    # Liste contenant les 7 étapes du dessin du pendu
    etapes = [
        # Étape 0: Potence vide
        """
           ------
           |    |
           |
           |
           |
           |
        --------
        """,
        # Étape 1: Tête
        """
           ------
           |    |
           |    O
           |
           |
           |
        --------
        """,
        # Étape 2: Corps
        """
           ------
           |    |
           |    O
           |    |
           |
           |
        --------
        """,
        # Étape 3: Bras gauche
        """
           ------
           |    |
           |    O
           |   /|
           |
           |
        --------
        """,
        # Étape 4: Bras droit
        """
           ------
           |    |
           |    O
           |   /|\\
           |
           |
        --------
        """,
        # Étape 5: Jambe gauche
        """
           ------
           |    |
           |    O
           |   /|\\
           |   /
           |
        --------
        """,
        # Étape 6: Jambe droite (pendu complet)
        """
           ------
           |    |
           |    O
           |   /|\\
           |   / \\
           |
        --------
        PERDU!
        """
    ]
    # Afficher l'étape correspondante (min pour ne pas dépasser 6)
    print(etapes[min(erreurs, 6)])


def choisir_difficulte():
    
    print("\n=== CHOISIR LA DIFFICULTÉ ===")
    print("1. Facile (10 essais)")
    print("2. Moyen (7 essais)")
    print("3. Difficile (5 essais)")
    
    # Boucle jusqu'à obtenir un choix valide
    while True:
        choix = input("Votre choix (1-3) : ").strip()
        # Retourner le nombre d'essais et le nom de la difficulté
        if choix == "1":
            return 10, "Facile"
        elif choix == "2":
            return 7, "Moyen"
        elif choix == "3":
            return 5, "Difficile"
        else:
            print("Choix invalide!")


def format_temps(secondes):
    # Calculer le nombre de minutes
    minutes = int(secondes // 60)
    # Calculer les secondes restantes
    secs = int(secondes % 60)
    # Retourner au format MM:SS avec 2 chiffres
    return f"{minutes:02d}:{secs:02d}"


def calculer_score(mot, erreurs, max_erreurs, difficulte, temps_ecoule=None):
    
    # Score de base: 10 points par lettre du mot
    score_base = len(mot) * 10
    
    # Multiplicateur selon la difficulté
    bonus_difficulte = {"Facile": 1, "Moyen": 1.5, "Difficile": 2}
    
    # Bonus pour les essais non utilisés: 5 points par essai restant
    bonus_perfection = (max_erreurs - erreurs) * 5
    
    # Calcul du score intermédiaire
    score = int((score_base + bonus_perfection) * bonus_difficulte[difficulte])
    
    # Bonus de vitesse si un temps est fourni
    if temps_ecoule is not None:
        if temps_ecoule < 30:  # Moins de 30 secondes
            score += 50
            print("BONUS VITESSE : +50 points (< 30s)")
        elif temps_ecoule < 60:  # Moins d'1 minute
            score += 30
            print("BONUS VITESSE : +30 points (< 1min)")
        elif temps_ecoule < 120:  # Moins de 2 minutes
            score += 10
            print("BONUS VITESSE : +10 points (< 2min)")
    
    return score


def jouer():
    
    # Charger tous les mots disponibles
    mots = charger_mots()
    if not mots:
        print("Aucun mot disponible dans le fichier!")
        return
    
    # Choisir un mot au hasard
    mot_secret = random.choice(mots)
    # Demander la difficulté
    max_erreurs, difficulte = choisir_difficulte()
    # Démarrer le chronomètre
    temps_debut = time.time()
    # Limiter les étapes du dessin à 6 maximum
    erreurs_dessin_max = min(max_erreurs, 6)
    
    # Ensemble des lettres trouvées (set évite les doublons)
    lettres_trouvees = set()
    # Ensemble de toutes les lettres essayées
    lettres_essayees = set()
    # Compteur d'erreurs
    erreurs = 0
    
    # Afficher les informations de départ
    print(f"\nDébut de la partie - Difficulté: {difficulte}")
    print(f"Chronomètre démarré!")
    print(f"Le mot contient {len(mot_secret)} lettres")
    
    # Boucle principale du jeu
    while erreurs < max_erreurs:
        # Calculer le temps écoulé depuis le début
        temps_ecoule = time.time() - temps_debut
        
        # Construire l'affichage du mot avec _ pour les lettres non trouvées
        mot_affiche = ""
        for lettre in mot_secret:
            if lettre in lettres_trouvees:
                mot_affiche += lettre + " "
            else:
                mot_affiche += "_ "
        
        # Afficher l'état actuel du jeu
        print("\n" + "="*50)
        # Dessiner le pendu si le nombre d'erreurs le permet
        if erreurs <= erreurs_dessin_max:
            dessiner_pendu(min(erreurs, 6))
        
        # Afficher le temps écoulé
        print(f"Temps écoulé: {format_temps(temps_ecoule)}")
        print(f"\nMot : {mot_affiche}")
        print(f"Erreurs : {erreurs}/{max_erreurs}")
        
        # Afficher les lettres déjà essayées
        if lettres_essayees:
            print(f"Lettres essayées : {', '.join(sorted(lettres_essayees))}")
        
        # Vérifier si le mot est complètement trouvé
        # all() vérifie que toutes les lettres du mot sont dans lettres_trouvees
        if all(lettre in lettres_trouvees for lettre in mot_secret):
            # Arrêter le chronomètre
            temps_final = time.time() - temps_debut
            
            # Afficher le message de victoire
            print("\nBRAVO! Vous avez trouvé le mot:", mot_secret.upper())
            print(f"Temps total: {format_temps(temps_final)}")
            
            # Calculer et afficher le score
            score = calculer_score(mot_secret, erreurs, max_erreurs, difficulte, temps_final)
            print(f"Votre score: {score} points")
            
            # Demander le nom du joueur pour sauvegarder le score
            nom = input("\nEntrez votre nom pour le tableau des scores: ").strip()
            if nom:
                sauvegarder_score(nom, score, difficulte, temps_final)
                print("Score enregistré!")
            return
        
        # Demander une lettre au joueur
        lettre = input("\nProposez une lettre : ").strip().lower()
        
        # Vérifier que l'entrée est valide (une seule lettre)
        if len(lettre) != 1 or not lettre.isalpha():
            print("Veuillez entrer une seule lettre!")
            continue
        
        # Vérifier que la lettre n'a pas déjà été essayée
        if lettre in lettres_essayees:
            print("Vous avez déjà essayé cette lettre!")
            continue
        
        # Ajouter la lettre aux lettres essayées
        lettres_essayees.add(lettre)
        
        # Vérifier si la lettre est dans le mot
        if lettre in mot_secret:
            # Ajouter aux lettres trouvées
            lettres_trouvees.add(lettre)
            print(f"Bien joué! La lettre '{lettre}' est dans le mot!")
        else:
            # Incrémenter le compteur d'erreurs
            erreurs += 1
            print(f"Dommage! La lettre '{lettre}' n'est pas dans le mot.")
    
    # Si on sort de la boucle, le joueur a perdu
    temps_final = time.time() - temps_debut
    print("\n" + "="*50)
    dessiner_pendu(6)
    print(f"\nPERDU! Le mot était: {mot_secret.upper()}")
    print(f"Temps total: {format_temps(temps_final)}")
    print("Meilleure chance la prochaine fois!")


def jouer_deux_joueurs():
    #Gère le mode deux joueurs avec fenêtres séparées"
    print("\n=== MODE DEUX JOUEURS ===")
    print("Chaque joueur jouera dans une fenêtre séparée")
    
    # Demander les noms des deux joueurs
    nom_j1 = input("Nom du Joueur 1: ").strip()
    nom_j2 = input("Nom du Joueur 2: ").strip()
    
    # Donner des noms par défaut si aucun nom n'est entré
    if not nom_j1:
        nom_j1 = "Joueur 1"
    if not nom_j2:
        nom_j2 = "Joueur 2"
    
    # Charger tous les mots disponibles
    mots = charger_mots()
    if len(mots) < 2:
        print("Il faut au moins 2 mots dans le fichier!")
        return
    
    # Créer une copie de la liste et la mélanger
    mots_disponibles = mots.copy()
    random.shuffle(mots_disponibles)
    # Assigner un mot différent à chaque joueur
    mot_j1 = mots_disponibles[0]
    mot_j2 = mots_disponibles[1]
    
    # Choisir la difficulté (même pour les deux joueurs)
    max_erreurs, difficulte = choisir_difficulte()
    
    print(f"\nLancement des fenêtres pour {nom_j1} et {nom_j2}...")
    print("Fermez cette fenêtre après avoir joué dans les deux fenêtres de jeu.")
    
    # Créer des fichiers temporaires avec les configurations pour chaque joueur
    # Fichier pour le joueur 1: nom, mot, nombre d'essais, difficulté
    with open("temp_j1.txt", "w", encoding="utf-8") as f:
        f.write(f"{nom_j1}\n{mot_j1}\n{max_erreurs}\n{difficulte}")
    
    # Fichier pour le joueur 2
    with open("temp_j2.txt", "w", encoding="utf-8") as f:
        f.write(f"{nom_j2}\n{mot_j2}\n{max_erreurs}\n{difficulte}")
    
    # Ouvrir deux nouvelles fenêtres de terminal
    if os.name == 'nt':  # Si Windows
        # Lancer deux fenêtres CMD avec le programme en mode joueur1 et joueur2
        subprocess.Popen(['start', 'cmd', '/k', 'python', sys.argv[0], 'joueur1'], shell=True)
        subprocess.Popen(['start', 'cmd', '/k', 'python', sys.argv[0], 'joueur2'], shell=True)
    else:  # Si Linux/Mac
        # Lancer deux terminaux GNOME
        subprocess.Popen(['gnome-terminal', '--', 'python3', sys.argv[0], 'joueur1'])
        subprocess.Popen(['gnome-terminal', '--', 'python3', sys.argv[0], 'joueur2'])
    
    print("\nLes deux joueurs jouent maintenant dans leurs fenêtres respectives.")
    print("Appuyez sur Entrée quand les deux parties sont terminées pour voir les résultats...")
    input()
    
    # Afficher les résultats comparatifs
    afficher_resultats_deux_joueurs()
    
    # Nettoyer les fichiers temporaires
    if os.path.exists("temp_j1.txt"):
        os.remove("temp_j1.txt")
    if os.path.exists("temp_j2.txt"):
        os.remove("temp_j2.txt")
    if os.path.exists("result_j1.txt"):
        os.remove("result_j1.txt")
    if os.path.exists("result_j2.txt"):
        os.remove("result_j2.txt")


def jouer_mode_joueur(fichier_config, fichier_result):
    
    # Lire la configuration depuis le fichier temporaire
    with open(fichier_config, "r", encoding="utf-8") as f:
        lignes = f.readlines()
        nom = lignes[0].strip()  # Nom du joueur
        mot_secret = lignes[1].strip()  # Mot à deviner
        max_erreurs = int(lignes[2].strip())  # Nombre d'essais maximum
        difficulte = lignes[3].strip()  # Niveau de difficulté
    
    # Démarrer le chronomètre
    temps_debut = time.time()
    erreurs_dessin_max = min(max_erreurs, 6)
    
    # Initialiser les variables du jeu
    lettres_trouvees = set()
    lettres_essayees = set()
    erreurs = 0
    victoire = False
    
    # Afficher l'en-tête personnalisé
    print("="*50)
    print(f"BIENVENUE {nom.upper()}".center(50))
    print("="*50)
    print(f"Difficulté: {difficulte}")
    print(f"Le mot contient {len(mot_secret)} lettres")
    print(f"Vous avez {max_erreurs} essais")
    
    # Boucle principale du jeu (identique au mode solo)
    while erreurs < max_erreurs:
        temps_ecoule = time.time() - temps_debut
        
        # Construire l'affichage du mot
        mot_affiche = ""
        for lettre in mot_secret:
            if lettre in lettres_trouvees:
                mot_affiche += lettre + " "
            else:
                mot_affiche += "_ "
        
        # Afficher l'état du jeu
        print("\n" + "="*50)
        if erreurs <= erreurs_dessin_max:
            dessiner_pendu(min(erreurs, 6))
        
        print(f"Temps écoulé: {format_temps(temps_ecoule)}")
        print(f"\nMot : {mot_affiche}")
        print(f"Erreurs : {erreurs}/{max_erreurs}")
        
        if lettres_essayees:
            print(f"Lettres essayées : {', '.join(sorted(lettres_essayees))}")
        
        # Vérifier la victoire
        if all(lettre in lettres_trouvees for lettre in mot_secret):
            temps_final = time.time() - temps_debut
            print("\nBRAVO! Vous avez trouvé le mot:", mot_secret.upper())
            print(f"Temps total: {format_temps(temps_final)}")
            score = calculer_score(mot_secret, erreurs, max_erreurs, difficulte, temps_final)
            print(f"Votre score: {score} points")
            victoire = True
            
            # Sauvegarder les résultats dans un fichier
            with open(fichier_result, "w", encoding="utf-8") as f:
                f.write(f"{nom}\n{score}\n{temps_final:.1f}\n{victoire}\n{mot_secret}")
            
            print("\nAppuyez sur Entrée pour fermer cette fenêtre...")
            input()
            return
        
        # Demander une lettre
        lettre = input("\nProposez une lettre : ").strip().lower()
        
        # Validation de l'entrée
        if len(lettre) != 1 or not lettre.isalpha():
            print("Veuillez entrer une seule lettre!")
            continue
        
        if lettre in lettres_essayees:
            print("Vous avez déjà essayé cette lettre!")
            continue
        
        lettres_essayees.add(lettre)
        
        # Vérifier la lettre
        if lettre in mot_secret:
            lettres_trouvees.add(lettre)
            print(f"Bien joué! La lettre '{lettre}' est dans le mot!")
        else:
            erreurs += 1
            print(f"Dommage! La lettre '{lettre}' n'est pas dans le mot.")
    
    # En cas de défaite
    temps_final = time.time() - temps_debut
    print("\n" + "="*50)
    dessiner_pendu(6)
    print(f"\nPERDU! Le mot était: {mot_secret.upper()}")
    print(f"Temps total: {format_temps(temps_final)}")
    
    # Sauvegarder les résultats même en cas de défaite (score = 0)
    with open(fichier_result, "w", encoding="utf-8") as f:
        f.write(f"{nom}\n0\n{temps_final:.1f}\n{victoire}\n{mot_secret}")
    
    print("\nAppuyez sur Entrée pour fermer cette fenêtre...")
    input()


def afficher_resultats_deux_joueurs():
    #Compare et affiche les résultats des deux joueurs
    print("\n" + "="*60)
    print("RESULTATS FINAUX".center(60))
    print("="*60)
    
    # Liste pour stocker les résultats des deux joueurs
    resultats = []
    
    # Lire les fichiers de résultats des deux joueurs
    for fichier in ["result_j1.txt", "result_j2.txt"]:
        if os.path.exists(fichier):
            with open(fichier, "r", encoding="utf-8") as f:
                lignes = f.readlines()
                nom = lignes[0].strip()
                score = int(lignes[1].strip())
                temps = float(lignes[2].strip())
                victoire = lignes[3].strip() == "True"  # Convertir string en booléen
                mot = lignes[4].strip()
                # Ajouter un tuple avec toutes les informations
                resultats.append((nom, score, temps, victoire, mot))
    
    # Vérifier que les deux joueurs ont terminé
    if len(resultats) != 2:
        print("En attente des résultats des deux joueurs...")
        return
    
    # Trier par score décroissant pour déterminer le gagnant
    resultats.sort(key=lambda x: x[1], reverse=True)
    
    # Afficher les résultats de chaque joueur
    for i, (nom, score, temps, victoire, mot) in enumerate(resultats, 1):
        statut = "VICTOIRE" if victoire else "DEFAITE"
        print(f"\n{i}. {nom}")
        print(f"   Statut: {statut}")
        print(f"   Mot: {mot.upper()}")
        print(f"   Score: {score} points")
        print(f"   Temps: {format_temps(temps)}")
    
    print("\n" + "="*60)
    
    # Déterminer et afficher le gagnant
    if resultats[0][1] > resultats[1][1]:
        print(f"GAGNANT: {resultats[0][0]} avec {resultats[0][1]} points!")
    elif resultats[0][1] == resultats[1][1]:
        print("EGALITE!")
    
    print("="*60)


def afficher_menu():
    
    print("\n" + "="*50)
    print("JEU DU PENDU".center(50))
    print("="*50)
    print("1. Jouer (solo)")
    print("2. Jouer à deux joueurs")
    print("3. Ajouter un mot")
    print("4. Voir le tableau des scores")
    print("5. Quitter")
    print("="*50)


def main():
    #Fonction principale 
    # Vérifier si le programme est lancé avec des arguments
    # (pour les fenêtres de joueurs séparées)
    if len(sys.argv) > 1:
        if sys.argv[1] == "joueur1":
            # Lancer le mode joueur 1
            jouer_mode_joueur("temp_j1.txt", "result_j1.txt")
            return
        elif sys.argv[1] == "joueur2":
            # Lancer le mode joueur 2
            jouer_mode_joueur("temp_j2.txt", "result_j2.txt")
            return
    
    # Initialiser les fichiers nécessaires
    initialiser_fichier_mots()
    initialiser_fichier_scores()
    
    # Afficher le message de bienvenue
    print("\nBienvenue dans le jeu du PENDU!")
    print("Version avec mode deux joueurs\n")
    
    # Boucle principale du menu
    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()
        
        # Traiter le choix de l'utilisateur
        if choix == "1":
            jouer()  # Lancer une partie solo
        elif choix == "2":
            jouer_deux_joueurs()  # Lancer le mode deux joueurs
        elif choix == "3":
            ajouter_mot()  # Ajouter un mot au fichier
        elif choix == "4":
            afficher_tableau_scores()  # Afficher les scores
        elif choix == "5":
            # Quitter le jeu
            print("\nMerci d'avoir joué! À bientôt!\n")
            break
        else:
            print("Choix invalide! Veuillez choisir entre 1 et 5.")


# Point d'entrée du programme
# Cette condition vérifie si le fichier est exécuté directement
if __name__ == "__main__":
    main()
    