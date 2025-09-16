#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core analysis logic for the Dota 2 Draft Analyzer.
Handles data management and strategic analysis.
"""

import json
import os
from typing import Dict, List, Any, Optional


class DataManager:
    """Manages loading and accessing all game data from the data directory."""

    def __init__(self, data_path: str = 'data') -> None:
        self.data_path: str = data_path
        self.heroes: List[Dict[str, Any]] = []
        self.hero_strategies: Dict[str, Dict[str, Any]] = {}
        self.normalized_heroes: List[Dict[str, Any]] = []
        self.hero_name_map: Dict[str, Dict[str, str]] = {}

        self._load_all_data()

    def _load_json(self, file_name: str) -> Optional[Any]:
        """Loads a JSON file from the data path."""
        path = os.path.join(self.data_path, file_name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {path} not found.")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {path}.")
        return None

    def _load_all_data(self) -> None:
        """Loads all necessary data files into memory."""
        print("Loading game data...")
        self.heroes = self._load_json('heroes.json') or []
        self.normalized_heroes = self._load_json('normalized_heroes.json') or []

        # Create a mapping from display name to a dict with safe_name and image_path
        self.hero_name_map = {
            hero['name']: {'safe_name': hero['safe_name'], 'image_path': hero.get('image_path', '')}
            for hero in self.normalized_heroes if 'name' in hero and 'safe_name' in hero
        }

        # Load individual hero strategy files
        strategy_path = os.path.join(self.data_path, 'howdoiplay_json')
        if os.path.isdir(strategy_path):
            for filename in os.listdir(strategy_path):
                if filename.endswith('.json'):
                    # The filename is the safe_name
                    safe_hero_name = filename.replace('.json', '')
                    strategy_data = self._load_json(os.path.join('howdoiplay_json', filename))
                    if strategy_data:
                        self.hero_strategies[safe_hero_name] = strategy_data
        
        print(f"Loaded {len(self.heroes)} heroes.")
        print(f"Loaded normalized data for {len(self.normalized_heroes)} heroes.")
        print(f"Loaded strategies for {len(self.hero_strategies)} heroes.")


# List of common items to check for in counter tips.
COUNTER_ITEMS = [
    # --- Core Defensive & Dispel Items ---
    "Black King Bar",       # Magic immunity
    "Linken's Sphere",      # Block single-target spells
    "Lotus Orb",            # Reflect single-target spells
    "Manta Style",          # Dispel debuffs, dodge projectiles
    "Aeon Disk",            # Survive burst damage
    "Guardian Greaves",     # AoE dispel and heal/mana restore
    "Satanic",              # Strong dispel and lifesteal

    # --- Evasion & Disarm ---
    "Heaven's Halberd",     # Disarm ranged/melee attackers
    "Butterfly",            # Evasion
    "Solar Crest",          # Evasion and armor reduction

    # --- Control & Lockdown ---
    "Scythe of Vyse",       # Hex (hard disable)
    "Abyssal Blade",        # Stun
    "Gleipnir",             # AoE root (from Rod of Atos)
    "Rod of Atos",          # Root
    
    # --- Silence & Mana Burn ---
    "Orchid Malevolence",   # Silence
    "Bloodthorn",           # Silence with crit
    "Diffusal Blade",       # Mana burn and slow

    # --- Vision & Invisibility Counter ---
    "Gem of True Sight",
    "Sentry Ward",
    "Dust of Appearance",
    "Monkey King Bar",      # True Strike against evasion

    # --- Damage Mitigation & Armor ---
    "Blade Mail",           # Return damage
    "Ghost Scepter",        # Ethereal form (immune to physical)
    "Eul's Scepter of Divinity", # Cyclone to dodge/disable
    "Pipe of Insight",      # Magic resistance barrier
    "Eternal Shroud",       # Magic resistance and mana from damage
    "Assault Cuirass",      # Armor aura
    "Crimson Guard",        # Damage block against physical attacks
    "Shiva's Guard",        # Armor and attack speed slow aura
    "Eye of Skadi",         # Slow and reduces health regen

    # --- Break & Special Counters ---
    "Silver Edge",          # Break passive abilities
    "Khanda",               # Break passive abilities (from Phylactery)
    "Nullifier",            # Continuously dispels buffs
    "Spirit Vessel",        # Reduces health regen
    
    # --- Positional & Escape ---
    "Force Staff",          # Reposition self or others
    "Hurricane Pike",       # Reposition and attack from distance
    "Blink Dagger",         # Instant positioning

    # --- Specific Hero Counters ---
    "Dagon",                # Burst damage, creep kill for Tinker
    "Hand of Midas"         # Instakill creeps
]


class AnalysisCore:
    """Handles the logic for analyzing hero picks and generating advice."""

    def __init__(self, data_manager: DataManager) -> None:
        self.data_manager = data_manager

    def get_item_suggestions(self, enemy_heroes: List[str]) -> Dict[str, List[str]]:
        """ 
        Analyzes enemy heroes and suggests items to counter them.
        Returns a dictionary mapping item names to a list of heroes they counter.
        """
        item_suggestions: Dict[str, List[str]] = {}

        for hero_name in enemy_heroes:
            hero_info = self.data_manager.hero_name_map.get(hero_name)
            if not hero_info:
                continue

            strategy = self.data_manager.hero_strategies.get(hero_info['safe_name'])
            if not strategy or 'counter_tips' not in strategy['strategies']:
                continue

            counter_tips_text = ' '.join(strategy['strategies']['counter_tips']).lower()

            for item in COUNTER_ITEMS:
                if item.lower() in counter_tips_text:
                    if item not in item_suggestions:
                        item_suggestions[item] = []
                    if hero_name not in item_suggestions[item]:
                        item_suggestions[item].append(hero_name)
        
        return item_suggestions

    def get_strategic_tips(self, your_hero: str) -> List[str]:
        """Gets general strategy tips for the player's chosen hero."""
        hero_info = self.data_manager.hero_name_map.get(your_hero)
        if not hero_info:
            return []
        strategy = self.data_manager.hero_strategies.get(hero_info['safe_name'])
        if strategy and 'general_tips' in strategy['strategies']:
            return strategy['strategies']['general_tips']
        return []

    def get_counter_tips(self, enemy_heroes: List[str]) -> Dict[str, List[str]]:
        """Gets tips on how to counter a list of enemy heroes."""
        counter_tips: Dict[str, List[str]] = {}
        for hero_name in enemy_heroes:
            hero_info = self.data_manager.hero_name_map.get(hero_name)
            if not hero_info:
                continue

            strategy = self.data_manager.hero_strategies.get(hero_info['safe_name'])
            if strategy and 'counter_tips' in strategy['strategies']:
                counter_tips[hero_name] = strategy['strategies']['counter_tips']
        return counter_tips