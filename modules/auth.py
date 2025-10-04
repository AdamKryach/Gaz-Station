# -*- coding: utf-8 -*-
"""
Module d'authentification pour les utilisateurs
"""

import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime

class LoginDialog:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.user_role = None
        self.user_id = None
        self.user_name = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connexion - Station Service")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+{}+{}".format(
            (self.dialog.winfo_screenwidth() // 2) - 200,
            (self.dialog.winfo_screenheight() // 2) - 150
        ))
        
        self.setup_login_form()
        self.dialog.focus()
        
        # Prevent closing with X button
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def setup_login_form(self):
        """Configuration du formulaire de connexion"""
        main_frame = ttk.Frame(self.dialog, padding=30)
        main_frame.pack(fill='both', expand=True)
        
        # Logo/Title
        title_label = ttk.Label(main_frame, text="GESTION STATION-SERVICE", 
                               font=('Arial', 18, 'bold'), foreground='blue')
        title_label.pack(pady=(0, 30))
        
        # Login form
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill='both', expand=True)
        
        # Username
        ttk.Label(form_frame, text="Nom d'utilisateur:", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, 
                                       font=('Arial', 12), width=25)
        self.username_entry.pack(pady=(0, 15), fill='x')
        
        # Password
        ttk.Label(form_frame, text="Mot de passe:", 
                 font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                       show='*', font=('Arial', 12), width=25)
        self.password_entry.pack(pady=(0, 20), fill='x')
        
        # Buttons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Connexion", 
                  command=self.authenticate,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Quitter", 
                  command=self.on_cancel,
                  style='Touch.TButton').pack(side='left')
        
        # Info panel
        info_frame = ttk.LabelFrame(main_frame, text="Comptes par défaut", padding=10)
        info_frame.pack(fill='x', pady=(20, 0))
        
        info_text = """
Admin: admin / admin123
Employé: employe / employe123
        """
        ttk.Label(info_frame, text=info_text.strip(), 
                 font=('Arial', 10), foreground='gray').pack()
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.authenticate())
        
        # Focus on username field
        self.username_entry.focus_set()
    
    def authenticate(self):
        """Authentifier l'utilisateur"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez saisir votre nom d'utilisateur et mot de passe")
            return
        
        try:
            # Hash du mot de passe pour comparaison
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Vérifier dans la base de données
            query = """
                SELECT id, nom_utilisateur, role, nom_complet, actif
                FROM utilisateurs
                WHERE nom_utilisateur = ? AND mot_de_passe = ? AND actif = 1
            """
            result = self.db_manager.execute_query(query, (username, password_hash))
            
            if result:
                user_data = result[0]
                self.user_id = user_data[0]
                self.user_name = user_data[3] or user_data[1]
                self.user_role = user_data[2]
                
                messagebox.showinfo("Connexion réussie", 
                                   f"Bienvenue {self.user_name}!\nRôle: {self.user_role.title()}")
                
                self.dialog.destroy()
                
            else:
                messagebox.showerror("Erreur de connexion", 
                                    "Nom d'utilisateur ou mot de passe incorrect")
                self.password_var.set('')
                self.password_entry.focus_set()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la connexion: {str(e)}")
    
    def on_cancel(self):
        """Annuler la connexion"""
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment quitter l'application?"):
            self.dialog.destroy()
            # Exit the main application
            self.dialog.master.quit()

class AdminPanel:
    def __init__(self, parent, db_manager, user_role):
        self.parent = parent
        self.db_manager = db_manager
        self.user_role = user_role
        
        if user_role != 'administrateur':
            messagebox.showerror("Accès refusé", "Vous n'avez pas les droits administrateur")
            return
        
        self.setup_admin_interface()
    
    def setup_admin_interface(self):
        """Interface d'administration"""
        admin_window = tk.Toplevel(self.parent)
        admin_window.title("Panneau d'Administration")
        admin_window.geometry("800x600")
        admin_window.transient(self.parent)
        admin_window.grab_set()
        
        notebook = ttk.Notebook(admin_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet Gestion des Prix
        self.setup_price_management(notebook)
        
        # Onglet Gestion des Stations
        self.setup_station_management(notebook)
        
        # Onglet Gestion des Utilisateurs
        self.setup_user_management(notebook)
    
    def setup_price_management(self, notebook):
        """Gestion des prix des carburants"""
        price_frame = ttk.Frame(notebook)
        notebook.add(price_frame, text="Gestion des Prix")
        
        main_frame = ttk.Frame(price_frame, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Gestion des Prix des Carburants", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Price list
        columns = ('ID', 'Carburant', 'Prix Actuel (DH/L)', 'Unité')
        self.price_tree = ttk.Treeview(main_frame, columns=columns, show='headings',
                                      style='Touch.Treeview', height=8)
        
        for col in columns:
            self.price_tree.heading(col, text=col)
            self.price_tree.column(col, width=150)
        
        scrollbar_price = ttk.Scrollbar(main_frame, orient='vertical', command=self.price_tree.yview)
        self.price_tree.configure(yscrollcommand=scrollbar_price.set)
        
        self.price_tree.pack(side='left', fill='both', expand=True)
        scrollbar_price.pack(side='right', fill='y')
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Nouveau Carburant", 
                  command=self.create_fuel,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Modifier Carburant", 
                  command=self.edit_fuel,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Modifier Prix", 
                  command=self.edit_price,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Supprimer Carburant", 
                  command=self.delete_fuel,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Actualiser", 
                  command=self.load_fuel_prices,
                  style='Touch.TButton').pack(side='left')
        
        # Load initial data
        self.load_fuel_prices()
    
    def setup_station_management(self, notebook):
        """Gestion des stations"""
        station_frame = ttk.Frame(notebook)
        notebook.add(station_frame, text="Gestion des Stations")
        
        main_frame = ttk.Frame(station_frame, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Gestion des Stations", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # Station list
        columns = ('ID', 'Nom Station', 'Adresse', 'Téléphone', 'Responsable')
        self.station_tree = ttk.Treeview(main_frame, columns=columns, show='headings',
                                        style='Touch.Treeview', height=8)
        
        for col in columns:
            self.station_tree.heading(col, text=col)
            self.station_tree.column(col, width=120)
        
        scrollbar_station = ttk.Scrollbar(main_frame, orient='vertical', command=self.station_tree.yview)
        self.station_tree.configure(yscrollcommand=scrollbar_station.set)
        
        self.station_tree.pack(side='left', fill='both', expand=True)
        scrollbar_station.pack(side='right', fill='y')
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Nouvelle Station", 
                  command=self.create_station,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Modifier Station", 
                  command=self.edit_station,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Supprimer Station", 
                  command=self.delete_station,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Actualiser", 
                  command=self.load_stations,
                  style='Touch.TButton').pack(side='left')
        
        # Load initial data
        self.load_stations()
    
    def setup_user_management(self, notebook):
        """Gestion des utilisateurs"""
        user_frame = ttk.Frame(notebook)
        notebook.add(user_frame, text="Gestion des Utilisateurs")
        
        main_frame = ttk.Frame(user_frame, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(main_frame, text="Gestion des Utilisateurs", 
                 font=('Arial', 16, 'bold')).pack(pady=(0, 20))
        
        # User list
        columns = ('ID', 'Nom d\'utilisateur', 'Rôle', 'Nom complet', 'Actif')
        self.user_tree = ttk.Treeview(main_frame, columns=columns, show='headings',
                                     style='Touch.Treeview', height=8)
        
        for col in columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=120)
        
        scrollbar_user = ttk.Scrollbar(main_frame, orient='vertical', command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar_user.set)
        
        self.user_tree.pack(side='left', fill='both', expand=True)
        scrollbar_user.pack(side='right', fill='y')
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(btn_frame, text="Nouvel Utilisateur", 
                  command=self.create_user,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Modifier Utilisateur", 
                  command=self.edit_user,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Supprimer Utilisateur", 
                  command=self.delete_user,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Actualiser", 
                  command=self.load_users,
                  style='Touch.TButton').pack(side='left')
        
        # Load initial data
        self.load_users()
    
    def load_fuel_prices(self):
        """Charger les prix des carburants"""
        try:
            # Clear existing items
            for item in self.price_tree.get_children():
                self.price_tree.delete(item)
            
            query = "SELECT id, nom, prix_unitaire, unite FROM carburants ORDER BY nom"
            fuels = self.db_manager.execute_query(query)
            
            for fuel in fuels:
                self.price_tree.insert('', 'end', values=fuel)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des prix: {str(e)}")
    
    def load_stations(self):
        """Charger les stations"""
        try:
            # Clear existing items
            for item in self.station_tree.get_children():
                self.station_tree.delete(item)
            
            query = "SELECT id, nom, adresse, telephone, responsable FROM stations ORDER BY nom"
            stations = self.db_manager.execute_query(query)
            
            for station in stations:
                self.station_tree.insert('', 'end', values=station)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des stations: {str(e)}")
    
    def load_users(self):
        """Charger les utilisateurs"""
        try:
            # Clear existing items
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            
            query = "SELECT id, nom_utilisateur, role, nom_complet, actif FROM utilisateurs ORDER BY nom_utilisateur"
            users = self.db_manager.execute_query(query)
            
            for user in users:
                user_id, username, role, nom_complet, actif = user
                actif_text = "Oui" if actif else "Non"
                values = (user_id, username, role.title(), nom_complet or '', actif_text)
                self.user_tree.insert('', 'end', values=values)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des utilisateurs: {str(e)}")
    
    def edit_price(self):
        """Modifier le prix d'un carburant"""
        selection = self.price_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un carburant")
            return
        
        item = selection[0]
        values = self.price_tree.item(item)['values']
        fuel_id, nom, prix_actuel, unite = values
        
        PriceEditDialog(self.parent, self.db_manager, fuel_id, nom, prix_actuel, self.load_fuel_prices)
    
    def edit_station(self):
        """Modifier une station"""
        selection = self.station_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une station")
            return
        
        item = selection[0]
        values = self.station_tree.item(item)['values']
        station_id, nom, adresse, telephone, responsable = values
        
        StationEditDialog(self.parent, self.db_manager, station_id, nom, adresse, telephone, responsable, self.load_stations)
    
    def create_user(self):
        """Créer un nouvel utilisateur"""
        UserEditDialog(self.parent, self.db_manager, None, self.load_users)
    
    def edit_user(self):
        """Modifier un utilisateur"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un utilisateur")
            return
        
        item = selection[0]
        user_id = self.user_tree.item(item)['values'][0]
        
        UserEditDialog(self.parent, self.db_manager, user_id, self.load_users)
    
    def create_station(self):
        """Créer une nouvelle station"""
        StationEditDialog(self.parent, self.db_manager, None, '', '', '', '', self.load_stations)
    
    def delete_station(self):
        """Supprimer une station"""
        selection = self.station_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une station")
            return
        
        item = selection[0]
        values = self.station_tree.item(item)['values']
        station_id, nom, adresse, responsable = values
        
        # Vérifier s'il y a des transactions liées
        check_query = "SELECT COUNT(*) FROM transactions WHERE station_id = ?"
        result = self.db_manager.execute_query(check_query, (station_id,))
        transaction_count = result[0][0] if result else 0
        
        if transaction_count > 0:
            if not messagebox.askyesno("Attention", 
                f"La station '{nom}' a {transaction_count} transaction(s) associée(s).\n" +
                "Supprimer cette station supprimera également toutes ses transactions.\n" +
                "Êtes-vous sûr de vouloir continuer?"):
                return
        
        if messagebox.askyesno("Confirmation", f"Supprimer la station '{nom}'?"):
            try:
                # Supprimer les transactions d'abord
                self.db_manager.execute_update("DELETE FROM transactions WHERE station_id = ?", (station_id,))
                
                # Supprimer la station
                self.db_manager.execute_update("DELETE FROM stations WHERE id = ?", (station_id,))
                
                messagebox.showinfo("Succès", f"Station '{nom}' supprimée avec succès")
                self.load_stations()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def delete_user(self):
        """Supprimer un utilisateur"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un utilisateur")
            return
        
        item = selection[0]
        values = self.user_tree.item(item)['values']
        user_id, username, role, nom_complet, actif = values
        
        # Empêcher la suppression du dernier administrateur
        if role.lower() == 'administrateur':
            admin_count_query = "SELECT COUNT(*) FROM utilisateurs WHERE role = 'administrateur' AND actif = 1"
            result = self.db_manager.execute_query(admin_count_query)
            admin_count = result[0][0] if result else 0
            
            if admin_count <= 1:
                messagebox.showerror("Erreur", 
                    "Impossible de supprimer le dernier administrateur actif.\n" +
                    "Il doit y avoir au moins un administrateur dans le système.")
                return
        
        if messagebox.askyesno("Confirmation", f"Supprimer l'utilisateur '{username}'?"):
            try:
                self.db_manager.execute_update("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
                
                messagebox.showinfo("Succès", f"Utilisateur '{username}' supprimé avec succès")
                self.load_users()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def create_fuel(self):
        """Créer un nouveau carburant"""
        FuelEditDialog(self.parent, self.db_manager, None, self.load_fuel_prices)
    
    def edit_fuel(self):
        """Modifier un carburant (nom, prix, unité)"""
        selection = self.price_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un carburant")
            return
        
        item = selection[0]
        values = self.price_tree.item(item)['values']
        fuel_id = values[0]
        
        FuelEditDialog(self.parent, self.db_manager, fuel_id, self.load_fuel_prices)
    
    def delete_fuel(self):
        """Supprimer un carburant"""
        selection = self.price_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un carburant")
            return
        
        item = selection[0]
        values = self.price_tree.item(item)['values']
        fuel_id, nom, prix_actuel, unite = values
        
        # Vérifier s'il y a des transactions liées
        check_query = "SELECT COUNT(*) FROM transactions WHERE carburant_id = ?"
        result = self.db_manager.execute_query(check_query, (fuel_id,))
        transaction_count = result[0][0] if result else 0
        
        if transaction_count > 0:
            if not messagebox.askyesno("Attention", 
                f"Le carburant '{nom}' a {transaction_count} transaction(s) associée(s).\n" +
                "Supprimer ce carburant supprimera également toutes ses transactions.\n" +
                "Êtes-vous sûr de vouloir continuer?"):
                return
        
        if messagebox.askyesno("Confirmation", f"Supprimer le carburant '{nom}'?"):
            try:
                # Supprimer les transactions d'abord
                if transaction_count > 0:
                    self.db_manager.execute_update("DELETE FROM transactions WHERE carburant_id = ?", (fuel_id,))
                
                # Supprimer le carburant
                self.db_manager.execute_update("DELETE FROM carburants WHERE id = ?", (fuel_id,))
                
                messagebox.showinfo("Succès", f"Carburant '{nom}' supprimé avec succès")
                self.load_fuel_prices()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

class FuelEditDialog:
    def __init__(self, parent, db_manager, fuel_id, callback):
        self.db_manager = db_manager
        self.fuel_id = fuel_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Carburant" if not fuel_id else "Modifier Carburant")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        
        if fuel_id:
            self.load_fuel_data()
    
    def setup_dialog(self):
        """Configuration de la fenêtre de carburant"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Variables
        self.nom_var = tk.StringVar()
        self.prix_var = tk.StringVar()
        self.unite_var = tk.StringVar(value='Litre')
        
        # Nom du carburant
        ttk.Label(main_frame, text="Nom du carburant:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.nom_var, 
                 font=('Arial', 12), width=30).pack(fill='x', pady=(0, 10))
        
        # Prix unitaire
        ttk.Label(main_frame, text="Prix unitaire (DH):", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.prix_var, 
                 font=('Arial', 12), width=30).pack(fill='x', pady=(0, 10))
        
        # Unité
        ttk.Label(main_frame, text="Unité de mesure:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        unite_combo = ttk.Combobox(main_frame, textvariable=self.unite_var,
                                  values=['Litre', 'Gallon', 'Kg'], 
                                  state='readonly', width=28)
        unite_combo.pack(fill='x', pady=(0, 20))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Enregistrer", 
                  command=self.save_fuel).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Annuler", 
                  command=self.dialog.destroy).pack(side='left')
    
    def load_fuel_data(self):
        """Charger les données du carburant à modifier"""
        try:
            query = "SELECT nom, prix_unitaire, unite FROM carburants WHERE id = ?"
            result = self.db_manager.execute_query(query, (self.fuel_id,))
            
            if result:
                nom, prix_unitaire, unite = result[0]
                self.nom_var.set(nom)
                self.prix_var.set(str(prix_unitaire))
                self.unite_var.set(unite)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def save_fuel(self):
        """Sauvegarder le carburant"""
        try:
            nom = self.nom_var.get().strip()
            prix_str = self.prix_var.get().strip()
            unite = self.unite_var.get()
            
            if not nom:
                messagebox.showerror("Erreur", "Le nom du carburant est obligatoire")
                return
            
            if not prix_str:
                messagebox.showerror("Erreur", "Le prix est obligatoire")
                return
            
            try:
                prix = float(prix_str)
                if prix <= 0:
                    messagebox.showerror("Erreur", "Le prix doit être supérieur à 0")
                    return
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez saisir un prix valide")
                return
            
            if not unite:
                messagebox.showerror("Erreur", "Veuillez sélectionner une unité")
                return
            
            if self.fuel_id:
                # Modification
                query = "UPDATE carburants SET nom = ?, prix_unitaire = ?, unite = ? WHERE id = ?"
                params = (nom, prix, unite, self.fuel_id)
                self.db_manager.execute_update(query, params)
                messagebox.showinfo("Succès", "Carburant modifié avec succès")
            else:
                # Création
                query = "INSERT INTO carburants (nom, prix_unitaire, unite) VALUES (?, ?, ?)"
                params = (nom, prix, unite)
                self.db_manager.execute_insert(query, params)
                messagebox.showinfo("Succès", "Carburant créé avec succès")
            
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")

class PriceEditDialog:
    def __init__(self, parent, db_manager, fuel_id, nom, prix_actuel, callback):
        self.db_manager = db_manager
        self.fuel_id = fuel_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Modifier Prix - {nom}")
        self.dialog.geometry("350x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog(nom, prix_actuel)
    
    def setup_dialog(self, nom, prix_actuel):
        """Configuration de la fenêtre de modification de prix"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text=f"Carburant: {nom}", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text=f"Prix actuel: {prix_actuel} DH/L", 
                 font=('Arial', 10)).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text="Nouveau prix (DH/L):", 
                 font=('Arial', 11, 'bold')).pack(anchor='w')
        
        self.price_var = tk.StringVar(value=str(prix_actuel))
        price_entry = ttk.Entry(main_frame, textvariable=self.price_var, 
                               font=('Arial', 14), width=15)
        price_entry.pack(pady=(5, 20))
        price_entry.select_range(0, tk.END)
        price_entry.focus_set()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Enregistrer", 
                  command=self.save_price).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Annuler", 
                  command=self.dialog.destroy).pack(side='left')
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.save_price())
    
    def save_price(self):
        """Sauvegarder le nouveau prix"""
        try:
            nouveau_prix = float(self.price_var.get())
            if nouveau_prix <= 0:
                messagebox.showerror("Erreur", "Le prix doit être supérieur à 0")
                return
            
            query = "UPDATE carburants SET prix_unitaire = ? WHERE id = ?"
            self.db_manager.execute_update(query, (nouveau_prix, self.fuel_id))
            
            messagebox.showinfo("Succès", f"Prix mis à jour: {nouveau_prix} DH/L")
            self.callback()
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir un prix valide")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour: {str(e)}")

class StationEditDialog:
    def __init__(self, parent, db_manager, station_id, nom, adresse, telephone, responsable, callback):
        self.db_manager = db_manager
        self.station_id = station_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouvelle Station" if not station_id else "Modifier Station")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog(nom, adresse, telephone, responsable)
    
    def setup_dialog(self, nom, adresse, telephone, responsable):
        """Configuration de la fenêtre de modification de station"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Nom
        ttk.Label(main_frame, text="Nom de la station:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.nom_var = tk.StringVar(value=nom)
        ttk.Entry(main_frame, textvariable=self.nom_var, 
                 font=('Arial', 12), width=35).pack(fill='x', pady=(0, 10))
        
        # Adresse
        ttk.Label(main_frame, text="Adresse:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.adresse_var = tk.StringVar(value=adresse)
        ttk.Entry(main_frame, textvariable=self.adresse_var, 
                 font=('Arial', 12), width=35).pack(fill='x', pady=(0, 10))
        
        # Téléphone
        ttk.Label(main_frame, text="Téléphone:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.telephone_var = tk.StringVar(value=telephone)
        ttk.Entry(main_frame, textvariable=self.telephone_var, 
                 font=('Arial', 12), width=35).pack(fill='x', pady=(0, 10))
        
        # Responsable
        ttk.Label(main_frame, text="Responsable:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        
        self.responsable_var = tk.StringVar(value=responsable)
        ttk.Entry(main_frame, textvariable=self.responsable_var, 
                 font=('Arial', 12), width=35).pack(fill='x', pady=(0, 20))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Enregistrer", 
                  command=self.save_station).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Annuler", 
                  command=self.dialog.destroy).pack(side='left')
    
    def save_station(self):
        """Sauvegarder les modifications de la station"""
        try:
            nom = self.nom_var.get().strip()
            if not nom:
                messagebox.showerror("Erreur", "Le nom de la station est obligatoire")
                return
            
            adresse = self.adresse_var.get().strip()
            responsable = self.responsable_var.get().strip()
            
            if self.station_id:
                # Modification
                query = """
                    UPDATE stations SET nom = ?, adresse = ?, responsable = ?
                    WHERE id = ?
                """
                params = (nom, adresse, responsable, self.station_id)
                self.db_manager.execute_update(query, params)
                messagebox.showinfo("Succès", "Station mise à jour avec succès")
            else:
                # Création
                query = """
                    INSERT INTO stations (nom, adresse, responsable)
                    VALUES (?, ?, ?)
                """
                params = (nom, adresse, responsable)
                self.db_manager.execute_insert(query, params)
                messagebox.showinfo("Succès", "Station créée avec succès")
            
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")

class UserEditDialog:
    def __init__(self, parent, db_manager, user_id, callback):
        self.db_manager = db_manager
        self.user_id = user_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouvel Utilisateur" if not user_id else "Modifier Utilisateur")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        
        if user_id:
            self.load_user_data()
    
    def setup_dialog(self):
        """Configuration de la fenêtre utilisateur"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.role_var = tk.StringVar()
        self.nom_complet_var = tk.StringVar()
        self.actif_var = tk.BooleanVar(value=True)
        
        # Nom d'utilisateur
        ttk.Label(main_frame, text="Nom d'utilisateur:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.username_var, 
                 font=('Arial', 12), width=30).pack(fill='x', pady=(0, 10))
        
        # Mot de passe
        ttk.Label(main_frame, text="Mot de passe:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.password_var, show='*',
                 font=('Arial', 12), width=30).pack(fill='x', pady=(0, 10))
        
        # Rôle
        ttk.Label(main_frame, text="Rôle:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        role_combo = ttk.Combobox(main_frame, textvariable=self.role_var,
                                 values=['administrateur', 'employe'], 
                                 state='readonly', width=28)
        role_combo.pack(fill='x', pady=(0, 10))
        
        # Nom complet
        ttk.Label(main_frame, text="Nom complet:", 
                 font=('Arial', 11, 'bold')).pack(anchor='w', pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.nom_complet_var, 
                 font=('Arial', 12), width=30).pack(fill='x', pady=(0, 10))
        
        # Actif
        ttk.Checkbutton(main_frame, text="Compte actif", 
                       variable=self.actif_var).pack(anchor='w', pady=(0, 20))
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Enregistrer", 
                  command=self.save_user).pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Annuler", 
                  command=self.dialog.destroy).pack(side='left')
    
    def load_user_data(self):
        """Charger les données de l'utilisateur à modifier"""
        try:
            query = "SELECT nom_utilisateur, role, nom_complet, actif FROM utilisateurs WHERE id = ?"
            result = self.db_manager.execute_query(query, (self.user_id,))
            
            if result:
                username, role, nom_complet, actif = result[0]
                self.username_var.set(username)
                self.role_var.set(role)
                self.nom_complet_var.set(nom_complet or '')
                self.actif_var.set(bool(actif))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def save_user(self):
        """Sauvegarder l'utilisateur"""
        try:
            username = self.username_var.get().strip()
            password = self.password_var.get().strip()
            role = self.role_var.get()
            nom_complet = self.nom_complet_var.get().strip()
            actif = self.actif_var.get()
            
            if not username:
                messagebox.showerror("Erreur", "Le nom d'utilisateur est obligatoire")
                return
            
            if not role:
                messagebox.showerror("Erreur", "Veuillez sélectionner un rôle")
                return
            
            if self.user_id:
                # Modification
                if password:
                    # Nouveau mot de passe fourni
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    query = """
                        UPDATE utilisateurs SET nom_utilisateur = ?, mot_de_passe = ?, 
                               role = ?, nom_complet = ?, actif = ?
                        WHERE id = ?
                    """
                    params = (username, password_hash, role, nom_complet, actif, self.user_id)
                else:
                    # Pas de changement de mot de passe
                    query = """
                        UPDATE utilisateurs SET nom_utilisateur = ?, 
                               role = ?, nom_complet = ?, actif = ?
                        WHERE id = ?
                    """
                    params = (username, role, nom_complet, actif, self.user_id)
                
                self.db_manager.execute_update(query, params)
                messagebox.showinfo("Succès", "Utilisateur modifié avec succès")
                
            else:
                # Création
                if not password:
                    messagebox.showerror("Erreur", "Le mot de passe est obligatoire pour un nouvel utilisateur")
                    return
                
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                query = """
                    INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, role, nom_complet, actif)
                    VALUES (?, ?, ?, ?, ?)
                """
                params = (username, password_hash, role, nom_complet, actif)
                
                self.db_manager.execute_insert(query, params)
                messagebox.showinfo("Succès", "Utilisateur créé avec succès")
            
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
