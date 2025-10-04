# -*- coding: utf-8 -*-
"""
Module de Gestion des Clients (Simplifié)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import re

class ClientManagement:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.current_client = None
        
        self.setup_interface()
        self.load_clients()
    
    def setup_interface(self):
        """Configuration de l'interface de gestion des clients"""
        # Frame principal avec deux panels
        main_paned = ttk.PanedWindow(self.parent, orient='horizontal')
        main_paned.pack(fill='both', expand=True)
        
        # Panel gauche - Liste des clients
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Panel droit - Détails du client
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=2)
        
        self.setup_client_list(left_frame)
        self.setup_client_details(right_frame)
    
    def setup_client_list(self, parent):
        """Configuration de la liste des clients"""
        # En-tête avec boutons
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text="Liste des Clients", 
                 font=('Arial', 14, 'bold')).pack(side='left')
        
        # Boutons d'action
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Nouveau Client",
                  command=self.nouveau_client,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Supprimer",
                  command=self.supprimer_client,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        # Recherche
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Label(search_frame, text="Rechercher:").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Liste des clients
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10)
        
        columns = ('ID', 'Nom', 'Type', 'Solde')
        self.clients_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                        style='Touch.Treeview')
        
        # Configuration des colonnes
        self.clients_tree.heading('ID', text='ID')
        self.clients_tree.heading('Nom', text='Nom Complet')
        self.clients_tree.heading('Type', text='Type')
        self.clients_tree.heading('Solde', text='Solde (DH)')
        
        self.clients_tree.column('ID', width=50)
        self.clients_tree.column('Nom', width=200)
        self.clients_tree.column('Type', width=100)
        self.clients_tree.column('Solde', width=100)
        
        # Scrollbar
        scrollbar_clients = ttk.Scrollbar(list_frame, orient='vertical', 
                                         command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar_clients.set)
        
        self.clients_tree.pack(side='left', fill='both', expand=True)
        scrollbar_clients.pack(side='right', fill='y')
        
        # Bind selection
        self.clients_tree.bind('<<TreeviewSelect>>', self.on_client_select)
    
    def setup_client_details(self, parent):
        """Configuration du panel de détails client"""
        # En-tête
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        self.client_title = ttk.Label(header_frame, text="Détails du Client", 
                                     font=('Arial', 14, 'bold'))
        self.client_title.pack(side='left')
        
        # Boutons d'action
        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Modifier",
                  command=self.modifier_client,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Enregistrer",
                  command=self.enregistrer_client,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        # Notebook pour les sections
        self.details_notebook = ttk.Notebook(parent)
        self.details_notebook.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Onglet Informations Générales
        info_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(info_frame, text="Informations Générales")
        self.setup_general_info(info_frame)
        
        # Onglet Véhicules
        vehicles_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(vehicles_frame, text="Véhicules")
        self.setup_vehicles_info(vehicles_frame)
        
        # Onglet Historique
        history_frame = ttk.Frame(self.details_notebook)
        self.details_notebook.add(history_frame, text="Historique")
        self.setup_history_info(history_frame)
    
    def setup_general_info(self, parent):
        """Configuration des informations générales"""
        # Frame avec scroll
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Formulaire
        form_frame = ttk.LabelFrame(scrollable_frame, text="Informations Client", padding=15)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Variables pour les champs
        self.client_vars = {}
        fields = [
            ('nom', 'Nom *', 'text'),
            ('prenom', 'Prénom', 'text'),
            ('entreprise', 'Entreprise', 'text'),
            ('telephone', 'Téléphone', 'text'),
            ('email', 'Email', 'text'),
            ('adresse', 'Adresse', 'text'),
            ('ice', 'ICE', 'text'),
            ('type_client', 'Type Client', 'combo'),
            ('credit_limite', 'Limite de Crédit (DH)', 'float'),
            ('statut', 'Statut', 'combo')
        ]
        
        row = 0
        for field_id, label, field_type in fields:
            ttk.Label(form_frame, text=label).grid(row=row, column=0, sticky='w', padx=(0, 10), pady=5)
            
            self.client_vars[field_id] = tk.StringVar()
            
            if field_type == 'combo':
                if field_id == 'type_client':
                    values = ['particulier', 'entreprise']
                elif field_id == 'statut':
                    values = ['actif', 'inactif', 'suspendu']
                
                widget = ttk.Combobox(form_frame, textvariable=self.client_vars[field_id],
                                     values=values, state='readonly', width=30)
            else:
                widget = ttk.Entry(form_frame, textvariable=self.client_vars[field_id], width=30)
            
            widget.grid(row=row, column=1, sticky='ew', pady=5)
            form_frame.columnconfigure(1, weight=1)
            row += 1
        
        # Informations calculées
        calc_frame = ttk.LabelFrame(scrollable_frame, text="Informations Calculées", padding=15)
        calc_frame.pack(fill='x', padx=10, pady=10)
        
        self.solde_label = ttk.Label(calc_frame, text="Solde Actuel: 0.00 DH", 
                                    font=('Arial', 12, 'bold'))
        self.solde_label.pack(anchor='w', pady=5)
        
        self.date_creation_label = ttk.Label(calc_frame, text="Date de Création: -")
        self.date_creation_label.pack(anchor='w', pady=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_vehicles_info(self, parent):
        """Configuration des informations véhicules"""
        # Boutons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Nouveau Véhicule",
                  command=self.nouveau_vehicule,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Modifier Véhicule",
                  command=self.modifier_vehicule,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Supprimer Véhicule",
                  command=self.supprimer_vehicule,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        # Liste des véhicules
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        columns = ('ID', 'Immatriculation', 'Marque', 'Modèle', 'Carburant')
        self.vehicles_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                         style='Touch.Treeview')
        
        for col in columns:
            self.vehicles_tree.heading(col, text=col)
            self.vehicles_tree.column(col, width=120)
        
        scrollbar_vehicles = ttk.Scrollbar(list_frame, orient='vertical', 
                                          command=self.vehicles_tree.yview)
        self.vehicles_tree.configure(yscrollcommand=scrollbar_vehicles.set)
        
        self.vehicles_tree.pack(side='left', fill='both', expand=True)
        scrollbar_vehicles.pack(side='right', fill='y')
    
    def setup_history_info(self, parent):
        """Configuration de l'historique client"""
        # Filtres
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Période:").pack(side='left')
        
        self.period_var = tk.StringVar(value="30_jours")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var,
                                   values=["7_jours", "30_jours", "3_mois", "6_mois", "1_an"],
                                   state='readonly', width=15)
        period_combo.pack(side='left', padx=(5, 20))
        
        ttk.Button(filter_frame, text="Actualiser",
                  command=self.load_client_history,
                  style='Touch.TButton').pack(side='left')
        
        # Historique des transactions
        history_frame = ttk.Frame(parent)
        history_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        columns = ('Date', 'Type', 'Description', 'Montant', 'Station')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings',
                                        style='Touch.Treeview')
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        scrollbar_history = ttk.Scrollbar(history_frame, orient='vertical', 
                                         command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar_history.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar_history.pack(side='right', fill='y')
    
    def load_clients(self):
        """Charger la liste des clients"""
        try:
            # Vider la liste actuelle
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            # Requête pour obtenir les clients avec leur solde
            query = """
                SELECT c.id, c.nom, c.prenom, c.type_client, c.solde_actuel,
                       c.entreprise
                FROM clients c
                WHERE c.statut = 'actif'
                ORDER BY c.nom, c.prenom
            """
            
            # Utiliser le cache pour la liste des clients
            clients = self.db_manager.execute_query(query, use_cache=True, cache_timeout=60)
            
            for client in clients:
                client_id, nom, prenom, type_client, solde, entreprise = client
                
                # Nom complet
                if entreprise and type_client == 'entreprise':
                    nom_complet = f"{entreprise} ({nom} {prenom or ''})"
                else:
                    nom_complet = f"{nom} {prenom or ''}"
                
                # Formatage du solde
                solde_str = f"{solde:.2f}" if solde else "0.00"
                
                self.clients_tree.insert('', 'end', values=(
                    client_id, nom_complet.strip(), type_client, solde_str
                ))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des clients: {str(e)}")
    
    def on_search_change(self, *args):
        """Filtrer les clients selon la recherche"""
        search_term = self.search_var.get().lower()
        
        # Cacher tous les éléments
        for item in self.clients_tree.get_children():
            self.clients_tree.detach(item)
        
        # Réafficher les éléments correspondants - sans utiliser le cache pour les recherches
        for item in self.clients_tree.get_children(''):
            values = self.clients_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.clients_tree.reattach(item, '', 'end')
    
    def on_client_select(self, event):
        """Gérer la sélection d'un client"""
        selection = self.clients_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        client_id = self.clients_tree.item(item)['values'][0]
        self.load_client_details(client_id)
    
    def load_client_details(self, client_id):
        """Charger les détails d'un client"""
        try:
            # Charger les informations du client
            query = """
                SELECT * FROM clients WHERE id = ?
            """
            # Utiliser le cache pour les détails du client
            result = self.db_manager.execute_query(query, (client_id,), use_cache=True, cache_timeout=30)
            
            if result:
                client_data = result[0]
                self.current_client = client_id
                
                # Remplir les champs
                fields = ['id', 'nom', 'prenom', 'entreprise', 'telephone', 'email', 
                         'adresse', 'ice', 'type_client', 'credit_limite', 'solde_actuel', 
                         'date_creation', 'statut']
                
                for i, field in enumerate(fields):
                    if field in self.client_vars:
                        self.client_vars[field].set(client_data[i] or '')
                
                # Mettre à jour les labels calculés
                self.solde_label.config(text=f"Solde Actuel: {client_data[10]:.2f} DH")
                self.date_creation_label.config(text=f"Date de Création: {client_data[11]}")
                
                # Charger les véhicules
                self.load_client_vehicles(client_id)
                
                # Charger l'historique
                self.load_client_history()
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du client: {str(e)}")
    
    def load_client_vehicles(self, client_id):
        """Charger les véhicules d'un client"""
        try:
            # Vider la liste
            for item in self.vehicles_tree.get_children():
                self.vehicles_tree.delete(item)
            
            query = """
                SELECT id, immatriculation, marque, modele, type_carburant
                FROM vehicules
                WHERE client_id = ?
                ORDER BY immatriculation
            """
            
            # Utiliser le cache pour les véhicules du client
            vehicles = self.db_manager.execute_query(query, (client_id,), use_cache=True, cache_timeout=30)
            
            for vehicle in vehicles:
                self.vehicles_tree.insert('', 'end', values=vehicle)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des véhicules: {str(e)}")
    
    def load_client_history(self):
        """Charger l'historique d'un client"""
        if not self.current_client:
            return
        
        try:
            # Vider la liste
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Calculer la période
            period_map = {
                "7_jours": 7,
                "30_jours": 30,
                "3_mois": 90,
                "6_mois": 180,
                "1_an": 365
            }
            
            days = period_map.get(self.period_var.get(), 30)
            
            # Transactions
            query = """
                SELECT t.date_transaction, 'Transaction' as type,
                       CONCAT(c.nom, ' - ', t.quantite, 'L') as description,
                       t.montant_total, s.nom
                FROM transactions t
                JOIN carburants c ON t.carburant_id = c.id
                JOIN stations s ON t.station_id = s.id
                WHERE t.client_id = ? AND DATE(t.date_transaction) >= DATE('now', '-{} days')
                
                UNION ALL
                
                SELECT p.date_paiement, 'Paiement' as type,
                       CONCAT('Paiement ', p.mode_paiement) as description,
                       p.montant, '' as station
                FROM paiements_avance p
                WHERE p.client_id = ? AND DATE(p.date_paiement) >= DATE('now', '-{} days')
                
                ORDER BY date_transaction DESC
            "".format(days, days)
            
            # Utiliser le cache avec un timeout court pour l'historique qui peut changer
            history = self.db_manager.execute_query(query, (self.current_client, self.current_client), 
                                                  use_cache=True, cache_timeout=60, 
                                                  table=["transactions", "paiements_avance", "clients"])
            
            for record in history:
                date_str = record[0][:16] if record[0] else ''  # Format datetime
                self.history_tree.insert('', 'end', values=(
                    date_str, record[1], record[2], f"{record[3]:.2f} DH", record[4]
                ))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'historique: {str(e)}")
    
    def nouveau_client(self):
        """Créer un nouveau client"""
        # Vider les champs
        for var in self.client_vars.values():
            var.set('')
        
        # Valeurs par défaut
        self.client_vars['type_client'].set('particulier')
        self.client_vars['statut'].set('actif')
        self.client_vars['credit_limite'].set('0')
        
        self.current_client = None
        self.client_title.config(text="Nouveau Client")
        
        # Vider les listes
        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
    
    def enregistrer_client(self):
        """Enregistrer les modifications du client"""
        try:
            # Validation
            if not self.client_vars['nom'].get().strip():
                messagebox.showerror("Erreur", "Le nom est obligatoire")
                return
            
            # Validation email
            email = self.client_vars['email'].get().strip()
            if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                messagebox.showerror("Erreur", "Format d'email invalide")
                return
            
            # Validation limite de crédit
            try:
                credit_limite = float(self.client_vars['credit_limite'].get() or 0)
            except ValueError:
                messagebox.showerror("Erreur", "Limite de crédit invalide")
                return
            
            if self.current_client:
                # Mise à jour
                query = """
                    UPDATE clients SET
                        nom = ?, prenom = ?, entreprise = ?, telephone = ?,
                        email = ?, adresse = ?, ice = ?, type_client = ?,
                        credit_limite = ?, statut = ?
                    WHERE id = ?
                """
                params = (
                    self.client_vars['nom'].get().strip(),
                    self.client_vars['prenom'].get().strip(),
                    self.client_vars['entreprise'].get().strip(),
                    self.client_vars['telephone'].get().strip(),
                    self.client_vars['email'].get().strip(),
                    self.client_vars['adresse'].get().strip(),
                    self.client_vars['ice'].get().strip(),
                    self.client_vars['type_client'].get(),
                    credit_limite,
                    self.client_vars['statut'].get(),
                    self.current_client
                )
                
                # Utiliser le paramètre table pour invalider automatiquement le cache
                self.db_manager.execute_update(query, params, table='clients')
                messagebox.showinfo("Succès", "Client mis à jour avec succès")
            else:
                # Nouveau client
                query = """
                    INSERT INTO clients (
                        nom, prenom, entreprise, telephone, email, adresse,
                        ice, type_client, credit_limite, statut, solde_actuel
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                """
                params = (
                    self.client_vars['nom'].get().strip(),
                    self.client_vars['prenom'].get().strip(),
                    self.client_vars['entreprise'].get().strip(),
                    self.client_vars['telephone'].get().strip(),
                    self.client_vars['email'].get().strip(),
                    self.client_vars['adresse'].get().strip(),
                    self.client_vars['ice'].get().strip(),
                    self.client_vars['type_client'].get(),
                    credit_limite,
                    self.client_vars['statut'].get()
                )
                
                # Utiliser le paramètre table pour invalider automatiquement le cache
                client_id = self.db_manager.execute_insert(query, params, table='clients')
                self.current_client = client_id
                messagebox.showinfo("Succès", "Nouveau client créé avec succès")
            
            # Recharger la liste
            self.load_clients()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
    
    def modifier_client(self):
        """Activer le mode modification"""
        if not self.current_client:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        self.client_title.config(text="Modification Client")
    
    def supprimer_client(self):
        """Supprimer un client"""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        if messagebox.askyesno("Confirmation", 
                              "Êtes-vous sûr de vouloir supprimer ce client ?\n" +
                              "Cette action changera son statut à 'inactif'."):
            try:
                item = selection[0]
                client_id = self.clients_tree.item(item)['values'][0]
                
                # Mettre le statut à inactif au lieu de supprimer
                query = "UPDATE clients SET statut = 'inactif' WHERE id = ?"
                # Utiliser le paramètre table pour invalider automatiquement le cache
                self.db_manager.execute_update(query, (client_id,), table='clients')
                
                self.load_clients()
                messagebox.showinfo("Succès", "Client désactivé avec succès")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def nouveau_vehicule(self):
        """Ajouter un nouveau véhicule"""
        if not self.current_client:
            messagebox.showwarning("Attention", "Aucun client sélectionné")
            return
        
        VehicleDialog(self.parent, self.db_manager, self.current_client, None, self.load_client_vehicles)
    
    def modifier_vehicule(self):
        """Modifier un véhicule"""
        selection = self.vehicles_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Aucun véhicule sélectionné")
            return
        
        item = selection[0]
        vehicle_id = self.vehicles_tree.item(item)['values'][0]
        
        VehicleDialog(self.parent, self.db_manager, self.current_client, vehicle_id, self.load_client_vehicles)
    
    def supprimer_vehicule(self):
        """Supprimer un véhicule"""
        selection = self.vehicles_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Aucun véhicule sélectionné")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce véhicule ?"):
            try:
                item = selection[0]
                vehicle_id = self.vehicles_tree.item(item)['values'][0]
                
                # Vérifier s'il y a des transactions liées
                check_query = "SELECT COUNT(*) FROM transactions WHERE vehicule_id = ?"
                # Ne pas utiliser le cache pour cette vérification critique
                result = self.db_manager.execute_query(check_query, (vehicle_id,), use_cache=False)
                
                if result and result[0][0] > 0:
                    messagebox.showerror("Erreur", "Ce véhicule a des transactions enregistrées.\nIl ne peut pas être supprimé.")
                    return
                
                query = "DELETE FROM vehicules WHERE id = ?"
                # Utiliser le paramètre table pour invalider automatiquement le cache
                self.db_manager.execute_update(query, (vehicle_id,), table='vehicules')
                
                self.load_client_vehicles(self.current_client)
                messagebox.showinfo("Succès", "Véhicule supprimé avec succès")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

class VehicleDialog:
    def __init__(self, parent, db_manager, client_id, vehicle_id, callback):
        self.db_manager = db_manager
        self.client_id = client_id
        self.vehicle_id = vehicle_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Véhicule" if vehicle_id else "Nouveau Véhicule")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        
        if vehicle_id:
            self.load_vehicle_data()
        
        self.dialog.focus()
    
    def setup_dialog(self):
        """Configuration de la fenêtre de dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Variables
        self.vehicle_vars = {}
        
        fields = [
            ('immatriculation', 'Immatriculation *'),
            ('marque', 'Marque'),
            ('modele', 'Modèle'),
            ('type_carburant', 'Type de Carburant'),
            ('capacite_reservoir', 'Capacité Réservoir (L)')
        ]
        
        row = 0
        for field_id, label in fields:
            ttk.Label(main_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)
            
            self.vehicle_vars[field_id] = tk.StringVar()
            
            if field_id == 'type_carburant':
                # Charger les types de carburant depuis la DB
                carburants = self.db_manager.execute_query("SELECT nom FROM carburants ORDER BY nom")
                values = [c[0] for c in carburants]
                widget = ttk.Combobox(main_frame, textvariable=self.vehicle_vars[field_id],
                                     values=values, width=25)
            else:
                widget = ttk.Entry(main_frame, textvariable=self.vehicle_vars[field_id], width=25)
            
            widget.grid(row=row, column=1, sticky='ew', pady=5)
            row += 1
        
        main_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Enregistrer", command=self.save_vehicle).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def load_vehicle_data(self):
        """Charger les données du véhicule"""
        try:
            query = "SELECT * FROM vehicules WHERE id = ?"
            result = self.db_manager.execute_query(query, (self.vehicle_id,))
            
            if result:
                vehicle_data = result[0]
                fields = ['id', 'client_id', 'immatriculation', 'marque', 'modele', 
                         'type_carburant', 'capacite_reservoir']
                
                for i, field in enumerate(fields):
                    if field in self.vehicle_vars:
                        self.vehicle_vars[field].set(vehicle_data[i] or '')
                        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement du véhicule: {str(e)}")
    
    def save_vehicle(self):
        """Enregistrer le véhicule"""
        try:
            # Validation
            if not self.vehicle_vars['immatriculation'].get().strip():
                messagebox.showerror("Erreur", "L'immatriculation est obligatoire")
                return
            
            if self.vehicle_id:
                # Mise à jour
                query = """
                    UPDATE vehicules SET
                        immatriculation = ?, marque = ?, modele = ?,
                        type_carburant = ?, capacite_reservoir = ?
                    WHERE id = ?
                """
                params = (
                    self.vehicle_vars['immatriculation'].get().strip(),
                    self.vehicle_vars['marque'].get().strip(),
                    self.vehicle_vars['modele'].get().strip(),
                    self.vehicle_vars['type_carburant'].get().strip(),
                    self.vehicle_vars['capacite_reservoir'].get().strip(),
                    self.vehicle_id
                )
            else:
                # Nouveau véhicule
                query = """
                    INSERT INTO vehicules (
                        client_id, immatriculation, marque, modele,
                        type_carburant, capacite_reservoir
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """
                params = (
                    self.client_id,
                    self.vehicle_vars['immatriculation'].get().strip(),
                    self.vehicle_vars['marque'].get().strip(),
                    self.vehicle_vars['modele'].get().strip(),
                    self.vehicle_vars['type_carburant'].get().strip(),
                    self.vehicle_vars['capacite_reservoir'].get().strip()
                )
            
            if self.vehicle_id:
                # Utiliser le paramètre table pour invalider automatiquement le cache
                self.db_manager.execute_update(query, params, table='vehicules')
            else:
                # Utiliser le paramètre table pour invalider automatiquement le cache
                self.db_manager.execute_insert(query, params, table='vehicules')
            
            # Callback pour recharger la liste
            self.callback(self.client_id)
            
            self.dialog.destroy()
            messagebox.showinfo("Succès", "Véhicule enregistré avec succès")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
