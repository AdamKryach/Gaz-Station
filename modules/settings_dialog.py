import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class SettingsDialog:
    def __init__(self, parent, db_manager, current_user_id=0):
        """Initialiser la boîte de dialogue des paramètres"""
        self.parent = parent
        self.db_manager = db_manager
        self.current_user_id = current_user_id
        
        # Créer une nouvelle fenêtre modale
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Paramètres d'affichage")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)  # Rendre la fenêtre modale
        self.dialog.grab_set()  # Bloquer les interactions avec la fenêtre principale
        
        # Centrer la fenêtre
        self.center_window()
        
        # Créer l'interface
        self.create_interface()
        
        # Charger les paramètres actuels
        self.load_settings()
    
    def center_window(self):
        """Centrer la fenêtre sur l'écran"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_interface(self):
        """Créer l'interface utilisateur de la boîte de dialogue"""
        # Créer un notebook pour organiser les paramètres
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Onglet des paramètres de fenêtre
        self.window_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.window_frame, text="Fenêtre")
        
        # Onglet des paramètres d'apparence
        self.appearance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.appearance_frame, text="Apparence")
        
        # Paramètres de fenêtre
        ttk.Label(self.window_frame, text="Taille de fenêtre au démarrage:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Options de taille de fenêtre
        self.window_size_var = tk.StringVar()
        size_frame = ttk.Frame(self.window_frame)
        size_frame.grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        ttk.Radiobutton(size_frame, text="Dernière taille utilisée", value="last_used", variable=self.window_size_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(size_frame, text="Taille personnalisée", value="custom", variable=self.window_size_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(size_frame, text="Plein écran", value="fullscreen", variable=self.window_size_var).pack(anchor="w", pady=2)
        
        # Taille personnalisée
        custom_size_frame = ttk.Frame(self.window_frame)
        custom_size_frame.grid(row=2, column=0, sticky="w", padx=20, pady=10)
        
        ttk.Label(custom_size_frame, text="Largeur:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.width_var = tk.StringVar()
        ttk.Entry(custom_size_frame, textvariable=self.width_var, width=6).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(custom_size_frame, text="Hauteur:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.height_var = tk.StringVar()
        ttk.Entry(custom_size_frame, textvariable=self.height_var, width=6).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Position de la fenêtre
        ttk.Label(self.window_frame, text="Position de la fenêtre:").grid(row=3, column=0, sticky="w", padx=10, pady=10)
        
        self.window_position_var = tk.StringVar()
        position_frame = ttk.Frame(self.window_frame)
        position_frame.grid(row=4, column=0, sticky="w", padx=20, pady=5)
        
        ttk.Radiobutton(position_frame, text="Dernière position utilisée", value="last_used", variable=self.window_position_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(position_frame, text="Centrer sur l'écran", value="center", variable=self.window_position_var).pack(anchor="w", pady=2)
        
        # Paramètres d'apparence
        ttk.Label(self.appearance_frame, text="Mode d'affichage:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        self.display_mode_var = tk.StringVar()
        mode_frame = ttk.Frame(self.appearance_frame)
        mode_frame.grid(row=1, column=0, sticky="w", padx=20, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Automatique (basé sur la taille de fenêtre)", value="auto", variable=self.display_mode_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(mode_frame, text="Normal", value="normal", variable=self.display_mode_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(mode_frame, text="Compact", value="compact", variable=self.display_mode_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(mode_frame, text="Très compact", value="very_compact", variable=self.display_mode_var).pack(anchor="w", pady=2)
        
        # Thème
        ttk.Label(self.appearance_frame, text="Thème:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        
        self.theme_var = tk.StringVar()
        theme_frame = ttk.Frame(self.appearance_frame)
        theme_frame.grid(row=3, column=0, sticky="w", padx=20, pady=5)
        
        ttk.Radiobutton(theme_frame, text="Clair", value="light", variable=self.theme_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(theme_frame, text="Sombre", value="dark", variable=self.theme_var).pack(anchor="w", pady=2)
        ttk.Radiobutton(theme_frame, text="Système", value="system", variable=self.theme_var).pack(anchor="w", pady=2)
        
        # Boutons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Appliquer", command=self.apply_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.save_and_close).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Annuler", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def load_settings(self):
        """Charger les paramètres actuels"""
        # Valeurs par défaut
        self.window_size_var.set("last_used")
        self.window_position_var.set("last_used")
        self.display_mode_var.set("auto")
        self.theme_var.set("light")
        
        # Récupérer la taille actuelle de la fenêtre principale
        width = self.parent.winfo_width()
        height = self.parent.winfo_height()
        self.width_var.set(str(width))
        self.height_var.set(str(height))
        
        try:
            # Vérifier si la table preferences existe
            query = """SELECT name FROM sqlite_master 
                      WHERE type='table' AND name='preferences'"""
            result = self.db_manager.execute_query(query)
            
            if not result:
                # Créer la table si elle n'existe pas
                self.create_preferences_table()
            
            # Charger les préférences de l'utilisateur
            query = """SELECT preference_key, preference_value FROM preferences 
                      WHERE user_id = ?"""
            result = self.db_manager.execute_query(query, (self.current_user_id,))
            
            if result:
                for row in result:
                    key, value = row
                    if key == "window_size_option":
                        self.window_size_var.set(value)
                    elif key == "window_position_option":
                        self.window_position_var.set(value)
                    elif key == "display_mode":
                        self.display_mode_var.set(value)
                    elif key == "theme":
                        self.theme_var.set(value)
                    elif key == "custom_width":
                        self.width_var.set(value)
                    elif key == "custom_height":
                        self.height_var.set(value)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des paramètres: {str(e)}")
    
    def create_preferences_table(self):
        """Créer la table des préférences si elle n'existe pas"""
        try:
            query = """CREATE TABLE IF NOT EXISTS preferences (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      preference_key TEXT NOT NULL,
                      preference_value TEXT,
                      UNIQUE(user_id, preference_key)
                      )"""
            self.db_manager.execute_query(query)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la table des préférences: {str(e)}")
    
    def save_preference(self, key, value):
        """Enregistrer une préférence dans la base de données"""
        try:
            query = """INSERT OR REPLACE INTO preferences (user_id, preference_key, preference_value)
                      VALUES (?, ?, ?)"""
            self.db_manager.execute_query(query, (self.current_user_id, key, value))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement des préférences: {str(e)}")
    
    def apply_settings(self):
        """Appliquer les paramètres sans fermer la boîte de dialogue"""
        try:
            # Enregistrer les préférences
            self.save_preference("window_size_option", self.window_size_var.get())
            self.save_preference("window_position_option", self.window_position_var.get())
            self.save_preference("display_mode", self.display_mode_var.get())
            self.save_preference("theme", self.theme_var.get())
            self.save_preference("custom_width", self.width_var.get())
            self.save_preference("custom_height", self.height_var.get())
            
            # Forcer une mise à jour des tâches inactives avant d'appliquer les paramètres
            self.parent.update_idletasks()
            
            # Appliquer les paramètres à la fenêtre principale
            self.apply_window_settings()
            self.apply_appearance_settings()
            
            # Récupérer l'instance de MainWindow
            if hasattr(self.parent, "main_window"):
                main_window = self.parent.main_window
            else:
                main_window = self.parent
                
            # Forcer un ajustement complet de l'interface
            if hasattr(main_window, "adjust_interface_for_size"):
                main_window.adjust_interface_for_size()
            
            # Forcer une mise à jour finale
            self.parent.update()
            
            messagebox.showinfo("Succès", "Les paramètres ont été appliqués avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'application des paramètres: {str(e)}")
    
    def save_and_close(self):
        """Enregistrer les paramètres et fermer la boîte de dialogue"""
        self.apply_settings()
        self.dialog.destroy()
    
    def apply_window_settings(self):
        """Appliquer les paramètres de fenêtre"""
        window_size_option = self.window_size_var.get()
        window_position_option = self.window_position_var.get()
        
        # Obtenir la taille actuelle de la fenêtre
        current_width = self.parent.winfo_width()
        current_height = self.parent.winfo_height()
        
        # Déterminer la nouvelle taille
        if window_size_option == "custom":
            try:
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                
                # Vérifier que les valeurs sont raisonnables
                screen_width = self.parent.winfo_screenwidth()
                screen_height = self.parent.winfo_screenheight()
                
                if width < 800:
                    width = 800
                if height < 600:
                    height = 600
                if width > screen_width:
                    width = screen_width
                if height > screen_height:
                    height = screen_height
            except ValueError:
                messagebox.showerror("Erreur", "Les dimensions doivent être des nombres entiers.")
                return
        elif window_size_option == "fullscreen":
            # Mettre en plein écran
            self.parent.state('zoomed')
            return
        else:  # last_used
            width = current_width
            height = current_height
        
        # Déterminer la position
        if window_position_option == "center":
            x = (self.parent.winfo_screenwidth() // 2) - (width // 2)
            y = (self.parent.winfo_screenheight() // 2) - (height // 2)
        else:  # last_used
            x = self.parent.winfo_x()
            y = self.parent.winfo_y()
        
        # Appliquer la géométrie
        self.parent.geometry(f"{width}x{height}+{x}+{y}")
        
        # Enregistrer la taille et la position actuelles
        if hasattr(self.parent, "main_window"):
            main_window = self.parent.main_window
        else:
            main_window = self.parent
            
        if hasattr(main_window, "save_window_preferences"):
            main_window.save_window_preferences()
    
    def apply_appearance_settings(self):
        """Appliquer les paramètres d'apparence"""
        display_mode = self.display_mode_var.get()
        theme = self.theme_var.get()
        
        # Appliquer le mode d'affichage
        if hasattr(self.parent, "main_window"):
            main_window = self.parent.main_window
        else:
            main_window = self.parent
            
        # Forcer une mise à jour des tâches inactives pour s'assurer que les dimensions sont correctes
        self.parent.update_idletasks()
            
        if display_mode != "auto" and hasattr(main_window, "adjust_interface_for_size"):
            main_window.current_display_mode = display_mode
            
            if display_mode == "very_compact":
                main_window.is_compact_mode = True
                main_window.apply_very_compact_layout()
            elif display_mode == "compact":
                main_window.is_compact_mode = True
                main_window.apply_compact_layout()
            else:  # normal
                main_window.is_compact_mode = False
                main_window.apply_normal_layout()
            
            # Forcer une mise à jour complète après l'application du layout
            self.parent.update()
        
        # Appliquer le thème
        if theme != "system" and hasattr(main_window, "is_dark_mode"):
            if theme == "dark" and not main_window.is_dark_mode:
                main_window.toggle_dark_mode()
            elif theme == "light" and main_window.is_dark_mode:
                main_window.toggle_dark_mode()
                
        # Forcer une mise à jour finale pour s'assurer que tous les changements sont appliqués
        self.parent.update_idletasks()