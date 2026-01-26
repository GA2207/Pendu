import pygame
import random
import time
import os
import sys
import subprocess
from main import (
    charger_mots, ajouter_nouveau_mot, PenduLogic,
    charger_meilleurs_scores, enregistrer_score, charger_profil_joueur
)

# --- CONFIGURATION VISUELLE ---
BOARD_DARK = (35, 43, 38)
CHALK_WHITE = (235, 235, 235)
RED_CHALK = (210, 80, 80)
YELLOW_CHALK = (240, 230, 140)
GREEN_CHALK = (100, 200, 100)

# États du jeu
STATE_LOGIN = 0
STATE_MENU = 1
STATE_DIFFICULTY = 2
STATE_GAME = 3
STATE_GAMEOVER = 4
STATE_ADD_WORD = 5
STATE_PLAYER_COUNT = 6
STATE_MULTI_NAMES = 7
STATE_MULTI_DIFFICULTY = 8


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
        self.vie -= 5


class PenduPygame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Le Pendu de l'École - Arcade Edition")

        self.W, self.H = self.screen.get_size()

        self.mots = charger_mots()
        self.top_scores = charger_meilleurs_scores()

        # Sons
        self.sons = {}
        try:
            self.sons['craie'] = pygame.mixer.Sound("craie.wav")
            self.sons['craie'].set_volume(0.5)
            self.sons['victoire'] = pygame.mixer.Sound("victoire.wav")
            self.sons['defaite'] = pygame.mixer.Sound("defaite.wav")
        except:
            print("Certains sons sont manquants (victoire.wav, defaite.wav ou craie.wav)")

        # Polices
        self.font_title = pygame.font.SysFont("Comic Sans MS", 60)
        self.font_main = pygame.font.SysFont("Comic Sans MS", 40)
        self.font_ui = pygame.font.SysFont("Comic Sans MS", 25)
        self.font_leader = pygame.font.SysFont("Comic Sans MS", 22)

        # Variables globales
        self.clock = pygame.time.Clock()
        self.input_text = ""
        self.poussieres = []

        # Variables de session (solo)
        self.difficulte = "MOYEN"
        self.session_score = 0
        self.session_jetons = 0
        self.start_time = 0
        self.time_limit = 60
        self.logic = None
        self.message = ""
        self.message_time = 0
        self.message_duration_ms = 2000  # 2 secondes
        self.nom_joueur = ""

        # --- MULTI (2 joueurs / 1 seul clavier / tour par tour / pas de timer) ---
        self.is_multiplayer = False
        self.players = []          # [{"nom": ..., "logic": ...}, {"nom": ..., "logic": ...}]
        self.current_player = 0
        self.multi_result = ""

        # État de départ
        self.state = STATE_LOGIN

        # Rectangles de boutons
        self.rect_jouer = None
        self.rect_ajouter = None
        self.rect_quitter = None
        self.rect_facile = None
        self.rect_moyen = None
        self.rect_difficile = None
        self.rect_retour = None

        self.rect_1p = None
        self.rect_2p = None
        self.rect_player_retour = None

        self.rect_multi_facile = None
        self.rect_multi_moyen = None
        self.rect_multi_difficile = None
        self.rect_multi_retour = None

        # Saisie mode 2 joueurs
        self.multi_nom_j1 = ""
        self.multi_nom_j2 = ""
        self.multi_etape_nom = 1  # 1 = saisie J1, 2 = saisie J2

        # Fond + potence fixe
        self.generer_fond()
        self.potence_surface = None
        self.potence_cache_size = None
        self.build_potence_surface()

    #  FOND PLEIN ÉCRAN
    def generer_fond(self):
        self.surface_tableau = pygame.Surface((self.W, self.H)).convert()
        self.surface_tableau.fill(BOARD_DARK)

        nb_points = int((self.W * self.H) / 200)
        for _ in range(nb_points):
            x, y = random.randint(0, self.W - 1), random.randint(0, self.H - 1)
            c = random.randint(40, 65)
            self.surface_tableau.set_at((x, y), (c, c, c))

    #  POTENCE FIXE (cachée)
    def build_potence_surface(self):
        self.potence_surface = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        self.potence_cache_size = (self.W, self.H)

        x0 = 90
        y_sol = self.H - 170
        y_top = 140

        pole_x = x0 + 70
        beam_len = 190

        pygame.draw.line(self.potence_surface, CHALK_WHITE, (x0, y_sol), (x0 + 180, y_sol), 6)
        pygame.draw.line(self.potence_surface, CHALK_WHITE, (pole_x, y_sol), (pole_x, y_top), 6)
        pygame.draw.line(self.potence_surface, CHALK_WHITE, (pole_x, y_top), (pole_x + beam_len, y_top), 6)
        pygame.draw.line(self.potence_surface, CHALK_WHITE, (pole_x + beam_len, y_top), (pole_x + beam_len, y_top + 35), 6)

    #  REDIMENSIONNEMENT
    def on_resize(self, size):
        self.W, self.H = size
        self.screen = pygame.display.set_mode((self.W, self.H), pygame.RESIZABLE)
        self.generer_fond()
        self.build_potence_surface()

    #  UTILITAIRES TEXTE / UI
    def draw_text_centered(self, text, y, font, color=CHALK_WHITE):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.W // 2, y))
        self.screen.blit(surf, rect)

    def draw_button(self, text, center_y, font, mouse_pos):
        rect_width = 380
        rect_height = 70
        rect_x = self.W // 2 - rect_width // 2
        rect_y = center_y - rect_height // 2
        rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)

        is_hovered = rect.collidepoint(mouse_pos)
        color = YELLOW_CHALK if is_hovered else CHALK_WHITE
        bg_alpha = 40 if is_hovered else 0

        if bg_alpha > 0:
            s = pygame.Surface((rect_width, rect_height)).convert_alpha()
            s.set_alpha(bg_alpha)
            s.fill((255, 255, 255))
            self.screen.blit(s, (rect.x, rect.y))

        pygame.draw.rect(self.screen, color, rect, 3, border_radius=10)

        surf = font.render(text, True, color)
        text_rect = surf.get_rect(center=rect.center)
        self.screen.blit(surf, text_rect)

        return rect

    #  ÉCRANS (DRAW)
    def update_and_draw(self):
        self.screen.blit(self.surface_tableau, (0, 0))

        if self.state == STATE_LOGIN:
            self.draw_text_centered("BIENVENUE EN CLASSE", 120, self.font_title, YELLOW_CHALK)
            self.draw_text_centered("Écris ton nom pour commencer :", 250, self.font_ui)

            input_rect = pygame.Rect(self.W // 2 - 300, 320, 600, 70)
            pygame.draw.rect(self.screen, CHALK_WHITE, input_rect, 2)
            self.draw_text_centered(self.input_text + "_", 355, self.font_main, YELLOW_CHALK)

        elif self.state == STATE_MENU:
            self.draw_text_centered("MENU PRINCIPAL", 120, self.font_title, YELLOW_CHALK)
            mouse_pos = pygame.mouse.get_pos()
            self.rect_jouer = self.draw_button("JOUER", 260, self.font_main, mouse_pos)
            self.rect_ajouter = self.draw_button("AJOUTER UN MOT", 360, self.font_main, mouse_pos)
            self.rect_quitter = self.draw_button("QUITTER", 460, self.font_main, mouse_pos)

            if self.nom_joueur:
                self.draw_text_centered(f"Joueur : {self.nom_joueur}", 600, self.font_ui, CHALK_WHITE)
                self.draw_text_centered(f"Jetons : {self.session_jetons}", 640, self.font_ui, YELLOW_CHALK)

        elif self.state == STATE_PLAYER_COUNT:
            self.draw_text_centered("CHOISIS LE MODE", 120, self.font_title, YELLOW_CHALK)
            mouse_pos = pygame.mouse.get_pos()
            self.rect_1p = self.draw_button("1 JOUEUR", 300, self.font_main, mouse_pos)
            self.rect_2p = self.draw_button("2 JOUEURS", 400, self.font_main, mouse_pos)
            self.rect_player_retour = self.draw_button("RETOUR", 520, self.font_main, mouse_pos)

        elif self.state == STATE_MULTI_NAMES:
            self.draw_text_centered("MODE 2 JOUEURS", 120, self.font_title, YELLOW_CHALK)
            prompt = "Nom Joueur 1 :" if self.multi_etape_nom == 1 else "Nom Joueur 2 :"
            self.draw_text_centered(prompt, 250, self.font_ui, CHALK_WHITE)

            input_rect = pygame.Rect(self.W // 2 - 300, 320, 600, 70)
            pygame.draw.rect(self.screen, CHALK_WHITE, input_rect, 2)
            self.draw_text_centered(self.input_text + "_", 355, self.font_main, YELLOW_CHALK)

            self.draw_text_centered("Entrée : valider / Échap : retour", 450, self.font_ui, CHALK_WHITE)

        elif self.state == STATE_DIFFICULTY:
            self.draw_text_centered("CHOISIS LA DIFFICULTÉ", 120, self.font_title, YELLOW_CHALK)
            mouse_pos = pygame.mouse.get_pos()
            self.rect_facile = self.draw_button("FACILE", 260, self.font_main, mouse_pos)
            self.rect_moyen = self.draw_button("MOYEN", 360, self.font_main, mouse_pos)
            self.rect_difficile = self.draw_button("DIFFICILE", 460, self.font_main, mouse_pos)
            self.rect_retour = self.draw_button("RETOUR", 580, self.font_main, mouse_pos)

        elif self.state == STATE_MULTI_DIFFICULTY:
            self.draw_text_centered("DIFFICULTÉ (2 JOUEURS)", 120, self.font_title, YELLOW_CHALK)
            mouse_pos = pygame.mouse.get_pos()
            self.rect_multi_facile = self.draw_button("FACILE", 260, self.font_main, mouse_pos)
            self.rect_multi_moyen = self.draw_button("MOYEN", 360, self.font_main, mouse_pos)
            self.rect_multi_difficile = self.draw_button("DIFFICILE", 460, self.font_main, mouse_pos)
            self.rect_multi_retour = self.draw_button("RETOUR", 580, self.font_main, mouse_pos)

        elif self.state == STATE_GAME:
            if self.logic is not None:
                self.draw_game_interface()
            else:
                self.draw_text_centered("Chargement...", self.H // 2, self.font_main, CHALK_WHITE)

        elif self.state == STATE_ADD_WORD:
            self.draw_text_centered("AJOUTER UN MOT", 120, self.font_title, YELLOW_CHALK)
            self.draw_text_centered("Écris : mot;theme  puis Entrée", 220, self.font_ui, CHALK_WHITE)

            input_rect = pygame.Rect(self.W // 2 - 300, 300, 600, 70)
            pygame.draw.rect(self.screen, CHALK_WHITE, input_rect, 2)
            self.draw_text_centered(self.input_text + "_", 335, self.font_main, YELLOW_CHALK)

            self.draw_text_centered("Échap : retour menu", 420, self.font_ui, CHALK_WHITE)

        elif self.state == STATE_GAMEOVER:
            self.draw_text_centered("FIN DE PARTIE", 160, self.font_title, RED_CHALK)

            if self.is_multiplayer:
                self.draw_text_centered(self.multi_result, 260, self.font_ui, CHALK_WHITE)
                self.draw_text_centered("Appuie sur ESPACE pour revenir au menu", 360, self.font_ui, CHALK_WHITE)
            else:
                self.draw_text_centered(f"Score : {self.session_score}", 260, self.font_main, CHALK_WHITE)
                self.draw_text_centered("Appuie sur ESPACE pour revenir au menu", 360, self.font_ui, CHALK_WHITE)

        if self.state in (
            STATE_LOGIN, STATE_MENU, STATE_PLAYER_COUNT, STATE_MULTI_NAMES,
            STATE_MULTI_DIFFICULTY, STATE_DIFFICULTY, STATE_ADD_WORD, STATE_GAMEOVER
        ):
            self.draw_leaderboard_box()

        pygame.display.flip()

    def draw_leaderboard_box(self):
        MARGIN = 30
        BOX_WIDTH = 300
        BOX_HEIGHT = 320

        start_x = self.W - BOX_WIDTH - MARGIN
        start_y = 180

        box = pygame.Rect(start_x, start_y, BOX_WIDTH, BOX_HEIGHT)

        bg = pygame.Surface((BOX_WIDTH, BOX_HEIGHT)).convert_alpha()
        bg.set_alpha(30)
        bg.fill((255, 255, 255))
        self.screen.blit(bg, (start_x, start_y))

        pygame.draw.rect(self.screen, CHALK_WHITE, box, 2, border_radius=8)

        title = self.font_ui.render("TABLEAU D'HONNEUR", True, YELLOW_CHALK)
        self.screen.blit(title, (start_x + 20, start_y + 15))

        pygame.draw.line(self.screen, CHALK_WHITE, (start_x + 15, start_y + 50), (start_x + BOX_WIDTH - 15, start_y + 50), 1)

        for i, entry in enumerate(self.top_scores[:6]):
            txt = f"{i + 1}. {entry['nom'][:10]}  {entry['score']}"
            color = GREEN_CHALK if entry['nom'] == self.nom_joueur else CHALK_WHITE
            line = self.font_leader.render(txt, True, color)
            self.screen.blit(line, (start_x + 20, start_y + 70 + i * 35))

    def draw_game_interface(self):
        # Timer uniquement en SOLO
        if not self.is_multiplayer:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            remaining = max(0, self.time_limit - elapsed)
            color_time = RED_CHALK if remaining < 10 else CHALK_WHITE
            self.screen.blit(self.font_title.render(f"{int(remaining)}s", True, color_time), (self.W - 150, 20))
        else:
            remaining = None

        # HUD
        if not self.is_multiplayer:
            self.screen.blit(self.font_ui.render(f"Score: {self.session_score}", True, GREEN_CHALK), (20, 20))
            self.screen.blit(self.font_ui.render(f"Jetons: {self.logic.jetons}", True, YELLOW_CHALK), (20, 50))
        else:
            p = self.players[self.current_player]["nom"]
            self.draw_text_centered(f"TOUR DE : {p}", 120, self.font_ui, YELLOW_CHALK)
            self.screen.blit(self.font_ui.render(f"Jetons: {self.logic.jetons}", True, YELLOW_CHALK), (20, 20))

        self.draw_pendu(len(self.logic.lettres_ratees))

        center_x = self.W // 2 + 50
        self.draw_text_centered(self.logic.etat_mot(), 300, self.font_title)

        # Message : permanent si message_time == 0, temporaire sinon
        if self.message:
            if self.message_time > 0:
                if (pygame.time.get_ticks() - self.message_time) <= self.message_duration_ms:
                    self.draw_text_centered(self.message, 200, self.font_ui)
                else:
                    self.message = ""
                    self.message_time = 0
            else:
                self.draw_text_centered(self.message, 200, self.font_ui)

        fautes = f"Fautes: {', '.join(self.logic.lettres_ratees)}"
        surf_f = self.font_ui.render(fautes, True, RED_CHALK)
        self.screen.blit(surf_f, surf_f.get_rect(center=(center_x, 400)))

        self.draw_text_centered("[1] Thème (1j)  [2] Lettre (5j)", 520, self.font_ui)

        # Fin de partie
        if not self.is_multiplayer:
            if remaining <= 0:
                self.game_over(victoire=False)
            elif len(self.logic.lettres_ratees) >= 7:
                self.game_over(victoire=False)
        else:
            if len(self.logic.lettres_ratees) >= 7:
                loser = self.current_player
                winner = 1 - self.current_player
                self.finish_multiplayer(winner, loser, f"{self.players[loser]['nom']} a perdu ! Gagnant : {self.players[winner]['nom']}")

    def draw_pendu(self, err):
        if self.potence_surface is None or self.potence_cache_size != (self.W, self.H):
            self.build_potence_surface()

        x0 = 90
        y_sol = self.H - 170
        y_top = 140

        pole_x = x0 + 70
        beam_len = 190

        x_hook = pole_x + beam_len
        y_beam = y_top
        rope_h = 35

        head_r = 22
        body_len = 90

        if err >= 1:
            self.screen.blit(self.potence_surface, (0, 0))


        x_head = x_hook
        y_head = y_beam + rope_h + head_r

        if err >= 2:
            pygame.draw.circle(self.screen, CHALK_WHITE, (x_head, y_head), head_r, 4)
        if err >= 3:
            pygame.draw.line(self.screen, CHALK_WHITE, (x_head, y_head + head_r), (x_head, y_head + head_r + body_len), 4)
        if err >= 4:
            pygame.draw.line(self.screen, CHALK_WHITE, (x_head, y_head + head_r + 20), (x_head - 40, y_head + head_r + 55), 4)
        if err >= 5:
            pygame.draw.line(self.screen, CHALK_WHITE, (x_head, y_head + head_r + 20), (x_head + 40, y_head + head_r + 55), 4)
        if err >= 6:
            pygame.draw.line(self.screen, CHALK_WHITE, (x_head, y_head + head_r + body_len), (x_head - 35, y_head + head_r + body_len + 55), 4)
        if err >= 7:
            pygame.draw.line(self.screen, CHALK_WHITE, (x_head, y_head + head_r + body_len), (x_head + 35, y_head + head_r + body_len + 55), 4)
        if err >= 8:
            pygame.draw.line(self.screen, RED_CHALK, (x_head - 10, y_head - 10), (x_head + 10, y_head + 10), 4)
            pygame.draw.line(self.screen, RED_CHALK, (x_head + 10, y_head - 10), (x_head - 10, y_head + 10), 4)

        # Particules
        for p in self.poussieres[:]:
            p.update()
            if p.vie <= 0:
                self.poussieres.remove(p)
                continue
            pygame.draw.circle(self.screen, (255, 255, 255, p.vie), (int(p.x), int(p.y)), 2)

    #  LOGIQUE JEU (DÉMARRAGE / SUITE)
    def start_game_session(self, difficulte):
        self.is_multiplayer = False
        self.difficulte = difficulte
        self.session_score = 0
        self.session_jetons = charger_profil_joueur(self.nom_joueur)
        self.start_time = pygame.time.get_ticks()

        if difficulte == "FACILE":
            self.time_limit = 90
        elif difficulte == "MOYEN":
            self.time_limit = 60
        else:
            self.time_limit = 45

        mot = random.choice(self.mots)
        self.logic = PenduLogic(mot, self.session_jetons)
        self.message = ""
        self.message_time = 0
        self.state = STATE_GAME

    def next_word(self, erreurs_a_garder=0):
        mot = random.choice(self.mots)
        self.logic = PenduLogic(mot, self.session_jetons, erreurs_a_garder)
        self.message = "Nouveau mot ! Bonne chance."

    def start_multiplayer_session(self, difficulte):
        self.is_multiplayer = True
        self.difficulte = difficulte
        self.multi_result = ""
        self.message = ""
        self.message_time = 0

        mots = charger_mots()
        if len(mots) < 2:
            self.is_multiplayer = False
            self.message = "Il faut au moins 2 mots dans mots.txt."
            self.state = STATE_MENU
            return

        mots_choisis = random.sample(mots, 2)
        self.players = [
            {"nom": self.multi_nom_j1 if self.multi_nom_j1 else "Joueur 1", "logic": PenduLogic(mots_choisis[0], 10)},
            {"nom": self.multi_nom_j2 if self.multi_nom_j2 else "Joueur 2", "logic": PenduLogic(mots_choisis[1], 10)},
        ]
        self.current_player = 0
        self.logic = self.players[self.current_player]["logic"]
        self.state = STATE_GAME

    def finish_multiplayer(self, winner, loser, text):
        self.multi_result = text
        self.play_sound('victoire')
        self.state = STATE_GAMEOVER

    def game_over(self, victoire):
        if victoire:
            self.play_sound('victoire')
        else:
            self.play_sound('defaite')

        if not self.is_multiplayer and self.nom_joueur:
            enregistrer_score(self.nom_joueur, self.session_score)

        self.top_scores = charger_meilleurs_scores()
        self.state = STATE_GAMEOVER

    def play_sound(self, key):
        try:
            if key in self.sons:
                self.sons[key].play()
        except:
            pass

    #  BOUCLE PRINCIPALE
    def run(self):
        while True:
            self.clock.tick(60)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                if event.type == pygame.VIDEORESIZE:
                    self.on_resize(event.size)

                # --- INPUT TEXTE ---
                if self.state in [STATE_LOGIN, STATE_ADD_WORD, STATE_MULTI_NAMES]:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.state == STATE_LOGIN and self.input_text.strip():
                                self.nom_joueur = self.input_text.strip()
                                self.session_jetons = charger_profil_joueur(self.nom_joueur)
                                self.top_scores = charger_meilleurs_scores()
                                self.play_sound('craie')
                                self.state = STATE_MENU

                            elif self.state == STATE_ADD_WORD and ";" in self.input_text:
                                parts = self.input_text.split(";")
                                ajouter_nouveau_mot(parts[0], parts[1])
                                self.mots = charger_mots()
                                self.play_sound('victoire')
                                self.state = STATE_MENU

                            elif self.state == STATE_MULTI_NAMES:
                                saisie = self.input_text.strip()
                                if self.multi_etape_nom == 1:
                                    self.multi_nom_j1 = saisie if saisie else "Joueur 1"
                                    self.input_text = ""
                                    self.multi_etape_nom = 2
                                else:
                                    self.multi_nom_j2 = saisie if saisie else "Joueur 2"
                                    self.input_text = ""
                                    self.multi_etape_nom = 1
                                    self.play_sound('craie')
                                    self.state = STATE_MULTI_DIFFICULTY
                                    continue

                            self.input_text = ""

                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]

                        elif event.key == pygame.K_ESCAPE and self.state == STATE_ADD_WORD:
                            self.state = STATE_MENU
                            self.input_text = ""

                        elif event.key == pygame.K_ESCAPE and self.state == STATE_MULTI_NAMES:
                            self.play_sound('craie')
                            self.input_text = ""
                            self.multi_etape_nom = 1
                            self.state = STATE_PLAYER_COUNT

                        else:
                            self.input_text += event.unicode

                # --- CLICK MENU ---
                elif self.state == STATE_MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.rect_jouer and self.rect_jouer.collidepoint((mx, my)):
                            self.state = STATE_PLAYER_COUNT
                            self.play_sound('craie')

                        elif self.rect_ajouter and self.rect_ajouter.collidepoint((mx, my)):
                            self.state = STATE_ADD_WORD
                            self.play_sound('craie')
                            self.input_text = ""

                        elif self.rect_quitter and self.rect_quitter.collidepoint((mx, my)):
                            pygame.quit()
                            return

                # --- CHOIX 1P/2P ---
                elif self.state == STATE_PLAYER_COUNT:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.rect_1p and self.rect_1p.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.state = STATE_DIFFICULTY

                        elif self.rect_2p and self.rect_2p.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.state = STATE_MULTI_NAMES
                            self.input_text = ""
                            self.multi_etape_nom = 1

                        elif self.rect_player_retour and self.rect_player_retour.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.state = STATE_MENU

                # --- CLICK DIFFICULTY SOLO ---
                elif self.state == STATE_DIFFICULTY:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.rect_facile and self.rect_facile.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.start_game_session("FACILE")

                        elif self.rect_moyen and self.rect_moyen.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.start_game_session("MOYEN")

                        elif self.rect_difficile and self.rect_difficile.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.start_game_session("DIFFICILE")

                        elif self.rect_retour and self.rect_retour.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.state = STATE_MENU

                # --- CLICK DIFFICULTY MULTI ---
                elif self.state == STATE_MULTI_DIFFICULTY:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.rect_multi_facile and self.rect_multi_facile.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.start_multiplayer_session("FACILE")

                        elif self.rect_multi_moyen and self.rect_multi_moyen.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.start_multiplayer_session("MOYEN")

                        elif self.rect_multi_difficile and self.rect_multi_difficile.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.start_multiplayer_session("DIFFICILE")

                        elif self.rect_multi_retour and self.rect_multi_retour.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.state = STATE_MENU

                # --- GAME INPUT ---
                elif self.state == STATE_GAME:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = STATE_MENU
                            self.play_sound('craie')

                        elif event.key == pygame.K_1:
                            res = self.logic.acheter_indice_theme()
                            self.message = f"THÈME : {res}" if res else "Pas assez de jetons"
                            self.play_sound('craie')

                        elif event.key == pygame.K_2:
                            res = self.logic.acheter_indice_lettre()
                            if res:
                                self.play_sound('craie')

                        # chiffres -> message d'erreur 2 secondes
                        elif event.unicode.isdigit():
                            self.message = "Tape une lettre, pas un nombre."
                            self.message_time = pygame.time.get_ticks()
                            self.play_sound('craie')

                        elif event.unicode.isalpha():
                            l = event.unicode.upper()
                            self.play_sound('craie')

                            ok = self.logic.proposer_lettre(l)
                            if not ok:
                                for _ in range(30):
                                    self.poussieres.append(
                                        Particule(
                                            random.randint(100, 300),
                                            random.randint(100, 450)
                                        )
                                    )

                            if self.is_multiplayer:
                                # Victoire du joueur courant ?
                                if set(self.logic.mot_secret).issubset(self.logic.lettres_trouvees):
                                    winner = self.current_player
                                    loser = 1 - self.current_player
                                    self.finish_multiplayer(winner, loser, f"{self.players[winner]['nom']} a trouvé son mot et gagne !")
                                    continue

                                # Sinon on passe la main (tour par tour)
                                self.current_player = 1 - self.current_player
                                self.logic = self.players[self.current_player]["logic"]
                                self.message = ""
                                self.message_time = 0
                                continue

                    # SOLO : quand le mot est trouvé -> mot suivant
                    if not self.is_multiplayer:
                        if set(self.logic.mot_secret).issubset(self.logic.lettres_trouvees):
                            self.play_sound('victoire')
                            self.session_score += 1
                            self.logic.jetons += 5
                            self.session_jetons = self.logic.jetons
                            self.start_time += 10000
                            self.next_word()

                # --- GAME OVER ---
                elif self.state == STATE_GAMEOVER:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.is_multiplayer = False
                        self.players = []
                        self.current_player = 0
                        self.multi_result = ""

                        self.session_jetons = charger_profil_joueur(self.nom_joueur) if self.nom_joueur else 0
                        self.top_scores = charger_meilleurs_scores()
                        self.state = STATE_MENU

            self.update_and_draw()


if __name__ == "__main__":
    PenduPygame().run()
