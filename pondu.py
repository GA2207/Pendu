import random
import os


def initialiser_fichier_mots():
    
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
        print("✓ Fichier mots.txt créé avec 20 mots par défaut\n")

def initialiser_fichier_scores():
    """Crée le fichier scores.txt s'il n'existe pas"""
    if not os.path.exists("scores.txt"):
        with open("scores.txt", "w", encoding="utf-8") as f:
            f.write("")
        print("✓ Fichier scores.txt créé\n")

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
        print("❌ Le mot doit contenir uniquement des lettres!")
        return
    
    mots_existants = charger_mots()
    if nouveau_mot in mots_existants:
        print("❌ Ce mot existe déjà!")
        return
    
    with open("mots.txt", "a", encoding="utf-8") as f:
        f.write(nouveau_mot + "\n")
    print(f"✓ Le mot '{nouveau_mot}' a été ajouté!")

def sauvegarder_score(nom, score):
    """Sauvegarde le score d'un joueur"""
    with open("scores.txt", "a", encoding="utf-8") as f:
        f.write(f"{nom},{score}\n")

def afficher_tableau_scores():
    """Affiche le tableau des meilleurs scores"""
    print("\n" + "="*50)
    print("🏆 TABLEAU DES SCORES 🏆".center(50))
    print("="*50)
    
    if not os.path.exists("scores.txt") or os.path.getsize("scores.txt") == 0:
        print("Aucun score enregistré pour le moment.")
        print("="*50 + "\n")
        return
    
    scores = []
    with open("scores.txt", "r", encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip():
                parties = ligne.strip().split(",")
                if len(parties) == 2:
                    nom, score = parties
                    scores.append((nom, int(score)))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    
    print(f"{'Rang':<8}{'Joueur':<25}{'Score':>15}")
    print("-"*50)
    
    for i, (nom, score) in enumerate(scores[:10], 1):
        print(f"{i:<8}{nom:<25}{score:>15}")
    
    print("="*50 + "\n")

# ========== FONCTIONS POUR LE DESSIN DU PENDU ==========

def dessiner_pendu(erreurs):
    """Dessine le pendu selon le nombre d'erreurs"""
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
    print(etapes[erreurs])

# ========== FONCTIONS POUR LE JEU ==========

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
            print("❌ Choix invalide!")

def calculer_score(mot, erreurs, max_erreurs, difficulte):
    """Calcule le score en fonction de la performance"""
    score_base = len(mot) * 10
    bonus_difficulte = {"Facile": 1, "Moyen": 1.5, "Difficile": 2}
    bonus_perfection = (max_erreurs - erreurs) * 5
    
    score_total = int((score_base + bonus_perfection) * bonus_difficulte[difficulte])
    return score_total

def jouer():
    """Lance une partie de pendu"""
    mots = charger_mots()
    if not mots:
        print("❌ Aucun mot disponible dans le fichier!")
        return
    
    mot_secret = random.choice(mots)
    max_erreurs, difficulte = choisir_difficulte()
    
    # Ajuster max_erreurs pour le dessin (max 6 étapes)
    erreurs_dessin_max = min(max_erreurs, 6)
    
    lettres_trouvees = set()
    lettres_essayees = set()
    erreurs = 0
    
    print(f"\n🎮 Début de la partie - Difficulté: {difficulte}")
    print(f"Le mot contient {len(mot_secret)} lettres")
    
    while erreurs < max_erreurs:
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
        print(f"\nMot : {mot_affiche}")
        print(f"Erreurs : {erreurs}/{max_erreurs}")
        if lettres_essayees:
            print(f"Lettres essayées : {', '.join(sorted(lettres_essayees))}")
        
        # Vérifier si le mot est trouvé
        if all(lettre in lettres_trouvees for lettre in mot_secret):
            print("\n🎉 BRAVO! Vous avez trouvé le mot:", mot_secret.upper())
            score = calculer_score(mot_secret, erreurs, max_erreurs, difficulte)
            print(f"🏆 Votre score: {score} points")
            
            nom = input("\nEntrez votre nom pour le tableau des scores: ").strip()
            if nom:
                sauvegarder_score(nom, score)
                print("✓ Score enregistré!")
            return
        
        # Demander une lettre
        lettre = input("\nProposez une lettre : ").strip().lower()
        
        if len(lettre) != 1 or not lettre.isalpha():
            print("❌ Veuillez entrer une seule lettre!")
            continue
        
        if lettre in lettres_essayees:
            print("❌ Vous avez déjà essayé cette lettre!")
            continue
        
        lettres_essayees.add(lettre)
        
        if lettre in mot_secret:
            lettres_trouvees.add(lettre)
            print(f"✓ Bien joué! La lettre '{lettre}' est dans le mot!")
        else:
            erreurs += 1
            print(f"✗ Dommage! La lettre '{lettre}' n'est pas dans le mot.")
    
    # Partie perdue
    print("\n" + "="*50)
    dessiner_pendu(6)
    print(f"\n💀 PERDU! Le mot était: {mot_secret.upper()}")
    print("Meilleure chance la prochaine fois!")

# ========== MENU PRINCIPAL ==========

def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "="*50)
    print("🎮 JEU DU PENDU 🎮".center(50))
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
    
    print("\n🎮 Bienvenue dans le jeu du PENDU! 🎮\n")
    
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
            print("\n👋 Merci d'avoir joué! À bientôt!\n")
            break
        else:
            print("❌ Choix invalide! Veuillez choisir entre 1 et 4.")

# ========== LANCEMENT DU JEU ==========

if __name__ == "__main__":
    main()