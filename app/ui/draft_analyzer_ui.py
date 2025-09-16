#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main UI components for the Dota 2 Draft Analyzer.
"""

import tkinter as tk
import os
from tkinter import ttk
from PIL import Image, ImageTk
from typing import List, Dict, Tuple, Optional, Any

from .custom_widgets import AutocompleteCombobox
from ..core.draft_analyzer_core import DataManager, AnalysisCore




class MainApplication:
    """The main UI for the Draft Analyzer application."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Dota 2 Draft Analyzer")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)

        print("Initializing UI...")
        self.data_manager = DataManager()
        self.analyzer = AnalysisCore(self.data_manager)
        # Use the more comprehensive normalized_heroes data for names
        self.hero_names = sorted([hero['name'] for hero in self.data_manager.normalized_heroes])
        self.hero_image_labels: Dict[str, ttk.Label] = {}
        self.hero_image_references: Dict[str, Any] = {}  # To prevent garbage collection

        self._create_widgets()

    def _update_hero_image(self, hero_name: str, label_key: str) -> None:
        """Loads and displays the image for the selected hero."""
        hero_info = self.data_manager.hero_name_map.get(hero_name)
        image_label = self.hero_image_labels.get(label_key)

        if not hero_info or not image_label or not hero_info.get('image_path'):
            if image_label:
                image_label.config(image='')
            return

        try:
            image_path = os.path.join(self.data_manager.data_path, hero_info['image_path'])
            img = Image.open(image_path)
            img = img.resize((64, 36), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)

            image_label.config(image=photo)
            self.hero_image_references[label_key] = photo  # Keep a reference
        except Exception as e:
            print(f"Error loading image for {hero_name}: {e}")
            if image_label:
                image_label.config(image='')

    def _create_widgets(self) -> None:
        """Creates and places all widgets in the main window."""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Configure main frame weights for better layout
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Results section gets most space

        # --- Hero Selection --- #
        selection_frame = ttk.LabelFrame(main_frame, text="Hero Selection", padding="15")
        selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        selection_frame.columnconfigure(2, weight=1)

        # Helper to create a hero selection row
        def create_hero_row(label_text: str, row_index: int, label_key: str) -> AutocompleteCombobox:
            # Image Label
            img_label = ttk.Label(selection_frame)
            img_label.grid(row=row_index, column=0, padx=5)
            self.hero_image_labels[label_key] = img_label

            # Text Label
            label = ttk.Label(selection_frame, text=label_text, font=("Segoe UI", 10))
            label.grid(row=row_index, column=1, sticky=tk.W, pady=3, padx=(10, 5))
            
            # Autocomplete Entry
            combo = AutocompleteCombobox(selection_frame, completion_list=self.hero_names, font=("Segoe UI", 10))
            combo.grid(row=row_index, column=2, sticky=(tk.W, tk.E), pady=3, padx=(0, 5))
            combo.selection_callback = lambda hero_name, lk=label_key: self._update_hero_image(hero_name, lk)

            # Dropdown Arrow Button
            arrow_button = ttk.Button(selection_frame, text="▼", width=3, command=combo.show_all_options)
            arrow_button.grid(row=row_index, column=3, sticky='w', pady=3)

            return combo

        self.your_hero_combo = create_hero_row("Your Hero:", 0, 'your_hero')
        self.enemy_hero_1 = create_hero_row("Enemy Hero 1:", 1, 'enemy_1')
        self.enemy_hero_2 = create_hero_row("Enemy Hero 2:", 2, 'enemy_2')
        self.enemy_hero_3 = create_hero_row("Enemy Hero 3:", 3, 'enemy_3')
        self.enemy_hero_4 = create_hero_row("Enemy Hero 4:", 4, 'enemy_4')
        self.enemy_hero_5 = create_hero_row("Enemy Hero 5:", 5, 'enemy_5')

        # --- Analysis Button --- #
        analyze_frame = ttk.Frame(main_frame)
        analyze_frame.grid(row=1, column=0, pady=15)

        self.analyze_button = ttk.Button(
            analyze_frame, text="Analyze Draft", command=self.run_analysis,
            style="Accent.TButton"
        )
        self.analyze_button.pack()

        # --- Results Display --- #
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="15")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Create a canvas and a scrollbar with improved styling
        canvas_frame = ttk.Frame(results_frame)
        canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind("<MouseWheel>", _on_mousewheel)

        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def _format_text_as_bullets(self, text_list: List[str], max_bullets: int = 5) -> str:
        """Formats a list of strings into a bulleted list."""
        if not text_list:
            return "- No information available.\n"
        
        output = ""
        for item in text_list[:max_bullets]:
            output += f"• {item}\n"
        return output



    def run_analysis(self) -> None:
        """Runs the analysis based on user input and displays the results."""
        your_hero = self.your_hero_combo.get()
        
        enemy_heroes = [
            self.enemy_hero_1.get(),
            self.enemy_hero_2.get(),
            self.enemy_hero_3.get(),
            self.enemy_hero_4.get(),
            self.enemy_hero_5.get(),
        ]
        enemy_heroes = sorted(list(set(h for h in enemy_heroes if h)))  # Filter out empty and duplicate selections

        if not your_hero or not enemy_heroes:
            # Clear previous results and show error
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            error_label = ttk.Label(self.scrollable_frame, text="Please select your hero and at least one enemy hero.")
            error_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
            return

        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # --- Get and display results ---
        row_counter = 0

        # 1. Item Suggestions
        item_advice = self.analyzer.get_item_suggestions(enemy_heroes)
        item_frame = ttk.LabelFrame(self.scrollable_frame, text="🛡️ Item Suggestions", padding=15)
        item_frame.grid(row=row_counter, column=0, sticky='ew', padx=10, pady=8)
        item_frame.columnconfigure(0, weight=1)
        row_counter += 1

        if item_advice:
            for i, (item, heroes) in enumerate(item_advice.items()):
                unique_heroes = sorted(list(set(heroes)))
                label = ttk.Label(
                    item_frame, 
                    text=f"• {item}: Recommended against {', '.join(unique_heroes)}",
                    font=("Segoe UI", 10),
                    wraplength=1000
                )
                label.grid(row=i, column=0, sticky='w', pady=2)
        else:
            ttk.Label(
                item_frame, 
                text="No specific item counters found.",
                font=("Segoe UI", 10),
                foreground="gray"
            ).grid(row=0, column=0, sticky='w')

        # 2. Strategic Tips for your hero
        your_hero_frame = ttk.LabelFrame(self.scrollable_frame, text=f"⚡ Tips for {your_hero}", padding=15)
        your_hero_frame.grid(row=row_counter, column=0, sticky='ew', padx=10, pady=8)
        your_hero_frame.columnconfigure(0, weight=1)
        row_counter += 1
        your_hero_tips = self.analyzer.get_strategic_tips(your_hero)
        if your_hero_tips:
            for i, tip in enumerate(your_hero_tips[:5]):
                label = ttk.Label(
                    your_hero_frame, 
                    text=f"• {tip}", 
                    wraplength=1000, 
                    justify=tk.LEFT,
                    font=("Segoe UI", 10)
                )
                label.grid(row=i, column=0, sticky='w', pady=2)
        else:
            ttk.Label(
                your_hero_frame, 
                text="No tips found.",
                font=("Segoe UI", 10),
                foreground="gray"
            ).grid(row=0, column=0, sticky='w')

        # 3. Counter Tips for enemies
        counter_tips = self.analyzer.get_counter_tips(enemy_heroes)
        if counter_tips:
            for hero, tips in counter_tips.items():
                hero_frame = ttk.LabelFrame(self.scrollable_frame, text=f"🎯 How to Counter {hero}", padding=15)
                hero_frame.grid(row=row_counter, column=0, sticky='ew', padx=10, pady=8)
                hero_frame.columnconfigure(1, weight=1)
                row_counter += 1

                # Display hero image
                hero_info = self.data_manager.hero_name_map.get(hero)
                if hero_info and hero_info.get('image_path'):
                    try:
                        image_path = os.path.join(self.data_manager.data_path, hero_info['image_path'])
                        img = Image.open(image_path).resize((80, 45), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        img_label = ttk.Label(hero_frame, image=photo)
                        img_label.image = photo  # Keep reference
                        img_label.grid(row=0, column=0, rowspan=len(tips[:3]), padx=(0, 15), sticky='n')
                    except Exception as e:
                        print(f"Error loading image for {hero}: {e}")

                # Display tips
                for i, tip in enumerate(tips[:3]):
                    label = ttk.Label(
                        hero_frame, 
                        text=f"• {tip}", 
                        wraplength=900, 
                        justify=tk.LEFT,
                        font=("Segoe UI", 10)
                    )
                    label.grid(row=i, column=1, sticky='w', pady=2)