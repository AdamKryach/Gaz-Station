# -*- coding: utf-8 -*-
"""
Test application for vehicle management with Moroccan license plates
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from database import DatabaseManager
from client_management_simple import ClientManagement


def main():
    """Launch test application"""
    try:
        # Create main window
        root = tk.Tk()
        root.title("Test - Gestion de Véhicules avec Matricules Marocains")
        root.geometry("1200x800")
        root.configure(bg='#f0f0f0')
        
        # Configure styles for touch-friendly interface
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom styles for touch interface
        style.configure('Touch.TButton', 
                       font=('Arial', 11, 'bold'),
                       padding=(10, 8))
        
        style.configure('Touch.TLabel', 
                       font=('Arial', 11))
        
        style.configure('Touch.Treeview', 
                       font=('Arial', 10),
                       rowheight=25)
        
        style.configure('Touch.Treeview.Heading', 
                       font=('Arial', 11, 'bold'))
        
        # Initialize database
        db_manager = DatabaseManager("test_gaz_station.db")
        
        # Create main interface
        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="Test - Gestion de Clients et Véhicules",
                               font=('Arial', 16, 'bold'),
                               foreground='darkblue')
        title_label.pack(pady=(0, 20))
        
        # Information panel
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding=10)
        info_frame.pack(fill='x', pady=(0, 10))
        
        info_text = """
Cette application de test démontre la gestion des véhicules avec matricules marocains:

• Format de matricule marocain: [Numéro séquentiel] | [Lettre arabe] | [Région 1-99]
• Lettres arabes supportées: أ ب ج د ه و ز ح ط ي ك ل م ن س ع ف ص ق ر ش ت ث خ ذ ض ظ غ
• Types spéciaux: ج (État), ش (Police), و م (Protection Civile), ق س (Forces Auxiliaires)
• Types de carburant: Essence, Diesel, Électrique, Hybride
• Exemples valides: 123456|ب|12, 98765 ش 34, 12345-د-56

Instructions:
1. Ajoutez un client avec nom, prénom et téléphone
2. Sélectionnez le client pour ajouter ses véhicules
3. Testez la validation du format de matricule
        """
        
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=('Arial', 10),
                              justify='left')
        info_label.pack(anchor='w')
        
        # Client management interface
        client_management = ClientManagement(main_frame, db_manager)
        
        # Run the application
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du lancement: {str(e)}")
        print(f"Erreur détaillée: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
