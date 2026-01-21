import random
import os

# --- GESTION DES FICHIERS ---

def charger_mots(nom_fichier="mots.txt"):
    """Charge la liste des mots et leurs thèmes depuis le fichier."""
    mots = []
    try:
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                if ";" in ligne:
                    mots.append(ligne.strip().split(";"))
    except FileNotFoundError:
        # Création automatique si absent
        return [["PYTHON", "INFORMATIQUE"], ["PLATEFORME", "ECOLE"]]
    return mots

def charger_dernier_profil(nom_fichier="scores.txt"):
    """Récupère le dernier score et solde de jetons enregistré[cite: 1]."""
    profil = {"nom": "Joueur", "score": 0, "jetons": 10}
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            lignes = f.readlines()
            if lignes:
                # Format attendu : Nom;Score;Jetons [cite: 1]
                derniere = lignes[-1].strip().split(";")
                if len(derniere) >= 3:
                    profil = {"nom": derniere[0], "score": int(derniere[1]), "jetons": int(derniere[2])}
    return profil

def enregistrer_score(nom, score, jetons, nom_fichier="scores.txt"):
    """Sauvegarde les données de fin de partie[cite: 1]."""
    with open(nom_fichier, "a", encoding="utf-8") as f:
        f.write(f"{nom};{score};{jetons}\n")

# --- LOGIQUE MÉTIER ---

class PenduLogic:
    def __init__(self, mot_data, jetons_depart):
        self.mot_secret = mot_data[0].upper()
        self.theme = mot_data[1].upper()
        self.lettres_trouvees = set()
        self.lettres_ratees = set()
        self.jetons = jetons_depart
        self.erreurs_max = 7 # Selon le schéma classique

    def proposer_lettre(self, lettre):
        lettre = lettre.upper()
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
        """Affiche le mot avec des '_' pour les lettres manquantes."""
        return " ".join([l if l in self.lettres_trouvees else "_" for l in self.mot_secret])
    
def charger_meilleurs_scores(nom_fichier="scores.txt"):
    meilleurs_par_nom = {}
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                parts = ligne.strip().split(";")
                if len(parts) >= 2:
                    nom = parts[0]
                    score = int(parts[1])
                    # On ne garde que le score le plus haut pour ce nom
                    if nom not in meilleurs_par_nom or score > meilleurs_par_nom[nom]:
                        meilleurs_par_nom[nom] = score
    
    # Transformer le dictionnaire en liste triée
    scores_tries = [{"nom": n, "score": s} for n, s in meilleurs_par_nom.items()]
    scores_tries.sort(key=lambda x: x["score"], reverse=True)
    return scores_tries[:5]