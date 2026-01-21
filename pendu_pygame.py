import pygame
import random
import os
# Importation de la logique depuis le fichier main.py
from main import charger_mots, charger_dernier_profil, enregistrer_score, PenduLogic, charger_meilleurs_scores

# --- CONFIGURATION VISUELLE ---
WIDTH, HEIGHT = 1000, 600  # Fenêtre agrandie pour plus d'espace
BOARD_DARK = (35, 43, 38)     
CHALK_WHITE = (235, 235, 235)  
RED_CHALK = (210, 80, 80)      
YELLOW_CHALK = (240, 230, 140) 

class Particule:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(1, 3)
        self.vie = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vie -= 3

class PenduPygame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Le Pendu de l'École - Tableau d'Honneur")
        
        self.mots = charger_mots()
        self.profil = charger_dernier_profil()
        self.top_scores = charger_meilleurs_scores()
        
        # Nom du fichier son (assure-toi qu'il est bien renommé ou présent)
        self.nom_son = "craie.wav"
        try:
            self.son_craie = pygame.mixer.Sound(self.nom_son)
            self.son_craie.set_volume(0.6)
        except:
            self.son_craie = None
        
        # Texture du tableau noir
        self.surface_tableau = pygame.Surface((WIDTH, HEIGHT))
        self.surface_tableau.fill(BOARD_DARK)
        for _ in range(3000):
            x, y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
            s = pygame.Surface((random.randint(1, 2), random.randint(1, 2)))
            s.set_alpha(random.randint(5, 15))
            s.fill((255, 255, 255))
            self.surface_tableau.blit(s, (x, y))

        self.poussieres = []
        self.reset_game()
        self.font_main = pygame.font.SysFont("Comic Sans MS", 55)
        self.font_ui = pygame.font.SysFont("Comic Sans MS", 25)
        self.font_leader = pygame.font.SysFont("Comic Sans MS", 20)
        self.clock = pygame.time.Clock()

    def reset_game(self):
        self.jeu = PenduLogic(random.choice(self.mots), self.profil['jetons'])
        self.message = "Écris une lettre au clavier !"
        self.game_over = False
        self.top_scores = charger_meilleurs_scores()

    def jouer_son(self):
        if self.son_craie:
            self.son_craie.play()

    def draw_chalk_line(self, start, end, width=4):
        points = []
        dist = max(abs(end[0]-start[0]), abs(end[1]-start[1]))
        steps = dist // 5
        for i in range(steps + 1):
            x = start[0] + (end[0]-start[0]) * i / steps + random.randint(-1, 1)
            y = start[1] + (end[1]-start[1]) * i / steps + random.randint(-1, 1)
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(self.screen, CHALK_WHITE, False, points, width)

    def draw_leaderboard(self):
        # Positionné tout à droite
        start_x = 780 
        start_y = 50
        title = self.font_ui.render("TOP 5", True, YELLOW_CHALK)
        self.screen.blit(title, (start_x, start_y))
        
        for i, entry in enumerate(self.top_scores):
            txt = f"{i+1}. {entry['nom']} : {entry['score']} pts"
            score_surf = self.font_leader.render(txt, True, CHALK_WHITE)
            self.screen.blit(score_surf, (start_x, start_y + 40 + (i * 35)))

    def update_and_draw(self):
        # 1. Effacer le tableau
        self.screen.blit(self.surface_tableau, (0, 0))
        
        # 2. Poussières
        for p in self.poussieres[:]:
            p.update()
            if p.vie <= 0: self.poussieres.remove(p)
            else:
                s = pygame.Surface((2, 2))
                s.set_alpha(p.vie); s.fill((255, 255, 255))
                self.screen.blit(s, (p.x, p.y))

        # 3. Dessin du Pendu (DECALÉ À GAUCHE : Base x=30)
        base_x = 80
        corde_x = 230
        err = len(self.jeu.lettres_ratees)
        if err > 0: self.draw_chalk_line((base_x, 500), (base_x+150, 500), 6)   # Socle
        if err > 1: self.draw_chalk_line((base_x+50, 500), (base_x+50, 100), 6) # Poteau
        if err > 2: self.draw_chalk_line((base_x+50, 100), (corde_x, 100), 6)   # Potence
        if err > 3: self.draw_chalk_line((corde_x, 100), (corde_x, 160), 3)     # Corde
        if err > 4: pygame.draw.circle(self.screen, CHALK_WHITE, (corde_x, 190), 30, 3) # Tête
        if err > 5: # Tronc et bras
            self.draw_chalk_line((corde_x, 220), (corde_x, 350), 4)
            self.draw_chalk_line((corde_x, 250), (corde_x-40, 300), 4)
            self.draw_chalk_line((corde_x, 250), (corde_x+40, 300), 4)
        if err > 6: # Jambes
            self.draw_chalk_line((corde_x, 350), (corde_x-40, 430), 4)
            self.draw_chalk_line((corde_x, 350), (corde_x+40, 430), 4)

        # 4. Leaderboard à droite
        self.draw_leaderboard()

        # 5. Zone de Jeu (CENTRÉE entre le pendu et le leaderboard)
        play_center_x = 530 
        
        # Mot secret
        surf_mot = self.font_main.render(self.jeu.etat_mot(), True, CHALK_WHITE)
        rect_mot = surf_mot.get_rect(center=(play_center_x, 300))
        self.screen.blit(surf_mot, rect_mot)

        # Message
        surf_msg = self.font_ui.render(self.message, True, CHALK_WHITE)
        rect_msg = surf_msg.get_rect(center=(play_center_x, 180))
        self.screen.blit(surf_msg, rect_msg)

        # Fautes
        txt_fautes = f"Fautes: {', '.join(self.jeu.lettres_ratees)}"
        surf_fautes = self.font_ui.render(txt_fautes, True, RED_CHALK)
        rect_fautes = surf_fautes.get_rect(center=(play_center_x, 400))
        self.screen.blit(surf_fautes, rect_fautes)

        # UI Stats & Commandes
        self.screen.blit(self.font_ui.render(f"Jetons: {self.jeu.jetons}", True, CHALK_WHITE), (20, 20))
        surf_cmd = self.font_ui.render("[1] Thème (1j)  [2] Lettre (5j)", True, (180, 180, 180))
        rect_cmd = surf_cmd.get_rect(center=(play_center_x, 520))
        self.screen.blit(surf_cmd, rect_cmd)

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); return
                
                if not self.game_over and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        res = self.jeu.acheter_indice_theme()
                        if res: 
                            self.message = f"Thème: {res}"
                            self.jouer_son()
                        else: self.message = "Pas de jetons !"
                    elif event.key == pygame.K_2:
                        res = self.jeu.acheter_indice_lettre()
                        if res: 
                            self.message = f"Lettre: {res}"
                            self.jouer_son()
                        else: self.message = "Pas de jetons !"
                    elif event.unicode.isalpha():
                        lettre = event.unicode.upper()
                        if lettre not in self.jeu.lettres_trouvees and lettre not in self.jeu.lettres_ratees:
                            self.jouer_son()
                            if not self.jeu.proposer_lettre(lettre):
                                for _ in range(40): 
                                    self.poussieres.append(Particule(random.randint(100, 300), random.randint(150, 450)))
                
                elif self.game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_game()

            if not self.game_over:
                if set(self.jeu.mot_secret).issubset(self.jeu.lettres_trouvees):
                    self.message = "GAGNÉ ! +5j [R]ecommencer"; self.game_over = True
                    self.profil['score'] += 10; self.profil['jetons'] = self.jeu.jetons + 5
                    enregistrer_score(self.profil['nom'], self.profil['score'], self.profil['jetons'])
                elif len(self.jeu.lettres_ratees) >= self.jeu.erreurs_max:
                    self.message = f"PERDU... C'était {self.jeu.mot_secret} [R]"; self.game_over = True
                    self.profil['jetons'] = self.jeu.jetons
                    enregistrer_score(self.profil['nom'], self.profil['score'], self.profil['jetons'])

            self.update_and_draw()

if __name__ == "__main__":
    PenduPygame().run()