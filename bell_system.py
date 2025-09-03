import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pygame
import json
import os
from datetime import datetime, time, timedelta
import threading
import sys
from pathlib import Path

class ModernBellSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("School Bell System - By LUIS F.")
        self.root.geometry("1200x1000")
        self.root.configure(bg='#0a0e14')
        
        self.colors = {
            'primary': '#1f6feb',       
            'secondary': '#388bfd',     
            'accent': '#58a6ff',        
            'danger': '#f85149',        
            'dark': '#0a0e14',         
            'darker': '#010409',       
            'card': '#161b22',          
            'surface': '#16202F',       
            'border': '#30363d',        
            'text_primary': '#f0f6fc',  
            'text_secondary': '#7d8590',
            'text_muted': '#656d76',    
            'success': '#3fb950',       
            'warning': '#d29922',       
            'error': '#da3633'          
        }
        
        
        pygame.mixer.init()
        
        
        self.schedules = {
            'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [], 
            'Friday': [], 'Saturday': [], 'Sunday': []
        }
        self.bell_sound_path = ""
        self.system_running = True
        self.current_page = "schedule"
        
       
        self.current_computer_day = datetime.now().strftime("%A")
        
        
        self.load_settings()
        
        self.setup_modern_gui()
        self.show_page("schedule")
        
       
        self.bell_thread = threading.Thread(target=self.monitor_bells, daemon=True)
        self.bell_thread.start()
    
    def setup_modern_gui(self):
        main_frame = tk.Frame(self.root, bg=self.colors['dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.create_header(main_frame)
        
        self.create_navigation(main_frame)
        
        self.content_frame = tk.Frame(main_frame, bg=self.colors['dark'])
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        self.pages = {}
        self.create_schedule_page()
        self.create_settings_page()
        self.create_status_page()
    
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['dark'], height=90, relief=tk.FLAT, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="🔔", 
            font=('Segoe UI', 24, 'bold'),
            fg=self.colors['text_primary'], 
            bg=self.colors['dark']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.status_frame = tk.Frame(header_frame, bg=self.colors['dark'])
        self.status_frame.pack(side=tk.RIGHT, padx=20, pady=20)
        
        self.status_indicator = tk.Label(
            self.status_frame,
            text="● ACTIVE",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['success'],
            bg=self.colors['dark']
        )
        self.status_indicator.pack()
        
        self.time_label = tk.Label(
            self.status_frame,
            text="",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        )
        self.time_label.pack()
        
        self.day_label = tk.Label(
            self.status_frame,
            text=f"Today: {self.current_computer_day}",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_secondary'],
            bg=self.colors['surface']
        )
        self.day_label.pack()
        
        self.next_bell_label = tk.Label(
            self.status_frame,
            text="Loading next bell...",
            font=('Segoe UI', 9),
            fg=self.colors['text_muted'],
            bg=self.colors['surface']
        )
        self.next_bell_label.pack()
        
        self.update_time_display()
    
    def create_navigation(self, parent):
        nav_frame = tk.Frame(parent, bg=self.colors['dark'])
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        nav_buttons = [
            ("📅 Schedule", "schedule"),
            ("⚙️ Settings", "settings"), 
            ("📊 Status", "status")
        ]
        
        for text, page in nav_buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['dark'],
                activebackground=self.colors['primary'],
                activeforeground=self.colors['text_primary'],
                relief=tk.FLAT,
                padx=20,
                pady=10,
                bd=2,
                command=lambda p=page: self.show_page(p)
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
            
            def on_enter(e, button=btn):
                button.configure(bg=self.colors['primary'])
            def on_leave(e, button=btn):
                button.configure(bg=self.colors['dark'])
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def create_schedule_page(self):
        page = tk.Frame(self.content_frame, bg=self.colors['dark'])
        self.pages["schedule"] = page
        
        title = tk.Label(
            page, 
            text="Bell Schedule Management", 
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        )
        title.pack(pady=(0, 20))
        
        day_frame = tk.LabelFrame(
            page, 
            text=" Select Day ", 
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        day_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.selected_day = tk.StringVar(value=self.current_computer_day)
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        day_buttons_frame = tk.Frame(day_frame, bg=self.colors['dark'])
        day_buttons_frame.pack(pady=15)
        
        for day in days:
            btn = tk.Radiobutton(
                day_buttons_frame,
                text=day,
                variable=self.selected_day,
                value=day,
                font=('Segoe UI', 10),
                bg=self.colors['dark'],
                fg=self.colors['text_secondary'],
                activebackground=self.colors['card'],
                activeforeground=self.colors['text_primary'],
                selectcolor=self.colors['text_primary'],
                command=self.refresh_schedule_display
            )
            btn.pack(side=tk.LEFT, padx=10)
        
        for widget in day_buttons_frame.winfo_children():
            if isinstance(widget, tk.Radiobutton) and widget.cget("text") == self.current_computer_day:
                widget.configure(fg=self.colors['primary'], font=('Segoe UI', 10, 'bold'))
        
        add_frame = tk.LabelFrame(
            page,
            text=" Add New Bell ",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        add_frame.pack(fill=tk.X, pady=(0, 20))
        
        input_frame = tk.Frame(add_frame, bg=self.colors['dark'])
        input_frame.pack(pady=15)
        
        time_label_frame = tk.Frame(input_frame, bg=self.colors['dark'])
        time_label_frame.grid(row=0, column=0, padx=10, sticky='w')
        
        tk.Label(
            time_label_frame, 
            text="Time (24hr):", 
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        ).pack()
        
        time_input_frame = tk.Frame(input_frame, bg=self.colors['dark'])
        time_input_frame.grid(row=0, column=1, padx=10)
        
        self.time_entry = tk.Entry(
            time_input_frame,
            font=('Segoe UI', 12, 'bold'),
            width=8,
            relief=tk.FLAT,
            bd=5,
            justify='center',
            bg=self.colors['surface'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary']
        )
        self.time_entry.pack()
        self.time_entry.insert(0, "08:00")
        
        tk.Label(
            input_frame, 
            text="Description:", 
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        ).grid(row=0, column=2, padx=10, sticky='w')
        
        self.desc_entry = tk.Entry(
            input_frame,
            font=('Segoe UI', 10),
            width=20,
            relief=tk.FLAT,
            bd=5,
            bg=self.colors['surface'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary']
        )
        self.desc_entry.grid(row=0, column=3, padx=10)
        
        add_btn = tk.Button(
            input_frame,
            text="➕ Add Bell",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['primary'],
            activebackground=self.colors['darker'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.add_bell_time
        )
        add_btn.grid(row=0, column=4, padx=15)
        
        self.create_schedule_table(page)
    
    def create_schedule_table(self, parent):
        table_frame = tk.LabelFrame(
            parent,
            text="Current Schedule",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Dark.Treeview", 
                       background=self.colors['surface'],
                       foreground=self.colors['text_primary'],
                       rowheight=30,
                       fieldbackground=self.colors['surface'],
                       borderwidth=0,
                       relief="flat")
        
        style.configure("Dark.Treeview.Heading",
                       font=('Segoe UI', 10, 'bold'),
                       background=self.colors['primary'],
                       foreground=self.colors['text_primary'],
                       relief="flat",
                       borderwidth=1)
        
        style.map("Dark.Treeview",
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['text_primary'])])
        
        style.map("Dark.Treeview.Heading",
                 background=[('active', self.colors['secondary'])])
        
        columns = ('Time', 'Description')
        self.schedule_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show='headings',
            style="Dark.Treeview"
        )
        
        self.schedule_tree.heading('Time', text='🕐 Time (24hr)')
        self.schedule_tree.heading('Description', text='📝 Description')
        
        self.schedule_tree.column('Time', width=150, anchor='center')
        self.schedule_tree.column('Description', width=300)
        
        self.schedule_tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        delete_btn = tk.Button(
            table_frame,
            text="🗑️ Remove Selected",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['danger'],
            activebackground=self.colors['error'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.remove_selected_bell
        )
        delete_btn.pack(pady=(0, 15))
    
    def create_settings_page(self):
        page = tk.Frame(self.content_frame, bg=self.colors['dark'])
        self.pages["settings"] = page
        
        title = tk.Label(
            page, 
            text="System Settings", 
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        )
        title.pack(pady=(0, 30))
        
        sound_frame = tk.LabelFrame(
            page,
            text=" 🔊 Bell Sound Configuration ",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        sound_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        current_frame = tk.Frame(sound_frame, bg=self.colors['dark'])
        current_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            current_frame,
            text="Current Bell Sound:",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        ).pack(anchor='w', padx=20)
        
        self.sound_label = tk.Label(
            current_frame,
            text=self.get_sound_filename() or "No sound selected",
            font=('Segoe UI', 11),
            fg=self.colors['success'] if self.bell_sound_path else self.colors['danger'],
            bg=self.colors['dark']
        )
        self.sound_label.pack(anchor='w', padx=40, pady=(5, 0))
        
        btn_frame = tk.Frame(sound_frame, bg=self.colors['dark'])
        btn_frame.pack(pady=(0, 20))
        
        select_btn = tk.Button(
            btn_frame,
            text="📁 Select Bell Sound",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['primary'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.select_bell_sound
        )
        select_btn.pack(side=tk.LEFT, padx=10)
        
        test_btn = tk.Button(
            btn_frame,
            text="▶️ Test Sound",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['accent'],
            activebackground=self.colors['secondary'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=20,
            pady=10,
            command=self.test_bell_sound
        )
        test_btn.pack(side=tk.LEFT, padx=10)
        
        manual_frame = tk.LabelFrame(
            page,
            text=" 🚨 Manual Controls ",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        manual_frame.pack(fill=tk.X, pady=(0, 20), padx=20)
        
        manual_btn = tk.Button(
            manual_frame,
            text="🔔 RING BELL NOW",
            font=('Segoe UI', 16, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['danger'],
            activebackground=self.colors['error'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=40,
            pady=15,
            command=self.manual_bell_ring
        )
        manual_btn.pack(pady=20)
        
        info_frame = tk.LabelFrame(
            page,
            text=" ℹ️ System Information ",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        info_canvas = tk.Canvas(
            info_frame,
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            height=120
        )
        
        style = ttk.Style()
        style.configure("Dark.Vertical.TScrollbar",
                       background=self.colors['surface'],
                       troughcolor=self.colors['border'],
                       bordercolor=self.colors['border'],
                       arrowcolor=self.colors['text_secondary'],
                       darkcolor=self.colors['surface'],
                       lightcolor=self.colors['surface'])
        
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=info_canvas.yview, style="Dark.Vertical.TScrollbar")
        info_scrollable_frame = tk.Frame(info_canvas, bg=self.colors['dark'])
        
        info_scrollable_frame.bind(
            "<Configure>",
            lambda e: info_canvas.configure(scrollregion=info_canvas.bbox("all"))
        )
        
        info_canvas.create_window((0, 0), window=info_scrollable_frame, anchor="nw")
        info_canvas.configure(yscrollcommand=info_scrollbar.set)
        
        info_text = tk.Text(
            info_scrollable_frame,
            font=('Segoe UI', 10),
            bg=self.colors['surface'],
            fg=self.colors['text_secondary'],
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD,
            width=150,
            height=10,
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['primary'],
            selectforeground=self.colors['text_primary']
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_content = """        
Copyright 2025 LUIS F. BARRERA LOPEZ

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
                
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        info_canvas.pack(side="left", fill=tk.BOTH, expand=True, padx=5, pady=5)
        info_scrollbar.pack(side="right", fill="y")
        
        def _on_mousewheel(event):
            info_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        info_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def create_status_page(self):
        page = tk.Frame(self.content_frame, bg=self.colors['dark'])
        self.pages["status"] = page
        
        title = tk.Label(
            page, 
            text="System Status & Activity Log", 
            font=('Segoe UI', 18, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark']
        )
        title.pack(pady=(0, 20))
        
        status_container = tk.Frame(page, bg=self.colors['dark'])
        status_container.pack(fill=tk.X, pady=(0, 20))
        
        sys_card = tk.Frame(
            status_container,
            bg=self.colors['success'],
            relief=tk.FLAT,
            bd=2
        )
        sys_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            sys_card,
            text="System Status",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['success']
        ).pack(pady=(15, 5))
        
        tk.Label(
            sys_card,
            text="🟢 RUNNING",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['success']
        ).pack(pady=(0, 15))
        
        bell_card = tk.Frame(
            status_container,
            bg=self.colors['primary'],
            relief=tk.FLAT,
            bd=2
        )
        bell_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(
            bell_card,
            text="Total Bells",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['primary']
        ).pack(pady=(15, 5))
        
        self.bell_count_label = tk.Label(
            bell_card,
            text=str(self.get_total_bells()),
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['primary']
        )
        self.bell_count_label.pack(pady=(0, 15))
        
        sound_card = tk.Frame(
            status_container,
            bg=self.colors['accent'],
            relief=tk.FLAT,
            bd=2
        )
        sound_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            sound_card,
            text="Bell Sound",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['accent']
        ).pack(pady=(15, 5))
        
        self.sound_status_label = tk.Label(
            sound_card,
            text="✅ READY" if self.bell_sound_path else "❌ NOT SET",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['accent']
        )
        self.sound_status_label.pack(pady=(0, 15))
        
        day_card = tk.Frame(
            status_container,
            bg=self.colors['surface'],
            relief=tk.FLAT,
            bd=2
        )
        day_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            day_card,
            text="Today Is",
            font=('Segoe UI', 12, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        ).pack(pady=(15, 5))
        
        self.day_status_label = tk.Label(
            day_card,
            text=self.current_computer_day,
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['surface']
        )
        self.day_status_label.pack(pady=(0, 15))
        
        log_frame = tk.LabelFrame(
            page,
            text=" 📝 Activity Log ",
            font=('Segoe UI', 14, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['dark'],
            relief=tk.FLAT,
            bd=2
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        log_container = tk.Frame(log_frame, bg=self.colors['card'])
        log_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.log_text = tk.Text(
            log_container,
            font=('Consolas', 9),
            bg=self.colors['darker'],
            fg='#58a6ff',  
            relief=tk.FLAT,
            bd=10,
            wrap=tk.WORD,
            insertbackground='#58a6ff',
            selectbackground=self.colors['primary'],
            selectforeground=self.colors['text_primary']
        )
        
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview, style="Dark.Vertical.TScrollbar")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        clear_btn = tk.Button(
            log_frame,
            text="🧹 Clear Log",
            font=('Segoe UI', 10, 'bold'),
            fg=self.colors['text_primary'],
            bg=self.colors['danger'],
            activebackground=self.colors['error'],
            activeforeground=self.colors['text_primary'],
            relief=tk.FLAT,
            padx=15,
            pady=5,
            command=self.clear_log
        )
        clear_btn.pack(pady=(0, 15))
        
        self.add_to_log("System initialized successfully")
        self.add_to_log(f"Bell sound: {self.get_sound_filename() or 'Not configured'}")
        self.add_to_log(f"Today is {self.current_computer_day}")
    
    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name
            
            if page_name == "schedule":
                self.refresh_schedule_display()
            elif page_name == "status":
                self.update_status_cards()
    
    def add_bell_time(self):
        time_str = self.time_entry.get().strip()
        description = self.desc_entry.get().strip() or "Bell"
        day = self.selected_day.get()
        
        try:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            hour = time_obj.hour
            
            if hour < 12:
                period = "Morning"
            elif hour < 17:
                period = "Afternoon"
            else:
                period = "Evening"
                
        except ValueError:
            messagebox.showerror("Invalid Time Format", 
                               "Please use 24-hour format (HH:MM):\n\n" +
                               "Morning: 06:00, 08:30, 11:45\n" +
                               "Afternoon: 12:00, 13:30, 16:15\n" +
                               "Evening: 17:00, 19:30, 22:00")
            return
        
        for bell in self.schedules[day]:
            if bell['time'] == time_str:
                messagebox.showwarning("Duplicate Time", 
                                     f"A bell is already scheduled at {time_str} on {day}")
                return
        
        self.schedules[day].append({
            'time': time_str,
            'description': description
        })
        
        self.schedules[day].sort(key=lambda x: x['time'])
        
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "08:00")
        self.desc_entry.delete(0, tk.END)
        
        self.refresh_schedule_display()
        self.save_settings()
        
        self.add_to_log(f"Added bell: {time_str} - {description} ({day})")
        
        messagebox.showinfo("Bell Added", 
                           f"✅ Bell added successfully!\n\n" +
                           f"Day: {day}\n" +
                           f"Time: {time_str} ({period})\n" +
                           f"Description: {description}")
    
    def remove_selected_bell(self):
        selection = self.schedule_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bell to remove")
            return
        
        item = self.schedule_tree.item(selection[0])
        time_display = item['values'][0]
        time_to_remove = time_display.split(' ')[0]
        day = self.selected_day.get()
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                              f"Remove bell at {time_to_remove} on {day}?"):
            self.schedules[day] = [bell for bell in self.schedules[day] 
                                  if bell['time'] != time_to_remove]
            
            self.refresh_schedule_display()
            self.save_settings()
            
            self.add_to_log(f"Removed bell: {time_to_remove} ({day})")
    
    def refresh_schedule_display(self):
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        day = self.selected_day.get()
        for bell in self.schedules[day]:
            time_str = bell['time']
            description = bell['description']
            
            hour = int(time_str.split(':')[0])
            if hour < 12:
                time_display = f"{time_str} (Morning)"
                tag = 'morning'
            elif hour < 17:
                time_display = f"{time_str} (Afternoon)"
                tag = 'afternoon'
            else:
                time_display = f"{time_str} (Evening)"
                tag = 'evening'
            
            item = self.schedule_tree.insert('', tk.END, values=(
                time_display, description
            ), tags=(tag,))
        
        self.schedule_tree.tag_configure('morning', background=self.colors['primary'], foreground=self.colors['text_primary'])
        self.schedule_tree.tag_configure('afternoon', background=self.colors['accent'], foreground=self.colors['text_primary'])
        self.schedule_tree.tag_configure('evening', background=self.colors['secondary'], foreground=self.colors['text_primary'])
        
        if day == self.current_computer_day:
            for widget in self.pages["schedule"].winfo_children():
                if isinstance(widget, tk.LabelFrame) and "Current Schedule" in widget.cget("text"):
                    widget.configure(text=f"Current Schedule")
    
    def select_bell_sound(self):
        file_path = filedialog.askopenfilename(
            title="Select Bell Sound File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.ogg *.m4a *.aac"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.bell_sound_path = file_path
            self.sound_label.config(
                text=self.get_sound_filename(),
                fg=self.colors['success']
            )
            self.save_settings()
            self.add_to_log(f"Bell sound updated: {self.get_sound_filename()}")
            
            if self.current_page == "status":
                self.update_status_cards()
    
    def test_bell_sound(self):
        if not self.bell_sound_path or not os.path.exists(self.bell_sound_path):
            messagebox.showerror("No Sound", "Please select a bell sound file first")
            return
        
        try:
            pygame.mixer.music.load(self.bell_sound_path)
            pygame.mixer.music.play()
            self.add_to_log("Testing bell sound...")
            
            messagebox.showinfo("Sound Test", "Playing bell sound...")
        except Exception as e:
            messagebox.showerror("Sound Error", f"Could not play sound file:\n{str(e)}")
            self.add_to_log(f"Sound test failed: {str(e)}")
    
    def manual_bell_ring(self):
        if not self.bell_sound_path or not os.path.exists(self.bell_sound_path):
            messagebox.showerror("No Sound", "Please select a bell sound file first")
            return
        
        try:
            pygame.mixer.music.load(self.bell_sound_path)
            pygame.mixer.music.play()
            self.add_to_log("MANUAL BELL TRIGGERED")
            
            messagebox.showinfo("Bell Ringing", "🔔 Bell is ringing manually!")
        except Exception as e:
            messagebox.showerror("Bell Error", f"Could not ring bell:\n{str(e)}")
            self.add_to_log(f"Manual bell failed: {str(e)}")
    
    def monitor_bells(self):
        """Enhanced background thread to monitor and trigger bells using system time"""
        last_triggered_times = {}
        
        while self.system_running:
            try:
                now = datetime.now()
                current_time_str = now.strftime("%H:%M")
                current_day = now.strftime("%A")
                
                if current_day != self.current_computer_day:
                    self.current_computer_day = current_day
                    self.root.after(0, self.update_day_display)
                
                today_schedule = self.schedules.get(current_day, [])
                
                for bell in today_schedule:
                    bell_time_str = bell['time']
                    
                    if current_time_str == bell_time_str:
                        bell_key = f"{current_day}_{bell_time_str}"
                        last_triggered = last_triggered_times.get(bell_key, datetime.min)
                        
                        if (now - last_triggered).total_seconds() > 55:
                            if self.bell_sound_path and os.path.exists(self.bell_sound_path):
                                try:
                                    pygame.mixer.music.load(self.bell_sound_path)
                                    pygame.mixer.music.play()
                                    
                                    last_triggered_times[bell_key] = now
                                    
                                    period = self.get_time_period(bell_time_str)
                                    log_msg = f"🔔 BELL RANG: {bell['description']} at {bell_time_str} ({period})"
                                    self.add_to_log(log_msg)
                                    
                                    if hasattr(self, 'current_page') and self.current_page == "status":
                                        self.update_status_cards()
                                        
                                except Exception as e:
                                    self.add_to_log(f"❌ ERROR ringing bell: {str(e)}")
                            else:
                                self.add_to_log(f"⚠️ Bell scheduled but no sound file: {bell['description']} at {bell_time_str}")
                
                self.update_next_bell_info()
                
                threading.Event().wait(1)
                
            except Exception as e:
                self.add_to_log(f"⚠️ Monitor error: {str(e)}")
                threading.Event().wait(60)
    
    def update_day_display(self):
        if hasattr(self, 'day_label'):
            self.day_label.config(text=f"Today: {self.current_computer_day}")
        
        if hasattr(self, 'day_status_label'):
            self.day_status_label.config(text=self.current_computer_day)
        
        if hasattr(self, 'selected_day') and self.selected_day.get() == self.current_computer_day:
            self.refresh_schedule_display()
    
    def get_time_period(self, time_str):
        hour = int(time_str.split(':')[0])
        if hour < 12:
            return "Morning"
        elif hour < 17:
            return "Afternoon"
        else:
            return "Evening"
    
    def update_next_bell_info(self):
        try:
            now = datetime.now()
            current_time = now.time()
            current_day = now.strftime("%A")
            
            today_schedule = self.schedules.get(current_day, [])
            next_bells = []
            
            for bell in today_schedule:
                bell_time = datetime.strptime(bell['time'], "%H:%M").time()
                if bell_time > current_time:
                    next_bells.append(bell)
            
            if next_bells:
                next_bell = next_bells[0]
                next_time = next_bell['time']
                next_desc = next_bell['description']
                period = self.get_time_period(next_time)
                
                if hasattr(self, 'next_bell_label'):
                    self.next_bell_label.config(
                        text=f"Next: {next_time} ({period}) - {next_desc}"
                    )
            else:
                tomorrow = (now + timedelta(days=1)).strftime("%A")
                tomorrow_schedule = self.schedules.get(tomorrow, [])
                
                if tomorrow_schedule:
                    first_bell = tomorrow_schedule[0]
                    if hasattr(self, 'next_bell_label'):
                        self.next_bell_label.config(
                            text=f"Next: Tomorrow {first_bell['time']} - {first_bell['description']}"
                        )
                else:
                    if hasattr(self, 'next_bell_label'):
                        self.next_bell_label.config(text="No upcoming bells scheduled")
                    
        except Exception as e:
            if hasattr(self, 'next_bell_label'):
                self.next_bell_label.config(text="Error checking schedule")
    
    def update_time_display(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        if hasattr(self, 'time_label'):
            self.time_label.config(text=f"{current_time}")
        
        if now.second == 0:
            self.update_next_bell_info()
        
        self.root.after(1000, self.update_time_display)
    
    def get_sound_filename(self):
        if self.bell_sound_path:
            return os.path.basename(self.bell_sound_path)
        return None
    
    def get_total_bells(self):
        total = 0
        for day_schedule in self.schedules.values():
            total += len(day_schedule)
        return total
    
    def update_status_cards(self):
        if hasattr(self, 'bell_count_label'):
            self.bell_count_label.config(text=str(self.get_total_bells()))
        
        if hasattr(self, 'sound_status_label'):
            self.sound_status_label.config(
                text="✅ READY" if self.bell_sound_path else "❌ NOT SET"
            )
        
        if hasattr(self, 'day_status_label'):
            self.day_status_label.config(text=self.current_computer_day)
    
    def add_to_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        def update_log():
            if hasattr(self, 'log_text'):
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
        
        self.root.after(0, update_log)
    
    def clear_log(self):
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            self.add_to_log("Log cleared")
    
    def save_settings(self):
        settings = {
            'schedules': self.schedules,
            'bell_sound_path': self.bell_sound_path
        }
        
        try:
            config_file = Path('bell_system_config.json')
            with open(config_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.add_to_log(f"Error saving settings: {str(e)}")
    
    def load_settings(self):
        try:
            config_file = Path('bell_system_config.json')
            if config_file.exists():
                with open(config_file, 'r') as f:
                    settings = json.load(f)
                
                self.schedules = settings.get('schedules', self.schedules)
                self.bell_sound_path = settings.get('bell_sound_path', '')
                
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
    
    def on_closing(self):
        self.system_running = False
        self.save_settings()
        self.root.destroy()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernBellSystem(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    try:
        root.iconbitmap(default='bell.ico')
    except:
        pass
    
    root.mainloop()