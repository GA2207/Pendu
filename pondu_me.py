import random
import os
import time  #  Pour le timer


def initialiser_fichier_mots():
    """Crée le fichier mots.txt s'il n'existe pas"""
    if not os.path.exists("mots.txt"):
        mots_defaut = [
            "python", "ordinateur", "programmation", "clavier", "souris",
            "ecran", "internet", "fichier", "algorithme", "fonction",
            "variable", "boucle", "condition", "tableau", "dictionnaire",
            "chaine", "nombre", "liste", "classe", "objet"
        ]
        with open("mots.txt", "w", encoding="utf-8") as f:
            for mot in mots_defaut:
                f.write(mot + "\n")
        print(" Fichier mots.txt créé avec 20 mots par défaut\n")


def initialiser_fichier_scores():
    """Crée le fichier scores.txt s'il n'existe pas"""
    if not os.path.exists("scores.txt"):
        with open("scores.txt", "w", encoding="utf-8") as f:
            f.write("")
        print(" Fichier scores.txt créé\n")


def charger_mots():
    """Charge tous les mots depuis le fichier"""
    with open("mots.txt", "r", encoding="utf-8") as f:
        mots = [ligne.strip().lower() for ligne in f if ligne.strip()]
    return mots


def ajouter_mot():
    """Permet d'ajouter un nouveau mot au fichier"""
    print("\n=== AJOUTER UN MOT ===")
    nouveau_mot = input("Entrez le nouveau mot : ").strip().lower()
    
    if not nouveau_mot.isalpha():
        print(" Le mot doit contenir uniquement des lettres!")
        return
    
    if len(nouveau_mot) < 4:
        print(" Le mot doit contenir au moins 4 lettres!")
        return
    
    mots_existants = charger_mots()
    if nouveau_mot in mots_existants:
        print(" Ce mot existe déjà!")
        return
    
    with open("mots.txt", "a", encoding="utf-8") as f:
        f.write(nouveau_mot + "\n")
    print(f" Le mot '{nouveau_mot}' a été ajouté!")


def sauvegarder_score(nom, score, difficulte, temps=None):

    #Sauvegarde le score d'un joueur
    
   # Ajout du temps et de la difficulté
    
    with open("scores.txt", "a", encoding="utf-8") as f:
        if temps:
            f.write(f"{nom},{score},{difficulte},{temps:.1f}\n")
        else:
            f.write(f"{nom},{score},{difficulte}\n")


def afficher_tableau_scores():
    #Affiche le tableau des meilleurs scores
    print("\n" + "="*70)
    print("TABLEAU DES SCORES ".center(70))
    print("="*70)
    
    if not os.path.exists("scores.txt") or os.path.getsize("scores.txt") == 0:
        print("Aucun score enregistré pour le moment.")
        print("="*70 + "\n")
        return
    
    scores = []
    with open("scores.txt", "r", encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                parties = ligne.strip().split(",")
                if len(parties) >= 3:
                    nom = parties[0]
                    score = int(parties[1])
                    difficulte = parties[2]
                    temps = float(parties[3]) if len(parties) >= 4 else None
                    scores.append((nom, score, difficulte, temps))
    
    # Trier par score décroissant
    scores.sort(key=lambda x: x[1], reverse=True)
    
    # En-tête
    print(f"{'Rang':<6}{'Joueur':<20}{'Score':>10}{'Difficulté':<15}{'Temps':>12}")
    print("-"*70)
    
    # Afficher top 10
    for i, (nom, score, diff, temps) in enumerate(scores[:10], 1):
        temps_str = f"{temps:.1f}s" if temps else "---"
        print(f"{i:<6}{nom:<20}{score:>10}{diff:<15}{temps_str:>12}")
    
    print("="*70 + "\n")


def dessiner_pendu(erreurs):
    
    etapes = [
        """
           ------
           |    |
           |
           |
           |
           |
        --------
        """,
        """
           ------
           |    |
           |    O
           |
           |
           |
        --------
        """,
        """
           ------
           |    |
           |    O
           |    |
           |
           |
        --------
        """,
        """
           ------
           |    |
           |    O
           |   /|
           |
           |
        --------
        """,
        """
           ------
           |    |
           |    O
           |   /|\\
           |
           |
        --------
        """,
        """
           ------
           |    |
           |    O
           |   /|\\
           |   /
           |
        --------
        """,
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
    print(etapes[min(erreurs, 6)])


def choisir_difficulte():
    """Permet de choisir le niveau de difficulté"""
    print("\n=== CHOISIR LA DIFFICULTÉ ===")
    print("1. Facile (10 essais)")
    print("2. Moyen (7 essais)")
    print("3. Difficile (5 essais)")
    
    while True:
        choix = input("Votre choix (1-3) : ").strip()
        if choix == "1":
            return 10, "Facile"
        elif choix == "2":
            return 7, "Moyen"
        elif choix == "3":
            return 5, "Difficile"
        else:
            print(" Choix invalide!")


def format_temps(secondes):
    
    minutes = int(secondes // 60)
    secs = int(secondes % 60)
    return f"{minutes:02d}:{secs:02d}"


def calculer_score(mot, erreurs, max_erreurs, difficulte, temps_ecoule=None):
    
    #Calcule le score en fonction de la performance
    
    # Bonus de temps ajouté

    # Score de base
    score_base = len(mot) * 10
    
    # Bonus difficulté
    bonus_difficulte = {"Facile": 1, "Moyen": 1.5, "Difficile": 2}
    
    # Bonus performance (essais restants)
    bonus_perfection = (max_erreurs - erreurs) * 5
    
    # Score intermédiaire
    score = int((score_base + bonus_perfection) * bonus_difficulte[difficulte])
    
    # NOUVEAU : Bonus temps
    if temps_ecoule is not None:
        if temps_ecoule < 30:
            score += 50
            print(" BONUS VITESSE : +50 points (< 30s)")
        elif temps_ecoule < 60:
            score += 30
            print(" BONUS VITESSE : +30 points (< 1min)")
        elif temps_ecoule < 120:
            score += 10
            print(" BONUS VITESSE : +10 points (< 2min)")
    
    return score


def jouer():
    """Lance une partie de pendu avec timer"""
    mots = charger_mots()
    if not mots:
        print(" Aucun mot disponible dans le fichier!")
        return
    
    mot_secret = random.choice(mots)
    max_erreurs, difficulte = choisir_difficulte()
    
    # NOUVEAU : Démarrer le chronomètre
    temps_debut = time.time()
    
    # Ajuster max_erreurs pour le dessin (max 6 étapes)
    erreurs_dessin_max = min(max_erreurs, 6)
    
    lettres_trouvees = set()
    lettres_essayees = set()
    erreurs = 0
    
    print(f"\n Début de la partie - Difficulté: {difficulte}")
    print(f" Chronomètre démarré!")  # NOUVEAU
    print(f"Le mot contient {len(mot_secret)} lettres")
    
    while erreurs < max_erreurs:
        # NOUVEAU : Calculer temps écoulé
        temps_ecoule = time.time() - temps_debut
        
        # Afficher l'état actuel
        mot_affiche = ""
        for lettre in mot_secret:
            if lettre in lettres_trouvees:
                mot_affiche += lettre + " "
            else:
                mot_affiche += "_ "
        
        print("\n" + "="*50)
        if erreurs <= erreurs_dessin_max:
            dessiner_pendu(min(erreurs, 6))
        
        # NOUVEAU : Afficher le temps
        print(f"  Temps écoulé: {format_temps(temps_ecoule)}")
        print(f"\nMot : {mot_affiche}")
        print(f"Erreurs : {erreurs}/{max_erreurs}")
        
        if lettres_essayees:
            print(f"Lettres essayées : {', '.join(sorted(lettres_essayees))}")
        
        # Vérifier si le mot est trouvé
        if all(lettre in lettres_trouvees for lettre in mot_secret):
            # NOUVEAU : Arrêter le chronomètre
            temps_final = time.time() - temps_debut
            
            print("\nBRAVO! Vous avez trouvé le mot:", mot_secret.upper())
            print(f" Temps total: {format_temps(temps_final)}")
            
            # Calculer score avec bonus temps
            score = calculer_score(mot_secret, erreurs, max_erreurs, difficulte, temps_final)
            print(f" Votre score: {score} points")
            
            nom = input("\nEntrez votre nom pour le tableau des scores: ").strip()
            if nom:
                sauvegarder_score(nom, score, difficulte, temps_final)
                print("Score enregistré!")
            return
        
        # Demander une lettre
        lettre = input("\nProposez une lettre : ").strip().lower()
        
        if len(lettre) != 1 or not lettre.isalpha():
            print(" Veuillez entrer une seule lettre!")
            continue
        
        if lettre in lettres_essayees:
            print(" Vous avez déjà essayé cette lettre!")
            continue
        
        lettres_essayees.add(lettre)
        
        if lettre in mot_secret:
            lettres_trouvees.add(lettre)
            print(f" Bien joué! La lettre '{lettre}' est dans le mot!")
        else:
            erreurs += 1
            print(f" Dommage! La lettre '{lettre}' n'est pas dans le mot.")
    
    # Partie perdue
    temps_final = time.time() - temps_debut
    print("\n" + "="*50)
    dessiner_pendu(6)
    print(f"\n PERDU! Le mot était: {mot_secret.upper()}")
    print(f" Temps total: {format_temps(temps_final)}")
    print("Meilleure chance la prochaine fois!")


def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*50)
    print(" JEU DU PENDU ".center(50))
    print("="*50)
    print("1. Jouer")
    print("2. Ajouter un mot")
    print("3. Voir le tableau des scores")
    print("4. Quitter")
    print("="*50)


def main():
    """Fonction principale du jeu"""
    initialiser_fichier_mots()
    initialiser_fichier_scores()
    
    print("\n Bienvenue dans le jeu du PENDU! ")
    print(" Version avec chronomètre activée\n")  # NOUVEAU
    
    while True:
        afficher_menu()
        choix = input("Votre choix : ").strip()
        
        if choix == "1":
            jouer()
        elif choix == "2":
            ajouter_mot()
        elif choix == "3":
            afficher_tableau_scores()
        elif choix == "4":
            print("\n Merci d'avoir joué! À bientôt!\n")
            break
        else:
            print(" Choix invalide! Veuillez choisir entre 1 et 4.")


if __name__ == "__main__":
    main()



