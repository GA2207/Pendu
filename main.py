import random
import os

# --- GESTION DES FICHIERS ---

def charger_mots(nom_fichier="mots.txt"):
    """Charge la liste des mots et leurs thèmes."""
    mots = []
    try:
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                if ";" in ligne:
                    parts = ligne.strip().split(";")
                    if len(parts) >= 2:
                        mots.append((parts[0].upper(), parts[1].upper()))
    except FileNotFoundError:
        return [("PYTHON", "INFORMATIQUE"), ("ECOLE", "EDUCATION")]
    return mots

def ajouter_nouveau_mot(mot, theme, nom_fichier="mots.txt"):
    """Ajoute un nouveau mot dans le fichier."""
    with open(nom_fichier, "a", encoding="utf-8") as f:
        f.write(f"\n{mot.upper()};{theme.upper()}")

def charger_meilleurs_scores(nom_fichier="scores.txt"):
    """Retourne le Top 5 des scores (format : Nom : Mots trouvés)."""
    scores = []
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                parts = ligne.strip().split(";")
                if len(parts) >= 3:
                    # Format: Nom;MotsTrouves;Jetons
                    scores.append({"nom": parts[0], "score": int(parts[1]), "jetons": int(parts[2])})
    
    # Tri par score (nombre de mots trouvés) décroissant
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores[:5]

def enregistrer_score(nom, mots_trouves, jetons, nom_fichier="scores.txt"):
    """Enregistre le score à la fin de la session."""
    with open(nom_fichier, "a", encoding="utf-8") as f:
        f.write(f"{nom};{mots_trouves};{jetons}\n")

def charger_profil_joueur(nom, nom_fichier="scores.txt"):
    """Récupère les jetons d'un joueur existant ou initialise."""
    jetons = 0
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                parts = ligne.strip().split(";")
                if len(parts) >= 3 and parts[0] == nom:
                    # On prend le dernier solde de jetons connu pour ce joueur
                    jetons = int(parts[2])
    return jetons

# --- LOGIQUE DU JEU ---

class PenduLogic:
    def __init__(self, donnees_mot, jetons, erreurs_precedentes=None):
        self.mot_secret = donnees_mot[0]
        self.theme = donnees_mot[1]
        self.jetons = jetons
        self.lettres_trouvees = set()
        self.lettres_ratees = set()
        
        # Gestion du mode difficile (récupération des erreurs d'avant)
        if erreurs_precedentes:
            self.lettres_ratees = erreurs_precedentes
            
        self.erreurs_max = 7

    def proposer_lettre(self, lettre):
        lettre = lettre.upper()
        if lettre in self.lettres_trouvees or lettre in self.lettres_ratees:
            return False 

        if lettre in self.mot_secret:
            self.lettres_trouvees.add(lettre)
            return True
        else:
            self.lettres_ratees.add(lettre)
            return False

    def acheter_indice_theme(self):
        """Coût : 1 jeton."""
        if self.jetons >= 1:
            self.jetons -= 1
            return self.theme
        return None

    def acheter_indice_lettre(self):
        """Coût : 5 jetons."""
        if self.jetons >= 5:
            restantes = [l for l in self.mot_secret if l not in self.lettres_trouvees]
            if restantes:
                lettre = random.choice(restantes)
                self.lettres_trouvees.add(lettre)
                self.jetons -= 5
                return lettre
        return None

    def etat_mot(self):
        return " ".join([l if l in self.lettres_trouvees else "_" for l in self.mot_secret])