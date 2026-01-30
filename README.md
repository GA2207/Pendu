# Pendu 🎮 (Python / Pygame)

Jeu du **pendu** développé en **Python** avec **Pygame** : devine le mot lettre par lettre avant d’épuiser tes essais.  
Le projet inclut un **dictionnaire de mots**, une **gestion de score** et des **effets sonores** (victoire / défaite).  

## ✅ Fonctionnalités

- Jeu du pendu en interface graphique (Pygame)
- Mots chargés depuis un fichier (`mots.txt`)
- Sauvegarde/lecture des scores (`scores.txt`)
- Sons intégrés :
  - `victoire.wav`
  - `defaite.wav`
  - `craie.wav`

## 🧰 Prérequis

- Python 3.x
- Pygame

### Installation de Pygame :

pip install pygame

## ▶️ Lancer le jeu

Clone le dépôt puis lance le script principal :

git clone https://github.com/GA2207/Pendu.git
cd Pendu
python main.py
Si main.py sert juste de lanceur, tu peux aussi tester directement :

python pendu_pygame.py

## 🕹️ Comment jouer

Le jeu choisit un mot dans mots.txt

Tu proposes des lettres pour révéler le mot

Si tu trouves le mot → victoire

Si tu épuises tes essais → défaite

Le score est enregistré dans scores.txt

(Les touches exactes dépendent de l’interface, mais le principe reste celui-ci.)

## 📁 Structure du projet

Pendu/
├─ main.py
├─ pendu_pygame.py
├─ mots.txt
├─ scores.txt
├─ victoire.wav
├─ defaite.wav
├─ craie.wav
└─ README.md

## 🔧 Personnalisation

Ajouter des mots
Ajoute un mot par ligne dans mots.txt.

Réinitialiser les scores
Tu peux vider scores.txt (ou le supprimer puis relancer le jeu).

## 🚀 Idées d’amélioration (Roadmap)

Choix de difficulté (nombre d’essais)

Catégories de mots (animaux, villes, etc.)

Bouton “Rejouer”

Affichage du clavier à l’écran

Classement (Top 10) plus lisible

## 👤 Auteur

Guillaume Averbouch (GA2207)
Repo : https://github.com/GA2207/Pendu

## 📜 Licence

Projet personnel et pédagogique.

Projet pédagogique / personnel.
