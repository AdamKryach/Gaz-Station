# -*- coding: utf-8 -*-
"""
Module de Gestion des Factures
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os

class InvoiceManagement:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.setup_interface()
        self.load_invoices()
    
    def setup_interface(self):
        """Configuration de l'interface de gestion des factures"""
        # Notebook pour les sections
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet Nouvelle Facture
        new_invoice_frame = ttk.Frame(self.notebook)
        self.notebook.add(new_invoice_frame, text="Nouvelle Facture")
        self.setup_new_invoice(new_invoice_frame)
        
        # Onglet Liste des Factures
        list_frame = ttk.Frame(self.notebook)
        self.notebook.add(list_frame, text="Liste des Factures")
        self.setup_invoices_list(list_frame)
    
    def setup_new_invoice(self, parent):
        """Configuration de l'interface de nouvelle facture"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Section sélection client et période
        selection_frame = ttk.LabelFrame(main_frame, text="Sélection", padding=15)
        selection_frame.pack(fill='x', pady=(0, 10))
        
        # Ligne 1 - Client et Station
        row1 = ttk.Frame(selection_frame)
        row1.pack(fill='x', pady=(0, 10))
        
        ttk.Label(row1, text="Client *", style='Touch.TLabel').pack(side='left')
        self.invoice_client_var = tk.StringVar()
        self.invoice_client_combo = ttk.Combobox(row1, textvariable=self.invoice_client_var,
                                               width=35, font=('Arial', 11))
        self.invoice_client_combo.pack(side='left', padx=(10, 30))
        self.invoice_client_combo.bind('<KeyRelease>', self.on_invoice_client_search)
        self.invoice_client_combo.bind('<<ComboboxSelected>>', self.on_invoice_client_select)
        
        ttk.Label(row1, text="Station", style='Touch.TLabel').pack(side='left')
        self.invoice_station_var = tk.StringVar()
        self.invoice_station_combo = ttk.Combobox(row1, textvariable=self.invoice_station_var,
                                                state='readonly', width=25, font=('Arial', 11))
        self.invoice_station_combo.pack(side='left', padx=10)
        
        # Ligne 2 - Période
        row2 = ttk.Frame(selection_frame)
        row2.pack(fill='x', pady=(0, 10))
        
        ttk.Label(row2, text="Du:", style='Touch.TLabel').pack(side='left')
        self.date_from_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-01"))
        date_from_entry = ttk.Entry(row2, textvariable=self.date_from_var, width=15)
        date_from_entry.pack(side='left', padx=(10, 20))
        
        ttk.Label(row2, text="Au:", style='Touch.TLabel').pack(side='left')
        self.date_to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_to_entry = ttk.Entry(row2, textvariable=self.date_to_var, width=15)
        date_to_entry.pack(side='left', padx=(10, 30))
        
        ttk.Button(row2, text="Charger Transactions",
                  command=self.load_unbilled_transactions,
                  style='Touch.TButton').pack(side='left')
        
        # Section transactions non facturées
        transactions_frame = ttk.LabelFrame(main_frame, text="Transactions à Facturer", padding=10)
        transactions_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Liste des transactions
        columns = ('Sélect', 'Date', 'Véhicule', 'Carburant', 'Quantité', 'Prix/L', 'Montant')
        self.unbilled_tree = ttk.Treeview(transactions_frame, columns=columns, show='headings',
                                         style='Touch.Treeview', height=8)
        
        # Configuration des colonnes
        column_widths = [60, 120, 120, 100, 80, 80, 100]
        for i, col in enumerate(columns):
            self.unbilled_tree.heading(col, text=col)
            self.unbilled_tree.column(col, width=column_widths[i])
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(transactions_frame, orient='vertical', command=self.unbilled_tree.yview)
        self.unbilled_tree.configure(yscrollcommand=v_scroll.set)
        
        self.unbilled_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        
        # Bind pour sélection
        self.unbilled_tree.bind('<Button-1>', self.on_transaction_click)
        
        # Section résumé et création
        summary_frame = ttk.LabelFrame(main_frame, text="Résumé de la Facture", padding=15)
        summary_frame.pack(fill='x')
        
        # Résumé
        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill='x', pady=(0, 10))
        
        self.summary_labels = {
            'nb_transactions': ttk.Label(summary_grid, text="Transactions: 0", font=('Arial', 11)),
            'total_ht': ttk.Label(summary_grid, text="Total HT: 0.00 DH", font=('Arial', 11, 'bold')),
            'tva': ttk.Label(summary_grid, text="TVA (20%): 0.00 DH", font=('Arial', 11)),
            'total_ttc': ttk.Label(summary_grid, text="Total TTC: 0.00 DH", font=('Arial', 14, 'bold'), foreground='green')
        }
        
        self.summary_labels['nb_transactions'].grid(row=0, column=0, padx=20, sticky='w')
        self.summary_labels['total_ht'].grid(row=0, column=1, padx=20, sticky='w')
        self.summary_labels['tva'].grid(row=0, column=2, padx=20, sticky='w')
        self.summary_labels['total_ttc'].grid(row=0, column=3, padx=20, sticky='w')
        
        # Boutons
        btn_frame = ttk.Frame(summary_frame)
        btn_frame.pack(fill='x')
        
        ttk.Button(btn_frame, text="Tout Sélectionner",
                  command=self.select_all_transactions,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Tout Désélectionner",
                  command=self.deselect_all_transactions,
                  style='Touch.TButton').pack(side='left', padx=(0, 20))
        
        ttk.Button(btn_frame, text="Créer Facture",
                  command=self.create_invoice,
                  style='Touch.TButton').pack(side='right', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Aperçu",
                  command=self.preview_invoice,
                  style='Touch.TButton').pack(side='right')
        
        # Charger les données initiales
        self.load_invoice_clients()
        self.load_invoice_stations()
    
    def setup_invoices_list(self, parent):
        """Configuration de la liste des factures"""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Filtres
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Période:", style='Touch.TLabel').pack(side='left')
        self.filter_invoice_period = tk.StringVar(value="ce_mois")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.filter_invoice_period,
                                   values=["cette_semaine", "ce_mois", "trimestre", "tous"],
                                   state='readonly', width=15)
        period_combo.pack(side='left', padx=(5, 20))
        
        ttk.Label(filter_frame, text="Statut:", style='Touch.TLabel').pack(side='left')
        self.filter_invoice_status = tk.StringVar(value="toutes")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.filter_invoice_status,
                                   values=["toutes", "impayee", "payee", "annulee"],
                                   state='readonly', width=15)
        status_combo.pack(side='left', padx=(5, 20))
        
        ttk.Button(filter_frame, text="Filtrer",
                  command=self.load_invoices,
                  style='Touch.TButton').pack(side='left', padx=10)
        
        # Boutons d'action
        action_frame = ttk.Frame(filter_frame)
        action_frame.pack(side='right')
        
        ttk.Button(action_frame, text="Imprimer",
                  command=self.print_invoice,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="Modifier Statut",
                  command=self.change_invoice_status,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        ttk.Button(action_frame, text="Supprimer",
                  command=self.delete_invoice,
                  style='Touch.TButton').pack(side='left', padx=5)
        
        # Liste des factures
        list_container = ttk.Frame(main_frame)
        list_container.pack(fill='both', expand=True)
        
        columns = ('Numéro', 'Date', 'Client', 'Station', 'Montant HT', 'TVA', 'Montant TTC', 'Statut')
        self.invoices_tree = ttk.Treeview(list_container, columns=columns, show='headings',
                                         style='Touch.Treeview')
        
        # Configuration des colonnes
        column_widths = [100, 100, 200, 150, 100, 80, 100, 80]
        for i, col in enumerate(columns):
            self.invoices_tree.heading(col, text=col)
            self.invoices_tree.column(col, width=column_widths[i])
        
        # Scrollbars
        v_scroll_inv = ttk.Scrollbar(list_container, orient='vertical', command=self.invoices_tree.yview)
        h_scroll_inv = ttk.Scrollbar(list_container, orient='horizontal', command=self.invoices_tree.xview)
        
        self.invoices_tree.configure(yscrollcommand=v_scroll_inv.set, xscrollcommand=h_scroll_inv.set)
        
        self.invoices_tree.pack(side='left', fill='both', expand=True)
        v_scroll_inv.pack(side='right', fill='y')
        h_scroll_inv.pack(side='bottom', fill='x')
    
    def load_invoice_clients(self):
        """Charger les clients pour la facturation"""
        try:
            query = """
                SELECT c.id, c.nom, c.prenom, c.entreprise, c.type_client
                FROM clients c 
                WHERE c.statut = 'actif'
                ORDER BY c.nom, c.prenom
            """
            clients = self.db_manager.execute_query(query, use_cache=True, cache_timeout=300, table="clients")
            
            client_list = []
            for client in clients:
                client_id, nom, prenom, entreprise, type_client = client
                
                if entreprise and type_client == 'entreprise':
                    display_name = f"{client_id} - {entreprise}"
                else:
                    display_name = f"{client_id} - {nom} {prenom or ''}"
                
                client_list.append(display_name.strip())
            
            self.invoice_client_combo['values'] = client_list
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des clients: {str(e)}")
    
    def load_invoice_stations(self):
        """Charger les stations"""
        try:
            stations = self.db_manager.execute_query("SELECT id, nom FROM stations ORDER BY nom", use_cache=True, cache_timeout=600, table="stations")
            station_list = ["toutes"] + [f"{station[0]} - {station[1]}" for station in stations]
            self.invoice_station_combo['values'] = station_list
            self.invoice_station_combo.current(0)  # Sélectionner "toutes"
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des stations: {str(e)}")
    
    def on_invoice_client_search(self, event):
        """Recherche client en temps réel"""
        search_term = self.invoice_client_combo.get().lower()
        if len(search_term) < 2:
            return
        
        try:
            query = """
                SELECT c.id, c.nom, c.prenom, c.entreprise, c.type_client
                FROM clients c 
                WHERE c.statut = 'actif' AND (
                    LOWER(c.nom) LIKE ? OR 
                    LOWER(c.prenom) LIKE ? OR 
                    LOWER(c.entreprise) LIKE ?
                )
                ORDER BY c.nom, c.prenom
                LIMIT 10
            """
            search_pattern = f"%{search_term}%"
            clients = self.db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern), use_cache=False, table="clients")
            
            client_list = []
            for client in clients:
                client_id, nom, prenom, entreprise, type_client = client
                
                if entreprise and type_client == 'entreprise':
                    display_name = f"{client_id} - {entreprise}"
                else:
                    display_name = f"{client_id} - {nom} {prenom or ''}"
                
                client_list.append(display_name.strip())
            
            self.invoice_client_combo['values'] = client_list
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {str(e)}")
    
    def on_invoice_client_select(self, event):
        """Client sélectionné pour facturation"""
        # Charger automatiquement les transactions non facturées
        self.load_unbilled_transactions()
    
    def load_unbilled_transactions(self):
        """Charger les transactions non facturées pour le client sélectionné"""
        try:
            # Vider la liste
            for item in self.unbilled_tree.get_children():
                self.unbilled_tree.delete(item)
            
            client_text = self.invoice_client_combo.get()
            if not client_text or ' - ' not in client_text:
                messagebox.showwarning("Attention", "Veuillez sélectionner un client")
                return
            
            client_id = int(client_text.split(' - ')[0])
            
            # Construire la requête
            where_conditions = [
                "t.client_id = ?",
                "t.type_paiement = 'credit'",  # Seulement les transactions à crédit
                "t.id NOT IN (SELECT DISTINCT lf.transaction_id FROM lignes_facture lf WHERE lf.transaction_id IS NOT NULL)"
            ]
            
            params = [client_id]
            
            # Filtres de date
            date_from = self.date_from_var.get()
            date_to = self.date_to_var.get()
            
            if date_from:
                where_conditions.append("DATE(t.date_transaction) >= DATE(?)")
                params.append(date_from)
            
            if date_to:
                where_conditions.append("DATE(t.date_transaction) <= DATE(?)")
                params.append(date_to)
            
            # Filtre station
            station_text = self.invoice_station_var.get()
            if station_text and station_text != "toutes" and ' - ' in station_text:
                station_id = int(station_text.split(' - ')[0])
                where_conditions.append("t.station_id = ?")
                params.append(station_id)
            
            where_clause = " AND ".join(where_conditions)
            
            query = f"""
                SELECT 
                    t.id, t.date_transaction,
                    COALESCE(v.immatriculation, '-') as vehicule,
                    car.nom as carburant,
                    t.quantite, t.prix_unitaire, t.montant_total
                FROM transactions t
                LEFT JOIN vehicules v ON t.vehicule_id = v.id
                JOIN carburants car ON t.carburant_id = car.id
                WHERE {where_clause}
                ORDER BY t.date_transaction DESC
            """
            
            transactions = self.db_manager.execute_query(query, params)
            
            self.selected_transactions = set()  # Pour stocker les IDs sélectionnés
            
            for transaction in transactions:
                date_str = transaction[1][:10] if transaction[1] else ''
                
                values = (
                    '☐',  # Checkbox vide
                    date_str,
                    transaction[2],  # Véhicule
                    transaction[3],  # Carburant
                    f"{transaction[4]:.1f}L",
                    f"{transaction[5]:.2f}",
                    f"{transaction[6]:.2f} DH"
                )
                
                item_id = self.unbilled_tree.insert('', 'end', values=values)
                # Stocker l'ID de la transaction dans les tags
                self.unbilled_tree.set(item_id, '#0', transaction[0])
            
            self.update_invoice_summary()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des transactions: {str(e)}")
    
    def on_transaction_click(self, event):
        """Gérer le clic sur une transaction pour la sélectionner/désélectionner"""
        item = self.unbilled_tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Vérifier si c'est la colonne de sélection
        column = self.unbilled_tree.identify_column(event.x, event.y)
        if column == '#1':  # Première colonne (sélection)
            transaction_id = int(self.unbilled_tree.item(item, 'text') or self.unbilled_tree.set(item, '#0'))
            
            if transaction_id in self.selected_transactions:
                # Désélectionner
                self.selected_transactions.remove(transaction_id)
                values = list(self.unbilled_tree.item(item)['values'])
                values[0] = '☐'
                self.unbilled_tree.item(item, values=values)
            else:
                # Sélectionner
                self.selected_transactions.add(transaction_id)
                values = list(self.unbilled_tree.item(item)['values'])
                values[0] = '☑'
                self.unbilled_tree.item(item, values=values)
            
            self.update_invoice_summary()
    
    def select_all_transactions(self):
        """Sélectionner toutes les transactions"""
        self.selected_transactions.clear()
        
        for item in self.unbilled_tree.get_children():
            transaction_id = int(self.unbilled_tree.set(item, '#0'))
            self.selected_transactions.add(transaction_id)
            
            values = list(self.unbilled_tree.item(item)['values'])
            values[0] = '☑'
            self.unbilled_tree.item(item, values=values)
        
        self.update_invoice_summary()
    
    def deselect_all_transactions(self):
        """Désélectionner toutes les transactions"""
        self.selected_transactions.clear()
        
        for item in self.unbilled_tree.get_children():
            values = list(self.unbilled_tree.item(item)['values'])
            values[0] = '☐'
            self.unbilled_tree.item(item, values=values)
        
        self.update_invoice_summary()
    
    def update_invoice_summary(self):
        """Mettre à jour le résumé de la facture"""
        if not hasattr(self, 'selected_transactions'):
            return
        
        nb_selected = len(self.selected_transactions)
        total_ht = 0
        
        # Calculer le total des transactions sélectionnées
        for item in self.unbilled_tree.get_children():
            transaction_id = int(self.unbilled_tree.set(item, '#0'))
            if transaction_id in self.selected_transactions:
                values = self.unbilled_tree.item(item)['values']
                montant_str = values[6].replace(' DH', '')
                total_ht += float(montant_str)
        
        tva = total_ht * 0.20  # TVA 20%
        total_ttc = total_ht + tva
        
        # Mettre à jour les labels
        self.summary_labels['nb_transactions'].config(text=f"Transactions: {nb_selected}")
        self.summary_labels['total_ht'].config(text=f"Total HT: {total_ht:.2f} DH")
        self.summary_labels['tva'].config(text=f"TVA (20%): {tva:.2f} DH")
        self.summary_labels['total_ttc'].config(text=f"Total TTC: {total_ttc:.2f} DH")
    
    def preview_invoice(self):
        """Aperçu de la facture"""
        if not hasattr(self, 'selected_transactions') or not self.selected_transactions:
            messagebox.showwarning("Attention", "Aucune transaction sélectionnée")
            return
        
        messagebox.showinfo("Aperçu", "Fonctionnalité d'aperçu à implémenter")
    
    def create_invoice(self):
        """Créer une nouvelle facture"""
        try:
            if not hasattr(self, 'selected_transactions') or not self.selected_transactions:
                messagebox.showwarning("Attention", "Aucune transaction sélectionnée")
                return
            
            client_text = self.invoice_client_combo.get()
            if not client_text or ' - ' not in client_text:
                messagebox.showwarning("Attention", "Veuillez sélectionner un client")
                return
            
            client_id = int(client_text.split(' - ')[0])
            
            # Déterminer la station (première transaction si plusieurs)
            first_transaction = list(self.selected_transactions)[0]
            station_query = "SELECT station_id FROM transactions WHERE id = ?"
            station_result = self.db_manager.execute_query(station_query, (first_transaction,))
            station_id = station_result[0][0] if station_result else 1
            
            # Calculer les montants
            total_ht = 0
            for item in self.unbilled_tree.get_children():
                transaction_id = int(self.unbilled_tree.set(item, '#0'))
                if transaction_id in self.selected_transactions:
                    values = self.unbilled_tree.item(item)['values']
                    montant_str = values[6].replace(' DH', '')
                    total_ht += float(montant_str)
            
            tva = total_ht * 0.20
            total_ttc = total_ht + tva
            
            # Générer le numéro de facture
            today = datetime.now()
            invoice_number = f"FACT-{today.strftime('%Y%m%d')}-{today.strftime('%H%M%S')}"
            
            # Insérer la facture
            invoice_query = """
                INSERT INTO factures (
                    numero_facture, client_id, station_id, date_facture,
                    montant_ht, tva, montant_ttc, statut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'impayee')
            """
            
            invoice_params = (
                invoice_number, client_id, station_id, today.strftime('%Y-%m-%d'),
                total_ht, tva, total_ttc
            )
            
            invoice_id = self.db_manager.execute_insert(invoice_query, invoice_params, table="factures")
            
            # Insérer les lignes de facture
            line_query = """
                INSERT INTO lignes_facture (
                    facture_id, transaction_id, description, quantite, prix_unitaire, montant
                ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            for item in self.unbilled_tree.get_children():
                transaction_id = int(self.unbilled_tree.set(item, '#0'))
                if transaction_id in self.selected_transactions:
                    values = self.unbilled_tree.item(item)['values']
                    
                    # Récupérer les détails de la transaction
                    trans_query = """
                        SELECT car.nom, t.quantite, t.prix_unitaire, t.montant_total
                        FROM transactions t
                        JOIN carburants car ON t.carburant_id = car.id
                        WHERE t.id = ?
                    """
                    trans_result = self.db_manager.execute_query(trans_query, (transaction_id,), use_cache=False, table="transactions")
                    
                    if trans_result:
                        carburant, quantite, prix_unit, montant = trans_result[0]
                        description = f"{carburant} - {values[2]}"  # Carburant + véhicule
                        
                        self.db_manager.execute_insert(line_query, (
                            invoice_id, transaction_id, description,
                            quantite, prix_unit, montant
                        ), table="lignes_facture")
            
            messagebox.showinfo("Succès", f"Facture créée avec succès!\nNuméro: {invoice_number}")
            
            # Recharger les données
            self.load_unbilled_transactions()
            self.load_invoices()
            
            # Proposer d'imprimer
            if messagebox.askyesno("Impression", "Voulez-vous imprimer la facture maintenant?"):
                self.print_invoice_by_id(invoice_id)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la création de la facture: {str(e)}")
    
    def load_invoices(self):
        """Charger la liste des factures"""
        try:
            # Vider la liste
            for item in self.invoices_tree.get_children():
                self.invoices_tree.delete(item)
            
            # Construire la requête selon les filtres
            period = self.filter_invoice_period.get()
            status = self.filter_invoice_status.get()
            
            where_conditions = []
            
            # Filtre période
            if period == "cette_semaine":
                where_conditions.append("DATE(f.date_facture) >= DATE('now', '-7 days')")
            elif period == "ce_mois":
                where_conditions.append("DATE(f.date_facture) >= DATE('now', 'start of month')")
            elif period == "trimestre":
                where_conditions.append("DATE(f.date_facture) >= DATE('now', '-3 months')")
            
            # Filtre statut
            if status != "toutes":
                where_conditions.append(f"f.statut = '{status}'")
            
            where_clause = " AND ".join(where_conditions)
            if where_clause:
                where_clause = "WHERE " + where_clause
            
            query = f"""
                SELECT 
                    f.id, f.numero_facture, f.date_facture,
                    CASE 
                        WHEN c.type_client = 'entreprise' AND c.entreprise IS NOT NULL 
                        THEN c.entreprise 
                        ELSE c.nom || ' ' || COALESCE(c.prenom, '')
                    END as client,
                    s.nom as station,
                    f.montant_ht, f.tva, f.montant_ttc, f.statut
                FROM factures f
                JOIN clients c ON f.client_id = c.id
                JOIN stations s ON f.station_id = s.id
                {where_clause}
                ORDER BY f.date_facture DESC
            """
            
            invoices = self.db_manager.execute_query(query, use_cache=True, cache_timeout=60, table="factures")
            
            for invoice in invoices:
                values = (
                    invoice[1],  # Numéro
                    invoice[2],  # Date
                    invoice[3],  # Client
                    invoice[4],  # Station
                    f"{invoice[5]:.2f}",  # HT
                    f"{invoice[6]:.2f}",  # TVA
                    f"{invoice[7]:.2f}",  # TTC
                    invoice[8]   # Statut
                )
                
                item_id = self.invoices_tree.insert('', 'end', values=values)
                # Stocker l'ID de la facture
                self.invoices_tree.set(item_id, '#0', invoice[0])
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des factures: {str(e)}")
    
    def print_invoice(self):
        """Imprimer la facture sélectionnée"""
        selection = self.invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture")
            return
        
        item = selection[0]
        invoice_id = int(self.invoices_tree.set(item, '#0'))
        self.print_invoice_by_id(invoice_id)
    
    def print_invoice_by_id(self, invoice_id):
        """Imprimer une facture par son ID"""
        try:
            # Demander où sauvegarder le PDF
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Enregistrer la facture"
            )
            
            if not filename:
                return
            
            # Récupérer les données de la facture
            invoice_query = """
                SELECT f.*, c.nom, c.prenom, c.entreprise, c.adresse, c.ice,
                       s.nom as station_nom, s.adresse as station_adresse
                FROM factures f
                JOIN clients c ON f.client_id = c.id
                JOIN stations s ON f.station_id = s.id
                WHERE f.id = ?
            """
            
            invoice_data = self.db_manager.execute_query(invoice_query, (invoice_id,))
            if not invoice_data:
                messagebox.showerror("Erreur", "Facture non trouvée")
                return
            
            invoice = invoice_data[0]
            
            # Récupérer les lignes de facture
            lines_query = """
                SELECT lf.description, lf.quantite, lf.prix_unitaire, lf.montant
                FROM lignes_facture lf
                WHERE lf.facture_id = ?
                ORDER BY lf.id
            """
            
            lines = self.db_manager.execute_query(lines_query, (invoice_id,))
            
            # Créer le PDF
            self.generate_pdf_invoice(filename, invoice, lines)
            
            messagebox.showinfo("Succès", f"Facture enregistrée: {filename}")
            
            # Ouvrir le PDF
            if messagebox.askyesno("Ouverture", "Voulez-vous ouvrir le fichier PDF?"):
                os.startfile(filename)
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'impression: {str(e)}")
    
    def generate_pdf_invoice(self, filename, invoice_data, lines_data):
        """Générer le PDF de la facture"""
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # En-tête entreprise
            company_style = ParagraphStyle(
                'CompanyHeader',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centré
            )
            
            story.append(Paragraph("STATIONS-SERVICE MANAGEMENT", company_style))
            story.append(Paragraph("Système de Gestion - Facturation", styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Informations facture
            invoice_info = f"""
            <b>FACTURE N° {invoice_data[1]}</b><br/>
            Date: {invoice_data[3]}<br/>
            Station: {invoice_data[15]}<br/>
            """
            
            story.append(Paragraph(invoice_info, styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Informations client
            client_name = invoice_data[10] if invoice_data[10] else f"{invoice_data[9]} {invoice_data[11] or ''}"
            client_info = f"""
            <b>Facturé à:</b><br/>
            {client_name}<br/>
            {invoice_data[12] or ''}<br/>
            {f'ICE: {invoice_data[13]}' if invoice_data[13] else ''}
            """
            
            story.append(Paragraph(client_info, styles['Normal']))
            story.append(Spacer(1, 30))
            
            # Tableau des lignes
            table_data = [['Description', 'Quantité', 'Prix Unit. (DH)', 'Montant (DH)']]
            
            for line in lines_data:
                table_data.append([
                    line[0],  # Description
                    f"{line[1]:.1f}L" if line[1] else '',
                    f"{line[2]:.2f}",
                    f"{line[3]:.2f}"
                ])
            
            # Lignes de totaux
            table_data.append(['', '', 'Total HT:', f"{invoice_data[4]:.2f}"])
            table_data.append(['', '', 'TVA (20%):', f"{invoice_data[5]:.2f}"])
            table_data.append(['', '', '<b>Total TTC:</b>', f"<b>{invoice_data[6]:.2f}</b>"])
            
            table = Table(table_data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -3), (-1, -1), colors.beige),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 30))
            
            # Pied de page
            footer = f"""
            <br/><br/>
            Statut: <b>{invoice_data[8].upper()}</b><br/>
            Date de création: {datetime.now().strftime('%d/%m/%Y à %H:%M')}
            """
            story.append(Paragraph(footer, styles['Normal']))
            
            doc.build(story)
            
        except Exception as e:
            raise Exception(f"Erreur génération PDF: {str(e)}")
    
    def change_invoice_status(self):
        """Modifier le statut d'une facture"""
        selection = self.invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture")
            return
        
        # Dialogue pour choisir le nouveau statut
        InvoiceStatusDialog(self.parent, self.db_manager, 
                          int(self.invoices_tree.set(selection[0], '#0')),
                          self.load_invoices)
    
    def delete_invoice(self):
        """Supprimer une facture"""
        selection = self.invoices_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une facture")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette facture?"):
            try:
                invoice_id = int(self.invoices_tree.set(selection[0], '#0'))
                
                # Supprimer les lignes de facture
                self.db_manager.execute_update("DELETE FROM lignes_facture WHERE facture_id = ?", (invoice_id,))
                
                # Supprimer la facture
                self.db_manager.execute_update("DELETE FROM factures WHERE id = ?", (invoice_id,))
                
                messagebox.showinfo("Succès", "Facture supprimée avec succès")
                self.load_invoices()
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

class InvoiceStatusDialog:
    def __init__(self, parent, db_manager, invoice_id, callback):
        self.db_manager = db_manager
        self.invoice_id = invoice_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier Statut Facture")
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        self.dialog.focus()
    
    def setup_dialog(self):
        """Configuration de la fenêtre de dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Nouveau statut:", font=('Arial', 12)).pack(pady=(0, 10))
        
        self.status_var = tk.StringVar()
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var,
                                   values=['impayee', 'payee', 'annulee'],
                                   state='readonly', width=20)
        status_combo.pack(pady=(0, 20))
        status_combo.current(0)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="Confirmer", command=self.save_status).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def save_status(self):
        """Enregistrer le nouveau statut"""
        try:
            new_status = self.status_var.get()
            
            update_query = "UPDATE factures SET statut = ? WHERE id = ?"
            self.db_manager.execute_update(update_query, (new_status, self.invoice_id), table="factures")
            
            messagebox.showinfo("Succès", "Statut modifié avec succès")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")
