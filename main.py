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

Version 2.0 - Avec gestion d'erreurs améliorée et validation des données
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
import traceback
from datetime import datetime

# === Ajouter le répertoire du projet au chemin Python ===
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.database import DatabaseManager
from modules.main_window import MainWindow
from modules.auth import LoginDialog, AdminPanel


class GazStationApp:
    def __init__(self):
        # === Configuration du logging ===
        self.setup_logging()
        
        try:
            # === Fenêtre principale ===
            self.root = tk.Tk()
            self.root.title("Gestion Stations-Service - Comptabilité")
            
            # Configuration pour permettre le redimensionnement à partir de 0
            self.root.minsize(800, 600)  # Taille minimale pour l'interface
            
            # Obtenir les dimensions de l'écran
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Définir la taille initiale à 80% de l'écran
            initial_width = int(screen_width * 0.8)
            initial_height = int(screen_height * 0.8)
            
            # Centrer la fenêtre
            x_position = (screen_width - initial_width) // 2
            y_position = (screen_height - initial_height) // 2
            
            # Appliquer la géométrie
            self.root.geometry(f"{initial_width}x{initial_height}+{x_position}+{y_position}")
            
            # Permettre le redimensionnement
            self.root.resizable(True, True)
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
            
            # Passer l'ID de l'utilisateur pour les préférences de fenêtre
            try:
                # Récupérer l'ID de l'utilisateur depuis la base de données
                query = "SELECT id FROM users WHERE username = ?"
                result = self.db_manager.execute_query(query, (self.current_user,))
                if result and result[0][0]:
                    self.main_window.current_user_id = result[0][0]
            except Exception as e:
                self.log_error("Erreur lors de la récupération de l'ID utilisateur", e)

            # === Menu ===
            self.setup_menu()
            
        except Exception as e:
            self.log_error("Erreur d'initialisation de l'application", e)
            messagebox.showerror("Erreur d'initialisation", 
                               f"Une erreur est survenue lors du démarrage de l'application:\n{str(e)}\n\nConsultez le fichier log pour plus de détails.")
            if hasattr(self, 'root'):
                self.root.quit()
    
    def setup_logging(self):
        """Configure le système de logging pour l'application"""
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        
        # Créer le répertoire logs s'il n'existe pas
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f'gaz_station_{datetime.now().strftime("%Y%m%d")}.log')
        
        # Configuration du logger
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Log de démarrage
        logging.info("=== Démarrage de l'application Gaz Station ===")
    
    def log_error(self, message, exception=None):
        """Enregistre une erreur dans le fichier log"""
        error_details = f"{message}: {str(exception)}" if exception else message
        logging.error(error_details)
        
        if exception:
            logging.error(traceback.format_exc())

    # -----------------------------------------------------
    # Menu
    # -----------------------------------------------------
    def setup_menu(self):
        """Configuration du menu selon le rôle utilisateur"""
        try:
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)

            # Menu Fichier
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Fichier", menu=file_menu)
            file_menu.add_command(label="Paramètres", command=self.open_settings)
            file_menu.add_command(label="Quitter", command=self.root.quit)

            # Menu Administration
            if self.user_role == 'administrateur':
                admin_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="Administration", menu=admin_menu)
                admin_menu.add_command(label="Panneau d'Administration", command=self.open_admin_panel)
                admin_menu.add_command(label="Statistiques DB", command=self.show_db_stats)
                admin_menu.add_command(label="Réinitialiser stats DB", command=lambda: self.db_manager.reset_stats())

            # Menu Aide
            help_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Aide", menu=help_menu)
            help_menu.add_command(label="À propos", command=self.show_about)
            help_menu.add_command(label="Logs", command=self.show_logs)

            # Ajouter l'utilisateur connecté au titre
            user_info = f"Connecté: {self.current_user} ({self.user_role.title()})"
            self.root.title(f"Gestion Stations-Service - {user_info}")
        except Exception as e:
            self.log_error("Erreur lors de la configuration du menu", e)
            messagebox.showwarning("Avertissement", "Erreur lors de la configuration du menu. Certaines fonctionnalités pourraient être indisponibles.")

    def open_admin_panel(self):
        """Ouvrir le panneau d'administration"""
        try:
            AdminPanel(self.root, self.db_manager, self.user_role)
        except Exception as e:
            self.log_error("Erreur lors de l'ouverture du panneau d'administration", e)
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le panneau d'administration:\n{str(e)}")

    def show_about(self):
        """Afficher les informations sur l'application"""
        try:
            about_text = """
Application de Gestion des Stations-Service
Version 2.0

Fonctionnalités:
- Gestion simplifiée des clients
- Suivi des transactions de carburant
- Gestion des véhicules avec matricules marocains
- Système de connexion sécurisé
- Rapports et statistiques
- Gestion d'erreurs améliorée

Optimisé pour écran tactile
            """
            messagebox.showinfo("À propos", about_text.strip())
        except Exception as e:
            self.log_error("Erreur lors de l'affichage des informations", e)
    
    def show_db_stats(self):
        """Afficher les statistiques de performance de la base de données"""
        try:
            stats = self.db_manager.get_performance_stats()
            stats_text = f"Statistiques de la base de données:\n\n"
            stats_text += f"Nombre total de requêtes: {stats['query_count']}\n"
            stats_text += f"Hits du cache: {stats['cache_hits']}\n"
            stats_text += f"Misses du cache: {stats['cache_misses']}\n"
            stats_text += f"Ratio de hits: {stats['cache_hit_ratio']:.2%}\n"
            stats_text += f"Taille du cache: {stats['cache_size']} entrées\n"
            stats_text += f"Connexions actives: {stats['connection_pool_size']}\n\n"
            
            if stats['slow_queries_count'] > 0:
                stats_text += f"Requêtes lentes ({stats['slow_queries_count']} au total):\n"
                for q in stats['slow_queries']:
                    stats_text += f"- {q['timestamp']}: {q['time']:.3f}s - {q['query'][:50]}...\n"
            else:
                stats_text += "Aucune requête lente détectée."
                
            messagebox.showinfo("Statistiques DB", stats_text)
        except Exception as e:
            self.log_error(f"Erreur lors de l'affichage des statistiques: {str(e)}")
            messagebox.showerror("Erreur", f"Impossible d'afficher les statistiques: {str(e)}")
    
    def show_logs(self):
        """Afficher le fichier log le plus récent"""
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            if not os.path.exists(log_dir):
                messagebox.showinfo("Logs", "Aucun fichier log disponible.")
                return
                
            # Trouver le fichier log le plus récent
            log_files = [f for f in os.listdir(log_dir) if f.startswith('gaz_station_') and f.endswith('.log')]
            if not log_files:
                messagebox.showinfo("Logs", "Aucun fichier log disponible.")
                return
                
            latest_log = max(log_files, key=lambda x: os.path.getmtime(os.path.join(log_dir, x)))
            log_path = os.path.join(log_dir, latest_log)
            
            # Créer une fenêtre pour afficher les logs
            log_window = tk.Toplevel(self.root)
            log_window.title(f"Fichier Log: {latest_log}")
            log_window.geometry("800x600")
            
            # Ajouter un widget Text avec scrollbar
            frame = tk.Frame(log_window)
            frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            scrollbar = tk.Scrollbar(frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar.config(command=text_widget.yview)
            
            # Charger le contenu du fichier log
            with open(log_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
                text_widget.insert(tk.END, log_content)
                text_widget.config(state=tk.DISABLED)  # Lecture seule
                
            # Bouton pour fermer
            tk.Button(log_window, text="Fermer", command=log_window.destroy).pack(pady=10)
            
        except Exception as e:
            self.log_error("Erreur lors de l'affichage des logs", e)
            messagebox.showerror("Erreur", f"Impossible d'afficher les logs:\n{str(e)}")

    def run(self):
        """Démarrer l'application"""
        try:
            if hasattr(self, 'user_role'):
                # Configurer le gestionnaire d'exceptions non gérées
                self.setup_exception_handler()
                # Nettoyer les connexions inactives toutes les 5 minutes
                self.root.after(300000, self.cleanup_db_connections)
                logging.info(f"Application démarrée par l'utilisateur: {self.current_user} ({self.user_role})")
                self.root.mainloop()
        except Exception as e:
            self.log_error("Erreur lors de l'exécution de l'application", e)
            messagebox.showerror("Erreur critique", 
                               f"Une erreur critique est survenue:\n{str(e)}\n\nL'application va se fermer.")
    
    def cleanup_db_connections(self):
        """Nettoyer les connexions inactives à la base de données"""
        try:
            self.db_manager.cleanup_old_connections()
            # Reprogrammer le nettoyage
            self.root.after(300000, self.cleanup_db_connections)
        except Exception as e:
            self.log_error(f"Erreur lors du nettoyage des connexions: {str(e)}")
    
    def setup_exception_handler(self):
        """Configure un gestionnaire global d'exceptions non gérées"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            # Ignorer les exceptions KeyboardInterrupt (Ctrl+C)
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            # Log l'exception
            exception_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            logging.critical(f"Exception non gérée:\n{exception_message}")
            
            # Afficher un message à l'utilisateur
            messagebox.showerror("Erreur non gérée", 
                               f"Une erreur inattendue s'est produite:\n{str(exc_value)}\n\nConsultez le fichier log pour plus de détails.")
        
        # Remplacer le gestionnaire d'exceptions par défaut
        sys.excepthook = handle_exception


# === Point d'entrée principal ===
if __name__ == "__main__":
    try:
        # Vérifier l'existence du répertoire de logs
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # Démarrer l'application
        app = GazStationApp()
        app.run()
    except Exception as e:
        # Fallback pour les erreurs critiques avant l'initialisation du logging
        error_message = f"Erreur critique lors du démarrage: {str(e)}\n\n{traceback.format_exc()}"
        
        # Tenter d'écrire dans un fichier log d'urgence
        try:
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            emergency_log = os.path.join(log_dir, f'emergency_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            with open(emergency_log, 'w', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERREUR CRITIQUE\n{error_message}")
                
            messagebox.showerror("Erreur critique", 
                               f"Erreur lors du démarrage: {str(e)}\n\nDétails enregistrés dans {emergency_log}")
        except:
            # Si même l'écriture du log échoue, afficher simplement l'erreur
            messagebox.showerror("Erreur critique", 
                               f"Erreur lors du démarrage: {str(e)}\n\n{traceback.format_exc()}")
