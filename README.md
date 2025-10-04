# Système de Gestion des Stations-Service

Application de comptabilité en français pour la gestion de 6 stations-service avec support écran tactile.

## Fonctionnalités

### 🏢 Gestion des Stations
- 6 stations-service pré-configurées
- Informations complètes pour chaque station
- Gestion des responsables et coordonnées

### 👥 Gestion des Clients
- Clients particuliers et entreprises
- Informations complètes (ICE, adresses, contacts)
- Gestion des véhicules par client
- Limites de crédit personnalisées
- Historique complet des transactions

### ⛽ Suivi des Transactions de Carburant
- Enregistrement des ventes de carburant
- Support de différents types de carburant
- Gestion des prix unitaires
- Suivi des quantités et montants
- Calculatrice intégrée

### 💰 Paiements d'Avance
- Enregistrement des paiements clients
- Différents modes de paiement (espèces, chèque, virement, carte)
- Suivi des soldes clients en temps réel
- Références de paiement

### 🧾 Facturation en Dirhams (DH)
- Création automatique de factures
- Calcul TVA (20%)
- Impression PDF des factures
- Suivi des statuts (payée, impayée, annulée)
- Numérotation automatique

### 📊 Rapports et Statistiques
- Tableau de bord avec statistiques en temps réel
- Graphiques d'évolution des ventes
- Rapports de ventes détaillés
- Rapports clients (soldes, consommation, paiements)
- Rapports financiers (CA, créances, factures)
- Export Excel des données

### 📱 Support Écran Tactile
- Interface adaptée aux écrans tactiles
- Boutons et contrôles de taille appropriée
- Navigation intuitive
- Styles visuels optimisés

## Installation

### Prérequis
- Python 3.8 ou plus récent
- Windows (testé sur Windows 10/11)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Dépendances incluses
- tkinter (interface graphique)
- sqlite3 (base de données)
- reportlab (génération PDF)
- matplotlib (graphiques)
- openpyxl (export Excel)
- Pillow (traitement d'images)

## Démarrage

```bash
python main.py
```

L'application démarre en mode plein écran avec la base de données SQLite automatiquement initialisée.

## Utilisation

### Premier Démarrage
1. L'application crée automatiquement la base de données
2. 6 stations sont pré-configurées
3. Types de carburant standard ajoutés (Essence Super, Gasoil, Sans Plomb 95, GPL)

### Navigation
- **Tableau de Bord** : Vue d'ensemble avec statistiques
- **Clients** : Gestion complète des clients et véhicules
- **Carburant** : Enregistrement des transactions de vente
- **Paiements** : Gestion des paiements d'avance
- **Factures** : Création et gestion des factures
- **Rapports** : Analyses et exports de données

### Workflow Typique
1. **Ajouter un client** avec ses informations
2. **Enregistrer ses véhicules** si nécessaire
3. **Enregistrer un paiement d'avance** (optionnel)
4. **Saisir les transactions de carburant**
5. **Générer des factures** périodiques
6. **Consulter les rapports** pour le suivi

## Structure de la Base de Données

### Tables Principales
- `stations` : Informations des 6 stations
- `clients` : Données clients (particuliers/entreprises)
- `vehicules` : Véhicules des clients
- `carburants` : Types et prix des carburants
- `transactions` : Ventes de carburant
- `paiements_avance` : Paiements clients
- `factures` : Factures générées
- `lignes_facture` : Détail des factures

### Gestion des Soldes
- Soldes clients mis à jour automatiquement
- Transactions à crédit déduites du solde
- Paiements d'avance ajoutés au solde
- Limites de crédit respectées

## Personnalisation

### Stations
Modifiez les stations dans `modules/database.py` :
```python
stations = [
    ("Votre Station", "Votre Adresse", "Votre Téléphone", "Responsable"),
    # ... autres stations
]
```

### Types de Carburant
Ajustez les carburants et prix dans `modules/database.py` :
```python
carburants = [
    ("Type Carburant", prix_unitaire, "litre", "#couleur"),
    # ... autres carburants
]
```

### TVA
Modifiez le taux de TVA dans `modules/invoice_management.py` :
```python
tva = total_ht * 0.20  # 20% par défaut
```

## Support et Maintenance

### Fichiers de Configuration
- `gaz_station.db` : Base de données SQLite
- `requirements.txt` : Dépendances Python

### Sauvegarde
Sauvegardez régulièrement le fichier `gaz_station.db` qui contient toutes les données.

### Logs
Les erreurs sont affichées via des messages d'erreur tkinter. Consultez la console pour les détails techniques.

## Fonctionnalités Avancées

### Calculatrice Intégrée
- Accessible depuis l'onglet Carburant
- Opérations arithmétiques de base
- Interface tactile

### Export Excel
- Rapports de ventes exportables
- Formatage professionnel
- Styles et bordures automatiques

### Impression PDF
- Factures au format PDF
- En-tête personnalisable
- Ouverture automatique du fichier

### Recherche en Temps Réel
- Recherche clients instantanée
- Filtrage dynamique des listes
- Suggestions automatiques

## Interface Utilisateur

### Écran Tactile
- Boutons adaptés à la taille des doigts
- Espacement généreux entre les éléments
- Police lisible (Arial, tailles appropriées)

### Navigation
- Onglets principaux clairement identifiés
- Icônes emoji pour la reconnaissance visuelle
- Barre de statut informative

### Ergonomie
- Formulaires organisés en sections logiques
- Validation des saisies en temps réel
- Messages d'erreur explicites en français

## Dépannage

### Problèmes Courants
1. **Erreur de base de données** : Vérifiez les permissions du répertoire
2. **Import manquant** : Installez les dépendances avec pip
3. **Problème d'affichage** : Vérifiez la résolution d'écran

### Contact
Pour toute assistance technique, consultez les logs d'erreur dans la console Python.

---

**Version** : 1.0.0  
**Langue** : Français  
**Plateforme** : Windows  
**Type** : Application Desktop Python/tkinter

### Deepseek API
```bash
sk-ce374a2dc4ae4f5ba63213935f081618
```