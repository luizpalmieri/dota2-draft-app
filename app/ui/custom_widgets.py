#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Custom UI widgets for the Dota 2 Draft Analyzer.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable


class AutocompleteCombobox(ttk.Entry):
    """A custom ttk.Entry widget with autocompletion functionality."""

    def __init__(self, parent: tk.Widget, completion_list: List[str], *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self._completion_list: List[str] = sorted(completion_list)
        self._hits: List[str] = []
        self._hit_index: int = 0
        self.position: int = 0
        self.selection_callback: Optional[Callable[[str], None]] = None

        self.bind('<KeyRelease>', self.handle_keyrelease)
        self.bind('<FocusIn>', self.handle_focus_in)
        self._listbox: Optional[tk.Listbox] = None

    def handle_focus_in(self, event: tk.Event) -> None:
        """Handle the widget gaining focus."""
        if not self.get():
            self._update_autocomplete_list(show_all=True)

    def handle_keyrelease(self, event: tk.Event) -> None:
        """Event handler for the keyrelease event."""
        if event.keysym == "BackSpace":
            if self.position > 0:
                self.position -= 1
        if event.keysym == "Left":
            if self.position > 0:
                self.position -= 1
        if event.keysym == "Right":
            self.position += 1

        if len(event.keysym) == 1 or event.keysym == "BackSpace":
            self._update_autocomplete_list()

    def _update_autocomplete_list(self, show_all: bool = False) -> None:
        """Updates the autocomplete listbox based on the current entry text."""
        if self._listbox:
            self._listbox.destroy()
            self._listbox = None

        text = self.get().lower()
        
        if show_all:
            self._hits = self._completion_list
        elif text:
            self._hits = [item for item in self._completion_list if item.lower().startswith(text)]
        else:
            self._hits = []
            
        if self._hits:
            # Calculate position relative to the root window
            x_pos = self.winfo_rootx() - self.winfo_toplevel().winfo_rootx()
            y_pos = self.winfo_rooty() - self.winfo_toplevel().winfo_rooty() + self.winfo_height()

            self._listbox = tk.Listbox(self.winfo_toplevel(), font=self.cget('font'), relief='flat', highlightthickness=0)
            self._listbox.place(x=x_pos, y=y_pos, width=self.winfo_width())
            
            for item in self._hits:
                self._listbox.insert(tk.END, item)

            self._listbox.bind('<ButtonRelease-1>', self._on_listbox_select)
            self.winfo_toplevel().bind('<Button-1>', self._on_parent_click, add='+')

    def _on_listbox_select(self, event: tk.Event) -> None:
        """Event handler for listbox selection."""
        if self._listbox and self._listbox.curselection():
            selection = self._listbox.get(self._listbox.curselection())
            self.delete(0, tk.END)
            self.insert(0, selection)
            self._listbox.destroy()
            self._listbox = None
            self.icursor(tk.END)
            if self.selection_callback:
                self.selection_callback(selection)

    def show_all_options(self) -> None:
        """Public method to show all options in the listbox."""
        self._update_autocomplete_list(show_all=True)

    def _on_parent_click(self, event: tk.Event) -> None:
        """Event handler for clicks outside the widget."""
        if self._listbox:
            if event.widget != self._listbox and event.widget != self:
                self._listbox.destroy()
                self._listbox = None