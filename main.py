import random
import os
import sys
import subprocess

#  FICHIERS / DONNÉES
#  Ici on gère tout ce qui touche aux fichiers : mots.txt et scores.txt

def charger_mots(nom_fichier="mots.txt"):
    """Charge la liste des mots et leurs thèmes depuis mots.txt.
    Format attendu par ligne : MOT;THEME
    """
    mots = []
    try:
        # On lit le fichier, une ligne = un mot + un thème
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                # On ignore les lignes "bizarres" / vides (pas de ';')
                if ";" in ligne:
                    parts = ligne.strip().split(";")
                    if len(parts) >= 2:
                        # On met en majuscules pour éviter les surprises (accents à part)
                        mots.append((parts[0].upper(), parts[1].upper()))
    except FileNotFoundError:
        # Petit filet de sécurité : si mots.txt n’existe pas,
        # on renvoie une mini liste pour que le jeu ne plante pas.
        return [("PYTHON", "INFORMATIQUE"), ("ECOLE", "EDUCATION")]
    return mots


def ajouter_nouveau_mot(mot, theme, nom_fichier="mots.txt"):
    """Ajoute un mot dans le fichier mots.txt (à la fin)."""
    # on ajoute un \n au début pour être sûr d’aller à la ligne
    with open(nom_fichier, "a", encoding="utf-8") as f:
        f.write(f"\n{mot.upper()};{theme.upper()}")


def charger_meilleurs_scores(nom_fichier="scores.txt"):
    """Retourne le Top 5 des scores.
    Format attendu : Nom;MotsTrouves;Jetons
    """
    scores = []
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                parts = ligne.strip().split(";")
                if len(parts) >= 3:
                    # On stocke sous forme de dictionnaire : plus simple à trier / afficher
                    scores.append({
                        "nom": parts[0],
                        "score": int(parts[1]),
                        "jetons": int(parts[2]),
                    })

    # Tri décroissant sur le nombre de mots trouvés
    scores.sort(key=lambda x: x["score"], reverse=True)

    # On garde seulement les 5 premiers (tableau d'honneur)
    return scores[:5]


def enregistrer_score(nom, mots_trouves, jetons, nom_fichier="scores.txt"):
    """Ajoute une ligne de score dans scores.txt."""
    # Ici on "append" à chaque fin de session, ça permet de garder un historique.
    with open(nom_fichier, "a", encoding="utf-8") as f:
        f.write(f"{nom};{mots_trouves};{jetons}\n")


def charger_profil_joueur(nom, nom_fichier="scores.txt"):
    """Récupère les jetons d'un joueur existant.
    Si on trouve plusieurs lignes, on prend la dernière (la plus récente).
    """
    jetons = 0
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                parts = ligne.strip().split(";")
                if len(parts) >= 3 and parts[0] == nom:
                    # On écrase à chaque fois : au final, on garde la dernière valeur vue
                    jetons = int(parts[2])
    return jetons


#  LOGIQUE DU JEU
#  Cette classe ne dessine rien : elle gère juste les règles du pendu.

class PenduLogic:
    def __init__(self, donnees_mot, jetons, erreurs_precedentes=None):
        # donnees_mot = (mot, thème)
        self.mot_secret = donnees_mot[0]
        self.theme = donnees_mot[1]

        # Les jetons servent à acheter des indices
        self.jetons = jetons

        # Lettres déjà trouvées / ratées
        self.lettres_trouvees = set()
        self.lettres_ratees = set()

        # Petite règle du mode DIFFICILE :
        # on garde les erreurs de la manche précédente
        if erreurs_precedentes:
            self.lettres_ratees = erreurs_precedentes

        # Nombre max d'erreurs avant la défaite
        self.erreurs_max = 7

    def proposer_lettre(self, lettre):
        """Teste une lettre. Retourne True si la lettre est dans le mot, sinon False."""
        lettre = lettre.upper()

        # Si déjà essayé, on ne compte pas et on renvoie False
        if lettre in self.lettres_trouvees or lettre in self.lettres_ratees:
            return False

        if lettre in self.mot_secret:
            self.lettres_trouvees.add(lettre)
            return True
        else:
            self.lettres_ratees.add(lettre)
            return False

    def etat_mot(self):
        """Affichage du mot avec _ pour les lettres non trouvées."""
        return " ".join([l if l in self.lettres_trouvees else "_" for l in self.mot_secret])

    def acheter_indice_theme(self):
        """Indice simple : révèle le thème (coûte 1 jeton)."""
        if self.jetons >= 1:
            self.jetons -= 1
            return self.theme
        return None

    def acheter_indice_lettre(self):
        """Indice plus fort : révèle une lettre du mot (coûte 5 jetons)."""
        if self.jetons >= 5:
            self.jetons -= 5

            # On cherche une lettre pas encore trouvée
            lettres_possibles = [l for l in set(self.mot_secret) if l not in self.lettres_trouvees]
            if lettres_possibles:
                lettre = random.choice(lettres_possibles)
                self.lettres_trouvees.add(lettre)
                return lettre

        # Pas assez de jetons OU plus de lettres à révéler
        return None


#  MODE 2 JOUEURS (Pygame en 2 fenêtres)
#  Ici on ne “joue” pas directement : on lance 2 fois pendu_pygame.py
#  avec une configuration différente pour chaque joueur.

def jouer_deux_joueurs_pygame():
    """Lance 2 parties Pygame dans 2 fenêtres différentes (un mot différent par joueur)."""
    print("\n=== MODE DEUX JOUEURS (PYGAME) ===")

    # On demande les noms "dans le terminal" (c’est volontaire : simple à gérer)
    nom_j1 = input("Nom du Joueur 1 : ").strip() or "Joueur 1"
    nom_j2 = input("Nom du Joueur 2 : ").strip() or "Joueur 2"

    # Même difficulté pour les deux (sinon ça devient dur de comparer)
    difficulte = input("Difficulté (FACILE / MOYEN / DIFFICILE) : ").strip().upper() or "MOYEN"
    if difficulte not in ("FACILE", "MOYEN", "DIFFICILE"):
        # Si l’utilisateur tape n’importe quoi, on retombe sur un choix safe
        difficulte = "MOYEN"

    # On récupère les mots disponibles
    mots = charger_mots()
    if len(mots) < 2:
        print("Il faut au moins 2 mots dans mots.txt.")
        return

    # Mélange pour ne pas retomber toujours sur les mêmes
    random.shuffle(mots)
    (mot1, theme1), (mot2, theme2) = mots[0], mots[1]

    # On calcule le dossier du projet pour lancer le bon fichier,
    # même si on exécute le script depuis un autre endroit
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pygame_script = os.path.join(base_dir, "pendu_pygame.py")

    # on passe la config via une variable d'environnement
    # Format : NOM|MOT|THEME|DIFFICULTE
    env1 = os.environ.copy()
    env1["PENDU_CONFIG"] = f"{nom_j1}|{mot1}|{theme1}|{difficulte}"

    env2 = os.environ.copy()
    env2["PENDU_CONFIG"] = f"{nom_j2}|{mot2}|{theme2}|{difficulte}"

    # On lance 2 processus indépendants → 2 fenêtres Pygame
    subprocess.Popen([sys.executable, pygame_script], env=env1, cwd=base_dir)
    subprocess.Popen([sys.executable, pygame_script], env=env2, cwd=base_dir)

    print("\n✅ Deux fenêtres Pygame ont été lancées.")
