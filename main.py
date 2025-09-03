#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application de Comptabilité pour Stations-Service
Système de gestion pour 6 stations-service avec:
- Gestion des clients
- Suivi de consommation de carburant
- Paiements d'avance
- Soldes restants
- Impression de factures en DH
- Support écran tactile
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# === Ajouter le répertoire du projet au chemin Python ===
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.main_window import MainWindow
from modules.auth import LoginDialog, AdminPanel


class GazStationApp:
    def __init__(self):
        # === Fenêtre principale ===
        self.root = tk.Tk()
        self.root.title("Gestion Stations-Service - Comptabilité")
        self.root.state('zoomed')  # Plein écran (utile pour tactile)
        self.root.configure(bg='#f0f0f0')

        # === Config responsive sur la fenêtre principale ===
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # === Base de données ===
        self.db_manager = DatabaseManager()

        # === Connexion utilisateur ===
        login = LoginDialog(self.root, self.db_manager)
        self.root.wait_window(login.dialog)

        if not login.user_role:
            self.root.quit()
            return

        # Stocker l'utilisateur connecté
        self.current_user = login.user_name
        self.user_role = login.user_role

        # === Création de l'interface principale ===
        self.main_window = MainWindow(self.root, self.db_manager, self.user_role)
        self.main_window.current_user = self.current_user
        self.main_window.user_role = self.user_role

        # === Menu ===
        self.setup_menu()

    # -----------------------------------------------------
    # Menu
    # -----------------------------------------------------
    def setup_menu(self):
        """Configuration du menu selon le rôle utilisateur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self.root.quit)

        # Menu Administration
        if self.user_role == 'administrateur':
            admin_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Administration", menu=admin_menu)
            admin_menu.add_command(label="Panneau d'Administration", command=self.open_admin_panel)

        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)

        # Ajouter l'utilisateur connecté au titre
        user_info = f"Connecté: {self.current_user} ({self.user_role.title()})"
        self.root.title(f"Gestion Stations-Service - {user_info}")

    def open_admin_panel(self):
        """Ouvrir le panneau d'administration"""
        AdminPanel(self.root, self.db_manager, self.user_role)

    def show_about(self):
        """Afficher les informations sur l'application"""
        about_text = """
Application de Gestion des Stations-Service
Version 2.0

Fonctionnalités:
- Gestion simplifiée des clients
- Suivi des transactions de carburant
- Gestion des véhicules avec matricules marocains
- Système de connexion sécurisé
- Rapports et statistiques

Optimisé pour écran tactile
        """
        messagebox.showinfo("À propos", about_text.strip())

    def run(self):
        """Démarrer l'application"""
        if hasattr(self, 'user_role'):
            self.root.mainloop()


# === Point d'entrée principal ===
if __name__ == "__main__":
    try:
        app = GazStationApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du démarrage: {str(e)}")
