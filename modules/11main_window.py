# -*- coding: utf-8 -*-
"""
Fenêtre principale simplifiée avec date/heure à gauche
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class MainWindow:
    def __init__(self, root, db_manager, user_role=None):
        self.root = root
        self.db_manager = db_manager
        self.user_role = user_role
        
        # Config responsive
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Créer l'interface principale
        self.create_main_interface()

    def create_main_interface(self):
        """Créer l'interface principale avec date/heure à gauche"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # === En-tête avec date/heure à gauche ===
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=10, padx=10)
        
        # Conteneur gauche pour la date/heure
        left_container = ttk.Frame(header_frame)
        left_container.pack(side="left", fill="y")
        
        # Affichage de la date et heure avec icône (à gauche)
        time_container = ttk.Frame(left_container)
        time_container.pack(side="left", padx=5)
        
        time_icon = ttk.Label(
            time_container,
            text="🕒",
            font=('Segoe UI', 16)
        )
        time_icon.pack(side="left", padx=(0, 5))
        
        self.time_label = ttk.Label(
            time_container, 
            text="", 
            font=('Segoe UI', 14, 'bold')
        )
        self.time_label.pack(side="right")
        self.update_time()
        
        # Séparateur vertical
        ttk.Separator(left_container, orient='vertical').pack(side="left", fill="y", padx=10, pady=5)
        
        # Logo et titre dans un conteneur
        title_container = ttk.Frame(header_frame)
        title_container.pack(side="left", fill="y")
        
        # Icône de l'application
        logo_label = ttk.Label(
            title_container,
            text="⛽",
            font=('Segoe UI', 24)
        )
        logo_label.pack(side="left", padx=(0, 10))
        
        # Titre de l'application
        title_label = ttk.Label(
            title_container,
            text="Système de Gestion de Station Timizar",
            font=('Segoe UI', 22, 'bold')
        )
        title_label.pack(side="left")

        # === Contenu principal (placeholder) ===
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", pady=10, padx=10)
        
        # Ajouter des onglets simples
        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill="both", expand=True)
        
        # Onglets de base
        tabs = ["Clients", "Carburant", "Paiements", "Factures", "Rapports"]
        for tab_name in tabs:
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=tab_name)
            
            # Ajouter un label dans chaque onglet
            ttk.Label(tab, text=f"Contenu de l'onglet {tab_name}").pack(pady=20)

    def update_time(self):
        """Mettre à jour l'heure affichée"""
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)