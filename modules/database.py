# -*- coding: utf-8 -*-
"""
Gestionnaire de base de données pour l'application Stations-Service
Optimisé pour de meilleures performances avec mise en cache et indexation
"""

import sqlite3
import os
import hashlib
import time
import functools
from datetime import datetime, date
import threading
from threading import RLock

class DatabaseManager:
    def __init__(self, db_path="gaz_station.db"):
        """Initialiser la connexion à la base de données"""
        self.db_path = db_path
        self.connection_pool = {}
        self.connection_lock = RLock()
        self.query_cache = {}
        self.cache_timeout = 60  # Durée de vie du cache en secondes
        self.init_database()
        
        # Statistiques de performance
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "query_count": 0,
            "slow_queries": []
        }
    
    def get_connection(self):
        """Obtenir une connexion à la base de données avec gestion d'erreurs et pool de connexions"""
        try:
            # Utiliser un pool de connexions pour réduire le temps d'ouverture
            with self.connection_lock:
                # Identifier le thread actuel
                thread_id = id(threading.current_thread()) if threading else 0
                
                # Vérifier si une connexion existe déjà pour ce thread
                if thread_id in self.connection_pool and self.connection_pool[thread_id]['conn']:
                    # Vérifier que la connexion est toujours valide
                    try:
                        self.connection_pool[thread_id]['conn'].execute("SELECT 1")
                        return self.connection_pool[thread_id]['conn']
                    except sqlite3.Error:
                        # La connexion n'est plus valide, la fermer
                        try:
                            self.connection_pool[thread_id]['conn'].close()
                        except:
                            pass
                
                # Créer une nouvelle connexion
                conn = sqlite3.connect(self.db_path, timeout=20, isolation_level=None)
                
                # Optimisations SQLite
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging pour de meilleures performances
                conn.execute("PRAGMA synchronous = NORMAL")  # Réduire les opérations d'I/O synchrones
                conn.execute("PRAGMA cache_size = 10000")  # Augmenter la taille du cache
                conn.execute("PRAGMA temp_store = MEMORY")  # Stocker les tables temporaires en mémoire
                
                # Stocker la connexion dans le pool
                self.connection_pool[thread_id] = {
                    'conn': conn,
                    'timestamp': time.time()
                }
                
                return conn
        except sqlite3.Error as e:
            # Journaliser l'erreur et la propager
            self._log_error(f"Erreur de connexion à la base de données: {str(e)}")
            raise
    
    def close_all_connections(self):
        """Fermer toutes les connexions du pool"""
        with self.connection_lock:
            for thread_id, conn_data in list(self.connection_pool.items()):
                try:
                    conn_data['conn'].close()
                except:
                    pass
                del self.connection_pool[thread_id]
    
    def cleanup_old_connections(self, max_age=300):
        """Nettoyer les connexions inactives depuis plus de max_age secondes"""
        current_time = time.time()
        with self.connection_lock:
            for thread_id, conn_data in list(self.connection_pool.items()):
                if current_time - conn_data['timestamp'] > max_age:
                    try:
                        conn_data['conn'].close()
                    except:
                        pass
                    del self.connection_pool[thread_id]
    
    def _log_error(self, message):
        """Journaliser les erreurs dans un fichier de log"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, "db_errors.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def init_database(self):
        """Créer les tables et les index si elles n'existent pas"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            conn.execute("BEGIN TRANSACTION")  # Accélérer les créations de tables avec une transaction
            
            # Table des stations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    adresse TEXT,
                    telephone TEXT,
                    responsable TEXT,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des clients (simplifiée)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prenom TEXT,
                    telephone TEXT,
                    solde_actuel REAL DEFAULT 0,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des véhicules clients avec matricule marocain
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    matricule TEXT NOT NULL,
                    marque TEXT,
                    modele TEXT,
                    type_carburant TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            # Table des types de carburant
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carburants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT NOT NULL,
                    prix_unitaire REAL NOT NULL,
                    unite TEXT DEFAULT 'litre',
                    couleur TEXT DEFAULT '#FF0000'
                )
            """)
            
            # Table des transactions de carburant
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id INTEGER NOT NULL,
                    client_id INTEGER NOT NULL,
                    vehicule_id INTEGER,
                    carburant_id INTEGER NOT NULL,
                    quantite REAL NOT NULL,
                    prix_unitaire REAL NOT NULL,
                    montant_total REAL NOT NULL,
                    type_paiement TEXT DEFAULT 'credit',
                    date_transaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    numero_pompe INTEGER,
                    notes TEXT,
                    FOREIGN KEY (station_id) REFERENCES stations (id),
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (vehicule_id) REFERENCES vehicules (id),
                    FOREIGN KEY (carburant_id) REFERENCES carburants (id)
                )
            """)
            
            # Table des paiements d'avance
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS paiements_avance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    montant REAL NOT NULL,
                    mode_paiement TEXT NOT NULL,
                    date_paiement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reference_paiement TEXT,
                    notes TEXT,
                    statut TEXT DEFAULT 'actif',
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            """)
            
            # Table des factures
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_facture TEXT UNIQUE NOT NULL,
                    client_id INTEGER NOT NULL,
                    station_id INTEGER NOT NULL,
                    date_facture DATE NOT NULL,
                    montant_ht REAL NOT NULL,
                    tva REAL NOT NULL,
                    montant_ttc REAL NOT NULL,
                    statut TEXT DEFAULT 'impayee',
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (client_id) REFERENCES clients (id),
                    FOREIGN KEY (station_id) REFERENCES stations (id)
                )
            """)
            
            # Table des lignes de facture
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lignes_facture (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    facture_id INTEGER NOT NULL,
                    transaction_id INTEGER,
                    description TEXT NOT NULL,
                    quantite REAL NOT NULL,
                    prix_unitaire REAL NOT NULL,
                    montant REAL NOT NULL,
                    FOREIGN KEY (facture_id) REFERENCES factures (id),
                    FOREIGN KEY (transaction_id) REFERENCES transactions (id)
                )
            """)
            
            # Table des utilisateurs pour le système de login
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_utilisateur TEXT UNIQUE NOT NULL,
                    mot_de_passe TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('administrateur', 'employe')),
                    nom_complet TEXT,
                    actif BOOLEAN DEFAULT 1,
                    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Créer des index pour optimiser les requêtes fréquentes
            self.create_indexes(cursor)
            
            conn.commit()
            
            # Insérer des données initiales si la base est vide
            self.insert_initial_data(cursor)
            conn.commit()
    
    def create_indexes(self, cursor):
        """Créer des index pour optimiser les requêtes fréquentes"""
        # Index pour les recherches de clients
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_nom ON clients (nom)")
        
        # Index pour les recherches de véhicules par client
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicules_client ON vehicules (client_id)")
        
        # Index pour les recherches de transactions par client
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_client ON transactions (client_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions (date_transaction)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_station ON transactions (station_id)")
        
        # Index pour les recherches de paiements par client
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paiements_client ON paiements_avance (client_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_paiements_date ON paiements_avance (date_paiement)")
        
        # Index pour les recherches de factures par client
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_factures_client ON factures (client_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_factures_date ON factures (date_facture)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_factures_numero ON factures (numero_facture)")
        
        # Index pour les lignes de facture
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lignes_facture ON lignes_facture (facture_id)")
        
        # Analyser la base pour optimiser le planificateur de requêtes
        cursor.execute("ANALYZE")
    
    def insert_initial_data(self, cursor):
        """Insérer les données initiales"""
        # Vérifier si des stations existent déjà
        cursor.execute("SELECT COUNT(*) FROM stations")
        if cursor.fetchone()[0] == 0:
            # Insérer les 6 stations
            stations = [
                ("Station Timizar", "route Sidi Kacem", "05********", "Yassin Tyal"),
                ("Station 2", "Local 2", "05********", "Géront 2"),
                ("Station 3", "Local 3", "05********", "Géront 3"),
                ("Station 4", "Local 4", "05********", "Géront 4"),
                ("Station 5", "Local 5", "05********", "Géront 5"),
                ("Station 6", "Local 6", "05********", "Géront 6")
            ]
            
            for station in stations:
                cursor.execute(
                    "INSERT INTO stations (nom, adresse, telephone, responsable) VALUES (?, ?, ?, ?)",
                    station
                )
        
        # Vérifier si des carburants existent déjà
        cursor.execute("SELECT COUNT(*) FROM carburants")
        if cursor.fetchone()[0] == 0:
            # Insérer les types de carburant
            carburants = [
                ("Essence", 14.50, "litre", "#FF4444"),
                ("Diesel", 11.80, "litre", "#44FF44"),
                ("Électrique", 0.00, "kWh", "#00FFFF"),
                ("Hybride", 13.20, "litre", "#FF8800")
            ]
            
            for carburant in carburants:
                cursor.execute(
                    "INSERT INTO carburants (nom, prix_unitaire, unite, couleur) VALUES (?, ?, ?, ?)",
                    carburant
                )
        
        # Vérifier si des utilisateurs existent déjà
        cursor.execute("SELECT COUNT(*) FROM utilisateurs")
        if cursor.fetchone()[0] == 0:
            # Créer l'utilisateur administrateur par défaut
            admin_password = hashlib.sha256("admin123".encode()).hexdigest()
            employe_password = hashlib.sha256("employe123".encode()).hexdigest()
            
            utilisateurs = [
                ("admin", admin_password, "administrateur", "Administrateur"),
                ("employe", employe_password, "employe", "Employé")
            ]
            
            for utilisateur in utilisateurs:
                cursor.execute(
                    "INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe, role, nom_complet) VALUES (?, ?, ?, ?)",
                    utilisateur
                )
    
    def execute_query(self, query, params=None, use_cache=True, cache_timeout=None, table=None):
        """Exécuter une requête SQL avec gestion d'erreurs, mise en cache et mesure de performance"""
        start_time = time.time()
        self.stats["query_count"] += 1
        
        # Déterminer si la requête est en lecture seule (SELECT)
        is_select = query.strip().upper().startswith("SELECT")
        
        # Utiliser le cache uniquement pour les requêtes SELECT si activé
        if is_select and use_cache:
            # Créer une clé de cache basée sur la requête et les paramètres
            cache_key = f"{query}_{str(params)}"
            
            # Vérifier si la requête est dans le cache et toujours valide
            if cache_key in self.query_cache:
                cache_entry = self.query_cache[cache_key]
                cache_age = time.time() - cache_entry["timestamp"]
                timeout = cache_timeout or self.cache_timeout
                
                if cache_age < timeout:
                    self.stats["cache_hits"] += 1
                    return cache_entry["data"]
            
            self.stats["cache_misses"] += 1
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Exécuter la requête avec ou sans paramètres
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Récupérer les résultats
                results = cursor.fetchall()
                
                # Mesurer le temps d'exécution
                execution_time = time.time() - start_time
                
                # Enregistrer les requêtes lentes (> 100ms)
                if execution_time > 0.1:
                    self.stats["slow_queries"].append({
                        "query": query,
                        "params": params,
                        "time": execution_time,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    # Limiter la liste des requêtes lentes à 100 entrées
                    if len(self.stats["slow_queries"]) > 100:
                        self.stats["slow_queries"].pop(0)
                
                # Mettre en cache les résultats pour les requêtes SELECT
                if is_select and use_cache:
                    self.query_cache[cache_key] = {
                        "data": results,
                        "timestamp": time.time(),
                        "table": table  # Stocker la table associée pour une invalidation plus précise
                    }
                    
                    # Nettoyer le cache si trop grand (> 1000 entrées)
                    if len(self.query_cache) > 1000:
                        self.clean_cache()
                
                return results
        except sqlite3.Error as e:
            error_msg = f"Erreur d'exécution de requête: {str(e)}\nRequête: {query}\nParamètres: {params}"
            self._log_error(error_msg)
            # Propager l'erreur avec un message plus informatif
            raise sqlite3.Error(f"Erreur de base de données: {str(e)}") from e
    
    def clean_cache(self):
        """Nettoyer les entrées expirées du cache"""
        current_time = time.time()
        expired_keys = []
        
        # Identifier les entrées expirées
        for key, entry in self.query_cache.items():
            if current_time - entry["timestamp"] > self.cache_timeout:
                expired_keys.append(key)
        
        # Supprimer les entrées expirées
        for key in expired_keys:
            del self.query_cache[key]
        
        # Si le cache est toujours trop grand, supprimer les entrées les plus anciennes
        if len(self.query_cache) > 500:
            sorted_entries = sorted(self.query_cache.items(), key=lambda x: x[1]["timestamp"])
            for key, _ in sorted_entries[:len(sorted_entries) // 2]:
                del self.query_cache[key]
    
    def invalidate_cache(self, table=None):
        """Invalider le cache, soit complètement soit pour une table spécifique"""
        if table:
            # Supprimer uniquement les entrées liées à la table spécifiée
            keys_to_remove = []
            for key in self.query_cache.keys():
                if f"FROM {table}" in key or f"JOIN {table}" in key:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self.query_cache[key]
        else:
            # Vider complètement le cache
            self.query_cache.clear()
    
    def execute_insert(self, query, params, table=None):
        """Exécuter une insertion avec gestion d'erreurs et retourner l'ID généré"""
        start_time = time.time()
        self.stats["query_count"] += 1
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                last_id = cursor.lastrowid
                
                # Mesurer le temps d'exécution
                execution_time = time.time() - start_time
                
                # Enregistrer les requêtes lentes (> 100ms)
                if execution_time > 0.1:
                    self.stats["slow_queries"].append({
                        "query": query,
                        "params": params,
                        "time": execution_time,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                # Invalider le cache pour la table concernée
                if table:
                    self.invalidate_cache(table)
                
                return last_id
        except sqlite3.Error as e:
            error_msg = f"Erreur d'insertion: {str(e)}\nRequête: {query}\nParamètres: {params}"
            self._log_error(error_msg)
            # Propager l'erreur avec un message plus informatif
            raise sqlite3.Error(f"Erreur d'insertion dans la base de données: {str(e)}") from e
    
    def execute_update(self, query, params, table=None):
        """Exécuter une mise à jour avec gestion d'erreurs et retourner le nombre de lignes affectées"""
        start_time = time.time()
        self.stats["query_count"] += 1
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows_affected = cursor.rowcount
                
                # Mesurer le temps d'exécution
                execution_time = time.time() - start_time
                
                # Enregistrer les requêtes lentes (> 100ms)
                if execution_time > 0.1:
                    self.stats["slow_queries"].append({
                        "query": query,
                        "params": params,
                        "time": execution_time,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                
                # Invalider le cache pour la table concernée
                if table:
                    self.invalidate_cache(table)
                else:
                    # Essayer de déterminer la table à partir de la requête
                    query_upper = query.upper()
                    if "UPDATE" in query_upper:
                        table_name = query_upper.split("UPDATE")[1].strip().split(" ")[0]
                        self.invalidate_cache(table_name)
                
                return rows_affected
        except sqlite3.Error as e:
            error_msg = f"Erreur de mise à jour: {str(e)}\nRequête: {query}\nParamètres: {params}"
            self._log_error(error_msg)
            # Propager l'erreur avec un message plus informatif
            raise sqlite3.Error(f"Erreur de mise à jour dans la base de données: {str(e)}") from e
    
    def get_performance_stats(self):
        """Retourner les statistiques de performance de la base de données"""
        return {
            "query_count": self.stats["query_count"],
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "cache_hit_ratio": self.stats["cache_hits"] / max(1, (self.stats["cache_hits"] + self.stats["cache_misses"])),
            "slow_queries_count": len(self.stats["slow_queries"]),
            "slow_queries": self.stats["slow_queries"][-10:],  # 10 dernières requêtes lentes
            "cache_size": len(self.query_cache),
            "connection_pool_size": len(self.connection_pool)
        }
    
    def reset_stats(self):
        """Réinitialiser les statistiques de performance"""
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "query_count": 0,
            "slow_queries": []
        }
    
    # Décorateur pour mettre en cache les résultats des méthodes fréquemment appelées
    @staticmethod
    def cached_method(timeout=60):
        """Décorateur pour mettre en cache les résultats des méthodes"""
        def decorator(func):
            cache = {}
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Créer une clé de cache basée sur les arguments
                key = str(args) + str(kwargs)
                
                # Vérifier si le résultat est dans le cache et toujours valide
                if key in cache:
                    result, timestamp = cache[key]
                    if time.time() - timestamp < timeout:
                        return result
                
                # Exécuter la méthode et mettre en cache le résultat
                result = func(*args, **kwargs)
                cache[key] = (result, time.time())
                
                # Nettoyer le cache si trop grand
                if len(cache) > 100:
                    current_time = time.time()
                    expired_keys = [k for k, (_, t) in cache.items() if current_time - t > timeout]
                    for k in expired_keys:
                        del cache[k]
                
                return result
            
            # Ajouter une méthode pour invalider le cache
            def clear_cache():
                cache.clear()
            
            wrapper.clear_cache = clear_cache
            return wrapper
        
        return decorator
    
    def validate_data(self, table, data):
        """Valider les données avant insertion ou mise à jour"""
        # Définir les règles de validation par table
        validation_rules = {
            'stations': {
                'required': ['nom'],
                'max_length': {'nom': 100, 'adresse': 200, 'telephone': 20, 'responsable': 100}
            },
            'clients': {
                'required': ['nom'],
                'max_length': {'nom': 100, 'prenom': 100, 'telephone': 20},
                'numeric': ['solde_actuel']
            },
            'vehicules': {
                'required': ['client_id', 'matricule'],
                'max_length': {'matricule': 20, 'marque': 50, 'modele': 50, 'type_carburant': 30},
                'foreign_key': {'client_id': 'clients'}
            },
            'carburants': {
                'required': ['nom', 'prix_unitaire'],
                'max_length': {'nom': 50, 'unite': 20, 'couleur': 20},
                'numeric': ['prix_unitaire']
            },
            'transactions': {
                'required': ['station_id', 'client_id', 'carburant_id', 'quantite', 'prix_unitaire', 'montant_total'],
                'numeric': ['quantite', 'prix_unitaire', 'montant_total', 'numero_pompe'],
                'foreign_key': {'station_id': 'stations', 'client_id': 'clients', 
                               'vehicule_id': 'vehicules', 'carburant_id': 'carburants'}
            },
            'paiements_avance': {
                'required': ['client_id', 'montant'],
                'numeric': ['montant'],
                'foreign_key': {'client_id': 'clients'}
            }
        }
        
        # Si la table n'a pas de règles définies, retourner True
        if table not in validation_rules:
            return True
        
        rules = validation_rules[table]
        errors = []
        
        # Vérifier les champs requis
        if 'required' in rules:
            for field in rules['required']:
                if field not in data or data[field] is None or data[field] == '':
                    errors.append(f"Le champ '{field}' est requis.")
        
        # Vérifier les longueurs maximales
        if 'max_length' in rules:
            for field, max_len in rules['max_length'].items():
                if field in data and data[field] and len(str(data[field])) > max_len:
                    errors.append(f"Le champ '{field}' dépasse la longueur maximale de {max_len} caractères.")
        
        # Vérifier les champs numériques
        if 'numeric' in rules:
            for field in rules['numeric']:
                if field in data and data[field] is not None:
                    try:
                        float(data[field])
                    except (ValueError, TypeError):
                        errors.append(f"Le champ '{field}' doit être une valeur numérique.")
        
        # Vérifier les clés étrangères
        if 'foreign_key' in rules:
            for field, ref_table in rules['foreign_key'].items():
                if field in data and data[field] is not None and data[field] != '':
                    try:
                        # Vérifier si l'ID existe dans la table référencée
                        query = f"SELECT COUNT(*) FROM {ref_table} WHERE id = ?"
                        result = self.execute_query(query, (data[field],))
                        if result[0][0] == 0:
                            errors.append(f"La référence '{field}' n'existe pas dans la table '{ref_table}'.")
                    except sqlite3.Error as e:
                        self._log_error(f"Erreur lors de la validation de clé étrangère: {str(e)}")
                        errors.append(f"Erreur de validation pour le champ '{field}'.")
        
        # Si des erreurs sont trouvées, lever une exception
        if errors:
            error_message = "\n".join(errors)
            self._log_error(f"Erreurs de validation pour la table '{table}': {error_message}")
            raise ValueError(f"Erreurs de validation: {error_message}")
        
        return True
