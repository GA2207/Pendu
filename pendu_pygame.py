import pygame
import random
import time
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

        # Taille de départ (fenêtre redimensionnable)
        SCREEN_WIDTH = 1280
        SCREEN_HEIGHT = 720
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Le Pendu de l'École - Arcade Edition")

        # Taille réelle courante de la fenêtre (source de vérité)
        self.W, self.H = self.screen.get_size()

        # Chargement des ressources
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
        self.state = STATE_LOGIN
        self.nom_joueur = ""
        self.input_text = ""
        self.poussieres = []

        # Variables de session de jeu
        self.difficulte = "MOYEN"
        self.session_score = 0  # Nombre de mots trouvés
        self.session_jetons = 0
        self.start_time = 0
        self.time_limit = 60  # secondes
        self.logic = None
        self.message = ""

        # Rectangles de boutons (clics fiables)
        self.rect_jouer = None
        self.rect_ajouter = None
        self.rect_quitter = None
        self.rect_facile = None
        self.rect_moyen = None
        self.rect_difficile = None
        self.rect_retour = None

        # Fond (tableau) : génération à la taille de la fenêtre
        self.generer_fond()

        # --- Cache potence (fixe) ---
        self.potence_surface = None
        self.potence_cache_size = None
        self.build_potence_surface()

    # ----------------------------
    #  FOND PLEIN ÉCRAN
    # ----------------------------
    def generer_fond(self):
        """Génère le tableau (texture + poussières) à la taille actuelle de la fenêtre."""
        self.surface_tableau = pygame.Surface((self.W, self.H)).convert()
        self.surface_tableau.fill(BOARD_DARK)

        # Petits grains (effet craie)
        nb_points = int((self.W * self.H) / 200)
        for _ in range(nb_points):
            x, y = random.randint(0, self.W - 1), random.randint(0, self.H - 1)
            s = pygame.Surface((2, 2)).convert_alpha()
            s.set_alpha(random.randint(5, 15))
            s.fill((255, 255, 255))
            self.surface_tableau.blit(s, (x, y))

    def on_resize(self, new_size):
        """À appeler quand la fenêtre change de taille."""
        self.screen = pygame.display.set_mode(new_size, pygame.RESIZABLE)
        self.W, self.H = self.screen.get_size()
        self.generer_fond()
        self.build_potence_surface()  # ✅ potence recalculée au resize

    # ----------------------------

    def play_sound(self, name):
        if name in self.sons and self.sons[name]:
            self.sons[name].play()

    def draw_chalk_line(self, start, end, width=4):
        """Ligne 'craie' (avec petit hasard) => tremblement."""
        points = []
        dist = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
        steps = int(dist // 5) + 1
        for i in range(steps):
            x = start[0] + (end[0] - start[0]) * i / steps + random.randint(-1, 1)
            y = start[1] + (end[1] - start[1]) * i / steps + random.randint(-1, 1)
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(self.screen, CHALK_WHITE, False, points, width)

    def draw_stable_line(self, surface, start, end, width=4):
        """Ligne fixe (pas de hasard) pour la potence."""
        pygame.draw.line(surface, CHALK_WHITE, start, end, width)

    def build_potence_surface(self):
        """Pré-dessine la potence sur une surface cache (fixe, jamais tremblante)."""
        size = (self.W, self.H)
        if self.potence_surface is not None and self.potence_cache_size == size:
            return

        self.potence_cache_size = size
        self.potence_surface = pygame.Surface(size, pygame.SRCALPHA)

        # ---- Placement potence ----
        x0 = 90
        y_sol = self.H - 170
        y_top = 140

        base_w = 240
        pole_x = x0 + 70
        beam_len = 190

        x_hook = pole_x + beam_len

        # Base
        self.draw_stable_line(self.potence_surface, (x0, y_sol), (x0 + base_w, y_sol), 4)
        # Poteau
        self.draw_stable_line(self.potence_surface, (pole_x, y_sol), (pole_x, y_top), 4)
        # Barre
        self.draw_stable_line(self.potence_surface, (pole_x, y_top), (x_hook, y_top), 4)

        # Renfort diagonal intérieur (bien placé)
        reinforce_start = (pole_x, y_top + 18)
        reinforce_end = (pole_x + 38, y_top)
        self.draw_stable_line(self.potence_surface, reinforce_start, reinforce_end, 4)

    # --- LOGIQUE DES ÉTATS ---

    def start_new_session(self):
        """Lance une nouvelle série de mots (Arcade)"""
        self.session_score = 0
        self.session_jetons = charger_profil_joueur(self.nom_joueur)
        self.start_time = pygame.time.get_ticks()

        # Temps selon difficulté
        if self.difficulte == "FACILE":
            self.time_limit = 120
        elif self.difficulte == "MOYEN":
            self.time_limit = 90
        else:
            self.time_limit = 60  # Difficile

        self.next_word()
        self.state = STATE_GAME

    def next_word(self):
        """Passe au mot suivant."""
        erreurs_a_garder = None
        if self.difficulte == "DIFFICILE" and self.logic:
            erreurs_a_garder = self.logic.lettres_ratees

        self.logic = PenduLogic(random.choice(self.mots), self.session_jetons, erreurs_a_garder)
        self.message = "Nouveau mot ! Bonne chance."

    def draw_text_centered(self, text, y, font, color=CHALK_WHITE):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(self.W // 2, y))
        self.screen.blit(surf, rect)

    def draw_button(self, text, rect_y, button_id):
        """Dessine un bouton et retourne son Rect (clic fiable)."""
        mouse_pos = pygame.mouse.get_pos()

        MENU_LEFT = 120
        MENU_RIGHT = 680
        MAX_W = MENU_RIGHT - MENU_LEFT

        rect_height = 60
        padding_x = 24

        size = 40
        font = pygame.font.SysFont("Comic Sans MS", size)

        while True:
            surf = font.render(text, True, CHALK_WHITE)
            if surf.get_width() + padding_x * 2 <= MAX_W or size <= 22:
                break
            size -= 2
            font = pygame.font.SysFont("Comic Sans MS", size)

        text_w = surf.get_width()
        rect_width = min(text_w + padding_x * 2, MAX_W)

        rect_x = MENU_LEFT + (MAX_W - rect_width) // 2
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

    def update_and_draw(self):
        # Fond plein écran
        self.screen.blit(self.surface_tableau, (0, 0))

        if self.state == STATE_LOGIN:
            self.draw_text_centered("BIENVENUE EN CLASSE", 120, self.font_title, YELLOW_CHALK)
            self.draw_text_centered("Écris ton nom pour commencer :", 250, self.font_ui)

            input_rect = pygame.Rect(self.W // 2 - 200, 300, 400, 70)
            pygame.draw.rect(self.screen, CHALK_WHITE, input_rect, 2)
            self.draw_text_centered(self.input_text + "_", 335, self.font_main, YELLOW_CHALK)

        elif self.state == STATE_MENU:
            self.draw_text_centered("MENU PRINCIPAL", 80, self.font_title, CHALK_WHITE)
            self.draw_text_centered(
                f"Joueur : {self.nom_joueur} | Jetons : {self.session_jetons}",
                160,
                self.font_ui,
                GREEN_CHALK
            )

            self.draw_chalk_line((self.W // 2 - 250, 190), (self.W // 2 + 250, 190), 2)

            self.rect_jouer = self.draw_button("1. COMMENCER L'EXAMEN", 230, 1)
            self.rect_ajouter = self.draw_button("2. AJOUTER DES MOTS", 320, 2)
            self.rect_quitter = self.draw_button("3. QUITTER L'ÉCOLE", 410, 3)

        elif self.state == STATE_DIFFICULTY:
            self.draw_text_centered("CHOISIS LA DIFFICULTÉ", 100, self.font_title, YELLOW_CHALK)
            pygame.draw.line(
                self.screen,
                CHALK_WHITE,
                (self.W // 2 - 260, 140),
                (self.W // 2 + 260, 140),
                2
            )

            self.rect_facile = self.draw_button("FACILE (120s)", 220, 1)
            self.rect_moyen = self.draw_button("MOYEN (90s)", 310, 2)
            self.rect_difficile = self.draw_button("DIFFICILE (60s)", 400, 3)
            self.rect_retour = self.draw_button("RETOUR AU MENU", 500, 4)

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
            self.draw_text_centered(f"Score : {self.session_score}", 260, self.font_main, CHALK_WHITE)
            self.draw_text_centered("Appuie sur ESPACE pour revenir au menu", 360, self.font_ui, CHALK_WHITE)

        # ✅ Tableau d'honneur visible dans tous les menus (pas pendant la partie)
        if self.state in (STATE_LOGIN, STATE_MENU, STATE_DIFFICULTY, STATE_ADD_WORD, STATE_GAMEOVER):
            self.draw_leaderboard_box()

        pygame.display.flip()

    def draw_leaderboard_box(self):
        """
        Dessine le tableau d'honneur ancré à droite de l'écran,
        sans jamais chevaucher le contenu central.
        """
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

        pygame.draw.line(
            self.screen,
            CHALK_WHITE,
            (start_x + 15, start_y + 50),
            (start_x + BOX_WIDTH - 15, start_y + 50),
            1
        )

        for i, entry in enumerate(self.top_scores[:6]):
            txt = f"{i + 1}. {entry['nom'][:10]}  {entry['score']}"
            color = GREEN_CHALK if entry['nom'] == self.nom_joueur else CHALK_WHITE
            line = self.font_leader.render(txt, True, color)
            self.screen.blit(line, (start_x + 20, start_y + 70 + i * 35))

    def draw_game_interface(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
        remaining = max(0, self.time_limit - elapsed)
        color_time = RED_CHALK if remaining < 10 else CHALK_WHITE
        self.screen.blit(self.font_title.render(f"{int(remaining)}s", True, color_time), (self.W - 150, 20))

        self.screen.blit(self.font_ui.render(f"Score: {self.session_score}", True, GREEN_CHALK), (20, 20))
        self.screen.blit(self.font_ui.render(f"Jetons: {self.logic.jetons}", True, YELLOW_CHALK), (20, 50))

        self.draw_pendu(len(self.logic.lettres_ratees))

        center_x = self.W // 2 + 50
        self.draw_text_centered(self.logic.etat_mot(), 300, self.font_title)
        self.draw_text_centered(self.message, 200, self.font_ui)

        fautes = f"Fautes: {', '.join(self.logic.lettres_ratees)}"
        surf_f = self.font_ui.render(fautes, True, RED_CHALK)
        self.screen.blit(surf_f, surf_f.get_rect(center=(center_x, 400)))

        self.draw_text_centered("[1] Thème (1j)  [2] Lettre (5j)", 520, self.font_ui)

        if remaining <= 0:
            self.game_over(victoire=False)
        elif len(self.logic.lettres_ratees) >= 7:
            self.game_over(victoire=False)

    def draw_pendu(self, err):
        """
        Potence FIXE (cache) + personnage qui TREMBLE.
        err = nombre d'erreurs (0 à 7)
        """
        if self.potence_surface is None or self.potence_cache_size != (self.W, self.H):
            self.build_potence_surface()

        # ---- Placement ----
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
        arm_len = 45
        leg_len = 60
        leg_spread = 35

        HEAD_FILL = (230, 170, 190)

        # 1) potence fixe
        if err >= 1:
            self.screen.blit(self.potence_surface, (0, 0))

        # tremblement perso
        jx = random.randint(-2, 2)
        jy = random.randint(-2, 2)

        xh = x_hook + jx
        y_rope_top = y_beam + jy
        y_rope_bottom = y_beam + rope_h + jy

        head_center = (xh, y_rope_bottom + head_r)

        body_top_y = head_center[1] + head_r + 5
        body_bottom_y = body_top_y + body_len

        arm_y = body_top_y + 20

        # 2) corde + tête
        if err >= 2:
            self.draw_chalk_line((xh, y_rope_top), (xh, y_rope_bottom), 4)
            pygame.draw.circle(self.screen, HEAD_FILL, head_center, head_r)
            pygame.draw.circle(self.screen, CHALK_WHITE, head_center, head_r, 3)

        # 3) corps
        if err >= 3:
            self.draw_chalk_line((xh, body_top_y), (xh, body_bottom_y), 4)

        # 4) bras droite
        if err >= 4:
            self.draw_chalk_line((xh, arm_y), (xh + arm_len, arm_y + 20), 4)

        # 5) bras gauche
        if err >= 5:
            self.draw_chalk_line((xh, arm_y), (xh - arm_len, arm_y + 20), 4)

        # 6) jambe droite
        if err >= 6:
            self.draw_chalk_line((xh, body_bottom_y), (xh + leg_spread, body_bottom_y + leg_len), 4)

        # 7) jambe gauche
        if err >= 7:
            self.draw_chalk_line((xh, body_bottom_y), (xh - leg_spread, body_bottom_y + leg_len), 4)

    def game_over(self, victoire):
        if victoire:
            self.play_sound('victoire')
        else:
            self.play_sound('defaite')

        enregistrer_score(self.nom_joueur, self.session_score, self.logic.jetons)
        self.session_jetons = self.logic.jetons
        self.top_scores = charger_meilleurs_scores()
        self.state = STATE_GAMEOVER

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

                # --- INPUT TEXTE (LOGIN ou AJOUT MOT) ---
                if self.state in [STATE_LOGIN, STATE_ADD_WORD]:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.state == STATE_LOGIN and self.input_text.strip():
                                self.nom_joueur = self.input_text.strip()

                                # ✅ bonus : recharge jetons + scores dès la connexion
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
                            self.input_text = ""

                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        elif event.key == pygame.K_ESCAPE and self.state == STATE_ADD_WORD:
                            self.state = STATE_MENU
                        else:
                            self.input_text += event.unicode

                # --- CLICK MENU ---
                elif self.state == STATE_MENU:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.rect_jouer and self.rect_jouer.collidepoint((mx, my)):
                            self.state = STATE_DIFFICULTY
                            self.play_sound('craie')

                        elif self.rect_ajouter and self.rect_ajouter.collidepoint((mx, my)):
                            self.state = STATE_ADD_WORD
                            self.play_sound('craie')

                        elif self.rect_quitter and self.rect_quitter.collidepoint((mx, my)):
                            pygame.quit()
                            return

                # --- CLICK DIFFICULTE ---
                elif self.state == STATE_DIFFICULTY:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()

                        if self.rect_facile and self.rect_facile.collidepoint((mx, my)):
                            self.difficulte = "FACILE"
                            self.play_sound('craie')
                            self.start_new_session()

                        elif self.rect_moyen and self.rect_moyen.collidepoint((mx, my)):
                            self.difficulte = "MOYEN"
                            self.play_sound('craie')
                            self.start_new_session()

                        elif self.rect_difficile and self.rect_difficile.collidepoint((mx, my)):
                            self.difficulte = "DIFFICILE"
                            self.play_sound('craie')
                            self.start_new_session()

                        elif self.rect_retour and self.rect_retour.collidepoint((mx, my)):
                            self.play_sound('craie')
                            self.state = STATE_MENU

                # --- JEU ---
                elif self.state == STATE_GAME:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            res = self.logic.acheter_indice_theme()
                            self.message = f"THÈME : {res}" if res else "Pas assez de jetons"
                            self.play_sound('craie')

                        elif event.key == pygame.K_2:
                            res = self.logic.acheter_indice_lettre()
                            if res:
                                self.play_sound('craie')

                        elif event.unicode.isalpha():
                            l = event.unicode.upper()
                            self.play_sound('craie')

                            if not self.logic.proposer_lettre(l):
                                for _ in range(30):
                                    self.poussieres.append(
                                        Particule(
                                            random.randint(100, 300),
                                            random.randint(100, 450)
                                        )
                                    )

                    if set(self.logic.mot_secret).issubset(self.logic.lettres_trouvees):
                        self.play_sound('victoire')
                        self.session_score += 1
                        self.logic.jetons += 5
                        self.session_jetons = self.logic.jetons
                        self.start_time += 10000  # +10 secondes
                        self.next_word()

                # --- GAME OVER ---
                elif self.state == STATE_GAMEOVER:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        # rafraîchit le tableau d'honneur quand on revient au menu
                        self.session_jetons = charger_profil_joueur(self.nom_joueur)
                        self.top_scores = charger_meilleurs_scores()
                        self.state = STATE_MENU

            self.update_and_draw()


if __name__ == "__main__":
    PenduPygame().run()
