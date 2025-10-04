# -*- coding: utf-8 -*-
"""
Fenêtre principale de l'application Stations-Service
Responsive + Scroll
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Import des modules de l'application
from .client_management_simple import ClientManagement
from .fuel_tracking import FuelTracking
from .invoice_management import InvoiceManagement
from .payment_management import PaymentManagement
from .reports import Reports
from .auth import AdminPanel


class ScrollableFrame(ttk.Frame):
    """Frame avec scrollbar verticale intégrée et support tactile amélioré"""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)

        # Scroll vertical uniquement avec barre plus large pour tactile
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        self.scrollable_frame = ttk.Frame(canvas, padding=(5, 5, 20, 5))  # Ajout de padding à droite (20px)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
                # Ne pas limiter la largeur pour éviter le défilement horizontal
            )
        )
        
        # Assurer que tout le contenu est visible, y compris à gauche
        def adjust_content(event):
            # Obtenir la largeur du contenu et du canvas
            content_width = self.scrollable_frame.winfo_reqwidth()
            canvas_width = event.width if hasattr(event, 'width') else canvas.winfo_width()
            
            # Toujours commencer le contenu à gauche avec un padding minimal
            # pour assurer que tout le contenu est visible
            offset = 10  # Padding fixe de 10px à gauche
            
            # Repositionner la fenêtre du contenu avec le décalage
            canvas.create_window((offset, 0), window=self.scrollable_frame, anchor="nw")
            
            # Assurer que le canvas est assez large et activer le défilement horizontal si nécessaire
            canvas.configure(width=canvas_width)
            
            # Si le contenu est plus large que le canvas, activer le défilement horizontal
            if content_width + offset > canvas_width:
                # Configurer la région de défilement pour inclure tout le contenu
                canvas.configure(scrollregion=(0, 0, content_width + offset, canvas.winfo_height()))
                # Activer le défilement horizontal
                if not hasattr(self, 'h_scrollbar') or not self.h_scrollbar.winfo_exists():
                    self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=canvas.xview)
                    self.h_scrollbar.grid(row=1, column=0, sticky="ew")
                    canvas.configure(xscrollcommand=self.h_scrollbar.set)
                    # Reconfigurer la grille pour ajouter la barre de défilement horizontale
                    self.rowconfigure(1, weight=0)
            else:
                # Désactiver le défilement horizontal si le contenu tient dans la largeur
                if hasattr(self, 'h_scrollbar') and self.h_scrollbar.winfo_exists():
                    self.h_scrollbar.grid_forget()
                    canvas.configure(xscrollcommand=None)
        
        # Lier à la fois au chargement initial et au redimensionnement
        self.scrollable_frame.bind('<Configure>', adjust_content)
        canvas.bind('<Configure>', adjust_content)
        
        # Création initiale de la fenêtre (sera mise à jour par adjust_content)
        canvas.create_window((10, 0), window=self.scrollable_frame, anchor="nw")

        # Scroll vertical toujours activé, horizontal activé dynamiquement si nécessaire
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Le défilement horizontal sera géré dynamiquement par adjust_content

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Support de défilement amélioré
        # Scroll molette souris
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        
        # Support tactile (glisser-déposer)
        def _start_drag(event):
            canvas.scan_mark(event.x, event.y)
            
        def _drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)
            return "break"  # Empêcher la propagation de l'événement
        
        # Lier les événements tactiles
        canvas.bind("<ButtonPress-1>", _start_drag)
        canvas.bind("<B1-Motion>", _drag)
        
        # Navigation clavier
        canvas.bind_all("<Up>", lambda e: canvas.yview_scroll(-3, "units"))
        canvas.bind_all("<Down>", lambda e: canvas.yview_scroll(3, "units"))
        canvas.bind_all("<Prior>", lambda e: canvas.yview_scroll(-1, "pages"))
        canvas.bind_all("<Next>", lambda e: canvas.yview_scroll(1, "pages"))



class MainWindow:
    def __init__(self, root, db_manager, user_role=None):
        self.root = root
        self.db_manager = db_manager
        self.user_role = user_role
        self.is_dark_mode = False  # Par défaut, mode clair
        
        # Variables pour le redimensionnement adaptatif
        self.current_width = self.root.winfo_width()
        self.current_height = self.root.winfo_height()
        self.is_compact_mode = False
        self.current_display_mode = "normal"
        self.current_user_id = 0  # Sera mis à jour avec l'ID de l'utilisateur connecté

        # Config responsive
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Bind pour détecter le redimensionnement
        self.root.bind('<Configure>', self.on_window_resize)

        # Styles
        self.setup_styles()
        
        # Charger les préférences de fenêtre si disponibles
        self.load_window_preferences()
        
        # Créer l'interface principale
        self.create_main_interface()

    def setup_styles(self):
        """Configuration des styles modernes pour l'application avec support tactile amélioré"""
        style = ttk.Style()
        
        # Définir les palettes de couleurs pour les modes clair et sombre
        self.light_colors = {
            'primary': '#1976D2',       # Bleu principal
            'primary_dark': '#0D47A1',  # Bleu foncé
            'secondary': '#FF5722',     # Orange accent
            'background': '#F5F5F5',    # Fond gris clair
            'surface': '#FFFFFF',       # Surface blanche
            'text': '#212121',          # Texte principal
            'text_secondary': '#757575', # Texte secondaire
            'success': '#4CAF50',       # Vert succès
            'warning': '#FFC107',       # Jaune avertissement
            'error': '#F44336',         # Rouge erreur
            'hover': '#E3F2FD'          # Couleur de survol
        }
        
        self.dark_colors = {
            'primary': '#2196F3',       # Bleu principal (plus vif pour le mode sombre)
            'primary_dark': '#1565C0',  # Bleu foncé
            'secondary': '#FF7043',     # Orange accent (plus vif)
            'background': '#121212',    # Fond noir/gris très foncé
            'surface': '#1E1E1E',       # Surface gris foncé
            'text': '#FFFFFF',          # Texte blanc
            'text_secondary': '#B0B0B0', # Texte secondaire gris clair
            'success': '#66BB6A',       # Vert succès (plus vif)
            'warning': '#FFCA28',       # Jaune avertissement (plus vif)
            'error': '#EF5350',         # Rouge erreur (plus vif)
            'hover': '#1A237E'          # Couleur de survol (bleu très foncé)
        }
        
        # Utiliser les couleurs selon le mode actuel
        self.colors = self.dark_colors if self.is_dark_mode else self.light_colors
        
        # Configuration du thème global
        self.root.configure(background=self.colors['background'])
        
        # Styles des boutons - Taille augmentée pour écran tactile
        style.configure('Touch.TButton',
                       font=('Segoe UI', 14, 'bold'),
                       background=self.colors['primary'],
                       foreground='white',
                       padding=(25, 18))
        
        style.map('Touch.TButton',
                 background=[('active', self.colors['primary_dark']),
                            ('pressed', self.colors['primary_dark'])],
                 foreground=[('pressed', '#2196F3')],  # Texte bleu lors du clic
                 relief=[('pressed', 'sunken')])
        
        # Style des labels
        style.configure('Touch.TLabel',
                       font=('Segoe UI', 14),
                       background=self.colors['background'],
                       foreground=self.colors['text'])
        
        # Style des en-têtes
        style.configure('Header.TLabel',
                       font=('Segoe UI', 22, 'bold'),
                       background=self.colors['background'],
                       foreground=self.colors['primary'])
        
        # Style des tableaux avec lignes plus hautes pour faciliter la sélection tactile
        style.configure('Touch.Treeview',
                       font=('Segoe UI', 12),
                       rowheight=45,
                       background=self.colors['surface'],
                       fieldbackground=self.colors['surface'],
                       foreground=self.colors['text'])
        
        style.configure('Touch.Treeview.Heading',
                       font=('Segoe UI', 14, 'bold'),
                       background=self.colors['primary'],
                       foreground='white',
                       padding=(5, 5))
        
        # Style des onglets avec cibles plus grandes
        style.configure('Touch.TNotebook',
                       background=self.colors['background'],
                       tabmargins=[2, 5, 2, 0])
        
        style.configure('Touch.TNotebook.Tab',
                       font=('Segoe UI', 14),
                       background=self.colors['background'],
                       foreground=self.colors['text'],
                       padding=[20, 12])
        
        style.map('Touch.TNotebook.Tab',
                 background=[('selected', self.colors['primary'])],
                 foreground=[('selected', 'white')],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # Style des frames
        style.configure('TFrame',
                       background=self.colors['background'])
        
        style.configure('TLabelframe',
                       background=self.colors['background'],
                       foreground=self.colors['primary'])
        
        style.configure('TLabelframe.Label',
                       font=('Segoe UI', 14, 'bold'),
                       background=self.colors['background'],
                       foreground=self.colors['primary'])
        
        # Style pour les entrées
        style.configure('TEntry',
                       fieldbackground=self.colors['surface'],
                       foreground=self.colors['text'])
        
        # Style pour les combobox
        style.configure('TCombobox',
                       fieldbackground=self.colors['surface'],
                       background=self.colors['surface'],
                       foreground=self.colors['text'])
        
        # Style pour les barres de défilement plus larges
        style.configure('Vertical.TScrollbar', 
                       width=20,  # Largeur augmentée pour faciliter le défilement tactile
                       arrowsize=20,  # Flèches plus grandes
                       background=self.colors['surface'],
                       troughcolor=self.colors['background'])
        
        style.configure('Horizontal.TScrollbar', 
                       width=20,  # Largeur augmentée pour faciliter le défilement tactile
                       arrowsize=20,  # Flèches plus grandes
                       background=self.colors['surface'],
                       troughcolor=self.colors['background'])


    def create_main_interface(self):
        """Créer l'interface principale"""
        
        # Configurer la grille principale
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # === Frame principal scrollable ===
        self.main_frame = ScrollableFrame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Empêcher le dépassement horizontal
        self.main_frame.scrollable_frame.columnconfigure(0, weight=1)

        # === En-tête moderne ===
        header_frame = ttk.Frame(self.main_frame.scrollable_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20), padx=(0, 20))  # Ajout de padding à droite
        header_frame.configure(style='TFrame')
        
        # Logo et titre dans un conteneur
        title_container = ttk.Frame(header_frame, style='TFrame')
        title_container.pack(side="left", fill="y")
        
        # Icône de l'application (simulée avec un label coloré)
        self.logo_label = ttk.Label(
            title_container,
            text="⛽",
            font=('Segoe UI', 24),
            foreground=self.colors['primary']
        )
        self.logo_label.pack(side="left", padx=(0, 10))
        
        # Stocker la référence du conteneur titre
        self.title_container = title_container
        
        # Titre de l'application
        title_label = ttk.Label(
            title_container,
            text="Système de Gestion de Station Timizar",
            style='Header.TLabel'
        )
        title_label.pack(side="left")
        
        # Conteneur droit pour l'heure et les infos utilisateur
        info_container = ttk.Frame(header_frame, style='TFrame')
        info_container.pack(side="right", fill="y", padx=(0, 10))  # Ajout de padding à droite
        
        # Bouton pour basculer entre mode clair et mode sombre
        self.dark_mode_button = ttk.Button(
            info_container,
            text="🌙 Mode Sombre",
            command=self.toggle_dark_mode,
            style='Touch.TButton'
        )
        self.dark_mode_button.pack(side="right", padx=(20, 10))
        
        # Bouton paramètres
        self.settings_button = ttk.Button(
            info_container,
            text="⚙️ Paramètres",
            command=self.open_settings_dialog,
            style='Touch.TButton'
        )
        self.settings_button.pack(side="right", padx=(20, 10))
        
        # Affichage de l'heure avec icône
        time_container = ttk.Frame(info_container, style='TFrame')
        time_container.pack(side="right", padx=(20, 0))
        
        time_icon = ttk.Label(
            time_container,
            text="🕒",
            font=('Segoe UI', 14),
            foreground=self.colors['text_secondary']
        )
        time_icon.pack(side="left", padx=(0, 5))
        
        self.time_label = ttk.Label(
            time_container, 
            text="", 
            font=('Segoe UI', 12),
            foreground=self.colors['text_secondary']
        )
        self.time_label.pack(side="right")
        self.update_time()

        # === Sélection de station (design moderne) ===
        station_card = ttk.Frame(self.main_frame.scrollable_frame, style='TFrame')
        station_card.grid(row=1, column=0, sticky="ew", pady=(0, 20), padx=10)
        
        # Créer un effet de carte avec bordure et padding
        station_inner = ttk.Frame(station_card)
        station_inner.pack(fill="x", expand=True, padx=2, pady=2)
        station_inner.configure(style='TFrame')
        
        # Conteneur pour l'icône et le texte
        station_header = ttk.Frame(station_inner, style='TFrame')
        station_header.pack(fill="x", padx=15, pady=10)
        
        # Icône de station
        station_icon = ttk.Label(
            station_header,
            text="🏢",
            font=('Segoe UI', 16),
            foreground=self.colors['primary']
        )
        station_icon.pack(side='left', padx=(0, 10))
        
        ttk.Label(station_header,
                  text="Station Active:",
                  font=('Segoe UI', 12, 'bold'),
                  foreground=self.colors['text'],
                  background=self.colors['background']).pack(side='left')
        
        # Conteneur pour le combobox
        combo_container = ttk.Frame(station_inner, style='TFrame')
        combo_container.pack(fill="x", padx=15, pady=(0, 15))
        
        self.station_var = tk.StringVar()
        self.station_combo = ttk.Combobox(
            combo_container,
            textvariable=self.station_var,
            font=('Segoe UI', 12),
            state='readonly',
            width=50
        )
        self.station_combo.pack(side='left', fill="x", expand=True)
        
        # Bouton de rafraîchissement
        refresh_btn = ttk.Button(
            combo_container,
            text="🔄",
            command=self.load_stations,
            width=3
        )
        refresh_btn.pack(side='left', padx=(10, 0))
        
        self.load_stations()

        # === Notebook principal ===
        self.notebook = ttk.Notebook(self.main_frame.scrollable_frame, style='Touch.TNotebook')
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=(0, 20))  # Ajout de padding à droite

        self.main_frame.scrollable_frame.rowconfigure(2, weight=1)
        self.create_tabs()

        # === Barre de statut moderne ===
        status_container = ttk.Frame(self.main_frame.scrollable_frame, style='TFrame')
        status_container.grid(row=3, column=0, sticky="ew", pady=(15, 0), padx=(0, 20))  # Ajout de padding à droite
        
        # Ligne de séparation
        separator = ttk.Separator(status_container, orient='horizontal')
        separator.pack(fill='x', pady=(0, 5))
        
        # Conteneur pour les éléments de statut
        status_elements = ttk.Frame(status_container, style='TFrame')
        status_elements.pack(fill='x', expand=True, padx=10, pady=5)
        
        # Icône de statut
        status_icon = ttk.Label(
            status_elements,
            text="✓",
            font=('Segoe UI', 12),
            foreground=self.colors['success']
        )
        status_icon.pack(side='left', padx=(5, 5))
        
        # Texte de statut
        self.status_bar = ttk.Label(
            status_elements,
            text="Système prêt",
            font=('Segoe UI', 10),
            foreground=self.colors['text_secondary'],
            background=self.colors['background']
        )
        self.status_bar.pack(side='left')
        
        # Version de l'application (côté droit)
        version_label = ttk.Label(
            status_elements,
            text="v2.0",
            font=('Segoe UI', 10),
            foreground=self.colors['text_secondary'],
            background=self.colors['background']
        )
        version_label.pack(side='right', padx=5)


    def create_tabs(self):
        """Créer les onglets principaux avec style moderne"""
        # Configuration des onglets
        tab_padding = 15
        
        # Onglet Tableau de Bord
        dashboard_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(dashboard_frame, text="  📊 Tableau de Bord  ", padding=tab_padding)
        self.create_dashboard(dashboard_frame)

        # Onglet Gestion Clients
        clients_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(clients_frame, text="  👥 Clients  ", padding=tab_padding)
        self.client_management = ClientManagement(clients_frame, self.db_manager)

        # Onglet Transactions Carburant
        fuel_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(fuel_frame, text="  ⛽ Carburant  ", padding=tab_padding)
        self.fuel_tracking = FuelTracking(fuel_frame, self.db_manager)

        # Onglet Paiements d'Avance
        payments_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(payments_frame, text="  💰 Paiements  ", padding=tab_padding)
        self.payment_management = PaymentManagement(payments_frame, self.db_manager)

        # Onglet Facturation
        invoices_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(invoices_frame, text="  🧾 Factures  ", padding=tab_padding)
        self.invoice_management = InvoiceManagement(invoices_frame, self.db_manager)

        # Onglet Rapports
        reports_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(reports_frame, text="  📈 Rapports  ", padding=tab_padding)
        
        # Configurer les événements de changement d'onglet
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        try:
            self.reports = Reports(reports_frame, self.db_manager)
        except Exception as e:
            self.show_error(f"Erreur lors du chargement des rapports: {str(e)}")
            
    def on_tab_changed(self, event):
        """Gère le changement d'onglet"""
        try:
            tab_id = self.notebook.select()
            tab_name = self.notebook.tab(tab_id, "text").strip()
            
            # Mettre à jour la barre de statut
            self.status_bar.configure(text=f"Module: {tab_name}")
            
            # Actualiser les données si nécessaire
            if "Tableau de Bord" in tab_name:
                # Actualiser les statistiques du tableau de bord
                pass
            elif "Clients" in tab_name:
                # Actualiser la liste des clients
                pass
        except Exception as e:
            self.show_error(f"Erreur lors du changement d'onglet: {str(e)}")
            
    def show_error(self, message):
        """Affiche un message d'erreur et l'enregistre dans la barre de statut"""
        # Changer l'icône de statut en erreur
        for widget in self.status_bar.master.winfo_children():
            if isinstance(widget, ttk.Label) and widget.cget("text") == "✓":
                widget.configure(text="⚠", foreground=self.colors['error'])
                break
                
        # Mettre à jour le texte de statut
        self.status_bar.configure(text=message)
        
        # Afficher une boîte de dialogue d'erreur
        messagebox.showerror("Erreur", message)

    def create_dashboard(self, parent):
        """Créer le tableau de bord"""

        # Allow dashboard tab to expand
        parent.rowconfigure(0, weight=0)   # stats row
        parent.rowconfigure(1, weight=0)   # actions row
        parent.rowconfigure(2, weight=1)   # recent activities expands
        parent.columnconfigure(0, weight=1)

        # === Statistiques ===
        stats_frame = ttk.LabelFrame(parent, text="Statistiques du Jour", padding=20)
        stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))

        # === Actions Rapides ===
        actions_frame = ttk.LabelFrame(parent, text="Actions Rapides", padding=20)
        actions_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))

        # === Activités Récentes ===
        recent_frame = ttk.LabelFrame(parent, text="Activités Récentes", padding=20)
        recent_frame.grid(row=2, column=0, sticky="nsew")

        # Let recent_frame expand
        recent_frame.rowconfigure(0, weight=1)
        recent_frame.columnconfigure(0, weight=1)

        self.recent_tree = ttk.Treeview(
            recent_frame,
            columns=("Date", "Type", "Client", "Montant", "Station"),
            show="headings",
            style="Touch.Treeview"
        )
        self.recent_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(recent_frame, orient="vertical", command=self.recent_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.recent_tree.configure(yscrollcommand=scrollbar.set)

        # Charger les données
        self.load_dashboard_data()


    def create_stat_card(self, parent, title, value, row, col):
        """Créer une carte de statistique"""
        card_frame = ttk.Frame(parent, relief='ridge', borderwidth=1)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky='ew')

        ttk.Label(card_frame, text=title, style='Touch.TLabel').pack(pady=(10, 5))
        ttk.Label(card_frame, text=value, font=('Arial', 16, 'bold')).pack(pady=(0, 10))

        parent.columnconfigure(col, weight=1)

    def load_stations(self):
        """Charger les stations dans le combo"""
        try:
            stations = self.db_manager.execute_query("SELECT id, nom FROM stations ORDER BY nom")
            station_list = [f"{station[0]} - {station[1]}" for station in stations]
            self.station_combo['values'] = station_list
            if station_list:
                self.station_combo.current(0)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des stations: {str(e)}")

    def load_dashboard_data(self):
        """Charger les données du tableau de bord"""
        try:
            # Placeholder pour stats réelles
            pass
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données: {str(e)}")

    def update_time(self):
        """Mettre à jour l'heure affichée"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def load_window_preferences(self):
        """Charger les préférences de taille de fenêtre depuis la base de données"""
        try:
            # Récupérer l'ID de l'utilisateur connecté
            self.current_user_id = getattr(self, 'current_user', 0)
            
            # Vérifier si la table preferences existe
            try:
                query = """SELECT name FROM sqlite_master 
                          WHERE type='table' AND name='preferences'"""
                result = self.db_manager.execute_query(query)
                
                if not result:
                    # La table n'existe pas encore, on utilise les valeurs par défaut
                    return
                    
                # Récupérer les préférences de fenêtre pour cet utilisateur
                query = """SELECT preference_value FROM preferences 
                          WHERE user_id = ? AND preference_key = 'window_size'"""
                result = self.db_manager.execute_query(query, (self.current_user_id,))
                
                if result and result[0][0]:
                    # Format: largeur,hauteur,position_x,position_y
                    values = result[0][0].split(',')
                    if len(values) == 4:
                        width = int(values[0])
                        height = int(values[1])
                        x = int(values[2])
                        y = int(values[3])
                        
                        # Vérifier que les valeurs sont raisonnables
                        screen_width = self.root.winfo_screenwidth()
                        screen_height = self.root.winfo_screenheight()
                        
                        if (width > 200 and height > 200 and 
                            width <= screen_width and height <= screen_height and
                            x >= 0 and y >= 0 and 
                            x + width <= screen_width and y + height <= screen_height):
                            
                            # Appliquer les dimensions sauvegardées
                            self.root.geometry(f"{width}x{height}+{x}+{y}")
                            self.current_width = width
                            self.current_height = height
                            
                            # Déterminer le mode d'affichage initial
                            if width < 800:
                                self.current_display_mode = "very_compact"
                                self.is_compact_mode = True
                            elif width < 1200:
                                self.current_display_mode = "compact"
                                self.is_compact_mode = True
                            else:
                                self.current_display_mode = "normal"
                                self.is_compact_mode = False
            except Exception as e:
                # Ignorer les erreurs silencieusement - utiliser les valeurs par défaut
                pass
        except Exception as e:
            # Ignorer les erreurs silencieusement - utiliser les valeurs par défaut
            pass
        
    def toggle_dark_mode(self):
        """Basculer entre le mode clair et le mode sombre"""
        self.is_dark_mode = not self.is_dark_mode
        self.colors = self.dark_colors if self.is_dark_mode else self.light_colors
        
        # Mettre à jour les styles avec les nouvelles couleurs
        self.setup_styles()
        
        # Mettre à jour l'interface
        self.update_interface_colors()
        
    def update_interface_colors(self):
        """Mettre à jour les couleurs de l'interface après changement de mode"""
        # Mettre à jour la couleur de fond de la fenêtre principale
        self.root.configure(background=self.colors['background'])
        
        # Mettre à jour les widgets principaux
        for widget in self.main_frame.scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Frame):
                widget.configure(style='TFrame')
                
            # Mettre à jour récursivement les widgets enfants
            self.update_widget_colors(widget)
                
        # Mettre à jour le texte du bouton de mode
        if hasattr(self, 'dark_mode_button'):
            self.dark_mode_button.configure(text="☀️ Mode Clair" if self.is_dark_mode else "🌙 Mode Sombre")
            
        # Mettre à jour les onglets
        if hasattr(self, 'notebook'):
            self.notebook.configure(style='Touch.TNotebook')
            
        # Mettre à jour la barre de statut
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(foreground=self.colors['text_secondary'], background=self.colors['background'])
            
    def update_widget_colors(self, parent):
        """Mettre à jour récursivement les couleurs des widgets enfants"""
        for child in parent.winfo_children():
            # Mettre à jour selon le type de widget
            if isinstance(child, ttk.Label):
                child.configure(foreground=self.colors['text'], background=self.colors['background'])
            elif isinstance(child, ttk.Button):
                # Les boutons sont gérés par le style
                pass
            elif isinstance(child, ttk.Treeview):
                child.configure(style='Touch.Treeview')
            elif isinstance(child, ttk.Entry) or isinstance(child, ttk.Combobox):
                # Les entrées sont gérées par le style
                pass
            elif isinstance(child, ttk.Frame):
                child.configure(style='TFrame')
                
            # Récursion pour les enfants
            if child.winfo_children():
                self.update_widget_colors(child)

    def nouvelle_transaction(self):
        self.notebook.select(2)

    def nouveau_client(self):
        self.notebook.select(1)

    def nouveau_paiement(self):
        self.notebook.select(3)

    def nouvelle_facture(self):
        self.notebook.select(4)

    def get_selected_station_id(self):
        try:
            if self.station_var.get():
                return int(self.station_var.get().split(' - ')[0])
            return None
        except:
            return None

    def open_admin_panel(self):
        if not self.user_role:
            messagebox.showwarning("Accès restreint",
                                   "Veuillez vous connecter pour accéder à l'administration")
            return

        if self.user_role != 'administrateur':
            messagebox.showerror("Accès refusé",
                                 "Vous n'avez pas les droits administrateur")
            return

        AdminPanel(self.root, self.db_manager, self.user_role)
        
    def open_settings_dialog(self):
        """Ouvrir la boîte de dialogue des paramètres"""
        from modules.settings_dialog import SettingsDialog
        settings_dialog = SettingsDialog(self.root, self.db_manager, self.current_user_id)

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def on_window_resize(self, event):
        """Gérer le redimensionnement de la fenêtre pour un affichage adaptatif"""
        # Ne traiter que les événements de la fenêtre principale
        if event.widget != self.root:
            return
            
        new_width = self.root.winfo_width()
        new_height = self.root.winfo_height()
        
        # Éviter les appels répétitifs pour de petits changements
        if abs(new_width - self.current_width) < 10 and abs(new_height - self.current_height) < 10:
            return
        
        # Vérifier si la fenêtre est en mode plein écran
        is_fullscreen = self.root.state() == 'zoomed'
        is_minimized = new_width < 600 or new_height < 400
        
        # Mettre à jour les dimensions actuelles
        self.current_width = new_width
        self.current_height = new_height
        
        # Déterminer le mode d'affichage en fonction de la taille
        # Très petit: < 800px de large
        # Compact: entre 800px et 1200px de large
        # Normal: > 1200px de large ou plein écran
        if is_fullscreen:
            # En mode plein écran, toujours utiliser le mode normal pour maximiser l'affichage
            display_mode = "normal"
        elif new_width < 800:
            display_mode = "very_compact"
        elif new_width < 1200:
            display_mode = "compact"
        else:
            display_mode = "normal"
            
        # Vérifier si le mode a changé
        current_mode = getattr(self, 'current_display_mode', None)
        if display_mode != current_mode:
            self.current_display_mode = display_mode
            self.is_compact_mode = display_mode != "normal"
            self.adjust_interface_for_size()
        
        # Traitement spécial pour les fenêtres très petites
        if is_minimized:
            self.optimize_minimized_layout()
        
        # Ajuster le scrollable frame pour s'adapter à la nouvelle taille
        if hasattr(self, 'main_frame') and hasattr(self.main_frame, 'scrollable_frame'):
            # Forcer une mise à jour des dimensions du scrollable frame
            self.main_frame.scrollable_frame.update_idletasks()
            
        # Sauvegarder les dimensions actuelles pour les futures sessions
        # Ne pas sauvegarder en mode plein écran pour éviter de perdre les dimensions personnalisées
        if not is_fullscreen:
            self.save_window_preferences()
    
    def adjust_interface_for_size(self):
        """Ajuster l'interface en fonction de la taille de la fenêtre"""
        # Forcer une mise à jour pour obtenir les dimensions actuelles
        self.root.update_idletasks()
        
        # Vérifier si la fenêtre est en mode plein écran
        is_fullscreen = self.root.state() == 'zoomed'
        
        # En mode plein écran, toujours utiliser le layout normal
        if is_fullscreen:
            self.apply_normal_layout()
            # Optimiser l'affichage pour le plein écran
            self.optimize_fullscreen_layout()
            return
        
        # Pour les autres modes, appliquer le layout correspondant
        if self.current_display_mode == "very_compact":
            self.apply_very_compact_layout()
        elif self.current_display_mode == "compact":
            self.apply_compact_layout()
        else:
            self.apply_normal_layout()
            
    def save_window_preferences(self):
        """Sauvegarder les préférences de taille de fenêtre"""
        try:
            # Forcer une mise à jour pour obtenir les dimensions actuelles précises
            self.root.update_idletasks()
            
            # Sauvegarder les dimensions actuelles dans la base de données
            # Format: largeur, hauteur, position_x, position_y
            user_id = getattr(self, 'current_user_id', 0)
            width = self.root.winfo_width()  # Utiliser les dimensions actuelles de la fenêtre
            height = self.root.winfo_height()
            x = self.root.winfo_x()
            y = self.root.winfo_y()
            
            # Mettre à jour les variables internes
            self.current_width = width
            self.current_height = height
            
            # Vérifier si une préférence existe déjà pour cet utilisateur
            query = """SELECT COUNT(*) FROM preferences 
                      WHERE user_id = ? AND preference_key = 'window_size'"""
            count = self.db_manager.execute_query(query, (user_id,))
            
            if count and count[0][0] > 0:
                # Mettre à jour la préférence existante
                query = """UPDATE preferences 
                          SET preference_value = ? 
                          WHERE user_id = ? AND preference_key = 'window_size'"""
                self.db_manager.execute_query(query, (f"{width},{height},{x},{y}", user_id))
            else:
                # Créer une nouvelle préférence
                # Vérifier d'abord si la table existe
                try:
                    query = """CREATE TABLE IF NOT EXISTS preferences (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              user_id INTEGER,
                              preference_key TEXT,
                              preference_value TEXT,
                              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
                    self.db_manager.execute_query(query)
                    
                    # Insérer la nouvelle préférence
                    query = """INSERT INTO preferences (user_id, preference_key, preference_value) 
                              VALUES (?, 'window_size', ?)"""
                    self.db_manager.execute_query(query, (user_id, f"{width},{height},{x},{y}"))
                except Exception as e:
                    print(f"Erreur lors de la création de la table des préférences: {str(e)}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des préférences: {str(e)}")
    
    def apply_very_compact_layout(self):
        """Appliquer un layout très compact pour les très petites tailles"""
        # Réduire fortement les paddings
        if hasattr(self, 'main_frame'):
            # Ajuster les paddings du header et autres éléments
            for child in self.main_frame.scrollable_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    child.grid_configure(pady=(1, 3), padx=(0, 3))
        
        # Réduire significativement la taille des polices
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 10, 'bold'))
        style.configure('Touch.TLabel', font=('Segoe UI', 8))
        style.configure('Touch.TButton', font=('Segoe UI', 7))
        style.configure('Touch.TNotebook.Tab', font=('Segoe UI', 8), padding=[5, 3])
        
        # Masquer les éléments non essentiels
        if hasattr(self, 'logo_label'):
            self.logo_label.pack_forget()
            
        # Réduire la hauteur des lignes dans les tableaux
        style.configure('Touch.Treeview', rowheight=25)
        
        # Ajuster les dimensions des widgets pour économiser l'espace
        if hasattr(self, 'dark_mode_button'):
            self.dark_mode_button.configure(text="🌙" if not self.is_dark_mode else "☀️")
            
        # Masquer la barre de statut si elle existe
        if hasattr(self, 'status_bar') and hasattr(self.status_bar, 'master'):
            self.status_bar.master.grid_forget()
            
        # Optimiser l'affichage des boutons dans la barre d'outils
        if hasattr(self, 'toolbar_frame'):
            for widget in self.toolbar_frame.winfo_children():
                if isinstance(widget, tk.Button) or isinstance(widget, ttk.Button):
                    # Réduire le padding des boutons
                    widget.configure(padx=1, pady=1)
                    
        # Assurer que les éléments essentiels sont visibles
        if hasattr(self, 'main_frame'):
            # Forcer une mise à jour pour appliquer les changements
            self.main_frame.update_idletasks()
            
        # Forcer une mise à jour pour appliquer les changements
        self.root.update_idletasks()
    
    def apply_compact_layout(self):
        """Appliquer un layout compact pour les petites tailles"""
        # Réduire les paddings
        if hasattr(self, 'main_frame'):
            # Ajuster les paddings du header
            for child in self.main_frame.scrollable_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    child.grid_configure(pady=(4, 8), padx=(0, 8))
        
        # Réduire la taille des polices
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Touch.TLabel', font=('Segoe UI', 10))
        style.configure('Touch.TButton', font=('Segoe UI', 9))
        style.configure('Touch.TNotebook.Tab', font=('Segoe UI', 10), padding=[15, 8])
        
        # Réduire la hauteur des lignes dans les tableaux
        style.configure('Touch.Treeview', rowheight=35)
        
        # Ajuster les dimensions des widgets pour économiser l'espace
        if hasattr(self, 'dark_mode_button'):
            self.dark_mode_button.configure(text="🌙/☀️")
            
        # Assurer que les éléments essentiels sont visibles
        if hasattr(self, 'logo_label') and not self.logo_label.winfo_ismapped():
            self.logo_label.pack(side=tk.LEFT, padx=(5, 3), pady=3)
            
        # Forcer une mise à jour pour appliquer les changements
        self.root.update_idletasks()
        
        # Masquer certains éléments non essentiels
        if hasattr(self, 'logo_label'):
            self.logo_label.pack_forget()
            
        # Ajuster la hauteur des lignes dans les tableaux
        style.configure('Touch.Treeview', rowheight=35)
        
        # Restaurer le texte complet du bouton de mode
        if hasattr(self, 'dark_mode_button'):
            self.dark_mode_button.configure(text="🌙 Mode Sombre" if not self.is_dark_mode else "☀️ Mode Clair")
            
        # Afficher la barre de statut si elle était masquée
        if hasattr(self, 'status_bar') and hasattr(self.status_bar, 'master'):
            if not self.status_bar.master.winfo_viewable():
                self.status_bar.master.grid(row=3, column=0, sticky="ew", pady=(15, 0), padx=(0, 20))
    
    def apply_normal_layout(self):
        """Appliquer un layout normal pour les tailles standard"""
        # Restaurer les paddings normaux
        if hasattr(self, 'main_frame'):
            for child in self.main_frame.scrollable_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    child.grid_configure(pady=(10, 20), padx=(0, 20))
        
        # Restaurer les tailles de police normales
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
        style.configure('Touch.TLabel', font=('Segoe UI', 14))
        style.configure('Touch.TButton', font=('Segoe UI', 14, 'bold'))
        style.configure('Touch.TNotebook.Tab', font=('Segoe UI', 14), padding=[20, 12])
        
        # Restaurer la hauteur des lignes dans les tableaux
        style.configure('Touch.Treeview', rowheight=45)
        
        # Réafficher les éléments masqués
        if hasattr(self, 'logo_label') and hasattr(self, 'title_container'):
            self.logo_label.pack(side="left", padx=(0, 10))
            
        # Restaurer le texte complet du bouton de mode
        if hasattr(self, 'dark_mode_button'):
            self.dark_mode_button.configure(text="🌙 Mode Sombre" if not self.is_dark_mode else "☀️ Mode Clair")
            
        # Afficher la barre de statut si elle était masquée
        if hasattr(self, 'status_bar') and hasattr(self.status_bar, 'master'):
            if not self.status_bar.master.winfo_viewable():
                self.status_bar.master.grid(row=3, column=0, sticky="ew", pady=(15, 0), padx=(0, 20))
                
    def optimize_fullscreen_layout(self):
        """Optimiser l'affichage en mode plein écran pour maximiser l'espace disponible"""
        # Vérifier si la fenêtre est en mode plein écran
        if self.root.state() != 'zoomed':
            return
            
        # Obtenir les dimensions de l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Ajuster les paddings pour utiliser l'espace disponible
        if hasattr(self, 'main_frame'):
            # Augmenter légèrement les paddings pour améliorer la lisibilité
            for child in self.main_frame.scrollable_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    child.grid_configure(pady=(12, 18), padx=(5, 20))
        
        # Optimiser la taille des polices pour une meilleure lisibilité
        style = ttk.Style()
        
        # Si l'écran est très large (>1920px), augmenter légèrement les polices
        if screen_width > 1920:
            style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
            style.configure('Touch.TLabel', font=('Segoe UI', 12))
            style.configure('Touch.TButton', font=('Segoe UI', 11))
            style.configure('Touch.TNotebook.Tab', font=('Segoe UI', 12), padding=[25, 12])
            style.configure('Touch.Treeview', rowheight=45)
        
        # Forcer une mise à jour pour appliquer les changements
        self.root.update_idletasks()
        
    def optimize_minimized_layout(self):
        """Optimiser l'affichage pour les fenêtres très petites"""
        # Réduire au maximum les paddings
        if hasattr(self, 'main_frame'):
            for child in self.main_frame.scrollable_frame.winfo_children():
                if isinstance(child, ttk.Frame):
                    child.grid_configure(pady=(0, 1), padx=(0, 1))
        
        # Réduire au minimum la taille des polices
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Segoe UI', 9, 'bold'))
        style.configure('Touch.TLabel', font=('Segoe UI', 7))
        style.configure('Touch.TButton', font=('Segoe UI', 7))
        style.configure('Touch.TNotebook.Tab', font=('Segoe UI', 7), padding=[3, 2])
        
        # Réduire au minimum la hauteur des lignes dans les tableaux
        style.configure('Touch.Treeview', rowheight=20)
        
        # Masquer tous les éléments non essentiels
        if hasattr(self, 'logo_label'):
            self.logo_label.pack_forget()
            
        if hasattr(self, 'title_container'):
            self.title_container.pack_forget()
            
        # Réduire les boutons à des icônes uniquement
        if hasattr(self, 'dark_mode_button'):
            self.dark_mode_button.configure(text="🌙" if not self.is_dark_mode else "☀️")
            
        # Masquer la barre de statut
        if hasattr(self, 'status_bar') and hasattr(self.status_bar, 'master'):
            self.status_bar.master.grid_forget()
            
        # Optimiser l'affichage des boutons dans la barre d'outils
        if hasattr(self, 'toolbar_frame'):
            for widget in self.toolbar_frame.winfo_children():
                if isinstance(widget, tk.Button) or isinstance(widget, ttk.Button):
                    # Réduire le padding des boutons au minimum
                    widget.configure(padx=0, pady=0)
        
        # Forcer une mise à jour pour appliquer les changements
        self.root.update_idletasks()