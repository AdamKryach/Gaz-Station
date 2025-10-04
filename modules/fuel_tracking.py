# -*- coding: utf-8 -*-
"""
Module de Suivi des Transactions de Carburant
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import re

class FuelTracking:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        
        self.setup_interface()
        self.load_fuel_prices()
        self.load_transactions()
    
    def setup_interface(self):
        """Configuration de l'interface de suivi des transactions"""
        # Frame principal avec deux panels
        main_paned = ttk.PanedWindow(self.parent, orient='vertical')
        main_paned.pack(fill='both', expand=True)
        
        # Panel haut - Nouvelle transaction
        top_frame = ttk.Frame(main_paned)
        main_paned.add(top_frame, weight=1)
        
        # Panel bas - Liste des transactions
        bottom_frame = ttk.Frame(main_paned)
        main_paned.add(bottom_frame, weight=2)
        
        self.setup_transaction_form(top_frame)
        self.setup_transactions_list(bottom_frame)
    
    def setup_transaction_form(self, parent):
        """Configuration du formulaire de nouvelle transaction"""
        form_frame = ttk.LabelFrame(parent, text="Nouvelle Transaction de Carburant", padding=20)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame principal du formulaire
        main_form = ttk.Frame(form_frame)
        main_form.pack(fill='both', expand=True)
        
        # Variables du formulaire
        self.transaction_vars = {}
        
        # Colonne 1
        col1_frame = ttk.Frame(main_form)
        col1_frame.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        # Station
        ttk.Label(col1_frame, text="Station *", style='Touch.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        self.transaction_vars['station'] = tk.StringVar()
        self.station_combo = ttk.Combobox(col1_frame, textvariable=self.transaction_vars['station'],
                                         state='readonly', width=30, font=('Arial', 11))
        self.station_combo.grid(row=0, column=1, sticky='ew', pady=5)
        self.load_stations()
        
        # Client
        ttk.Label(col1_frame, text="Client *", style='Touch.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.transaction_vars['client'] = tk.StringVar()
        self.client_combo = ttk.Combobox(col1_frame, textvariable=self.transaction_vars['client'],
                                        width=30, font=('Arial', 11))
        self.client_combo.grid(row=1, column=1, sticky='ew', pady=5)
        self.client_combo.bind('<KeyRelease>', self.on_client_search)
        self.client_combo.bind('<<ComboboxSelected>>', self.on_client_select)
        self.load_clients()
        
        # Véhicule
        ttk.Label(col1_frame, text="Véhicule", style='Touch.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.transaction_vars['vehicule'] = tk.StringVar()
        self.vehicule_combo = ttk.Combobox(col1_frame, textvariable=self.transaction_vars['vehicule'],
                                          state='readonly', width=30, font=('Arial', 11))
        self.vehicule_combo.grid(row=2, column=1, sticky='ew', pady=5)
        
        # Type de carburant
        ttk.Label(col1_frame, text="Carburant *", style='Touch.TLabel').grid(row=3, column=0, sticky='w', pady=5)
        self.transaction_vars['carburant'] = tk.StringVar()
        self.carburant_combo = ttk.Combobox(col1_frame, textvariable=self.transaction_vars['carburant'],
                                           state='readonly', width=30, font=('Arial', 11))
        self.carburant_combo.grid(row=3, column=1, sticky='ew', pady=5)
        self.carburant_combo.bind('<<ComboboxSelected>>', self.on_fuel_select)
        self.load_fuels()
        
        # Numéro de pompe
        ttk.Label(col1_frame, text="Numéro Pompe", style='Touch.TLabel').grid(row=4, column=0, sticky='w', pady=5)
        self.transaction_vars['pompe'] = tk.StringVar()
        pompe_entry = ttk.Entry(col1_frame, textvariable=self.transaction_vars['pompe'], width=30, font=('Arial', 11))
        pompe_entry.grid(row=4, column=1, sticky='ew', pady=5)
        
        col1_frame.columnconfigure(1, weight=1)
        
        # Colonne 2
        col2_frame = ttk.Frame(main_form)
        col2_frame.pack(side='left', fill='both', expand=True)
        
        # Quantité
        ttk.Label(col2_frame, text="Quantité (L) *", style='Touch.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        self.transaction_vars['quantite'] = tk.StringVar()
        quantite_entry = ttk.Entry(col2_frame, textvariable=self.transaction_vars['quantite'], 
                                  width=30, font=('Arial', 11))
        quantite_entry.grid(row=0, column=1, sticky='ew', pady=5)
        quantite_entry.bind('<KeyRelease>', self.calculate_total)
        
        # Prix unitaire
        ttk.Label(col2_frame, text="Prix/L (DH) *", style='Touch.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        self.transaction_vars['prix_unitaire'] = tk.StringVar()
        prix_entry = ttk.Entry(col2_frame, textvariable=self.transaction_vars['prix_unitaire'], 
                              width=30, font=('Arial', 11))
        prix_entry.grid(row=1, column=1, sticky='ew', pady=5)
        prix_entry.bind('<KeyRelease>', self.calculate_total)
        
        # Montant total (calculé)
        ttk.Label(col2_frame, text="Montant Total (DH)", style='Touch.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        self.transaction_vars['montant_total'] = tk.StringVar(value="0.00")
        self.total_label = ttk.Label(col2_frame, textvariable=self.transaction_vars['montant_total'],
                                    font=('Arial', 14, 'bold'), foreground='green')
        self.total_label.grid(row=2, column=1, sticky='w', pady=5)
        
        # Notes
        ttk.Label(col2_frame, text="Notes", style='Touch.TLabel').grid(row=3, column=0, sticky='w', pady=5)
        self.transaction_vars['notes_inline'] = tk.StringVar()
        notes_entry = ttk.Entry(col2_frame, textvariable=self.transaction_vars['notes_inline'], 
                               width=30, font=('Arial', 11))
        notes_entry.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Type de paiement
        ttk.Label(col2_frame, text="Type Paiement", style='Touch.TLabel').grid(row=4, column=0, sticky='w', pady=5)
        self.transaction_vars['type_paiement'] = tk.StringVar(value='credit')
        paiement_combo = ttk.Combobox(col2_frame, textvariable=self.transaction_vars['type_paiement'],
                                     values=['credit', 'especes', 'carte', 'cheque'],
                                     state='readonly', width=30, font=('Arial', 11))
        paiement_combo.grid(row=4, column=1, sticky='ew', pady=5)
        
        col2_frame.columnconfigure(1, weight=1)
        
        
        # Boutons d'action
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(btn_frame, text="Enregistrer Transaction",
                  command=self.save_transaction,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Imprimer Facture",
                  command=self.print_invoice,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Effacer",
                  command=self.clear_form,
                  style='Touch.TButton').pack(side='left', padx=10)
        
        ttk.Button(btn_frame, text="Calculatrice",
                  command=self.open_calculator,
                  style='Touch.TButton').pack(side='right')
    
    def setup_transactions_list(self, parent):
        """Configuration de la liste des transactions"""
        list_frame = ttk.LabelFrame(parent, text="Transactions Récentes", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Filtres
        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Période:", style='Touch.TLabel').pack(side='left')
        self.filter_period = tk.StringVar(value="aujourd_hui")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.filter_period,
                                   values=["aujourd_hui", "cette_semaine", "ce_mois"],
                                   state='readonly', width=15)
        period_combo.pack(side='left', padx=(5, 20))
        
        ttk.Label(filter_frame, text="Station:", style='Touch.TLabel').pack(side='left')
        self.filter_station = tk.StringVar(value="toutes")
        filter_station_combo = ttk.Combobox(filter_frame, textvariable=self.filter_station,
                                           state='readonly', width=20)
        filter_station_combo.pack(side='left', padx=(5, 20))
        
        ttk.Button(filter_frame, text="Filtrer",
                  command=self.load_transactions,
                  style='Touch.TButton').pack(side='left', padx=10)
        
        ttk.Button(filter_frame, text="Imprimer Facture",
                  command=self.print_selected_transaction,
                  style='Touch.TButton').pack(side='right', padx=(0, 10))
        
        ttk.Button(filter_frame, text="Modifier Transaction",
                  command=self.edit_transaction,
                  style='Touch.TButton').pack(side='right', padx=(0, 10))
        
        ttk.Button(filter_frame, text="Supprimer",
                  command=self.delete_transaction,
                  style='Touch.TButton').pack(side='right')
        
        # Liste des transactions
        columns = ('ID', 'Date', 'Station', 'Client', 'Véhicule', 'Carburant', 'Quantité', 'Prix/L', 'Total', 'Paiement')
        self.transactions_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                            style='Touch.Treeview', height=12)
        
        # Configuration des colonnes
        column_widths = [50, 120, 120, 150, 100, 100, 80, 80, 100, 80]
        for i, col in enumerate(columns):
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=column_widths[i])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.transactions_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.transactions_tree.xview)
        
        self.transactions_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement
        self.transactions_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind selection
        self.transactions_tree.bind('<Double-1>', self.on_transaction_double_click)
    
    def load_stations(self):
        """Charger les stations"""
        try:
            # Utiliser le cache pour les stations qui changent rarement
            stations = self.db_manager.execute_query(
                "SELECT id, nom FROM stations ORDER BY nom", 
                use_cache=True, 
                cache_timeout=3600  # Cache d'une heure
            )
            station_list = [f"{station[0]} - {station[1]}" for station in stations]
            self.station_combo['values'] = station_list
            
            # Pour le filtre aussi
            if hasattr(self, 'filter_station'):
                filter_list = ["toutes"] + [station[1] for station in stations]
                # Trouver le widget de filtre station et mettre à jour ses valeurs
                # (cette partie sera mise à jour après la création complète)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des stations: {str(e)}")
    
    def load_clients(self):
        """Charger les clients actifs"""
        try:
            query = """
                SELECT c.id, c.nom, c.prenom, c.solde_actuel
                FROM clients c 
                ORDER BY c.nom, c.prenom
            """
            # Utiliser le cache avec un timeout court car les soldes peuvent changer
            clients = self.db_manager.execute_query(query, use_cache=True, cache_timeout=60)
            
            client_list = []
            for client in clients:
                client_id, nom, prenom, solde = client
                
                display_name = f"{client_id} - {nom} {prenom or ''} [Solde: {solde:.2f} DH]"
                client_list.append(display_name.strip())
            
            self.client_combo['values'] = client_list
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des clients: {str(e)}")
    
    def load_fuels(self):
        """Charger les types de carburant"""
        try:
            # Utiliser le cache pour les carburants qui changent rarement
            fuels = self.db_manager.execute_query(
                "SELECT id, nom, prix_unitaire FROM carburants ORDER BY nom",
                use_cache=True,
                cache_timeout=3600  # Cache d'une heure
            )
            fuel_list = [f"{fuel[0]} - {fuel[1]} ({fuel[2]:.2f} DH/L)" for fuel in fuels]
            self.carburant_combo['values'] = fuel_list
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des carburants: {str(e)}")
    
    def load_fuel_prices(self):
        """Charger les prix des carburants"""
        try:
            self.fuel_prices = {}
            # Utiliser le cache pour les prix qui changent rarement
            fuels = self.db_manager.execute_query(
                "SELECT id, prix_unitaire FROM carburants",
                use_cache=True,
                cache_timeout=3600  # Cache d'une heure
            )
            for fuel_id, price in fuels:
                self.fuel_prices[fuel_id] = price
        except Exception as e:
            print(f"Erreur lors du chargement des prix: {str(e)}")
    
    def on_client_search(self, event):
        """Filtrer les clients en temps réel"""
        search_term = self.client_combo.get().lower()
        if len(search_term) < 2:
            return
        
        try:
            query = """
                SELECT c.id, c.nom, c.prenom, c.solde_actuel
                FROM clients c 
                WHERE (
                    LOWER(c.nom) LIKE ? OR 
                    LOWER(c.prenom) LIKE ?
                )
                ORDER BY c.nom, c.prenom
                LIMIT 10
            """
            search_pattern = f"%{search_term}%"
            # Ne pas utiliser le cache pour les recherches en temps réel
            clients = self.db_manager.execute_query(query, (search_pattern, search_pattern), use_cache=False)
            
            client_list = []
            for client in clients:
                client_id, nom, prenom, solde = client
                
                display_name = f"{client_id} - {nom} {prenom or ''} [Solde: {solde:.2f} DH]"
                client_list.append(display_name.strip())
            
            self.client_combo['values'] = client_list
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {str(e)}")
    
    def on_client_select(self, event):
        """Charger les véhicules du client sélectionné"""
        client_text = self.client_combo.get()
        if not client_text or ' - ' not in client_text:
            return
        
        try:
            client_id = int(client_text.split(' - ')[0])
            
            # Charger les véhicules
            query = """
                SELECT id, matricule, marque, modele
                FROM vehicules 
                WHERE client_id = ?
                ORDER BY matricule
            """
            # Utiliser le cache pour les véhicules d'un client
            vehicles = self.db_manager.execute_query(query, (client_id,), use_cache=True, cache_timeout=60)
            
            vehicle_list = []
            for vehicle in vehicles:
                vehicle_id, matricule, marque, modele = vehicle
                display = f"{vehicle_id} - {matricule}"
                if marque or modele:
                    display += f" ({marque or ''} {modele or ''})"
                vehicle_list.append(display.strip())
            
            self.vehicule_combo['values'] = vehicle_list
            
            # Réinitialiser la sélection de véhicule
            self.transaction_vars['vehicule'].set('')
            
        except Exception as e:
            print(f"Erreur lors du chargement des véhicules: {str(e)}")
    
    def on_fuel_select(self, event):
        """Mettre à jour le prix unitaire quand un carburant est sélectionné"""
        fuel_text = self.carburant_combo.get()
        if not fuel_text or ' - ' not in fuel_text:
            return
        
        try:
            fuel_id = int(fuel_text.split(' - ')[0])
            if fuel_id in self.fuel_prices:
                self.transaction_vars['prix_unitaire'].set(str(self.fuel_prices[fuel_id]))
                self.calculate_total()
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour du prix: {str(e)}")
    
    def calculate_total(self, event=None):
        """Calculer le montant total"""
        try:
            quantite_str = self.transaction_vars['quantite'].get()
            prix_str = self.transaction_vars['prix_unitaire'].get()
            
            if quantite_str and prix_str:
                quantite = float(quantite_str)
                prix = float(prix_str)
                total = quantite * prix
                self.transaction_vars['montant_total'].set(f"{total:.2f}")
            else:
                self.transaction_vars['montant_total'].set("0.00")
                
        except ValueError:
            self.transaction_vars['montant_total'].set("0.00")
    
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
    
    def save_transaction(self):
        """Enregistrer une nouvelle transaction"""
        try:
            # Validation simplifiée - seulement les champs essentiels
            if not all([
                self.transaction_vars['station'].get(),
                self.transaction_vars['client'].get(),
                self.transaction_vars['carburant'].get(),
                self.transaction_vars['quantite'].get(),
                self.transaction_vars['prix_unitaire'].get()
            ]):
                messagebox.showwarning("Attention", "Veuillez remplir tous les champs obligatoires")
                return
            
            # Validation du matricule si un véhicule est sélectionné
            if self.transaction_vars['vehicule'].get():
                vehicule_text = self.transaction_vars['vehicule'].get()
                if ' - ' in vehicule_text:
                    # Extraire le matricule
                    matricule = vehicule_text.split(' - ')[1].split(' ')[0]
                    is_valid, info = self.validate_moroccan_plate(matricule)
                    if not is_valid:
                        if not messagebox.askyesno("Validation Matricule", 
                            f"Matricule invalide: {info}\n" +
                            f"Format attendu: [Numéro 1-6 chiffres] | [Lettre arabe] | [Région 1-99]\n" +
                            "Voulez-vous continuer quand même?"):
                            return
            
            # Extraction des IDs
            station_id = int(self.transaction_vars['station'].get().split(' - ')[0])
            client_id = int(self.transaction_vars['client'].get().split(' - ')[0])
            carburant_id = int(self.transaction_vars['carburant'].get().split(' - ')[0])
            
            vehicule_id = None
            if self.transaction_vars['vehicule'].get():
                vehicule_id = int(self.transaction_vars['vehicule'].get().split(' - ')[0])
            
            # Validation numérique
            quantite = float(self.transaction_vars['quantite'].get())
            prix_unitaire = float(self.transaction_vars['prix_unitaire'].get())
            montant_total = quantite * prix_unitaire
            
            pompe = None
            if self.transaction_vars['pompe'].get().strip():
                pompe = int(self.transaction_vars['pompe'].get())
            
            # Insertion de la transaction
            query = """
                INSERT INTO transactions (
                    station_id, client_id, vehicule_id, carburant_id,
                    quantite, prix_unitaire, montant_total, type_paiement,
                    numero_pompe, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # Utiliser les notes inline si disponibles
            notes = self.transaction_vars.get('notes_inline', tk.StringVar()).get().strip() or None
            
            params = (
                station_id, client_id, vehicule_id, carburant_id,
                quantite, prix_unitaire, montant_total,
                self.transaction_vars['type_paiement'].get(),
                pompe, notes
            )
            
            # Utiliser le paramètre table pour invalider automatiquement le cache
            transaction_id = self.db_manager.execute_insert(query, params, table='transactions')
            
            # Mise à jour du solde client (si paiement à crédit)
            if self.transaction_vars['type_paiement'].get() == 'credit':
                update_query = """
                    UPDATE clients 
                    SET solde_actuel = solde_actuel - ? 
                    WHERE id = ?
                """
                self.db_manager.execute_update(update_query, (montant_total, client_id), table='clients')
            
            messagebox.showinfo("Succès", f"Transaction enregistrée avec succès (ID: {transaction_id})")
            
            # Effacer le formulaire et recharger la liste
            self.clear_form()
            self.load_transactions()
            self.load_clients()  # Recharger pour mettre à jour les soldes
            
        except ValueError as ve:
            messagebox.showerror("Erreur", f"Valeur numérique invalide: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
    
    def clear_form(self):
        """Effacer le formulaire"""
        for var in self.transaction_vars.values():
            var.set('')
        
        # Remettre les valeurs par défaut
        self.transaction_vars['type_paiement'].set('credit')
        self.transaction_vars['montant_total'].set('0.00')
        
        # Vider la liste des véhicules
        self.vehicule_combo['values'] = []
    
    def load_transactions(self):
        """Charger la liste des transactions selon les filtres"""
        try:
            # Vider la liste actuelle
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            
            # Construire la requête selon la période
            period = self.filter_period.get()
            where_clause = ""
            
            if period == "aujourd_hui":
                where_clause = "DATE(t.date_transaction) = DATE('now')"
            elif period == "cette_semaine":
                where_clause = "DATE(t.date_transaction) >= DATE('now', '-7 days')"
            elif period == "ce_mois":
                where_clause = "DATE(t.date_transaction) >= DATE('now', 'start of month')"
            
            # Filtre par station
            station_filter = self.filter_station.get()
            if station_filter and station_filter != "toutes":
                if where_clause:
                    where_clause += " AND "
                where_clause += f"s.nom = '{station_filter}'"
            
            query = f"""
                SELECT 
                    t.id, t.date_transaction, s.nom as station,
                    c.nom || ' ' || COALESCE(c.prenom, '') as client,
                    COALESCE(v.matricule, '-') as vehicule,
                    car.nom as carburant,
                    t.quantite, t.prix_unitaire, t.montant_total, t.type_paiement
                FROM transactions t
                JOIN stations s ON t.station_id = s.id
                JOIN clients c ON t.client_id = c.id
                LEFT JOIN vehicules v ON t.vehicule_id = v.id
                JOIN carburants car ON t.carburant_id = car.id
                {('WHERE ' + where_clause) if where_clause else ''}
                ORDER BY t.date_transaction DESC
                LIMIT 100
            """
            
            # Utiliser le cache avec un timeout court pour les transactions récentes
            transactions = self.db_manager.execute_query(query, use_cache=True, cache_timeout=30)
            
            for transaction in transactions:
                # Formatage de la date
                date_str = transaction[1][:16] if transaction[1] else ''
                
                values = (
                    transaction[0],  # ID
                    date_str,        # Date
                    transaction[2],  # Station
                    transaction[3],  # Client
                    transaction[4],  # Véhicule
                    transaction[5],  # Carburant
                    f"{transaction[6]:.1f}L",      # Quantité
                    f"{transaction[7]:.2f}",       # Prix/L
                    f"{transaction[8]:.2f} DH",    # Total
                    transaction[9]   # Paiement
                )
                
                self.transactions_tree.insert('', 'end', values=values)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des transactions: {str(e)}")
    
    def edit_transaction(self):
        """Modifier une transaction sélectionnée"""
        selection = self.transactions_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une transaction")
            return
        
        item = selection[0]
        transaction_id = self.transactions_tree.item(item)['values'][0]
        
        # Ouvrir la fenêtre de modification
        EditTransactionDialog(self.parent, self.db_manager, transaction_id, self.load_transactions)
    
    def delete_transaction(self):
        """Supprimer une transaction"""
        selection = self.transactions_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une transaction")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette transaction ?"):
            try:
                item = selection[0]
                transaction_id = self.transactions_tree.item(item)['values'][0]
                
                # Récupérer les détails de la transaction pour ajuster le solde
                query = """
                    SELECT client_id, montant_total, type_paiement 
                    FROM transactions 
                    WHERE id = ?
                """
                # Ne pas utiliser le cache pour cette vérification critique
                result = self.db_manager.execute_query(query, (transaction_id,), use_cache=False)
                
                if result:
                    client_id, montant, type_paiement = result[0]
                    
                    # Supprimer la transaction
                delete_query = "DELETE FROM transactions WHERE id = ?"
                # Utiliser le paramètre table pour invalider automatiquement le cache
                self.db_manager.execute_update(delete_query, (transaction_id,), table='transactions')
                
                # Ajuster le solde client si c'était à crédit
                if type_paiement == 'credit':
                    update_query = """
                        UPDATE clients 
                        SET solde_actuel = solde_actuel + ? 
                        WHERE id = ?
                    """
                    # Utiliser le paramètre table pour invalider automatiquement le cache
                    self.db_manager.execute_update(update_query, (montant, client_id), table='clients')
                    
                    messagebox.showinfo("Succès", "Transaction supprimée avec succès")
                    self.load_transactions()
                    self.load_clients()  # Recharger pour mettre à jour les soldes
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
    
    def on_transaction_double_click(self, event):
        """Gérer le double-clic sur une transaction"""
        self.edit_transaction()
    
    def print_selected_transaction(self):
        """Imprimer la facture de la transaction sélectionnée"""
        selection = self.transactions_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une transaction pour imprimer sa facture")
            return
        
        item = selection[0]
        transaction_id = self.transactions_tree.item(item)['values'][0]
        self.generate_html_invoice_from_transaction(transaction_id)
    
    def print_invoice(self):
        """Imprimer une facture HTML pour la transaction actuelle ou sélectionnée"""
        # D'abord, vérifier s'il y a une transaction sélectionnée dans la liste
        selection = self.transactions_tree.selection()
        
        if selection:
            # Utiliser la transaction sélectionnée
            item = selection[0]
            transaction_id = self.transactions_tree.item(item)['values'][0]
            self.generate_html_invoice_from_transaction(transaction_id)
        else:
            # Utiliser les données du formulaire actuel
            if not self.validate_form_for_invoice():
                return
            self.generate_html_invoice_from_form()
    
    def validate_form_for_invoice(self):
        """Valider que le formulaire contient assez d'informations pour une facture"""
        required_fields = ['station', 'client', 'carburant', 'quantite', 'prix_unitaire']
        
        for field in required_fields:
            if not self.transaction_vars[field].get().strip():
                messagebox.showwarning("Attention", 
                    "Veuillez remplir tous les champs obligatoires avant d'imprimer une facture")
                return False
        
        try:
            float(self.transaction_vars['quantite'].get())
            float(self.transaction_vars['prix_unitaire'].get())
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez saisir des valeurs numériques valides")
            return False
        
        return True
    
    def generate_html_invoice_from_form(self):
        """Générer une facture HTML à partir des données du formulaire"""
        try:
            # Extraire les données du formulaire
            station_text = self.transaction_vars['station'].get()
            client_text = self.transaction_vars['client'].get()
            carburant_text = self.transaction_vars['carburant'].get()
            vehicule_text = self.transaction_vars['vehicule'].get() or "Non spécifié"
            
            # Parsing des sélections
            station_nom = station_text.split(' - ')[1] if ' - ' in station_text else station_text
            client_nom = client_text.split(' - ')[1].split(' [')[0] if ' - ' in client_text else client_text
            carburant_nom = carburant_text.split(' - ')[1].split(' (')[0] if ' - ' in carburant_text else carburant_text
            vehicule_info = vehicule_text.split(' - ')[1] if ' - ' in vehicule_text and vehicule_text != "Non spécifié" else vehicule_text
            
            quantite = float(self.transaction_vars['quantite'].get())
            prix_unitaire = float(self.transaction_vars['prix_unitaire'].get())
            total = quantite * prix_unitaire
            
            # Date et heure actuelles
            now = datetime.now()
            date_str = now.strftime("%d/%m/%Y")
            heure_str = now.strftime("%H:%M")
            
            # Récupérer les informations de la station depuis la base de données
            station_id = int(station_text.split(' - ')[0]) if ' - ' in station_text else 1
            station_query = "SELECT nom, adresse, telephone FROM stations WHERE id = ?"
            station_result = self.db_manager.execute_query(station_query, (station_id,))
            
            if station_result:
                station_nom_db, station_adresse, station_tel = station_result[0]
                station_nom = station_nom_db or station_nom
                station_adresse = station_adresse or "Adresse non spécifiée"
                station_tel = station_tel or "05 ** ** ** **"
            else:
                station_adresse = "Adresse non spécifiée"
                station_tel = "05 ** ** ** **"
            
            # Générer le HTML
            html_content = self.create_invoice_html(
                station_nom, station_adresse, station_tel,
                date_str, heure_str, client_nom, vehicule_info,
                [(carburant_nom, quantite, prix_unitaire, total)],
                total
            )
            
            # Sauvegarder et ouvrir
            self.save_and_open_invoice(html_content, f"facture_{now.strftime('%Y%m%d_%H%M%S')}.html")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération de la facture: {str(e)}")
    
    def generate_html_invoice_from_transaction(self, transaction_id):
        """Générer une facture HTML à partir d'une transaction existante"""
        try:
            # Récupérer toutes les données de la transaction
            query = """
                SELECT 
                    t.id, t.date_transaction, t.quantite, t.prix_unitaire, t.montant_total,
                    s.nom as station_nom, s.adresse as station_adresse, s.telephone as station_tel,
                    c.nom as client_nom, c.prenom as client_prenom,
                    COALESCE(v.matricule, 'Non spécifié') as vehicule,
                    car.nom as carburant_nom
                FROM transactions t
                JOIN stations s ON t.station_id = s.id
                JOIN clients c ON t.client_id = c.id
                LEFT JOIN vehicules v ON t.vehicule_id = v.id
                JOIN carburants car ON t.carburant_id = car.id
                WHERE t.id = ?
            """
            
            result = self.db_manager.execute_query(query, (transaction_id,))
            
            if not result:
                messagebox.showerror("Erreur", "Transaction non trouvée")
                return
            
            data = result[0]
            
            # Extraire les données
            transaction_date = datetime.strptime(data[1][:19], '%Y-%m-%d %H:%M:%S')
            date_str = transaction_date.strftime("%d/%m/%Y")
            heure_str = transaction_date.strftime("%H:%M")
            
            station_nom = data[5]
            station_adresse = data[6] or "Adresse non spécifiée"
            station_tel = data[7] or "05 ** ** ** **"
            
            client_nom = f"{data[8]} {data[9] or ''}" .strip()
            vehicule_info = data[10]
            carburant_nom = data[11]
            
            quantite = data[2]
            prix_unitaire = data[3]
            total = data[4]
            
            # Générer le HTML
            html_content = self.create_invoice_html(
                station_nom, station_adresse, station_tel,
                date_str, heure_str, client_nom, vehicule_info,
                [(carburant_nom, quantite, prix_unitaire, total)],
                total
            )
            
            # Sauvegarder et ouvrir
            filename = f"facture_transaction_{transaction_id}_{transaction_date.strftime('%Y%m%d_%H%M%S')}.html"
            self.save_and_open_invoice(html_content, filename)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération de la facture: {str(e)}")
    
    def create_invoice_html(self, station_nom, station_adresse, station_tel, 
                           date_str, heure_str, client_nom, vehicule_info,
                           fuel_items, total_general):
        """Créer le contenu HTML de la facture"""
        
        # Créer les lignes du tableau pour les carburants
        fuel_rows = ""
        for carburant, quantite, prix_unitaire, total in fuel_items:
            fuel_rows += f"""
        <tr>
            <td>{carburant}</td>
            <td>{quantite:.1f}</td>
            <td>{prix_unitaire:.2f}</td>
            <td>{total:.2f}</td>
        </tr>"""
        
        html_template = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Facture de Carburant</title>
<style>
    body {{
        font-family: "Arial", sans-serif;
        max-width: 400px;
        margin: 0 auto;
        padding: 20px;
        border: 1px solid #000;
    }}
    header {{
        text-align: center;
        margin-bottom: 20px;
    }}
    header h1 {{
        margin: 0;
        font-size: 18px;
    }}
    .info {{
        margin-bottom: 15px;
        font-size: 14px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
    }}
    table, th, td {{
        border: 1px solid #000;
    }}
    th, td {{
        padding: 5px;
        text-align: left;
        font-size: 14px;
    }}
    .total {{
        text-align: right;
        font-weight: bold;
        font-size: 16px;
        margin-top: 10px;
    }}
    footer {{
        text-align: center;
        font-size: 12px;
        margin-top: 15px;
        border-top: 1px solid #000;
        padding-top: 5px;
    }}
</style>
</head>
<body>

<header>
    <h1>{station_nom}</h1>
    <p>Adresse: {station_adresse}</p>
    <p>Téléphone: {station_tel}</p>
</header>

<div class="info">
    <p><strong>Date:</strong> {date_str}</p>
    <p><strong>Heure:</strong> {heure_str}</p>
    <p><strong>Client:</strong> {client_nom}</p>
    <p><strong>Véhicule:</strong> {vehicule_info}</p>
</div>

<table>
    <thead>
        <tr>
            <th>Type de carburant</th>
            <th>Quantité (L)</th>
            <th>Prix / L (MAD)</th>
            <th>Total (MAD)</th>
        </tr>
    </thead>
    <tbody>
{fuel_rows}
    </tbody>
</table>

<div class="total">
    Total à payer: {total_general:.2f} MAD
</div>

<footer>
    Merci pour votre visite ! <br>
</footer>

</body>
</html>
        """
        
        return html_template
    
    def save_and_open_invoice(self, html_content, filename):
        """Sauvegarder la facture HTML et l'ouvrir"""
        try:
            from tkinter import filedialog
            import webbrowser
            import os
            
            # Demander où sauvegarder
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("Fichiers HTML", "*.html"), ("Tous les fichiers", "*.*")],
                title="Enregistrer la facture",
                initialvalue=filename
            )
            
            if not file_path:
                return
            
            # Écrire le fichier HTML
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            messagebox.showinfo("Succès", f"Facture sauvegardée: {file_path}")
            
            # Proposer d'ouvrir le fichier
            if messagebox.askyesno("Ouverture", "Voulez-vous ouvrir la facture dans votre navigateur?"):
                webbrowser.open(f'file://{os.path.abspath(file_path)}')
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def open_calculator(self):
        """Ouvrir une calculatrice simple"""
        CalculatorDialog(self.parent)

class EditTransactionDialog:
    def __init__(self, parent, db_manager, transaction_id, callback):
        self.db_manager = db_manager
        self.transaction_id = transaction_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier Transaction")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        self.load_transaction_data()
        
        self.dialog.focus()
    
    def setup_dialog(self):
        """Configuration de la fenêtre de dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Variables
        self.edit_vars = {}
        
        # Champs modifiables
        fields = [
            ('quantite', 'Quantité (L)'),
            ('prix_unitaire', 'Prix Unitaire (DH)'),
            ('numero_pompe', 'Numéro Pompe'),
            ('kilometrage', 'Kilométrage'),
            ('type_paiement', 'Type Paiement'),
            ('notes', 'Notes')
        ]
        
        row = 0
        for field_id, label in fields:
            ttk.Label(main_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)
            
            self.edit_vars[field_id] = tk.StringVar()
            
            if field_id == 'type_paiement':
                widget = ttk.Combobox(main_frame, textvariable=self.edit_vars[field_id],
                                     values=['credit', 'especes', 'carte', 'cheque'],
                                     state='readonly', width=25)
            else:
                widget = ttk.Entry(main_frame, textvariable=self.edit_vars[field_id], width=25)
            
            widget.grid(row=row, column=1, sticky='ew', pady=5)
            
            if field_id in ['quantite', 'prix_unitaire']:
                widget.bind('<KeyRelease>', self.calculate_total)
            
            row += 1
        
        # Montant calculé
        ttk.Label(main_frame, text="Montant Total (DH)").grid(row=row, column=0, sticky='w', pady=5)
        self.edit_vars['montant_total'] = tk.StringVar()
        self.total_label = ttk.Label(main_frame, textvariable=self.edit_vars['montant_total'],
                                    font=('Arial', 12, 'bold'))
        self.total_label.grid(row=row, column=1, sticky='w', pady=5)
        
        main_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row+1, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Enregistrer", command=self.save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def load_transaction_data(self):
        """Charger les données de la transaction"""
        try:
            query = "SELECT * FROM transactions WHERE id = ?"
            result = self.db_manager.execute_query(query, (self.transaction_id,))
            
            if result:
                data = result[0]
                # Mapping des champs selon la structure de la table
                fields = ['id', 'station_id', 'client_id', 'vehicule_id', 'carburant_id',
                         'quantite', 'prix_unitaire', 'montant_total', 'type_paiement',
                         'date_transaction', 'numero_pompe', 'kilometrage', 'notes']
                
                # Remplir les champs modifiables
                self.edit_vars['quantite'].set(str(data[5]) if data[5] else '')
                self.edit_vars['prix_unitaire'].set(str(data[6]) if data[6] else '')
                self.edit_vars['montant_total'].set(f"{data[7]:.2f}" if data[7] else '0.00')
                self.edit_vars['type_paiement'].set(str(data[8]) if data[8] else 'credit')
                self.edit_vars['numero_pompe'].set(str(data[10]) if data[10] else '')
                self.edit_vars['kilometrage'].set(str(data[11]) if data[11] else '')
                self.edit_vars['notes'].set(str(data[12]) if data[12] else '')
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def calculate_total(self, event=None):
        """Calculer le nouveau total"""
        try:
            quantite = float(self.edit_vars['quantite'].get() or 0)
            prix = float(self.edit_vars['prix_unitaire'].get() or 0)
            total = quantite * prix
            self.edit_vars['montant_total'].set(f"{total:.2f}")
        except ValueError:
            self.edit_vars['montant_total'].set("0.00")
    
    def save_changes(self):
        """Enregistrer les modifications"""
        try:
            # Validation
            quantite = float(self.edit_vars['quantite'].get() or 0)
            prix = float(self.edit_vars['prix_unitaire'].get() or 0)
            
            if quantite <= 0 or prix <= 0:
                messagebox.showerror("Erreur", "La quantité et le prix doivent être supérieurs à 0")
                return
            
            montant = quantite * prix
            
            # Récupérer l'ancien montant pour ajuster le solde
            old_query = "SELECT client_id, montant_total, type_paiement FROM transactions WHERE id = ?"
            old_data = self.db_manager.execute_query(old_query, (self.transaction_id,))[0]
            old_client_id, old_montant, old_type_paiement = old_data
            
            # Mise à jour de la transaction
            update_query = """
                UPDATE transactions SET
                    quantite = ?, prix_unitaire = ?, montant_total = ?,
                    type_paiement = ?, numero_pompe = ?, kilometrage = ?, notes = ?
                WHERE id = ?
            """
            
            params = (
                quantite, prix, montant,
                self.edit_vars['type_paiement'].get(),
                int(self.edit_vars['numero_pompe'].get()) if self.edit_vars['numero_pompe'].get() else None,
                int(self.edit_vars['kilometrage'].get()) if self.edit_vars['kilometrage'].get() else None,
                self.edit_vars['notes'].get().strip() or None,
                self.transaction_id
            )
            
            self.db_manager.execute_update(update_query, params)
            
            # Ajuster le solde client si nécessaire
            new_type_paiement = self.edit_vars['type_paiement'].get()
            
            if old_type_paiement == 'credit' or new_type_paiement == 'credit':
                # Remettre l'ancien solde
                if old_type_paiement == 'credit':
                    adjust_query = "UPDATE clients SET solde_actuel = solde_actuel + ? WHERE id = ?"
                    self.db_manager.execute_update(adjust_query, (old_montant, old_client_id))
                
                # Appliquer le nouveau solde
                if new_type_paiement == 'credit':
                    adjust_query = "UPDATE clients SET solde_actuel = solde_actuel - ? WHERE id = ?"
                    self.db_manager.execute_update(adjust_query, (montant, old_client_id))
            
            messagebox.showinfo("Succès", "Transaction modifiée avec succès")
            self.callback()
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erreur", "Valeurs numériques invalides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")

class CalculatorDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Calculatrice")
        self.dialog.geometry("300x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.result_var = tk.StringVar(value="0")
        self.expression = ""
        
        self.setup_calculator()
        self.dialog.focus()
    
    def setup_calculator(self):
        """Configuration de la calculatrice"""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Écran
        screen = ttk.Entry(main_frame, textvariable=self.result_var, 
                          font=('Arial', 16), state='readonly', justify='right')
        screen.pack(fill='x', pady=(0, 10))
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='both', expand=True)
        
        # Définir les boutons
        buttons = [
            ['C', '±', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=']
        ]
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text == '0':
                    btn = ttk.Button(buttons_frame, text=text, 
                                   command=lambda t=text: self.on_button_click(t))
                    btn.grid(row=i, column=j, columnspan=2, sticky='ew', padx=2, pady=2)
                elif text == '=':
                    btn = ttk.Button(buttons_frame, text=text,
                                   command=lambda t=text: self.on_button_click(t))
                    btn.grid(row=i, column=j+1, sticky='ew', padx=2, pady=2)
                else:
                    btn = ttk.Button(buttons_frame, text=text,
                                   command=lambda t=text: self.on_button_click(t))
                    btn.grid(row=i, column=j, sticky='ew', padx=2, pady=2)
        
        # Configuration de la grille
        for i in range(4):
            buttons_frame.columnconfigure(i, weight=1)
        for i in range(len(buttons)):
            buttons_frame.rowconfigure(i, weight=1)
    
    def on_button_click(self, button):
        """Gérer les clics de boutons"""
        if button == 'C':
            self.expression = ""
            self.result_var.set("0")
        elif button == '=':
            try:
                # Remplacer les symboles par des opérateurs Python
                expr = self.expression.replace('×', '*').replace('÷', '/')
                result = eval(expr)
                self.result_var.set(str(result))
                self.expression = str(result)
            except:
                self.result_var.set("Erreur")
                self.expression = ""
        elif button in ['×', '÷', '+', '-']:
            if self.expression and self.expression[-1] not in ['×', '÷', '+', '-']:
                self.expression += button
                self.result_var.set(self.expression)
        elif button == '±':
            if self.expression:
                try:
                    current = float(self.result_var.get())
                    self.result_var.set(str(-current))
                    self.expression = str(-current)
                except:
                    pass
        elif button == '%':
            if self.expression:
                try:
                    current = float(self.result_var.get())
                    result = current / 100
                    self.result_var.set(str(result))
                    self.expression = str(result)
                except:
                    pass
        else:
            # Chiffres et point décimal
            if self.expression == "0":
                self.expression = button
            else:
                self.expression += button
            self.result_var.set(self.expression)
