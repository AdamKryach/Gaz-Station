# -*- coding: utf-8 -*-
"""
Module de Gestion des Paiements d'Avance
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

class PaymentManagement:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.setup_interface()
        self.load_payments()
    
    def setup_interface(self):
        """Configuration de l'interface de gestion des paiements"""
        # Frame principal avec deux sections
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill='both', expand=True)
        
        # Section haut - Nouveau paiement
        top_frame = ttk.LabelFrame(main_frame, text="Nouveau Paiement d'Avance", padding=20)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        self.setup_payment_form(top_frame)
        
        # Section bas - Liste des paiements
        bottom_frame = ttk.LabelFrame(main_frame, text="Paiements d'Avance", padding=10)
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.setup_payments_list(bottom_frame)
    
    def setup_payment_form(self, parent):
        """Configuration du formulaire de nouveau paiement"""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill='x')
        
        # Variables du formulaire
        self.payment_vars = {}
        
        # Ligne 1 - Client et Montant
        row1_frame = ttk.Frame(form_frame)
        row1_frame.pack(fill='x', pady=(0, 10))
        
        # Client
        ttk.Label(row1_frame, text="Client *", style='Touch.TLabel').pack(side='left')
        self.payment_vars['client'] = tk.StringVar()
        self.client_combo = ttk.Combobox(row1_frame, textvariable=self.payment_vars['client'],
                                        width=30, font=('Arial', 11))
        self.client_combo.pack(side='left', padx=(10, 20))
        self.client_combo.bind('<KeyRelease>', self.on_client_search)
        
        # Montant
        ttk.Label(row1_frame, text="Montant (DH) *", style='Touch.TLabel').pack(side='left')
        self.payment_vars['montant'] = tk.StringVar()
        montant_entry = ttk.Entry(row1_frame, textvariable=self.payment_vars['montant'],
                                 width=15, font=('Arial', 11))
        montant_entry.pack(side='left', padx=10)
        
        # Ligne 2 - Mode de paiement et Référence
        row2_frame = ttk.Frame(form_frame)
        row2_frame.pack(fill='x', pady=(0, 10))
        
        # Mode de paiement
        ttk.Label(row2_frame, text="Mode de Paiement *", style='Touch.TLabel').pack(side='left')
        self.payment_vars['mode_paiement'] = tk.StringVar(value='especes')
        mode_combo = ttk.Combobox(row2_frame, textvariable=self.payment_vars['mode_paiement'],
                                 values=['especes', 'cheque', 'virement', 'carte'],
                                 state='readonly', width=15, font=('Arial', 11))
        mode_combo.pack(side='left', padx=(10, 20))
        
        # Référence
        ttk.Label(row2_frame, text="Référence", style='Touch.TLabel').pack(side='left')
        self.payment_vars['reference'] = tk.StringVar()
        ref_entry = ttk.Entry(row2_frame, textvariable=self.payment_vars['reference'],
                             width=20, font=('Arial', 11))
        ref_entry.pack(side='left', padx=10)
        
        # Ligne 3 - Notes
        row3_frame = ttk.Frame(form_frame)
        row3_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(row3_frame, text="Notes:", style='Touch.TLabel').pack(anchor='w')
        self.payment_vars['notes'] = tk.StringVar()
        notes_entry = ttk.Entry(row3_frame, textvariable=self.payment_vars['notes'],
                               font=('Arial', 11))
        notes_entry.pack(fill='x', pady=(5, 0))
        
        # Boutons
        btn_frame = ttk.Frame(form_frame)
        btn_frame.pack(fill='x', pady=(15, 0))
        
        ttk.Button(btn_frame, text="Enregistrer Paiement",
                  command=self.save_payment,
                  style='Touch.TButton').pack(side='left', padx=(0, 10))
        
        ttk.Button(btn_frame, text="Effacer",
                  command=self.clear_form,
                  style='Touch.TButton').pack(side='left')
        
        # Charger les clients
        self.load_clients()
    
    def setup_payments_list(self, parent):
        """Configuration de la liste des paiements"""
        # Filtres
        filter_frame = ttk.Frame(parent)
        filter_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(filter_frame, text="Période:", style='Touch.TLabel').pack(side='left')
        self.filter_period = tk.StringVar(value="ce_mois")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.filter_period,
                                   values=["aujourd_hui", "cette_semaine", "ce_mois", "tous"],
                                   state='readonly', width=15)
        period_combo.pack(side='left', padx=(5, 20))
        
        ttk.Label(filter_frame, text="Statut:", style='Touch.TLabel').pack(side='left')
        self.filter_status = tk.StringVar(value="actif")
        status_combo = ttk.Combobox(filter_frame, textvariable=self.filter_status,
                                   values=["tous", "actif", "utilise"],
                                   state='readonly', width=15)
        status_combo.pack(side='left', padx=(5, 20))
        
        ttk.Button(filter_frame, text="Filtrer",
                  command=self.load_payments,
                  style='Touch.TButton').pack(side='left', padx=10)
        
        # Boutons d'action
        ttk.Button(filter_frame, text="Modifier",
                  command=self.edit_payment,
                  style='Touch.TButton').pack(side='right', padx=(0, 10))
        
        ttk.Button(filter_frame, text="Supprimer",
                  command=self.delete_payment,
                  style='Touch.TButton').pack(side='right')
        
        # Liste des paiements
        list_container = ttk.Frame(parent)
        list_container.pack(fill='both', expand=True)
        
        columns = ('ID', 'Date', 'Client', 'Montant', 'Mode', 'Référence', 'Statut', 'Notes')
        self.payments_tree = ttk.Treeview(list_container, columns=columns, show='headings',
                                         style='Touch.Treeview')
        
        # Configuration des colonnes
        column_widths = [50, 120, 200, 100, 100, 120, 80, 150]
        for i, col in enumerate(columns):
            self.payments_tree.heading(col, text=col)
            self.payments_tree.column(col, width=column_widths[i])
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient='vertical', 
                                   command=self.payments_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient='horizontal', 
                                   command=self.payments_tree.xview)
        
        self.payments_tree.configure(yscrollcommand=v_scrollbar.set, 
                                    xscrollcommand=h_scrollbar.set)
        
        # Placement
        self.payments_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Résumé des paiements
        summary_frame = ttk.LabelFrame(parent, text="Résumé", padding=10)
        summary_frame.pack(fill='x', pady=(10, 0))
        
        summary_grid = ttk.Frame(summary_frame)
        summary_grid.pack(fill='x')
        
        # Labels pour le résumé
        self.summary_labels = {
            'total_paiements': ttk.Label(summary_grid, text="Total Paiements: 0 DH", 
                                        font=('Arial', 11, 'bold')),
            'paiements_actifs': ttk.Label(summary_grid, text="Paiements Actifs: 0 DH", 
                                         font=('Arial', 11)),
            'nombre_paiements': ttk.Label(summary_grid, text="Nombre: 0", 
                                         font=('Arial', 11))
        }
        
        self.summary_labels['total_paiements'].grid(row=0, column=0, padx=20, pady=5, sticky='w')
        self.summary_labels['paiements_actifs'].grid(row=0, column=1, padx=20, pady=5, sticky='w')
        self.summary_labels['nombre_paiements'].grid(row=0, column=2, padx=20, pady=5, sticky='w')
    
    def load_clients(self):
        """Charger les clients actifs"""
        try:
            query = """
                SELECT c.id, c.nom, c.prenom, c.entreprise, c.type_client, c.solde_actuel
                FROM clients c 
                WHERE c.statut = 'actif'
                ORDER BY c.nom, c.prenom
            """
            # Utiliser le cache avec un timeout court car les soldes peuvent changer
            clients = self.db_manager.execute_query(query, use_cache=True, cache_timeout=60)
            
            client_list = []
            for client in clients:
                client_id, nom, prenom, entreprise, type_client, solde = client
                
                if entreprise and type_client == 'entreprise':
                    display_name = f"{client_id} - {entreprise} ({nom} {prenom or ''}) [Solde: {solde:.2f} DH]"
                else:
                    display_name = f"{client_id} - {nom} {prenom or ''} [Solde: {solde:.2f} DH]"
                
                client_list.append(display_name.strip())
            
            self.client_combo['values'] = client_list
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des clients: {str(e)}")
    
    def on_client_search(self, event):
        """Filtrer les clients en temps réel"""
        search_term = self.client_combo.get().lower()
        if len(search_term) < 2:
            return
        
        try:
            query = """
                SELECT c.id, c.nom, c.prenom, c.entreprise, c.type_client, c.solde_actuel
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
            clients = self.db_manager.execute_query(query, (search_pattern, search_pattern, search_pattern), use_cache=True, cache_timeout=30, table="clients")
            
            client_list = []
            for client in clients:
                client_id, nom, prenom, entreprise, type_client, solde = client
                
                if entreprise and type_client == 'entreprise':
                    display_name = f"{client_id} - {entreprise} ({nom} {prenom or ''}) [Solde: {solde:.2f} DH]"
                else:
                    display_name = f"{client_id} - {nom} {prenom or ''} [Solde: {solde:.2f} DH]"
                
                client_list.append(display_name.strip())
            
            self.client_combo['values'] = client_list
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {str(e)}")
    
    def save_payment(self):
        """Enregistrer un nouveau paiement d'avance"""
        try:
            # Validation simplifiée
            if not all([
                self.payment_vars['client'].get(),
                self.payment_vars['montant'].get(),
                self.payment_vars['mode_paiement'].get()
            ]):
                messagebox.showwarning("Attention", "Veuillez remplir les champs obligatoires")
                return
            
            # Extraction de l'ID client
            client_text = self.payment_vars['client'].get()
            if ' - ' not in client_text:
                messagebox.showwarning("Attention", "Veuillez sélectionner un client valide")
                return
            
            client_id = int(client_text.split(' - ')[0])
            
            # Validation du montant
            try:
                montant = float(self.payment_vars['montant'].get())
                if montant <= 0:
                    messagebox.showerror("Erreur", "Le montant doit être positif")
                    return
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide")
                return
            
            # Insertion du paiement
            query = """
                INSERT INTO paiements_avance (
                    client_id, montant, mode_paiement, reference_paiement, notes
                ) VALUES (?, ?, ?, ?, ?)
            """
            
            params = (
                client_id,
                montant,
                self.payment_vars['mode_paiement'].get(),
                self.payment_vars['reference'].get().strip() or None,
                self.payment_vars['notes'].get().strip() or None
            )
            
            # Utiliser le paramètre table pour invalider automatiquement le cache
            payment_id = self.db_manager.execute_insert(query, params, table='paiements_avance')
            
            # Mise à jour du solde client (ajouter le montant)
            update_query = """
                UPDATE clients 
                SET solde_actuel = solde_actuel + ? 
                WHERE id = ?
            """
            # Utiliser le paramètre table pour invalider automatiquement le cache
            self.db_manager.execute_update(update_query, (montant, client_id), table='clients')
            
            messagebox.showinfo("Succès", f"Paiement d'avance enregistré avec succès (ID: {payment_id})")
            
            # Effacer le formulaire et recharger
            self.clear_form()
            self.load_payments()
            self.load_clients()  # Recharger pour mettre à jour les soldes
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
    
    def clear_form(self):
        """Effacer le formulaire"""
        for var in self.payment_vars.values():
            var.set('')
        
        # Valeurs par défaut
        self.payment_vars['mode_paiement'].set('especes')
    
    def load_payments(self):
        """Charger la liste des paiements selon les filtres"""
        try:
            # Vider la liste actuelle
            for item in self.payments_tree.get_children():
                self.payments_tree.delete(item)
            
            # Construire la requête selon les filtres
            period = self.filter_period.get()
            status = self.filter_status.get()
            
            where_conditions = []
            
            # Filtre période
            if period == "aujourd_hui":
                where_conditions.append("DATE(p.date_paiement) = DATE('now')")
            elif period == "cette_semaine":
                where_conditions.append("DATE(p.date_paiement) >= DATE('now', '-7 days')")
            elif period == "ce_mois":
                where_conditions.append("DATE(p.date_paiement) >= DATE('now', 'start of month')")
            
            # Filtre statut
            if status != "tous":
                where_conditions.append(f"p.statut = '{status}'")
            
            where_clause = " AND ".join(where_conditions)
            if where_clause:
                where_clause = "WHERE " + where_clause
            
            query = f"""
                SELECT 
                    p.id, p.date_paiement, 
                    CASE 
                        WHEN c.type_client = 'entreprise' AND c.entreprise IS NOT NULL 
                        THEN c.entreprise 
                        ELSE c.nom || ' ' || COALESCE(c.prenom, '')
                    END as client,
                    p.montant, p.mode_paiement, p.reference_paiement, p.statut, p.notes
                FROM paiements_avance p
                JOIN clients c ON p.client_id = c.id
                {where_clause}
                ORDER BY p.date_paiement DESC
            """
            
            # Utiliser le cache avec un timeout court pour les paiements récents
            payments = self.db_manager.execute_query(query, use_cache=True, cache_timeout=30)
            
            total_montant = 0
            actif_montant = 0
            nombre_paiements = len(payments)
            
            for payment in payments:
                # Formatage de la date
                date_str = payment[1][:16] if payment[1] else ''
                
                values = (
                    payment[0],  # ID
                    date_str,    # Date
                    payment[2],  # Client
                    f"{payment[3]:.2f} DH",  # Montant
                    payment[4],  # Mode
                    payment[5] or '-',  # Référence
                    payment[6],  # Statut
                    payment[7] or '-'   # Notes
                )
                
                self.payments_tree.insert('', 'end', values=values)
                
                # Calculs pour le résumé
                total_montant += payment[3]
                if payment[6] == 'actif':
                    actif_montant += payment[3]
            
            # Mise à jour du résumé
            self.summary_labels['total_paiements'].config(
                text=f"Total Paiements: {total_montant:.2f} DH"
            )
            self.summary_labels['paiements_actifs'].config(
                text=f"Paiements Actifs: {actif_montant:.2f} DH"
            )
            self.summary_labels['nombre_paiements'].config(
                text=f"Nombre: {nombre_paiements}"
            )
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des paiements: {str(e)}")
    
    def edit_payment(self):
        """Modifier un paiement sélectionné"""
        selection = self.payments_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un paiement")
            return
        
        item = selection[0]
        payment_id = self.payments_tree.item(item)['values'][0]
        
        EditPaymentDialog(self.parent, self.db_manager, payment_id, self.load_payments)
    
    def delete_payment(self):
        """Supprimer un paiement"""
        selection = self.payments_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner un paiement")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce paiement ?"):
            try:
                item = selection[0]
                payment_id = self.payments_tree.item(item)['values'][0]
                
                # Récupérer les détails du paiement pour ajuster le solde
                query = """
                    SELECT client_id, montant, statut
                    FROM paiements_avance 
                    WHERE id = ?
                """
                # Ne pas utiliser le cache pour cette vérification critique
                result = self.db_manager.execute_query(query, (payment_id,), use_cache=False)
                
                if result:
                    client_id, montant, statut = result[0]
                    
                    # Supprimer le paiement
                    delete_query = "DELETE FROM paiements_avance WHERE id = ?"
                    # Utiliser le paramètre table pour invalider automatiquement le cache
                    self.db_manager.execute_update(delete_query, (payment_id,), table='paiements_avance')
                    
                    # Ajuster le solde client si le paiement était actif
                    if statut == 'actif':
                        update_query = """
                            UPDATE clients 
                            SET solde_actuel = solde_actuel - ? 
                            WHERE id = ?
                        """
                        # Utiliser le paramètre table pour invalider automatiquement le cache
                        self.db_manager.execute_update(update_query, (montant, client_id), table='clients')
                    
                    messagebox.showinfo("Succès", "Paiement supprimé avec succès")
                    self.load_payments()
                    self.load_clients()  # Recharger pour mettre à jour les soldes
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")

class EditPaymentDialog:
    def __init__(self, parent, db_manager, payment_id, callback):
        self.db_manager = db_manager
        self.payment_id = payment_id
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier Paiement d'Avance")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_dialog()
        self.load_payment_data()
        
        self.dialog.focus()
    
    def setup_dialog(self):
        """Configuration de la fenêtre de dialogue"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Variables
        self.edit_vars = {}
        
        # Champs modifiables
        fields = [
            ('montant', 'Montant (DH)'),
            ('mode_paiement', 'Mode de Paiement'),
            ('reference_paiement', 'Référence'),
            ('statut', 'Statut'),
            ('notes', 'Notes')
        ]
        
        row = 0
        for field_id, label in fields:
            ttk.Label(main_frame, text=label).grid(row=row, column=0, sticky='w', pady=5)
            
            self.edit_vars[field_id] = tk.StringVar()
            
            if field_id == 'mode_paiement':
                widget = ttk.Combobox(main_frame, textvariable=self.edit_vars[field_id],
                                     values=['especes', 'cheque', 'virement', 'carte'],
                                     state='readonly', width=25)
            elif field_id == 'statut':
                widget = ttk.Combobox(main_frame, textvariable=self.edit_vars[field_id],
                                     values=['actif', 'utilise'],
                                     state='readonly', width=25)
            else:
                widget = ttk.Entry(main_frame, textvariable=self.edit_vars[field_id], width=25)
            
            widget.grid(row=row, column=1, sticky='ew', pady=5)
            row += 1
        
        main_frame.columnconfigure(1, weight=1)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(btn_frame, text="Enregistrer", command=self.save_changes).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.dialog.destroy).pack(side='left', padx=5)
    
    def load_payment_data(self):
        """Charger les données du paiement"""
        try:
            query = "SELECT * FROM paiements_avance WHERE id = ?"
            # Utiliser le cache pour les données qui ne changent pas fréquemment
            result = self.db_manager.execute_query(query, (self.payment_id,), use_cache=True, cache_timeout=60)
            
            if result:
                data = result[0]
                # Mapping des champs
                self.edit_vars['montant'].set(str(data[2]) if data[2] else '')
                self.edit_vars['mode_paiement'].set(str(data[3]) if data[3] else 'especes')
                self.edit_vars['reference_paiement'].set(str(data[5]) if data[5] else '')
                self.edit_vars['statut'].set(str(data[7]) if data[7] else 'actif')
                self.edit_vars['notes'].set(str(data[6]) if data[6] else '')
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement: {str(e)}")
    
    def save_changes(self):
        """Enregistrer les modifications"""
        try:
            # Validation
            try:
                montant = float(self.edit_vars['montant'].get())
                if montant <= 0:
                    messagebox.showerror("Erreur", "Le montant doit être positif")
                    return
            except ValueError:
                messagebox.showerror("Erreur", "Montant invalide")
                return
            
            # Récupérer l'ancien montant et statut pour ajuster le solde
            old_query = """
                SELECT client_id, montant, statut 
                FROM paiements_avance 
                WHERE id = ?
            """
            # Ne pas utiliser le cache pour cette vérification critique
            old_data = self.db_manager.execute_query(old_query, (self.payment_id,), use_cache=False)[0]
            client_id, old_montant, old_statut = old_data
            
            # Mise à jour du paiement
            update_query = """
                UPDATE paiements_avance SET
                    montant = ?, mode_paiement = ?, reference_paiement = ?,
                    statut = ?, notes = ?
                WHERE id = ?
            """
            
            params = (
                montant,
                self.edit_vars['mode_paiement'].get(),
                self.edit_vars['reference_paiement'].get().strip() or None,
                self.edit_vars['statut'].get(),
                self.edit_vars['notes'].get().strip() or None,
                self.payment_id
            )
            
            # Utiliser le paramètre table pour invalider automatiquement le cache
            self.db_manager.execute_update(update_query, params, table='paiements_avance')
            
            # Ajuster le solde client si nécessaire
            new_statut = self.edit_vars['statut'].get()
            
            if old_statut != new_statut or (old_statut == 'actif' and montant != old_montant):
                # Remettre l'ancien solde si c'était actif
                if old_statut == 'actif':
                    adjust_query = "UPDATE clients SET solde_actuel = solde_actuel - ? WHERE id = ?"
                    # Utiliser le paramètre table pour invalider automatiquement le cache
                    self.db_manager.execute_update(adjust_query, (old_montant, client_id), table='clients')
                
                # Appliquer le nouveau solde si c'est maintenant actif
                if new_statut == 'actif':
                    adjust_query = "UPDATE clients SET solde_actuel = solde_actuel + ? WHERE id = ?"
                    # Utiliser le paramètre table pour invalider automatiquement le cache
                    self.db_manager.execute_update(adjust_query, (montant, client_id), table='clients')
            
            messagebox.showinfo("Succès", "Paiement modifié avec succès")
            self.callback()
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")
