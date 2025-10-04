# -*- coding: utf-8 -*-
"""
Module de Gestion des Clients Simplifié
Contient uniquement: nom, prénom, téléphone
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

class ClientManagement:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.current_client = None
        
        self.setup_interface()
        self.load_clients()
        self.load_clients()
    
    def setup_interface(self):
        """Configuration de l'interface simplifiée"""
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Section Nouveau Client (toujours visible en haut)
        self.setup_client_form(main_frame)
        
        # Section Liste des Clients
        self.setup_client_list(main_frame)
        
        # Section Véhicules du client sélectionné
        self.setup_vehicles_section(main_frame)
    
    def setup_client_form(self, parent):
        """Formulaire simplifié pour nouveau client"""
        form_frame = ttk.LabelFrame(parent, text="Nouveau Client", padding=20)
        form_frame.pack(fill='x', pady=(0, 10))
        
        # Variables du formulaire
        self.client_vars = {
            'nom': tk.StringVar(),
            'prenom': tk.StringVar(),
            'telephone': tk.StringVar()
        }
        
        # Disposition horizontale pour simplicité
        fields_frame = ttk.Frame(form_frame)
        fields_frame.pack(fill='x')
        
        # Nom
        ttk.Label(fields_frame, text="Nom *:", style='Touch.TLabel', font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        nom_entry = ttk.Entry(fields_frame, textvariable=self.client_vars['nom'], 
                             width=20, font=('Arial', 12))
        nom_entry.grid(row=0, column=1, padx=(0, 20), pady=5)
        
        # Prénom
        ttk.Label(fields_frame, text="Prénom:", style='Touch.TLabel', font=('Arial', 12, 'bold')).grid(row=0, column=2, sticky='w', padx=(0, 10))
        prenom_entry = ttk.Entry(fields_frame, textvariable=self.client_vars['prenom'], 
                                width=20, font=('Arial', 12))
        prenom_entry.grid(row=0, column=3, padx=(0, 20), pady=5)
        
        # Téléphone
        ttk.Label(fields_frame, text="Téléphone:", style='Touch.TLabel', font=('Arial', 12, 'bold')).grid(row=0, column=4, sticky='w', padx=(0, 10))
        tel_entry = ttk.Entry(fields_frame, textvariable=self.client_vars['telephone'], 
                             width=15, font=('Arial', 12))
        tel_entry.grid(row=0, column=5, padx=(0, 20), pady=5)
        
        # Bouton Ajouter
        ttk.Button(fields_frame, text="Ajouter Client",
                  command=self.ajouter_client_rapide,
                  style='Touch.TButton').grid(row=0, column=6, padx=10)
        
        # Configurer la grille
        for i in range(7):
            fields_frame.columnconfigure(i, weight=1 if i in [1, 3, 5] else 0)
    
    def setup_client_list(self, parent):
        """Liste des clients simplifiée"""
        list_frame = ttk.LabelFrame(parent, text="Clients Enregistrés", padding=10)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Barre de recherche
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Rechercher:", style='Touch.TLabel').pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                                width=30, font=('Arial', 11))
        search_entry.pack(side='left', padx=(10, 20), fill='x', expand=True)
        
        ttk.Button(search_frame, text="Supprimer Client",
                  command=self.supprimer_client,
                  style='Touch.TButton').pack(side='right')
        
        # Liste des clients
        columns = ('ID', 'Nom Complet', 'Téléphone', 'Solde (DH)')
        self.clients_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                        style='Touch.Treeview', height=8)
        
        # Configuration des colonnes
        self.clients_tree.heading('ID', text='ID')
        self.clients_tree.heading('Nom Complet', text='Nom Complet')
        self.clients_tree.heading('Téléphone', text='Téléphone')
        self.clients_tree.heading('Solde (DH)', text='Solde (DH)')
        
        self.clients_tree.column('ID', width=50)
        self.clients_tree.column('Nom Complet', width=250)
        self.clients_tree.column('Téléphone', width=120)
        self.clients_tree.column('Solde (DH)', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        
        self.clients_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind selection
        self.clients_tree.bind('<<TreeviewSelect>>', self.on_client_select)
    
    def setup_vehicles_section(self, parent):
        """Section des véhicules du client sélectionné"""
        vehicles_frame = ttk.LabelFrame(parent, text="Véhicules du Client Sélectionné", padding=10)
        vehicles_frame.pack(fill='x')
        
        # Info client sélectionné
        self.selected_client_label = ttk.Label(vehicles_frame, 
                                              text="Aucun client sélectionné",
                                              font=('Arial', 12, 'bold'),
                                              foreground='blue')
        self.selected_client_label.pack(anchor='w', pady=(0, 10))
        
        # Boutons véhicules
        btn_frame = ttk.Frame(vehicles_frame)
        btn_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(btn_frame, text="Nouveau Véhicule",
                  command=self.nouveau_vehicule,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Supprimer Véhicule",
                  command=self.supprimer_vehicule,
                  style='Touch.TButton').pack(side='left')
        
        # Liste des véhicules
        columns = ('ID', 'Matricule', 'Marque', 'Modèle')
        self.vehicles_tree = ttk.Treeview(vehicles_frame, columns=columns, show='headings',
                                         style='Touch.Treeview', height=4)
        
        for col in columns:
            self.vehicles_tree.heading(col, text=col)
            self.vehicles_tree.column(col, width=120)
        
        v_scrollbar = ttk.Scrollbar(vehicles_frame, orient='vertical', command=self.vehicles_tree.yview)
        self.vehicles_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.vehicles_tree.pack(side='left', fill='x', expand=True)
        v_scrollbar.pack(side='right', fill='y')
    
    def ajouter_client_rapide(self):
        """Ajouter un client rapidement avec validation minimale"""
        try:
            # Validation simple
            nom = self.client_vars['nom'].get().strip()
            prenom = self.client_vars['prenom'].get().strip()
            telephone = self.client_vars['telephone'].get().strip()
            
            if not nom:
                messagebox.showerror("Erreur", "Le nom est obligatoire")
                return
            
            # Validation téléphone marocain simple (optionnel)
            if telephone and not re.match(r'^(0[5-7]\d{8}|06\d{8}|08\d{8})$', telephone):
                if not messagebox.askyesno("Confirmation", 
                    f"Le numéro '{telephone}' ne semble pas être un numéro marocain valide.\n" +
                    "Voulez-vous continuer quand même?"):
                    return
            
            # Insertion automatique
            query = """
                INSERT INTO clients (nom, prenom, telephone, solde_actuel) 
                VALUES (?, ?, ?, 0)
            """
            params = (nom, prenom, telephone)
            
            client_id = self.db_manager.execute_insert(query, params, table='clients')
            
            # Message de succès
            messagebox.showinfo("Succès", f"Client '{nom} {prenom}' ajouté avec succès!")
            
            # Vider le formulaire
            for var in self.client_vars.values():
                var.set('')
            
            # Recharger la liste
            self.load_clients()
            
            # Sélectionner le nouveau client
            self.select_client_by_id(client_id)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'ajout: {str(e)}")
    
    def load_clients(self):
        """Charger la liste des clients"""
        try:
            # Vider la liste
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            
            # Requête simplifiée
            query = """
                SELECT id, nom, prenom, telephone, solde_actuel
                FROM clients
                ORDER BY nom, prenom
            """
            
            clients = self.db_manager.execute_query(query, use_cache=True, cache_timeout=60, table='clients')
            
            for client in clients:
                client_id, nom, prenom, telephone, solde = client
                
                # Nom complet
                nom_complet = f"{nom} {prenom or ''}".strip()
                
                # Formatage du solde
                solde_str = f"{solde:.2f}" if solde else "0.00"
                
                self.clients_tree.insert('', 'end', values=(
                    client_id, nom_complet, telephone or '', solde_str
                ))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def on_search_change(self, *args):
        """Filtrer les clients en temps réel"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            # Réafficher tous les éléments
            for item in self.clients_tree.get_children():
                self.clients_tree.reattach(item, '', 'end')
            return
        
        # Cacher tous les éléments puis réafficher ceux qui correspondent
        for item in self.clients_tree.get_children():
            values = self.clients_tree.item(item)['values']
            if any(search_term in str(value).lower() for value in values):
                self.clients_tree.reattach(item, '', 'end')
            else:
                self.clients_tree.detach(item)
    
    def on_client_select(self, event):
        """Gérer la sélection d'un client"""
        selection = self.clients_tree.selection()
        if not selection:
            self.current_client = None
            self.selected_client_label.config(text="Aucun client sélectionné")
            self.clear_vehicles()
            return
        
        item = selection[0]
        values = self.clients_tree.item(item)['values']
        self.current_client = values[0]  # ID
        
        # Mettre à jour l'affichage
        client_name = values[1]  # Nom complet
        solde = values[3]  # Solde
        self.selected_client_label.config(
            text=f"Client: {client_name} | Solde: {solde} DH"
        )
        
        # Charger les véhicules
        self.load_client_vehicles()
    
    def select_client_by_id(self, client_id):
        """Sélectionner un client par son ID"""
        for item in self.clients_tree.get_children():
            if self.clients_tree.item(item)['values'][0] == client_id:
                self.clients_tree.selection_set(item)
                self.clients_tree.focus(item)
                break
    
    def supprimer_client(self):
        """Supprimer un client sélectionné"""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un client à supprimer")
            return
        
        item = selection[0]
        values = self.clients_tree.item(item)['values']
        client_name = values[1]
        
        if messagebox.askyesno("Confirmation", 
                              f"Supprimer le client '{client_name}' ?\n" +
                              "Cette action est définitive."):
            try:
                client_id = values[0]
                
                # Supprimer les véhicules d'abord
                self.db_manager.execute_update("DELETE FROM vehicules WHERE client_id = ?", (client_id,))
                
                # Supprimer le client
                self.db_manager.execute_update("DELETE FROM clients WHERE id = ?", (client_id,))
                
                messagebox.showinfo("Succès", f"Client '{client_name}' supprimé")
                
                # Recharger et réinitialiser
                self.load_clients()
                self.current_client = None
                self.selected_client_label.config(text="Aucun client sélectionné")
                self.clear_vehicles()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def clear_vehicles(self):
        """Vider la liste des véhicules"""
        for item in self.vehicles_tree.get_children():
            self.vehicles_tree.delete(item)
    
    def load_client_vehicles(self):
        """Charger les véhicules du client sélectionné"""
        if not self.current_client:
            return
        
        try:
            self.clear_vehicles()
            
            query = """
                SELECT id, matricule, marque, modele
                FROM vehicules
                WHERE client_id = ?
                ORDER BY matricule
            """
            
            vehicles = self.db_manager.execute_query(query, (self.current_client,))
            
            for vehicle in vehicles:
                self.vehicles_tree.insert('', 'end', values=vehicle)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des véhicules: {str(e)}")
    
    def nouveau_vehicule(self):
        """Ajouter un véhicule au client sélectionné"""
        if not self.current_client:
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner un client")
            return
        
        VehicleDialog(self.parent, self.db_manager, self.current_client, None, self.load_client_vehicles)
    
    def supprimer_vehicule(self):
        """Supprimer le véhicule sélectionné"""
        selection = self.vehicles_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un véhicule à supprimer")
            return
        
        item = selection[0]
        values = self.vehicles_tree.item(item)['values']
        matricule = values[1]
        
        if messagebox.askyesno("Confirmation", f"Supprimer le véhicule '{matricule}' ?"):
            try:
                vehicle_id = values[0]
                self.db_manager.execute_update("DELETE FROM vehicules WHERE id = ?", (vehicle_id,))
                
                messagebox.showinfo("Succès", f"Véhicule '{matricule}' supprimé")
                self.load_client_vehicles()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

class VehicleDialog:
    def __init__(self, parent, db_manager, client_id, vehicle_id, callback):
        self.db_manager = db_manager
        self.client_id = client_id
        self.vehicle_id = vehicle_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau Véhicule" if not vehicle_id else "Modifier Véhicule")
        self.dialog.geometry("450x250")
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
        
        # Instructions pour plaque marocaine
        info_label = ttk.Label(main_frame, 
                              text="Format marocain: [Numéro]|[Lettre Arabe]|[Région 1-99]\nExemple: 123456|ب|12 ou 12345 ش 34",
                              font=('Arial', 10), foreground='blue', justify='center')
        info_label.pack(pady=(0, 15))
        
        fields = [
            ('matricule', 'Matricule *'),
            ('marque', 'Marque'),
            ('modele', 'Modèle'),
            ('type_carburant', 'Type de Carburant')
        ]
        
        row = 0
        for field_id, label in fields:
            ttk.Label(main_frame, text=label, font=('Arial', 11, 'bold')).grid(row=row, column=0, sticky='w', pady=10)
            
            self.vehicle_vars[field_id] = tk.StringVar()
            
            if field_id == 'type_carburant':
                # Charger les carburants
                carburants = self.db_manager.execute_query("SELECT nom FROM carburants ORDER BY nom")
                values = [c[0] for c in carburants]
                widget = ttk.Combobox(main_frame, textvariable=self.vehicle_vars[field_id],
                                     values=values, width=30, font=('Arial', 11))
            else:
                widget = ttk.Entry(main_frame, textvariable=self.vehicle_vars[field_id], 
                                  width=30, font=('Arial', 11))
            
            widget.grid(row=row, column=1, sticky='ew', pady=10, padx=(10, 0))
            row += 1
        
        main_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Enregistrer", 
                  command=self.save_vehicle,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Annuler", 
                  command=self.dialog.destroy,
                  style='Touch.TButton').pack(side='left')
    
    def validate_moroccan_plate(self, matricule):
        """Valider le format de matricule marocain avec lettres arabes"""
        # Format marocain: [Numéro séquentiel] | [Lettre arabe] | [Numéro de région 1-99]
        matricule = matricule.strip()
        
        # Lettres arabes autorisées
        lettres_normales = ['أ', 'ب', 'ج', 'د', 'ه', 'و', 'ز', 'ح', 'ط', 'ي', 'ك', 'ل', 'م', 'ن', 'س', 'ع', 'ف', 'ص', 'ق', 'ر', 'ش', 'ت', 'ث', 'خ', 'ذ', 'ض', 'ظ', 'غ']
        lettres_etat = ['ج']  # Voitures d'état
        lettres_police = ['ش']  # Police
        lettres_protection_civile = ['و', 'م']  # Protection Civile
        lettres_forces_auxiliaires = ['ق', 'س']  # Forces Auxiliaires
        
        toutes_lettres = lettres_normales + lettres_etat + lettres_police + lettres_protection_civile + lettres_forces_auxiliaires
        
        # Pattern pour le format marocain avec séparateurs | - ou espaces
        import re
        pattern = r'^(\d{1,6})[\\|\-\s]([' + ''.join(toutes_lettres) + '])[\\|\-\s](\d{1,2})$'
        
        match = re.match(pattern, matricule)
        if not match:
            return False, "Format invalide"
        
        numero_seq, lettre_arabe, numero_region = match.groups()
        
        # Valider le numéro de région (1-99)
        try:
            region = int(numero_region)
            if not (1 <= region <= 99):
                return False, "Le numéro de région doit être entre 1 et 99"
        except ValueError:
            return False, "Numéro de région invalide"
        
        # Déterminer le type de véhicule selon la lettre
        if lettre_arabe in lettres_etat:
            type_vehicule = "Véhicule d'État"
        elif lettre_arabe in lettres_police:
            type_vehicule = "Véhicule de Police"
        elif lettre_arabe in lettres_protection_civile:
            type_vehicule = "Protection Civile"
        elif lettre_arabe in lettres_forces_auxiliaires:
            type_vehicule = "Forces Auxiliaires"
        else:
            type_vehicule = "Véhicule Civil"
        
        return True, type_vehicule
    
    def load_vehicle_data(self):
        """Charger les données du véhicule à modifier"""
        try:
            query = "SELECT * FROM vehicules WHERE id = ?"
            result = self.db_manager.execute_query(query, (self.vehicle_id,))
            
            if result:
                vehicle_data = result[0]
                fields = ['id', 'client_id', 'matricule', 'marque', 'modele', 'type_carburant']
                
                for i, field in enumerate(fields):
                    if field in self.vehicle_vars:
                        self.vehicle_vars[field].set(vehicle_data[i] or '')
                        
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def save_vehicle(self):
        """Enregistrer le véhicule"""
        try:
            # Validation
            matricule = self.vehicle_vars['matricule'].get().strip()
            if not matricule:
                messagebox.showerror("Erreur", "Le matricule est obligatoire")
                return
            
            # Validation format marocain
            if not self.validate_moroccan_plate(matricule):
                if not messagebox.askyesno("Confirmation",
                    f"La plaque '{matricule}' ne respecte pas le format marocain standard.\n" +
                    "Exemples valides: 123456|A|12, 12345-B-34, 1234 C 56\n" +
                    "Voulez-vous continuer quand même?"):
                    return
            
            if self.vehicle_id:
                # Mise à jour
                query = """
                    UPDATE vehicules SET
                        matricule = ?, marque = ?, modele = ?, type_carburant = ?
                    WHERE id = ?
                """
                params = (
                    matricule,
                    self.vehicle_vars['marque'].get().strip(),
                    self.vehicle_vars['modele'].get().strip(),
                    self.vehicle_vars['type_carburant'].get().strip(),
                    self.vehicle_id
                )
                self.db_manager.execute_update(query, params, table='vehicules')
                messagebox.showinfo("Succès", "Véhicule modifié avec succès")
            else:
                # Nouveau véhicule
                query = """
                    INSERT INTO vehicules (client_id, matricule, marque, modele, type_carburant)
                    VALUES (?, ?, ?, ?, ?)
                """
                params = (
                    self.client_id,
                    matricule,
                    self.vehicle_vars['marque'].get().strip(),
                    self.vehicle_vars['modele'].get().strip(),
                    self.vehicle_vars['type_carburant'].get().strip()
                )
                self.db_manager.execute_insert(query, params, table='vehicules')
                messagebox.showinfo("Succès", "Véhicule ajouté avec succès")
            
            # Recharger et fermer
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
