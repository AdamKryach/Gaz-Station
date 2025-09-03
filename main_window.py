import tkinter as tk
from tkinter import ttk

class MainWindow(ttk.Frame):
    def __init__(self, parent, db_manager, user_role):
        super().__init__(parent)
        self.parent = parent
        self.db_manager = db_manager
        self.user_role = user_role
        
        # Configuration du frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)
        
        # Configuration responsive
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Ajouter le contenu de l'interface ici
        self.create_widgets()
    
    def create_widgets(self):
        """Crée les composants de l'interface"""
        label = ttk.Label(self.main_frame, text="Interface Principale", font=('Helvetica', 16))
        label.grid(row=0, column=0, pady=20)
