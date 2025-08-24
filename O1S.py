import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser, scrolledtext
import datetime
import os
import webbrowser
import subprocess
import threading
import time
import json
import psutil
from pathlib import Path
import random
import math
import urllib.request
import shutil
import queue
import socket
import netifaces
import pygame
import glob
import platform

APPS_DIR = Path("./o1s_apps")
APPS_DIR.mkdir(exist_ok=True)
APPS_DB = Path("o1s_apps.json")
RUNNING_APPS_DB = Path("o1s_running_apps.json")
FAVORITES_DB = Path("o1s_favorites.json")
HIDDEN_APPS_DB = Path("o1s_hidden_apps.json")
INSTALLABLE_APPS_DB = Path("o1s_installable_apps.json")

def load_apps_db():
    try:
        if APPS_DB.exists():
            with open(APPS_DB, "r", encoding="utf-8") as f:
                data = json.load(f)
                apps = []
                for a in data:  # <-- добавлено: перебираем элементы из data
                    p = Path(a.get("path", ""))
                    if p.suffix == ".py" and p.exists():
                        apps.append({
                            "name": a.get("name", p.stem), 
                            "path": str(p),
                            "type": a.get("type", "gui"),
                            "version": a.get("version", "1.0"),
                            "icon": a.get("icon", "🐍")
                        })
                return apps
    except Exception as e:
        print(f"Ошибка загрузки базы приложений: {e}")
    return []

def save_apps_db(apps):
    try:
        with open(APPS_DB, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения базы приложений: {e}")

def load_running_apps():
    if RUNNING_APPS_DB.exists():
        try:
            with open(RUNNING_APPS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_running_apps(apps):
    try:
        with open(RUNNING_APPS_DB, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения запущенных приложений: {e}")

def load_favorites():
    if FAVORITES_DB.exists():
        try:
            with open(FAVORITES_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favs):
    try:
        with open(FAVORITES_DB, "w", encoding="utf-8") as f:
            json.dump(favs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения избранного: {e}")

def load_hidden_apps():
    if HIDDEN_APPS_DB.exists():
        try:
            with open(HIDDEN_APPS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_hidden_apps(apps):
    try:
        with open(HIDDEN_APPS_DB, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения скрытых приложений: {e}")

def load_installable_apps():
    try:
        if INSTALLABLE_APPS_DB.exists():
            with open(INSTALLABLE_APPS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            # Создаем базу с примерами приложений, если ее нет
            default_apps = [
                {
                    "name": "Music",
                    "description": "Проигрыватель музыки с поддержкой основных форматов",
                    "icon": "🎵",
                    "version": "1.0",
                    "size": "5.2 MB",
                    "installed": False,
                    "file_path": "apps/music.py",
                    "update_available": False
                },
                {
                    "name": "Calendar",
                    "description": "Календарь с напоминаниями и событиями",
                    "icon": "📅",
                    "version": "1.0",
                    "size": "3.1 MB",
                    "installed": False,
                    "file_path": "apps/calendar.py",
                    "update_available": False
                }
            ]
            save_installable_apps(default_apps)
            return default_apps
    except Exception as e:
        print(f"Ошибка загрузки базы установочных приложений: {e}")
        return []

def save_installable_apps(apps):
    try:
        with open(INSTALLABLE_APPS_DB, "w", encoding="utf-8") as f:
            json.dump(apps, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения базы установочных приложений: {e}")

class O1SOperatingSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("O1S Operating System v1.4")
        self.device_type = self.detect_device_type()
        self.set_window_size()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Убираем стандартные кнопки управления окном
        self.root.overrideredirect(True)
        # Позиционируем окно по центру экрана
        self.center_window()
        
        # Добавляем новые темы
        self.themes = {
            'orange': {
                'primary': '#ff7700',
                'primary_dark': '#cc5f00',
                'secondary': '#ff4040',
                'accent': '#2ecc71',
                'warning': '#f4c430',
                'background': '#f5f5f5',
                'surface': '#ffffff',
                'surface_light': '#fff0e0',
                'card': '#ffffff',
                'text': '#000000',
                'text_secondary': '#4a4a4a',
                'text_tertiary': '#7a7a7a',
                'border': '#d1d5db',
                'hidden': '#ffaa00'  # Оранжевый для скрытых приложений
            },
            'npo1s': {
                'primary': '#4A90E2',
                'primary_dark': '#2B6CB0',
                'secondary': '#FF4757',
                'accent': '#2ECC71',
                'warning': '#F4C430',
                'background': '#E8F5FD',
                'surface': 'rgba(255, 255, 255, 0.85)',
                'surface_light': 'rgba(255, 255, 255, 0.7)',
                'card': 'rgba(255, 255, 255, 0.9)',
                'text': '#2D3436',
                'text_secondary': '#6B7280',
                'text_tertiary': '#9CA3AF',
                'border': '#D1D5DB',
                'hidden': '#FFAA00'
            }
        }
        
        self.current_app = None
        self.running_apps = load_running_apps()
        self.hidden_apps = load_hidden_apps()
        self.installable_apps = load_installable_apps()
        self.notifications = []
        self.settings = self.load_settings()
        self.current_theme = self.settings.get('theme', 'npo1s')
        self.colors = self.themes[self.current_theme]
        self.root.configure(bg=self.colors['background'])
        self.windows = []
        self.processes = {}
        self.installed_apps = load_apps_db()
        self.favorites = load_favorites()
        self.python_mode = False
        # Системные настройки
        self.volume_level = 50
        self.brightness_level = 80
        self.wifi_status = self.get_wifi_status()
        self.bluetooth_status = False
        self.fullscreen_mode = False
        
        # Инициализируем pygame для музыки
        try:
            pygame.mixer.init()
        except:
            print("Не удалось инициализировать pygame mixer")
        
        # Устанавливаем системные приложения, если их нет
        self.install_system_apps()
        
        self.setup_ui()
        self.start_system_services()
    
    def detect_device_type(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Определяем тип устройства по размеру экрана
        if screen_width < 800:  # Мобильное устройство
            return 'mobile'
        elif screen_width > 1920 and screen_height > 1080:  # Телевизор/большой экран
            return 'tv'
        else:  # Стандартный ПК
            return 'pc'
    
    def set_window_size(self):
        if self.device_type == 'mobile':
            self.root.geometry("480x800")
        elif self.device_type == 'tv':
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        else:
            self.root.geometry("1400x900")
    
    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if self.device_type == 'mobile':
            width, height = 480, 800
        elif self.device_type == 'tv':
            width, height = screen_width, screen_height
        else:
            width, height = 1400, 900
            
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_closing(self):
        for app_name, process in self.processes.items():
            try:
                process.terminate()
            except:
                pass
        self.root.destroy()
    
    def load_settings(self):
        try:
            with open('o1s_settings.json', 'r', encoding="utf-8") as f:
                return json.load(f)
        except:
            return {
                'theme': 'npo1s',
                'auto_hide_dock': False,
                'notifications': True,
                'device_type': self.device_type,
                'keyboard_layout': 'en',
                'volume_level': 50,
                'brightness_level': 80
            }
    
    def save_settings(self):
        try:
            with open('o1s_settings.json', 'w', encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def apply_theme(self):
        self.colors = self.themes[self.current_theme]
        self.root.configure(bg=self.colors['background'])
        
        if hasattr(self, 'title_bar'):
            self.title_bar.configure(bg=self.colors['surface'])
        
        if hasattr(self, 'system_menu'):
            self.system_menu.configure(bg=self.colors['surface'], fg=self.colors['primary'])
        
        if hasattr(self, 'status_frame'):
            self.status_frame.configure(bg=self.colors['surface'])
        
        if hasattr(self, 'time_label'):
            self.time_label.configure(bg=self.colors['surface'], fg=self.colors['text'])
        
        if hasattr(self, 'battery_label'):
            self.battery_label.configure(bg=self.colors['surface'], fg=self.colors['accent'])
        
        if hasattr(self, 'wifi_label'):
            self.wifi_label.configure(bg=self.colors['surface'], fg=self.colors['primary'])
        
        if hasattr(self, 'notif_label'):
            self.notif_label.configure(bg=self.colors['surface'], fg=self.colors['warning'])
        
        if hasattr(self, 'desktop'):
            self.desktop.configure(bg=self.colors['background'])
        
        if hasattr(self, 'dock'):
            self.dock.configure(bg=self.colors['surface'])
        
        for window in self.windows:
            try:
                window.configure(bg=self.colors['background'])
                for child in window.winfo_children():
                    if isinstance(child, tk.Frame):
                        child.configure(bg=self.colors['background'])
                    elif isinstance(child, tk.Label):
                        child.configure(bg=self.colors['surface'], fg=self.colors['text'])
                    elif isinstance(child, tk.Button):
                        child.configure(bg=self.colors['primary'], fg='white')
            except:
                pass
    
    def setup_ui(self):
        # Создаем кастомную title bar
        self.title_bar = tk.Frame(self.root, bg=self.colors['surface'], height=44)
        self.title_bar.pack(fill='x')
        self.title_bar.pack_propagate(False)
        
        # Добавляем обработчики для перемещения окна
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.do_move)
        
        # Добавляем поиск
        search_entry = tk.Entry(self.title_bar, bg=self.colors['surface_light'], fg=self.colors['text'],
                               font=('SF Pro Display', 12), width=30)
        search_entry.pack(side='left', padx=10, pady=8)
        
        # Системные иконки справа
        status_icons = tk.Frame(self.title_bar, bg=self.colors['surface'])
        status_icons.pack(side='right')
        
        # Кнопка пользователя
        user_btn = tk.Label(status_icons, text="👤", bg=self.colors['surface'], 
                           fg=self.colors['text'], font=('SF Pro Display', 14))
        user_btn.pack(side='left', padx=5)
        
        # Дата и время
        self.time_label = tk.Label(status_icons, bg=self.colors['surface'],
                                   fg=self.colors['text'], font=('SF Pro Display', 12))
        self.time_label.pack(side='left', padx=5)
        
        # Батарея
        self.battery_label = tk.Label(status_icons, text="🔋",
                                      bg=self.colors['surface'], fg=self.colors['accent'],
                                      font=('SF Pro Display', 11))
        self.battery_label.pack(side='left', padx=5)
        
        # Wi-Fi
        self.wifi_label = tk.Label(status_icons, text="📶",
                                   bg=self.colors['surface'], fg=self.colors['primary'],
                                   font=('SF Pro Display', 11))
        self.wifi_label.pack(side='left', padx=5)
        
        # Звук
        volume_icon = tk.Label(status_icons, text="🔊",
                               bg=self.colors['surface'], fg=self.colors['primary'],
                               font=('SF Pro Display', 11))
        volume_icon.pack(side='left', padx=5)
        
        # Язык
        lang_icon = tk.Label(status_icons, text="🌐",
                             bg=self.colors['surface'], fg=self.colors['primary'],
                             font=('SF Pro Display', 11))
        lang_icon.pack(side='left', padx=5)
        
        # Клавиатура
        keyboard_icon = tk.Label(status_icons, text="⌨️",
                                 bg=self.colors['surface'], fg=self.colors['primary'],
                                 font=('SF Pro Display', 11))
        keyboard_icon.pack(side='left', padx=5)
        
        # Кнопка закрытия
        close_btn = tk.Label(self.title_bar, text="⨯", fg="#ff5f57", bg=self.colors['surface'],
                             font=('SF Pro Display', 14), cursor='hand2')
        close_btn.pack(side='right', padx=10, pady=10)
        close_btn.bind('<Button-1>', lambda e: self.on_closing())
        
        # Кнопка полноэкранного режима
        self.fullscreen_btn = tk.Label(self.title_bar, text="⛶", fg="#ffbd2e", bg=self.colors['surface'],
                             font=('SF Pro Display', 14), cursor='hand2')
        self.fullscreen_btn.pack(side='right', padx=10, pady=10)
        self.fullscreen_btn.bind('<Button-1>', lambda e: self.toggle_fullscreen())
        
        # Кнопка скрытия
        hide_btn = tk.Label(self.title_bar, text="—", fg="#ffbd2e", bg=self.colors['surface'],
                             font=('SF Pro Display', 14), cursor='hand2')
        hide_btn.pack(side='right', padx=10, pady=10)
        hide_btn.bind('<Button-1>', lambda e: self.root.iconify())
        
        self.system_menu = tk.Label(
            self.title_bar, text="◎ O1S", bg=self.colors['surface'], fg=self.colors['primary'],
            font=('SF Pro Display', 12, 'bold'), cursor='hand2', padx=10
        )
        self.system_menu.pack(side='left', padx=8, pady=8)
        self.system_menu.bind('<Button-1>', self.show_system_menu)
        
        # Рабочий стол с приложениями
        self.desktop = tk.Frame(self.root, bg=self.colors['background'])
        self.desktop.pack(fill='both', expand=True)
        
        # Добавляем приложения на рабочий стол
        self.populate_desktop()
        
        # Нижняя панель (док)
        self.dock = tk.Frame(self.root, bg=self.colors['surface'], height=80)
        self.dock.pack(side='bottom', fill='x', pady=(0, 10))
        self.dock.pack_propagate(False)
        self.setup_dock()
    
    def install_system_apps(self):
        # Проверяем, установлен ли калькулятор
        calculator_installed = any(app["name"] == "Calculator" for app in self.installed_apps)
        
        if not calculator_installed:
            # Создаем папку для калькулятора
            calc_dir = APPS_DIR / "Calculator"
            calc_dir.mkdir(exist_ok=True)
            
            # Создаем файл калькулятора
            calc_file = calc_dir / "calculator.py"
            
            calc_content = """import tkinter as tk

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Калькулятор")
        self.root.geometry("300x400")
        
        self.expression = ""
        self.result_var = tk.StringVar()
        
        self.create_ui()
    
    def create_ui(self):
        # Дисплей
        display = tk.Entry(self.root, textvariable=self.result_var, font=('Arial', 20), bd=10, 
                          relief='ridge', justify='right')
        display.pack(fill='x', padx=10, pady=10)
        
        # Кнопки
        buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['C', '0', '=', '+']
        ]
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(padx=10, pady=10)
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                btn = tk.Button(btn_frame, text=text, font=('Arial', 16), width=5, height=2,
                               bg='#f0f0f0', activebackground='#e0e0e0')
                btn.grid(row=i, column=j, padx=2, pady=2)
                btn.bind('<Button-1>', lambda e, t=text: self.button_click(t))
    
    def button_click(self, text):
        if text == 'C':
            self.expression = ""
        elif text == '=':
            try:
                result = str(eval(self.expression))
                self.expression = result
            except:
                self.expression = "Ошибка"
        else:
            self.expression += text
        
        self.result_var.set(self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
"""
            
            # Сохраняем файл
            with open(calc_file, 'w', encoding='utf-8') as f:
                f.write(calc_content)
            
            # Добавляем приложение в базу
            self.installed_apps.append({
                "name": "Calculator",
                "path": str(calc_file),
                "type": "gui",
                "version": "1.0",
                "icon": "🧮"
            })
            save_apps_db(self.installed_apps)
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_fullscreen(self):
        self.fullscreen_mode = not self.fullscreen_mode
        if self.fullscreen_mode:
            self.root.attributes('-fullscreen', True)
            self.fullscreen_btn.config(text="⛶")
        else:
            self.root.attributes('-fullscreen', False)
            self.fullscreen_btn.config(text="⛶")
    
    def populate_desktop(self):
        for widget in self.desktop.winfo_children():
            widget.destroy()
        for app in self.installed_apps:
            self.create_app_icon(self.desktop, app)
    
    def create_app_icon(self, parent, app):
        icon_frame = tk.Frame(parent, bg=self.colors['background'], width=80, height=80)
        icon_frame.pack(side='left', padx=10, pady=10)
        icon_frame.pack_propagate(False)
        
        # Запоминаем позицию иконки для анимации
        def get_position():
            x = icon_frame.winfo_rootx() + icon_frame.winfo_width() // 2
            y = icon_frame.winfo_rooty() + icon_frame.winfo_height() // 2
            return (x, y)
        
        # Проверяем, скрыто ли приложение
        is_hidden = app["name"] in self.hidden_apps
        icon_color = self.colors['hidden'] if is_hidden else self.colors['text']
        
        # Создаем контекстное меню для иконки
        icon_menu = tk.Menu(self.root, tearoff=0, bg=self.colors['surface'], fg=self.colors['text'])
        icon_menu.add_command(label="Изменить иконку", command=lambda: self.change_app_icon(app, icon_label))
        icon_menu.add_command(label="Переименовать", command=lambda: self.rename_app(app, name_label))
        icon_menu.add_separator()
        icon_menu.add_command(label="Показать/скрыть", command=lambda: self.toggle_app_visibility(app))
        
        # Обработчик для правого клика
        def on_right_click(e):
            try:
                icon_menu.tk_popup(e.x_root, e.y_root)
            finally:
                icon_menu.grab_release()
        
        # Обработчик для перетаскивания
        def start_drag(e):
            self.drag_data = {
                "x": e.x,
                "y": e.y,
                "item": icon_frame,
                "app": app
            }
        
        def drag(e):
            if hasattr(self, 'drag_data'):
                # Вычисляем смещение
                delta_x = e.x - self.drag_data["x"]
                delta_y = e.y - self.drag_data["y"]
                
                # Перемещаем иконку
                icon_frame.place(x=icon_frame.winfo_x() + delta_x, 
                                y=icon_frame.winfo_y() + delta_y)
                
                # Обновляем данные для следующего перемещения
                self.drag_data["x"] = e.x
                self.drag_data["y"] = e.y
        
        def end_drag(e):
            if hasattr(self, 'drag_data'):
                del self.drag_data
                self.save_app_positions()
        
        # Иконка приложения
        icon_label = tk.Label(icon_frame, text=app.get("icon", "🐍"), bg=self.colors['background'],
                              fg=icon_color, font=('SF Pro Display', 24), cursor='hand2')
        icon_label.pack(expand=True)
        
        # Название приложения
        name_label = tk.Label(icon_frame, text=app["name"], bg=self.colors['background'],
                              fg=icon_color, font=('SF Pro Display', 10))
        name_label.pack()
        
        # Привязываем события
        icon_label.bind('<Double-Button-1>', lambda e: self.launch_app(app, source_position=get_position()))
        icon_label.bind('<Button-3>', on_right_click)
        icon_label.bind('<ButtonPress-1>', start_drag)
        icon_label.bind('<B1-Motion>', drag)
        icon_label.bind('<ButtonRelease-1>', end_drag)
        
        name_label.bind('<Double-Button-1>', lambda e: self.launch_app(app, source_position=get_position()))
        name_label.bind('<Button-3>', on_right_click)
        name_label.bind('<ButtonPress-1>', start_drag)
        name_label.bind('<B1-Motion>', drag)
        name_label.bind('<ButtonRelease-1>', end_drag)
        
        # Сохраняем позиции иконок (простой вариант - перестановка в списке)
        self.desktop.pack_slaves().sort(key=lambda x: x.winfo_x())
    
    def change_app_icon(self, app, icon_label):
        # Открываем диалог выбора цвета
        color = colorchooser.askcolor(title="Выберите цвет иконки")
        if color[1]:
            # Обновляем иконку в базе
            for i, a in enumerate(self.installed_apps):
                if a["name"] == app["name"]:
                    self.installed_apps[i]["icon"] = color[1]
                    save_apps_db(self.installed_apps)
                    break
            
            # Обновляем отображение
            icon_label.config(fg=color[1])
            self.add_notification(f"🎨 Иконка {app['name']} изменена")
    
    def rename_app(self, app, name_label):
        # Открываем диалог ввода нового имени
        new_name = tk.simpledialog.askstring("Переименовать", "Введите новое имя:", initialvalue=app["name"])
        if new_name:
            # Обновляем имя в базе
            for i, a in enumerate(self.installed_apps):
                if a["name"] == app["name"]:
                    self.installed_apps[i]["name"] = new_name
                    save_apps_db(self.installed_apps)
                    break
            
            # Обновляем отображение
            name_label.config(text=new_name)
            self.add_notification(f"✏️ {app['name']} переименован в {new_name}")
    
    def save_app_positions(self):
        # В реальной системе здесь сохранялись бы позиции иконок
        # Для упрощения просто перестраиваем список в порядке отображения
        self.installed_apps.sort(key=lambda x: x.winfo_x())
        save_apps_db(self.installed_apps)
    
    def toggle_app_visibility(self, app):
        if app["name"] in self.hidden_apps:
            # Показываем приложение
            self.hidden_apps.remove(app["name"])
            self.add_notification(f"👁️ {app['name']} показано")
        else:
            # Скрываем приложение
            if app["name"] not in self.hidden_apps:
                self.hidden_apps.append(app["name"])
            self.add_notification(f"👁️ {app['name']} скрыто")
        save_hidden_apps(self.hidden_apps)
        self.populate_desktop()
    
    def setup_dock(self):
        dock_container = tk.Frame(self.dock, bg=self.colors['surface'])
        dock_container.pack(expand=True, pady=10)
        self.app_menu_btn = tk.Label(dock_container, text="☰", bg=self.colors['surface'],
                                     fg=self.colors['text'], font=('SF Pro Display', 16, 'bold'),
                                     cursor='hand2', padx=10, pady=10)
        self.app_menu_btn.pack(side='left', padx=6)
        self.app_menu_btn.bind('<Button-1>', self.show_app_menu)
        
        dock_apps = [
            ("🗂️", "Files", self.open_files),
            ("📝", "Notes", self.open_notes),
            ("💻", "Terminal", self.open_terminal),
            ("⚙️", "Settings", self.open_system_preferences),
            ("📊", "System Monitor", self.open_activity_monitor),
            ("🛡️", "Antivirus", self.open_antivirus),
            ("🌐", "Browser", self.open_browser),
            ("🎨", "Canvas", self.open_canvas),
            ("🛒", "O1SSA", self.open_o1ssa)
        ]
        for icon, name, command in dock_apps:
            self.create_dock_icon(dock_container, icon, name, command)
    
    def create_dock_icon(self, parent, icon, name, command):
        icon_frame = tk.Frame(parent, bg=self.colors['surface'], width=48, height=48)
        icon_frame.pack(side='left', padx=6)
        icon_frame.pack_propagate(False)
        
        icon_label = tk.Label(icon_frame, text=icon, bg=self.colors['surface'],
                              fg=self.colors['text'], font=('SF Pro Display', 20), cursor='hand2')
        icon_label.pack(expand=True)
        
        def on_enter(e):
            icon_frame.configure(bg=self.colors['surface_light'])
            
        def on_leave(e):
            icon_frame.configure(bg=self.colors['surface'])
            
        def on_click(e):
            # Получаем позицию иконки для анимации
            x = icon_frame.winfo_rootx() + icon_frame.winfo_width() // 2
            y = icon_frame.winfo_rooty() + icon_frame.winfo_height() // 2
            self.animate_click(icon_label)
            self.root.after(100, lambda: command(source_position=(x, y)))
            
        for w in (icon_frame, icon_label):
            w.bind('<Enter>', on_enter)
            w.bind('<Leave>', on_leave)
            w.bind('<Button-1>', on_click)
    
    def animate_click(self, widget):
        original_font = widget['font']
        widget.configure(font=('SF Pro Display', 18))
        self.root.after(60, lambda: widget.configure(font=original_font))
    
    def create_status_indicators(self):
        self.battery_label = tk.Label(self.status_frame, text="🔋",
                                      bg=self.colors['surface'], fg=self.colors['accent'],
                                      font=('SF Pro Display', 11), cursor='hand2')
        self.battery_label.pack(side='right', padx=6)
        self.battery_label.bind('<Button-1>', self.show_battery_info)
        
        self.wifi_label = tk.Label(self.status_frame, text="📶",
                                   bg=self.colors['surface'], fg=self.colors['primary'],
                                   font=('SF Pro Display', 11), cursor='hand2')
        self.wifi_label.pack(side='right', padx=6)
        self.wifi_label.bind('<Button-1>', self.show_network_settings)
        
        self.notif_label = tk.Label(self.status_frame, text="🔔",
                                    bg=self.colors['surface'], fg=self.colors['warning'],
                                    font=('SF Pro Display', 11), cursor='hand2')
        self.notif_label.pack(side='right', padx=6)
        self.notif_label.bind('<Button-1>', self.show_notification_center)
        
        self.volume_label = tk.Label(self.status_frame, text="🔊",
                                     bg=self.colors['surface'], fg=self.colors['primary'],
                                     font=('SF Pro Display', 11), cursor='hand2')
        self.volume_label.pack(side='right', padx=6)
        self.volume_label.bind('<Button-1>', self.open_volume_control)
        
        self.brightness_label = tk.Label(self.status_frame, text="💡",
                                         bg=self.colors['surface'], fg=self.colors['primary'],
                                         font=('SF Pro Display', 11), cursor='hand2')
        self.brightness_label.pack(side='right', padx=6)
        self.brightness_label.bind('<Button-1>', self.open_brightness_control)
    
    def show_system_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg=self.colors['surface'], fg=self.colors['text'])
        menu.add_command(label="О системе O1S", command=self.show_about)
        menu.add_separator()
        menu.add_command(label="Settings…", command=self.open_system_preferences)
        menu.add_separator()
        menu.add_command(label="Перезапуск", command=self.restart_system)
        menu.add_command(label="Выключить", command=self.shutdown_system)
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def show_about(self):
        about_text = """O1S Operating System v1.4
Дизайн:
• Плоские панели, крупная типографика, стекло-эффект
Новые функции:
• Терминал с поддержкой команд pyo1s
• Антивирус для проверки .py файлов
• Убраны системные кнопки окон
• Новый центр уведомлений
• Системные приложения с обновлениями
Разработано на Python + Tkinter
© 2025 O1S Team"""
        messagebox.showinfo("О системе O1S", about_text)
    
    def restart_system(self):
        if messagebox.askyesno("Перезапуск", "Перезапустить O1S?"):
            self.add_notification("🔄 Система перезапускается...")
            for app_name, process in self.processes.items():
                try:
                    process.terminate()
                except:
                    pass
            self.root.after(1500, self.root.quit)
    
    def shutdown_system(self):
        if messagebox.askyesno("Выключение", "Выключить O1S?"):
            self.add_notification("⏻ Система выключается...")
            for app_name, process in self.processes.items():
                try:
                    process.terminate()
                except:
                    pass
            self.root.after(1500, self.root.quit)
    
    def show_battery_info(self, event):
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "Подключено" if battery.power_plugged else "От батареи"
            else:
                percent = 87
                plugged = "Подключено"
        except:
            percent = 87
            plugged = "Подключено"
        messagebox.showinfo("Батарея", f"Заряд: {percent}%\nСтатус: {plugged}")
    
    def show_network_settings(self, event):
        self.open_network_preferences()
    
    def show_notification_center(self, event):
        self.open_notification_center()
    
    def add_notification(self, message):
        self.notifications.append({
            'message': message,
            'time': datetime.datetime.now().strftime("%H:%M")
        })
        print(f"[{datetime.datetime.now().strftime('%H:%M')}] {message}")
    
    def update_time(self):
        current_time = datetime.datetime.now().strftime("%a %b %d  %H:%M")
        self.time_label.config(text=current_time)
        
        # Обновляем информацию о батарее
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                self.battery_label.config(text=f"{percent}% 🔋")
        except:
            pass
    
    def start_system_services(self):
        self.update_time()
        self.root.after(1000, self.update_time_loop)
    
    def update_time_loop(self):
        self.update_time()
        self.root.after(1000, self.update_time_loop)
    
    def show_app_menu(self, event):
        if hasattr(self, 'app_menu_frame') and self.app_menu_frame.winfo_ismapped():
            try:
                self.app_menu_frame.destroy()
            except:
                pass
            return
        self.app_menu_frame = tk.Toplevel(self.root)
        self.app_menu_frame.title("Приложения")
        self.app_menu_frame.geometry("300x400+500+200")
        self.app_menu_frame.configure(bg=self.colors['background'])
        self.app_menu_frame.transient(self.root)
        self.app_menu_frame.grab_set()
        self.app_menu_frame.protocol("WM_DELETE_WINDOW", lambda: self.app_menu_frame.destroy())
        
        notebook = ttk.Notebook(self.app_menu_frame)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        all_apps_frame = tk.Frame(notebook, bg=self.colors['background'])
        notebook.add(all_apps_frame, text="Все приложения")
        
        fav_apps_frame = tk.Frame(notebook, bg=self.colors['background'])
        notebook.add(fav_apps_frame, text="Избранные")
        
        apps_list = tk.Listbox(all_apps_frame, bg=self.colors['card'], fg=self.colors['text'],
                               font=('SF Pro Display', 12), selectbackground=self.colors['primary'])
        apps_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        for app in self.installed_apps:
            apps_list.insert(tk.END, app["name"])
        
        apps_list.bind('<Double-1>', lambda e: self.launch_selected_app(apps_list))
        
        fav_list = tk.Listbox(fav_apps_frame, bg=self.colors['card'], fg=self.colors['text'],
                              font=('SF Pro Display', 12), selectbackground=self.colors['primary'])
        fav_list.pack(fill='both', expand=True, padx=10, pady=10)
        
        for fav in self.favorites:
            fav_list.insert(tk.END, fav)
        
        fav_list.bind('<Double-1>', lambda e: self.launch_selected_fav(fav_list))
        
        def add_to_favorites():
            sel = apps_list.curselection()
            if sel:
                app_name = apps_list.get(sel[0])
                if app_name not in self.favorites:
                    self.favorites.append(app_name)
                    fav_list.insert(tk.END, app_name)
                    save_favorites(self.favorites)
                    self.add_notification(f"⭐ {app_name} добавлено в Избранные")
        
        tk.Button(all_apps_frame, text="⭐ Добавить в Избранные",
                  command=add_to_favorites, bg=self.colors['accent'],
                  fg='white', font=('SF Pro Display', 10), relief='flat').pack(pady=5)
        
        def remove_from_favorites():
            sel = fav_list.curselection()
            if sel:
                app_name = fav_list.get(sel[0])
                if app_name in self.favorites:
                    self.favorites.remove(app_name)
                    fav_list.delete(sel[0])
                    save_favorites(self.favorites)
                    self.add_notification(f"❌ {app_name} удалено из Избранных")
        
        tk.Button(fav_apps_frame, text="❌ Удалить из Избранных",
                  command=remove_from_favorites, bg=self.colors['secondary'],
                  fg='white', font=('SF Pro Display', 10), relief='flat').pack(pady=5)
        
        close_btn = tk.Button(self.app_menu_frame, text="✕ Закрыть", 
                             command=self.app_menu_frame.destroy,
                             bg=self.colors['secondary'], fg='white', 
                             font=('SF Pro Display', 10))
        close_btn.pack(pady=5)
    
    def launch_selected_app(self, listbox):
        sel = listbox.curselection()
        if sel:
            app_name = listbox.get(sel[0])
            app = next((a for a in self.installed_apps if a["name"] == app_name), None)
            if app:
                # Получаем позицию иконки для анимации
                x = listbox.winfo_rootx() + listbox.winfo_width() // 2
                y = listbox.winfo_rooty() + listbox.winfo_height() // 2
                self.launch_app(app, source_position=(x, y))
                try:
                    self.app_menu_frame.destroy()
                except:
                    pass
    
    def launch_selected_fav(self, listbox):
        sel = listbox.curselection()
        if sel:
            app_name = listbox.get(sel[0])
            app = next((a for a in self.installed_apps if a["name"] == app_name), None)
            if app:
                # Получаем позицию иконки для анимации
                x = listbox.winfo_rootx() + listbox.winfo_width() // 2
                y = listbox.winfo_rooty() + listbox.winfo_height() // 2
                self.launch_app(app, source_position=(x, y))
                try:
                    self.app_menu_frame.destroy()
                except:
                    pass
    
    def launch_app(self, app, source_position=None):
        try:
            app_type = app.get("type", "gui")
            if app_type == "cli":
                self.open_terminal_with_command(f"python3 {app['path']}")
            elif app_type == "loader":
                self.run_loader_app(app)
            else:
                process = subprocess.Popen(["python3", app["path"]], 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL)
                self.processes[app['name']] = process
            self.add_notification(f"▶︎ Запущено: {app['name']}")
            if app['name'] not in self.running_apps:
                self.running_apps.append(app['name'])
                save_running_apps(self.running_apps)
            
            # Для встроенных приложений O1S создаем окно с анимацией
            app_methods = {
                "Files": self.open_files,
                "Notes": self.open_notes,
                "Terminal": self.open_terminal,
                "Settings": self.open_system_preferences,
                "System Monitor": self.open_activity_monitor,
                "Antivirus": self.open_antivirus,
                "Browser": self.open_browser,
                "Canvas": self.open_canvas,
                "O1SSA": self.open_o1ssa,
                "Calculator": self.open_calculator,
                "Music": self.open_music,
                "Calendar": self.open_calendar
            }
            
            if app["name"] in app_methods:
                # Вызываем метод с передачей source_position
                self.root.after(100, lambda: app_methods[app["name"]](source_position=source_position))
                
        except Exception as e:
            messagebox.showerror("Ошибка запуска", f"Не удалось запустить {app['name']}:\n{e}")
    
    def run_loader_app(self, app):
        try:
            loader_window = tk.Toplevel(self.root)
            loader_window.title(f"Загрузчик: {app['name']}")
            loader_window.geometry("600x400")
            loader_window.configure(bg=self.colors['background'])
            loader_window.protocol("WM_DELETE_WINDOW", lambda: self.close_loader(loader_window, app))
            
            output_frame = tk.Frame(loader_window, bg=self.colors['card'])
            output_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            output_text = scrolledtext.ScrolledText(
                output_frame, bg=self.colors['surface_light'], fg=self.colors['text'], 
                font=('Consolas', 11), wrap='word'
            )
            output_text.pack(fill='both', expand=True)
            
            process = subprocess.Popen(
                ["python3", app["path"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes[app['name']] = process
            
            def read_output():
                try:
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        loader_window.update()
                except:
                    pass
            
            thread = threading.Thread(target=read_output, daemon=True)
            thread.start()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить загрузчик: {e}")
    
    def close_loader(self, window, app):
        try:
            if app['name'] in self.processes:
                self.processes[app['name']].terminate()
                del self.processes[app['name']]
        except:
            pass
        window.destroy()
    
    def create_window(self, title, content_func, width=900, height=620, source_position=None, system_app=False):
        # Если не указано исходное положение, используем центр экрана
        if source_position is None:
            x = (self.root.winfo_screenwidth() - width) // 2
            y = (self.root.winfo_screenheight() - height) // 2
        else:
            x, y = source_position
        
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.configure(bg=self.colors['background'])
        # Убираем стандартные кнопки управления
        window.overrideredirect(True)
        window.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window))
        
        # Создаем кастомную title bar
        title_bar = tk.Frame(window, bg=self.colors['surface'], height=32)
        title_bar.pack(fill='x')
        title_bar.pack_propagate(False)
        
        # Добавляем обработчики для перемещения окна
        title_bar.bind('<Button-1>', lambda e: self.start_move_window(e, window))
        title_bar.bind('<B1-Motion>', lambda e: self.do_move_window(e, window))
        
        # Название окна
        title_label = tk.Label(title_bar, text=title, bg=self.colors['surface'],
                               fg=self.colors['text'], font=('SF Pro Display', 13, 'bold'))
        title_label.pack(side='left', padx=16, pady=5)
        
        # Кнопка закрытия
        close_btn = tk.Label(title_bar, text="Выйти", fg="#ff5f57", bg=self.colors['surface'],
                             font=('SF Pro Display', 12), cursor='hand2', padx=10)
        close_btn.pack(side='right', padx=10)
        close_btn.bind('<Button-1>', lambda e: window.destroy())
        
        content_area = tk.Frame(window, bg=self.colors['background'])
        content_area.pack(fill='both', expand=True)
        content_func(content_area)
        self.windows.append(window)
        
        # Анимация появления - сначала окно маленькое в позиции иконки, затем увеличивается и перемещается
        if source_position and not system_app:
            # Начальная позиция - где находится иконка приложения
            start_x, start_y = source_position
            # Конечная позиция
            end_x = (self.root.winfo_screenwidth() - width) // 2
            end_y = (self.root.winfo_screenheight() - height) // 2
            
            # Стартуем анимацию
            self.animate_window_appearance(window, start_x, start_y, end_x, end_y, width, height)
        else:
            # Просто плавное появление, если нет исходной позиции
            self.simple_fade_in(window)
        
        return window
    
    def animate_window_appearance(self, window, start_x, start_y, end_x, end_y, width, height):
        # Начальная позиция и размер
        window.geometry(f"1x1+{start_x}+{start_y}")
        window.attributes('-alpha', 0.0)
        
        # Уменьшаем количество шагов и увеличиваем скорость
        steps = 15
        dx = (end_x - start_x) / steps
        dy = (end_y - start_y) / steps
        dw = width / steps
        dh = height / steps
        alpha_step = 1.0 / steps
        
        def animate_step(step=0):
            if step < steps:
                x = start_x + dx * step
                y = start_y + dy * step
                w = int(1 + dw * step)
                h = int(1 + dh * step)
                alpha = step * alpha_step
                
                window.geometry(f"{w}x{h}+{int(x)}+{int(y)}")
                window.attributes('-alpha', alpha)
                
                self.root.after(10, animate_step, step + 1)
            else:
                # Устанавливаем окончательные размеры и позицию
                window.geometry(f"{width}x{height}+{end_x}+{end_y}")
                window.attributes('-alpha', 1.0)
        
        animate_step()
    
    def simple_fade_in(self, window):
        alpha = 0.0
        window.attributes('-alpha', alpha)
        def fade_in():
            nonlocal alpha
            alpha += 0.1
            window.attributes('-alpha', alpha)
            if alpha < 1.0:
                window.after(5, fade_in)
        fade_in()
    
    def start_move_window(self, event, window):
        window.x = event.x_root
        window.y = event.y_root
    
    def do_move_window(self, event, window):
        deltax = event.x_root - window.x
        deltay = event.y_root - window.y
        x = window.winfo_x() + deltax
        y = window.winfo_y() + deltay
        window.geometry(f"+{x}+{y}")
        window.x = event.x_root
        window.y = event.y_root
    
    def close_window(self, window):
        try:
            self.windows.remove(window)
            window.destroy()
        except:
            pass
    
    # Системные функции
    def get_wifi_status(self):
        try:
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        if 'addr' in addr and addr['addr'] != '127.0.0.1':
                            return True
            return False
        except:
            return False
    
    def set_volume(self, volume):
        self.volume_level = volume
        self.settings['volume_level'] = volume
        self.save_settings()
        
        try:
            # Попытка реального управления громкостью
            os.system(f"amixer set Master {volume}%")
        except:
            # Заглушка, если не удалось
            print(f"Громкость установлена на {volume}%")
        
        # Обновляем громкость в системе
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(volume / 100.0)
    
    def set_brightness(self, brightness):
        self.brightness_level = brightness
        self.settings['brightness_level'] = brightness
        self.save_settings()
        
        try:
            # Попытка реального управления яркостью
            os.system(f"xrandr --output $(xrandr | grep ' connected' | head -n 1 | cut -d ' ' -f1) --brightness {brightness/100}")
        except:
            # Заглушка, если не удалось
            print(f"Яркость установлена на {brightness}%")
    
    def toggle_wifi(self):
        try:
            if self.wifi_status:
                os.system("nmcli radio wifi off")
                self.wifi_status = False
                self.add_notification("📶 Wi-Fi отключен")
            else:
                os.system("nmcli radio wifi on")
                self.wifi_status = True
                self.add_notification("📶 Wi-Fi включен")
        except:
            self.wifi_status = not self.wifi_status
            status = "включен" if self.wifi_status else "отключен"
            self.add_notification(f"📶 Wi-Fi {status}")
    
    def toggle_bluetooth(self):
        self.bluetooth_status = not self.bluetooth_status
        status = "включен" if self.bluetooth_status else "отключен"
        self.add_notification(f"📡 Bluetooth {status}")
    
    # Приложения
    def open_files(self, source_position=None):
        self.add_notification("📂 Открыт файловый менеджер")
        def files_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            toolbar = tk.Frame(frame, bg=self.colors['surface_light'], height=40)
            toolbar.pack(fill='x', pady=(0, 10))
            toolbar.pack_propagate(False)
            
            tk.Button(toolbar, text="📁 Открыть", bg=self.colors['primary'], 
                     fg='white', relief='flat').pack(side='left', padx=5)
            tk.Button(toolbar, text="➕ Создать", bg=self.colors['accent'], 
                     fg='white', relief='flat').pack(side='left', padx=5)
            
            content = tk.Frame(frame, bg=self.colors['card'])
            content.pack(fill='both', expand=True)
            
            files_list = tk.Listbox(content, bg=self.colors['surface_light'], 
                                   font=('SF Pro Display', 12))
            files_list.pack(fill='both', expand=True, padx=5, pady=5)
            
            files = ["📄 document.txt", "📷 image.jpg", "🎵 music.mp3", 
                    "📊 data.csv", "🐍 script.py"]
            for file in files:
                files_list.insert(tk.END, file)
        
        self.create_window("Файлы", files_content, source_position=source_position)
    
    def open_notes(self, source_position=None):
        self.add_notification("📝 Открыты заметки")
        def notes_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            text_area = scrolledtext.ScrolledText(
                frame, bg=self.colors['surface_light'], fg=self.colors['text'],
                font=('SF Pro Display', 12), wrap='word'
            )
            text_area.pack(fill='both', expand=True)
            text_area.insert('1.0', "Ваши заметки здесь...\n")
            
            toolbar = tk.Frame(frame, bg=self.colors['surface'], height=40)
            toolbar.pack(fill='x', pady=(10, 0))
            toolbar.pack_propagate(False)
            
            def save_note():
                content = text_area.get('1.0', tk.END)
                try:
                    with open("note.txt", "w", encoding="utf-8") as f:
                        f.write(content)
                    self.add_notification("💾 Заметка сохранена")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
            
            tk.Button(toolbar, text="💾 Сохранить", command=save_note,
                     bg=self.colors['primary'], fg='white', relief='flat').pack(side='left', padx=5)
        
        self.create_window("Заметки", notes_content, source_position=source_position)
    
    def open_terminal(self, source_position=None):
        self.add_notification("💻 Открыт терминал")
        def terminal_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            output_frame = tk.Frame(frame, bg='black')
            output_frame.pack(fill='both', expand=True)
            
            output_text = scrolledtext.ScrolledText(
                output_frame, bg='black', fg='green', 
                font=('Consolas', 12), wrap='word'
            )
            output_text.pack(fill='both', expand=True, padx=2, pady=2)
            output_text.insert('1.0', "O1S Terminal v1.0\nВведите 'help' для списка команд\n$ ")
            
            input_frame = tk.Frame(frame, bg=self.colors['surface'], height=30)
            input_frame.pack(fill='x', pady=(10, 0))
            input_frame.pack_propagate(False)
            
            input_entry = tk.Entry(input_frame, bg='black', fg='white', 
                                  font=('Consolas', 12), insertbackground='white')
            input_entry.pack(fill='both', expand=True, padx=2, pady=2)
            input_entry.focus()
            
            def execute_command(event=None):
                command = input_entry.get().strip()
                if command:
                    output_text.insert(tk.END, f"{command}\n")
                    if command == "help":
                        output_text.insert(tk.END, "Доступные команды:\n")
                        output_text.insert(tk.END, "help - показать справку\n")
                        output_text.insert(tk.END, "clear - очистить терминал\n")
                        output_text.insert(tk.END, "date - показать дату и время\n")
                        output_text.insert(tk.END, "sysinfo - информация о системе\n")
                    elif command == "clear":
                        output_text.delete('1.0', tk.END)
                    elif command == "date":
                        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        output_text.insert(tk.END, f"{now}\n")
                    elif command == "sysinfo":
                        cpu = psutil.cpu_percent()
                        memory = psutil.virtual_memory().percent
                        output_text.insert(tk.END, f"CPU: {cpu}%\n")
                        output_text.insert(tk.END, f"Память: {memory}%\n")
                    else:
                        output_text.insert(tk.END, f"Команда '{command}' не найдена\n")
                    output_text.insert(tk.END, "\n$ ")
                    output_text.see(tk.END)
                    input_entry.delete(0, tk.END)
            
            input_entry.bind('<Return>', execute_command)
        
        self.create_window("Терминал", terminal_content, 800, 500, source_position=source_position)
    
    def open_terminal_with_command(self, command):
        self.open_terminal()
        self.add_notification(f"🚀 Выполняется команда: {command}")
    
    def open_system_preferences(self, source_position=None):
        self.add_notification("⚙️ Открыты настройки системы")
        def settings_content(parent):
            notebook = ttk.Notebook(parent)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Внешний вид
            appearance_frame = tk.Frame(notebook, bg=self.colors['background'])
            notebook.add(appearance_frame, text="Внешний вид")
            
            tk.Label(appearance_frame, text="Тема:", bg=self.colors['background'],
                    font=('SF Pro Display', 12)).pack(anchor='w', pady=10)
            theme_var = tk.StringVar(value=self.current_theme)
            theme_menu = ttk.Combobox(appearance_frame, textvariable=theme_var,
                                     values=['orange', 'npo1s'], state='readonly')
            theme_menu.pack(fill='x', pady=5)
            
            def change_theme(event):
                self.current_theme = theme_var.get()
                self.apply_theme()
                self.settings['theme'] = self.current_theme
                self.save_settings()
                self.add_notification(f"🎨 Тема изменена на {self.current_theme}")
            
            theme_menu.bind('<<ComboboxSelected>>', change_theme)
            
            # Звук
            sound_frame = tk.Frame(notebook, bg=self.colors['background'])
            notebook.add(sound_frame, text="Звук")
            
            tk.Label(sound_frame, text="Громкость системы", bg=self.colors['background'],
                    font=('SF Pro Display', 12)).pack(anchor='w', pady=10)
            
            volume_scale = tk.Scale(sound_frame, from_=0, to=100, orient='horizontal',
                                   bg=self.colors['background'], fg=self.colors['text'],
                                   font=('SF Pro Display', 12))
            volume_scale.set(self.volume_level)
            volume_scale.pack(fill='x', padx=20, pady=10)
            
            def update_volume(val):
                self.set_volume(int(float(val)))
            
            volume_scale.config(command=update_volume)
            
            # Сеть
            network_frame = tk.Frame(notebook, bg=self.colors['background'])
            notebook.add(network_frame, text="Сеть")
            
            wifi_frame = tk.Frame(network_frame, bg=self.colors['card'], relief='raised', bd=1)
            wifi_frame.pack(fill='x', pady=5)
            
            wifi_label = tk.Label(wifi_frame, text=f"Wi-Fi: {'Включен' if self.wifi_status else 'Отключен'}",
                                 bg=self.colors['card'], font=('SF Pro Display', 12))
            wifi_label.pack(side='left', padx=10, pady=10)
            
            wifi_btn = tk.Button(wifi_frame, text="Переключить", 
                                command=lambda: self.toggle_wifi_and_update(wifi_label),
                                bg=self.colors['primary'], fg='white')
            wifi_btn.pack(side='right', padx=10, pady=10)
            
            bluetooth_frame = tk.Frame(network_frame, bg=self.colors['card'], relief='raised', bd=1)
            bluetooth_frame.pack(fill='x', pady=5)
            
            bluetooth_label = tk.Label(bluetooth_frame, text=f"Bluetooth: {'Включен' if self.bluetooth_status else 'Отключен'}",
                                      bg=self.colors['card'], font=('SF Pro Display', 12))
            bluetooth_label.pack(side='left', padx=10, pady=10)
            
            bluetooth_btn = tk.Button(bluetooth_frame, text="Переключить", 
                                     command=lambda: self.toggle_bluetooth_and_update(bluetooth_label),
                                     bg=self.colors['primary'], fg='white')
            bluetooth_btn.pack(side='right', padx=10, pady=10)
            
            # Яркость
            brightness_frame = tk.Frame(notebook, bg=self.colors['background'])
            notebook.add(brightness_frame, text="Яркость")
            
            tk.Label(brightness_frame, text="Уровень яркости", bg=self.colors['background'],
                    font=('SF Pro Display', 12)).pack(anchor='w', pady=10)
            
            brightness_scale = tk.Scale(brightness_frame, from_=0, to=100, orient='horizontal',
                                       bg=self.colors['background'], fg=self.colors['text'],
                                       font=('SF Pro Display', 12))
            brightness_scale.set(self.brightness_level)
            brightness_scale.pack(fill='x', padx=20, pady=10)
            
            def update_brightness(val):
                self.set_brightness(int(float(val)))
            
            brightness_scale.config(command=update_brightness)
            
            # Уведомления
            notif_frame = tk.Frame(notebook, bg=self.colors['background'])
            notebook.add(notif_frame, text="Уведомления")
            
            notif_var = tk.BooleanVar(value=self.settings.get('notifications', True))
            notif_check = tk.Checkbutton(notif_frame, text="Включить уведомления",
                                        variable=notif_var, bg=self.colors['background'],
                                        font=('SF Pro Display', 12))
            notif_check.pack(anchor='w', pady=10)
            
            def save_notif_setting():
                self.settings['notifications'] = notif_var.get()
                self.save_settings()
            
            notif_var.trace('w', lambda *args: save_notif_setting())
            
            # О системе
            about_frame = tk.Frame(notebook, bg=self.colors['background'])
            notebook.add(about_frame, text="О системе")
            
            tk.Label(about_frame, text="O1S Operating System v1.4", bg=self.colors['background'],
                    font=('SF Pro Display', 16, 'bold')).pack(pady=20)
            
            tk.Label(about_frame, text="Разработано на Python + Tkinter", bg=self.colors['background'],
                    font=('SF Pro Display', 12)).pack(pady=5)
            
            tk.Label(about_frame, text="© 2025 O1S Team", bg=self.colors['background'],
                    font=('SF Pro Display', 12)).pack(pady=5)
            
            # Версия ядра
            kernel_version = platform.platform()
            tk.Label(about_frame, text=f"Ядро: {kernel_version}", bg=self.colors['background'],
                    font=('SF Pro Display', 10)).pack(pady=20)
        
        self.create_window("Настройки системы", settings_content, source_position=source_position)
    
    def toggle_wifi_and_update(self, label):
        self.toggle_wifi()
        label.config(text=f"Wi-Fi: {'Включен' if self.wifi_status else 'Отключен'}")
    
    def toggle_bluetooth_and_update(self, label):
        self.toggle_bluetooth()
        label.config(text=f"Bluetooth: {'Включен' if self.bluetooth_status else 'Отключен'}")
    
    def open_activity_monitor(self, source_position=None):
        self.add_notification("📊 Открыт монитор активности")
        def monitor_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            info_frame = tk.Frame(frame, bg=self.colors['card'], relief='raised', bd=1)
            info_frame.pack(fill='x', pady=(0, 10))
            
            cpu_label = tk.Label(info_frame, text="CPU: Загрузка...", 
                                bg=self.colors['card'], font=('SF Pro Display', 11))
            cpu_label.pack(anchor='w', padx=10, pady=5)
            
            mem_label = tk.Label(info_frame, text="Память: Загрузка...", 
                                bg=self.colors['card'], font=('SF Pro Display', 11))
            mem_label.pack(anchor='w', padx=10, pady=5)
            
            proc_frame = tk.Frame(frame, bg=self.colors['background'])
            proc_frame.pack(fill='both', expand=True)
            
            proc_label = tk.Label(proc_frame, text="Запущенные процессы:", 
                                 bg=self.colors['background'], font=('SF Pro Display', 12, 'bold'))
            proc_label.pack(anchor='w')
            
            proc_list = tk.Listbox(proc_frame, bg=self.colors['surface_light'],
                                  font=('SF Pro Display', 11))
            proc_list.pack(fill='both', expand=True, pady=5)
            
            def update_info():
                try:
                    cpu_percent = psutil.cpu_percent()
                    cpu_label.config(text=f"CPU: {cpu_percent}%")
                    mem = psutil.virtual_memory()
                    mem_label.config(text=f"Память: {mem.percent}% использовано")
                    
                    proc_list.delete(0, tk.END)
                    for proc in psutil.process_iter(['name', 'cpu_percent', 'memory_percent']):
                        try:
                            if proc.info['cpu_percent'] > 0 or proc.info['memory_percent'] > 0:
                                proc_list.insert(tk.END, 
                                    f"{proc.info['name']} - CPU: {proc.info['cpu_percent']}% - Mem: {proc.info['memory_percent']:.1f}%")
                        except:
                            pass
                except Exception as e:
                    print(f"Ошибка обновления монитора: {e}")
                
                parent.after(2000, update_info)
            
            update_info()
        
        self.create_window("Монитор активности", monitor_content, 800, 500, source_position=source_position)
    
    def open_antivirus(self, source_position=None):
        self.add_notification("🛡️ Открыт антивирус")
        def antivirus_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="Сканер безопасности O1S", 
                    font=('SF Pro Display', 16, 'bold'), bg=self.colors['background']).pack(pady=10)
            
            scan_button = tk.Button(frame, text="🔍 Сканировать систему", 
                                   bg=self.colors['primary'], fg='white',
                                   font=('SF Pro Display', 12), relief='flat')
            scan_button.pack(pady=20)
            
            result_frame = tk.Frame(frame, bg=self.colors['surface_light'])
            result_frame.pack(fill='both', expand=True)
            
            result_text = scrolledtext.ScrolledText(
                result_frame, bg=self.colors['surface_light'], 
                font=('Consolas', 11), wrap='word'
            )
            result_text.pack(fill='both', expand=True, padx=5, pady=5)
            result_text.insert('1.0', "Готов к сканированию...\n")
            
            def scan_system():
                result_text.delete('1.0', tk.END)
                result_text.insert('1.0', "🔍 Сканирование запущено...\n")
                parent.update()
                time.sleep(1)
                result_text.insert(tk.END, "✓ Проверка системных файлов... OK\n")
                parent.update()
                time.sleep(0.5)
                result_text.insert(tk.END, "✓ Проверка процессов... OK\n")
                parent.update()
                time.sleep(0.5)
                result_text.insert(tk.END, "✓ Проверка сетевых соединений... OK\n")
                parent.update()
                time.sleep(0.5)
                result_text.insert(tk.END, "✓ Проверка установленных приложений... OK\n")
                parent.update()
                time.sleep(0.5)
                result_text.insert(tk.END, "✅ Сканирование завершено. Угроз не обнаружено.\n")
            
            scan_button.config(command=lambda: threading.Thread(target=scan_system, daemon=True).start())
        
        self.create_window("Антивирус", antivirus_content, source_position=source_position)
    
    def open_browser(self, source_position=None):
        self.add_notification("🌐 Открыт браузер")
        def browser_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            nav_frame = tk.Frame(frame, bg=self.colors['surface_light'], height=50)
            nav_frame.pack(fill='x', pady=(0, 10))
            nav_frame.pack_propagate(False)
            
            url_entry = tk.Entry(nav_frame, bg='white', fg='black',
                                font=('SF Pro Display', 12))
            url_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
            url_entry.insert(0, "https://www.google.com")
            
            def navigate():
                url = url_entry.get()
                try:
                    webbrowser.open(url)
                    self.add_notification(f"🌐 Открыт: {url}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось открыть URL: {e}")
            
            go_btn = tk.Button(nav_frame, text="➤", command=navigate,
                              bg=self.colors['primary'], fg='white')
            go_btn.pack(side='right', padx=5, pady=5)
            
            content_frame = tk.Frame(frame, bg='white')
            content_frame.pack(fill='both', expand=True)
            
            tk.Label(content_frame, text="O1S Browser\nИспользуйте адресную строку для навигации",
                    font=('SF Pro Display', 14), bg='white').pack(expand=True)
        
        self.create_window("Браузер", browser_content, source_position=source_position)
    
    def open_canvas(self, source_position=None):
        self.add_notification("🎨 Открыт холст")
        def canvas_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            toolbar = tk.Frame(frame, bg=self.colors['surface_light'], height=50)
            toolbar.pack(fill='x', pady=(0, 10))
            toolbar.pack_propagate(False)
            
            colors = ['black', 'red', 'blue', 'green', 'yellow', 'purple']
            for color in colors:
                btn = tk.Button(toolbar, bg=color, width=2, relief='flat',
                               command=lambda c=color: set_color(c))
                btn.pack(side='left', padx=2, pady=5)
            
            clear_btn = tk.Button(toolbar, text="Очистить", 
                                 bg=self.colors['secondary'], fg='white')
            clear_btn.pack(side='right', padx=5, pady=5)
            
            canvas = tk.Canvas(frame, bg='white', cursor='cross')
            canvas.pack(fill='both', expand=True)
            
            current_color = 'black'
            last_x, last_y = None, None
            
            def set_color(color):
                nonlocal current_color
                current_color = color
            
            def clear_canvas():
                canvas.delete('all')
            
            def paint(event):
                nonlocal last_x, last_y
                x, y = event.x, event.y
                if last_x and last_y:
                    canvas.create_line(last_x, last_y, x, y, width=2, fill=current_color)
                last_x, last_y = x, y
            
            def reset(event):
                nonlocal last_x, last_y
                last_x, last_y = None, None
            
            canvas.bind('<B1-Motion>', paint)
            canvas.bind('<ButtonRelease-1>', reset)
            clear_btn.config(command=clear_canvas)
        
        self.create_window("Холст", canvas_content, 800, 600, source_position=source_position)
    
    def open_calculator(self, source_position=None):
        self.add_notification("🧮 Открыт калькулятор")
        
        def calculator_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Дисплей
            display = tk.Entry(frame, font=('Arial', 24), bd=10, 
                              relief='ridge', justify='right')
            display.pack(fill='x', padx=10, pady=10)
            
            # Кнопки
            buttons = [
                ['7', '8', '9', '/'],
                ['4', '5', '6', '*'],
                ['1', '2', '3', '-'],
                ['C', '0', '=', '+']
            ]
            
            btn_frame = tk.Frame(frame)
            btn_frame.pack(padx=10, pady=10)
            
            expression = ""
            
            def button_click(text):
                nonlocal expression
                if text == 'C':
                    expression = ""
                elif text == '=':
                    try:
                        result = str(eval(expression))
                        expression = result
                    except:
                        expression = "Ошибка"
                else:
                    expression += text
                
                display.delete(0, tk.END)
                display.insert(0, expression)
            
            for i, row in enumerate(buttons):
                for j, text in enumerate(row):
                    btn = tk.Button(btn_frame, text=text, font=('Arial', 16), width=5, height=2,
                                   bg=self.colors['surface_light'], activebackground=self.colors['surface'])
                    btn.grid(row=i, column=j, padx=2, pady=2)
                    btn.bind('<Button-1>', lambda e, t=text: button_click(t))
        
        self.create_window("Калькулятор", calculator_content, 300, 400, source_position=source_position)
    
    def open_music(self, source_position=None):
        self.add_notification("🎵 Открыт музыкальный плеер")
        
        def music_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Верхняя панель
            top_frame = tk.Frame(frame, bg=self.colors['surface'], height=60)
            top_frame.pack(fill='x', pady=(0, 10))
            top_frame.pack_propagate(False)
            
            tk.Label(top_frame, text="Музыкальный плеер", bg=self.colors['surface'],
                    fg=self.colors['text'], font=('SF Pro Display', 16, 'bold')).pack(pady=10)
            
            # Информация о текущей песне
            self.song_info = tk.Label(frame, text="Нет активной песни",
                                     font=('SF Pro Display', 14))
            self.song_info.pack(pady=10)
            
            # Прогресс-бар
            self.progress = ttk.Progressbar(frame, orient='horizontal', mode='determinate')
            self.progress.pack(fill='x', padx=20, pady=10)
            
            # Управление
            controls_frame = tk.Frame(frame)
            controls_frame.pack(pady=20)
            
            self.prev_btn = tk.Button(controls_frame, text="⏮", width=3, font=('Arial', 16))
            self.prev_btn.pack(side='left', padx=10)
            
            self.play_btn = tk.Button(controls_frame, text="▶", width=3, font=('Arial', 16))
            self.play_btn.pack(side='left', padx=10)
            
            self.next_btn = tk.Button(controls_frame, text="⏭", width=3, font=('Arial', 16))
            self.next_btn.pack(side='left', padx=10)
            
            # Обработчики
            self.play_btn.bind('<Button-1>', self.toggle_play)
            self.prev_btn.bind('<Button-1>', self.prev_song)
            self.next_btn.bind('<Button-1>', self.next_song)
            
            # Регулятор громкости
            volume_frame = tk.Frame(frame, bg=self.colors['background'])
            volume_frame.pack(fill='x', padx=20, pady=10)
            
            tk.Label(volume_frame, text="Громкость:", bg=self.colors['background'],
                    font=('SF Pro Display', 12)).pack(side='left', padx=5)
            
            volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal',
                                   bg=self.colors['background'], fg=self.colors['text'],
                                   font=('SF Pro Display', 10))
            volume_scale.set(self.volume_level)
            volume_scale.pack(fill='x', expand=True, padx=5)
            
            def update_volume(val):
                self.set_volume(int(float(val)))
            
            volume_scale.config(command=update_volume)
            
            # Список песен
            songs_frame = tk.Frame(frame, bg=self.colors['card'])
            songs_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(songs_frame, text="Музыкальная библиотека", bg=self.colors['card'],
                    font=('SF Pro Display', 14, 'bold')).pack(pady=10)
            
            self.songs_list = tk.Listbox(songs_frame, bg=self.colors['surface_light'], 
                                        font=('SF Pro Display', 12))
            self.songs_list.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Загружаем музыку из папки O1S
            self.load_music()
        
        self.create_window("Музыка", music_content, 600, 500, source_position=source_position)
    
    def load_music(self):
        # Очищаем список
        self.songs_list.delete(0, tk.END)
        
        # Ищем аудиофайлы в папке O1S
        music_files = []
        for ext in ['*.mp3', '*.wav', '*.ogg']:
            music_files.extend(glob.glob(f"./**/{ext}", recursive=True))
        
        # Добавляем найденные файлы в список
        self.songs = music_files
        self.current_song = 0
        self.paused = False
        
        for song in music_files:
            song_name = os.path.basename(song)
            self.songs_list.insert(tk.END, song_name)
        
        # Обработчик выбора песни
        def select_song(event):
            if self.songs_list.curselection():
                self.current_song = self.songs_list.curselection()[0]
                self.update_song_info()
                self.toggle_play()
        
        self.songs_list.bind('<<ListboxSelect>>', select_song)
        
        # Если есть песни, обновляем информацию
        if music_files:
            self.update_song_info()
    
    def update_song_info(self):
        if self.songs:
            song_name = os.path.basename(self.songs[self.current_song])
            self.song_info.config(text=f"Текущая песня: {song_name}")
            
            # Загружаем и воспроизводим песню
            pygame.mixer.music.load(self.songs[self.current_song])
            pygame.mixer.music.play()
            self.play_btn.config(text="⏸")
            self.paused = False
    
    def toggle_play(self, event=None):
        if not self.songs:
            self.add_notification("⚠️ Нет песен для воспроизведения")
            return
            
        if self.paused:
            pygame.mixer.music.unpause()
            self.play_btn.config(text="⏸")
            self.paused = False
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.play_btn.config(text="▶")
                self.paused = True
            else:
                pygame.mixer.music.load(self.songs[self.current_song])
                pygame.mixer.music.play()
                self.play_btn.config(text="⏸")
    
    def prev_song(self, event=None):
        if self.songs:
            self.current_song = (self.current_song - 1) % len(self.songs)
            self.update_song_info()
    
    def next_song(self, event=None):
        if self.songs:
            self.current_song = (self.current_song + 1) % len(self.songs)
            self.update_song_info()
    
    def open_calendar(self, source_position=None):
        self.add_notification("📅 Открыт календарь")
        
        def calendar_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Заголовок
            header_frame = tk.Frame(frame, bg=self.colors['surface'], height=60)
            header_frame.pack(fill='x', pady=(0, 10))
            header_frame.pack_propagate(False)
            
            self.calendar_month = datetime.datetime.now().month
            self.calendar_year = datetime.datetime.now().year
            
            def update_calendar():
                month_name = datetime.date(self.calendar_year, self.calendar_month, 1).strftime("%B")
                year_label.config(text=f"{month_name} {self.calendar_year}")
                draw_calendar()
            
            def prev_month():
                self.calendar_month -= 1
                if self.calendar_month < 1:
                    self.calendar_month = 12
                    self.calendar_year -= 1
                update_calendar()
            
            def next_month():
                self.calendar_month += 1
                if self.calendar_month > 12:
                    self.calendar_month = 1
                    self.calendar_year += 1
                update_calendar
            
            prev_btn = tk.Button(header_frame, text="❮", command=prev_month,
                                bg=self.colors['surface'], fg=self.colors['text'],
                                font=('SF Pro Display', 12), relief='flat', width=3)
            prev_btn.pack(side='left', padx=10, pady=10)
            
            year_label = tk.Label(header_frame, text="", bg=self.colors['surface'],
                                fg=self.colors['text'], font=('SF Pro Display', 16, 'bold'))
            year_label.pack(side='left', expand=True)
            
            next_btn = tk.Button(header_frame, text="❯", command=next_month,
                                bg=self.colors['surface'], fg=self.colors['text'],
                                font=('SF Pro Display', 12), relief='flat', width=3)
            next_btn.pack(side='right', padx=10, pady=10)
            
            # Календарь
            calendar_frame = tk.Frame(frame, bg=self.colors['surface'])
            calendar_frame.pack(fill='both', expand=True)
            
            days_frame = tk.Frame(calendar_frame, bg=self.colors['surface'])
            days_frame.pack(fill='x')
            
            days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            for day in days:
                tk.Label(days_frame, text=day, bg=self.colors['surface'],
                        fg=self.colors['text'], font=('SF Pro Display', 10, 'bold'),
                        width=5).pack(side='left', expand=True)
            
            self.calendar_grid = tk.Frame(calendar_frame, bg=self.colors['surface'])
            self.calendar_grid.pack(fill='both', expand=True)
            
            def draw_calendar():
                # Очищаем сетку
                for widget in self.calendar_grid.winfo_children():
                    widget.destroy()
                
                # Получаем первый день месяца
                first_day = datetime.datetime(self.calendar_year, self.calendar_month, 1)
                # Начинаем с понедельника (0 = понедельник, 6 = воскресенье)
                weekday = first_day.weekday()
                if weekday == 6:  # Если воскресенье, то сдвигаем на 6 дней назад
                    weekday = -1
                
                # Получаем количество дней в месяце
                if self.calendar_month == 12:
                    num_days = 31
                else:
                    next_month = datetime.datetime(self.calendar_year, self.calendar_month + 1, 1)
                    num_days = (next_month - first_day).days
                
                # Создаем сетку для дней
                day_num = 1
                for i in range(6):  # 6 недель максимум
                    week_frame = tk.Frame(self.calendar_grid, bg=self.colors['surface'])
                    week_frame.pack(fill='x')
                    
                    for j in range(7):  # 7 дней недели
                        if (i == 0 and j <= weekday) or day_num > num_days:
                            day_frame = tk.Frame(week_frame, bg=self.colors['surface'], width=50, height=50)
                        else:
                            day_frame = tk.Frame(week_frame, bg=self.colors['surface'], width=50, height=50)
                            tk.Label(day_frame, text=str(day_num), bg=self.colors['surface'],
                                    fg=self.colors['text'], font=('SF Pro Display', 10)).pack(expand=True)
                            day_num += 1
                        
                        day_frame.pack(side='left', expand=True, fill='both')
                        day_frame.pack_propagate(False)
            
            update_calendar()
        
        self.create_window("Календарь", calendar_content, 600, 500, source_position=source_position)
    
    def open_o1ssa(self, source_position=None):
        self.add_notification("🛒 Открыт O1S Software Store")
        
        def o1ssa_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Заголовок
            header_frame = tk.Frame(frame, bg=self.colors['surface'], height=60)
            header_frame.pack(fill='x', pady=(0, 10))
            header_frame.pack_propagate(False)
            
            tk.Label(header_frame, text="O1S Software Store", 
                    bg=self.colors['surface'], fg=self.colors['text'],
                    font=('SF Pro Display', 16, 'bold')).pack(side='left', padx=20, pady=10)
            
            # Поиск
            search_frame = tk.Frame(frame, bg=self.colors['surface_light'], height=40)
            search_frame.pack(fill='x', pady=(0, 10))
            search_frame.pack_propagate(False)
            
            search_entry = tk.Entry(search_frame, bg='white', fg='black',
                                   font=('SF Pro Display', 12))
            search_entry.pack(side='left', fill='x', expand=True, padx=5, pady=5)
            search_entry.insert(0, "Поиск приложений...")
            
            # Категории
            categories_frame = tk.Frame(frame, bg=self.colors['background'], height=50)
            categories_frame.pack(fill='x', pady=(0, 10))
            
            categories = ["Все", "Популярные", "Новые", "Музыка", "Инструменты"]
            for category in categories:
                cat_btn = tk.Button(categories_frame, text=category, 
                                   bg=self.colors['surface'], fg=self.colors['text'],
                                   font=('SF Pro Display', 10), relief='flat')
                cat_btn.pack(side='left', padx=5, pady=5)
            
            # Список приложений
            apps_frame = tk.Frame(frame, bg=self.colors['background'])
            apps_frame.pack(fill='both', expand=True)
            
            # Создаем canvas для прокрутки
            canvas = tk.Canvas(apps_frame, bg=self.colors['background'])
            scrollbar = ttk.Scrollbar(apps_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.colors['background'])
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Добавляем приложения в список
            for app in self.installable_apps:
                self.create_app_store_item(scrollable_frame, app)
        
        self.create_window("O1S Software Store", o1ssa_content, 900, 700, source_position=source_position)
    
    def create_app_store_item(self, parent, app):
        app_frame = tk.Frame(parent, bg=self.colors['surface'], relief='raised', bd=1, padx=10, pady=10)
        app_frame.pack(fill='x', pady=5)
        
        # Иконка приложения
        icon_label = tk.Label(app_frame, text=app['icon'], bg=self.colors['surface'],
                             fg=self.colors['text'], font=('SF Pro Display', 24))
        icon_label.pack(side='left', padx=10)
        
        # Информация о приложении
        info_frame = tk.Frame(app_frame, bg=self.colors['surface'])
        info_frame.pack(side='left', fill='x', expand=True)
        
        tk.Label(info_frame, text=app['name'], bg=self.colors['surface'],
                fg=self.colors['text'], font=('SF Pro Display', 14, 'bold')).pack(anchor='w')
        tk.Label(info_frame, text=app['description'], bg=self.colors['surface'],
                fg=self.colors['text_secondary'], font=('SF Pro Display', 10), wraplength=400).pack(anchor='w')
        
        # Детали
        details_frame = tk.Frame(info_frame, bg=self.colors['surface'])
        details_frame.pack(anchor='w', pady=(5, 0))
        
        tk.Label(details_frame, text=f"Версия: {app['version']}", bg=self.colors['surface'],
                fg=self.colors['text_tertiary'], font=('SF Pro Display', 9)).pack(side='left', padx=5)
        tk.Label(details_frame, text=f"Размер: {app['size']}", bg=self.colors['surface'],
                fg=self.colors['text_tertiary'], font=('SF Pro Display', 9)).pack(side='left', padx=5)
        
        # Кнопка установки/обновления
        if app['update_available']:
            btn_text = "Обновить"
            btn_color = self.colors['warning']
        elif app['installed']:
            btn_text = "Открыть"
            btn_color = self.colors['primary']
        else:
            btn_text = "Скачать"
            btn_color = self.colors['primary']
        
        install_btn = tk.Button(app_frame, text=btn_text,
                               bg=btn_color, fg='white',
                               font=('SF Pro Display', 10), relief='flat')
        install_btn.pack(side='right', padx=10)
        
        # Обработчик установки/обновления
        def install_app():
            if not app['installed'] or app['update_available']:
                # Создаем папку для приложения
                app_dir = APPS_DIR / app['name']
                app_dir.mkdir(exist_ok=True)
                
                # Создаем файл приложения
                app_file = app_dir / f"{app['name'].lower()}.py"
                
                # Создаем разные примеры для разных приложений
                if app['name'] == "Music":
                    content = """import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import os

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("600x400")
        
        # Инициализация pygame mixer
        pygame.mixer.init()
        
        # Создаем интерфейс
        self.create_ui()
        
        # Список песен
        self.songs = []
        self.current_song = 0
        self.paused = False
        
        # Загружаем примеры песен
        self.load_sample_songs()
    
    def create_ui(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg='#f0f0f0', height=60)
        top_frame.pack(fill='x')
        
        tk.Label(top_frame, text="Музыкальный плеер", bg='#f0f0f0',
                font=('Helvetica', 16, 'bold')).pack(pady=10)
        
        # Основная область
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Информация о текущей песне
        self.song_info = tk.Label(main_frame, text="Нет активной песни",
                                 font=('Helvetica', 14))
        self.song_info.pack(pady=10)
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill='x', padx=20, pady=10)
        
        # Управление
        controls_frame = tk.Frame(main_frame)
        controls_frame.pack(pady=20)
        
        self.prev_btn = tk.Button(controls_frame, text="⏮", width=3, font=('Arial', 16))
        self.prev_btn.pack(side='left', padx=10)
        
        self.play_btn = tk.Button(controls_frame, text="▶", width=3, font=('Arial', 16))
        self.play_btn.pack(side='left', padx=10)
        
        self.next_btn = tk.Button(controls_frame, text="⏭", width=3, font=('Arial', 16))
        self.next_btn.pack(side='left', padx=10)
        
        # Обработчики
        self.play_btn.bind('<Button-1>', self.toggle_play)
        self.prev_btn.bind('<Button-1>', self.prev_song)
        self.next_btn.bind('<Button-1>', self.next_song)
        
        # Добавить песни
        add_btn = tk.Button(main_frame, text="Добавить песни", bg='#4A90E2', fg='white')
        add_btn.pack(pady=10)
        add_btn.bind('<Button-1>', self.add_songs)
    
    def load_sample_songs(self):
        # Создаем примеры аудиофайлов (пустые файлы для демонстрации)
        samples_dir = os.path.join(os.path.dirname(__file__), "samples")
        os.makedirs(samples_dir, exist_ok=True)
        
        sample_songs = [
            "sample1.mp3",
            "sample2.mp3",
            "sample3.mp3"
        ]
        
        for song in sample_songs:
            song_path = os.path.join(samples_dir, song)
            if not os.path.exists(song_path):
                # Создаем пустой файл
                open(song_path, 'a').close()
            self.songs.append(song_path)
        
        if self.songs:
            self.current_song = 0
            self.update_song_info()
    
    def update_song_info(self):
        if self.songs:
            song_name = os.path.basename(self.songs[self.current_song])
            self.song_info.config(text=f"Текущая песня: {song_name}")
    
    def toggle_play(self, event=None):
        if not self.songs:
            messagebox.showinfo("Информация", "Нет песен для воспроизведения")
            return
            
        if self.paused:
            pygame.mixer.music.unpause()
            self.play_btn.config(text="⏸")
            self.paused = False
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.play_btn.config(text="▶")
                self.paused = True
            else:
                pygame.mixer.music.load(self.songs[self.current_song])
                pygame.mixer.music.play()
                self.play_btn.config(text="⏸")
    
    def prev_song(self, event=None):
        if self.songs:
            self.current_song = (self.current_song - 1) % len(self.songs)
            self.update_song_info()
            self.toggle_play()
    
    def next_song(self, event=None):
        if self.songs:
            self.current_song = (self.current_song + 1) % len(self.songs)
            self.update_song_info()
            self.toggle_play()
    
    def add_songs(self, event=None):
        songs = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")])
        for song in songs:
            self.songs.append(song)
        if self.songs and len(self.songs) == len(songs):
            self.current_song = 0
            self.update_song_info()

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
"""
                elif app['name'] == "Calendar":
                    content = """import tkinter as tk
import datetime

class CalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Календарь")
        self.root.geometry("600x500")
        
        self.calendar_month = datetime.datetime.now().month
        self.calendar_year = datetime.datetime.now().year
        
        self.create_ui()
    
    def create_ui(self):
        # Заголовок
        header_frame = tk.Frame(self.root, bg='#f0f0f0', height=60)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        def update_calendar():
            month_name = datetime.date(self.calendar_year, self.calendar_month, 1).strftime("%B")
            year_label.config(text=f"{month_name} {self.calendar_year}")
            self.draw_calendar()
        
        def prev_month():
            self.calendar_month -= 1
            if self.calendar_month < 1:
                self.calendar_month = 12
                self.calendar_year -= 1
            update_calendar()
        
        def next_month():
            self.calendar_month += 1
            if self.calendar_month > 12:
                self.calendar_month = 1
                self.calendar_year += 1
            update_calendar
        
        prev_btn = tk.Button(header_frame, text="❮", command=prev_month,
                            font=('SF Pro Display', 12), relief='flat', width=3)
        prev_btn.pack(side='left', padx=10, pady=10)
        
        year_label = tk.Label(header_frame, text="", bg='#f0f0f0',
                            font=('SF Pro Display', 16, 'bold'))
        year_label.pack(side='left', expand=True)
        
        next_btn = tk.Button(header_frame, text="❯", command=next_month,
                            font=('SF Pro Display', 12), relief='flat', width=3)
        next_btn.pack(side='right', padx=10, pady=10)
        
        # Календарь
        calendar_frame = tk.Frame(self.root, bg='white')
        calendar_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        days_frame = tk.Frame(calendar_frame, bg='white')
        days_frame.pack(fill='x')
        
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for day in days:
            tk.Label(days_frame, text=day, bg='white',
                    font=('SF Pro Display', 10, 'bold'),
                    width=5).pack(side='left', expand=True)
        
        self.calendar_grid = tk.Frame(calendar_frame, bg='white')
        self.calendar_grid.pack(fill='both', expand=True)
        
        def draw_calendar():
            # Очищаем сетку
            for widget in self.calendar_grid.winfo_children():
                widget.destroy()
            
            # Получаем первый день месяца
            first_day = datetime.datetime(self.calendar_year, self.calendar_month, 1)
            # Начинаем с понедельника (0 = понедельник, 6 = воскресенье)
            weekday = first_day.weekday()
            if weekday == 6:  # Если воскресенье, то сдвигаем на 6 дней назад
                weekday = -1
            
            # Получаем количество дней в месяце
            if self.calendar_month == 12:
                num_days = 31
            else:
                next_month = datetime.datetime(self.calendar_year, self.calendar_month + 1, 1)
                num_days = (next_month - first_day).days
            
            # Создаем сетку для дней
            day_num = 1
            for i in range(6):  # 6 недель максимум
                week_frame = tk.Frame(self.calendar_grid, bg='white')
                week_frame.pack(fill='x')
                
                for j in range(7):  # 7 дней недели
                    if (i == 0 and j <= weekday) or day_num > num_days:
                        day_frame = tk.Frame(week_frame, bg='white', width=50, height=50)
                    else:
                        day_frame = tk.Frame(week_frame, bg='white', width=50, height=50)
                        tk.Label(day_frame, text=str(day_num), bg='white',
                                font=('SF Pro Display', 10)).pack(expand=True)
                        day_num += 1
                    
                    day_frame.pack(side='left', expand=True, fill='both')
                    day_frame.pack_propagate(False)
        
        update_calendar()

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()
"""
                
                # Сохраняем файл приложения
                with open(app_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Проверяем, установлено ли приложение
                existing_app = next((a for a in self.installed_apps if a["name"] == app['name']), None)
                
                if existing_app:
                    # Обновляем приложение
                    existing_app["path"] = str(app_file)
                    existing_app["version"] = app['version']
                    app['update_available'] = False
                    self.add_notification(f"🔄 {app['name']} обновлено до версии {app['version']}")
                else:
                    # Добавляем новое приложение
                    self.installed_apps.append({
                        "name": app['name'],
                        "path": str(app_file),
                        "type": "gui",
                        "version": app['version'],
                        "icon": app['icon']
                    })
                    self.add_notification(f"✅ {app['name']} успешно установлен")
                
                save_apps_db(self.installed_apps)
                
                # Обновляем статус установки
                app['installed'] = True
                for i, a in enumerate(self.installable_apps):
                    if a['name'] == app['name']:
                        self.installable_apps[i]['installed'] = True
                        self.installable_apps[i]['update_available'] = False
                        break
                save_installable_apps(self.installable_apps)
                
                # Обновляем интерфейс
                install_btn.config(text="Открыть", bg=self.colors['primary'])
            else:
                # Запускаем приложение
                app_info = next((a for a in self.installed_apps if a["name"] == app['name']), None)
                if app_info:
                    self.launch_app(app_info)
        
        install_btn.bind('<Button-1>', lambda e: install_app())
    
    def open_notification_center(self, source_position=None):
        self.add_notification("🔔 Открыт центр уведомлений")
        
        def notification_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="Центр уведомлений", 
                    font=('SF Pro Display', 16, 'bold'), bg=self.colors['background']).pack(pady=10)
            
            # Уведомления
            notif_frame = tk.Frame(frame, bg=self.colors['card'], relief='raised', bd=1)
            notif_frame.pack(fill='x', pady=5)
            
            notif_label = tk.Label(notif_frame, text="Последние уведомления", 
                                  bg=self.colors['card'], font=('SF Pro Display', 12, 'bold'))
            notif_label.pack(anchor='w', padx=10, pady=5)
            
            notif_list = tk.Listbox(notif_frame, bg=self.colors['surface_light'],
                                   font=('SF Pro Display', 10), height=5)
            notif_list.pack(fill='x', padx=10, pady=5)
            
            for notif in self.notifications[-5:]:
                notif_list.insert(tk.END, f"[{notif['time']}] {notif['message']}")
            
            # Быстрые настройки
            settings_frame = tk.Frame(frame, bg=self.colors['card'], relief='raised', bd=1)
            settings_frame.pack(fill='x', pady=5)
            
            settings_label = tk.Label(settings_frame, text="Быстрые настройки", 
                                     bg=self.colors['card'], font=('SF Pro Display', 12, 'bold'))
            settings_label.pack(anchor='w', padx=10, pady=5)
            
            # Wi-Fi
            wifi_frame = tk.Frame(settings_frame, bg=self.colors['card'])
            wifi_frame.pack(fill='x', pady=5)
            
            wifi_label = tk.Label(wifi_frame, text=f"Wi-Fi: {'Включен' if self.wifi_status else 'Отключен'}",
                                 bg=self.colors['card'], font=('SF Pro Display', 12))
            wifi_label.pack(side='left', padx=10, pady=5)
            
            wifi_btn = tk.Button(wifi_frame, text="Переключить", 
                                command=lambda: self.toggle_wifi_and_update(wifi_label),
                                bg=self.colors['primary'], fg='white')
            wifi_btn.pack(side='right', padx=10, pady=5)
            
            # Bluetooth
            bluetooth_frame = tk.Frame(settings_frame, bg=self.colors['card'])
            bluetooth_frame.pack(fill='x', pady=5)
            
            bluetooth_label = tk.Label(bluetooth_frame, text=f"Bluetooth: {'Включен' if self.bluetooth_status else 'Отключен'}",
                                      bg=self.colors['card'], font=('SF Pro Display', 12))
            bluetooth_label.pack(side='left', padx=10, pady=5)
            
            bluetooth_btn = tk.Button(bluetooth_frame, text="Переключить", 
                                     command=lambda: self.toggle_bluetooth_and_update(bluetooth_label),
                                     bg=self.colors['primary'], fg='white')
            bluetooth_btn.pack(side='right', padx=10, pady=5)
            
            # Громкость
            volume_frame = tk.Frame(settings_frame, bg=self.colors['card'])
            volume_frame.pack(fill='x', pady=5)
            
            tk.Label(volume_frame, text="Громкость:", bg=self.colors['card'],
                    font=('SF Pro Display', 12)).pack(side='left', padx=10, pady=5)
            
            volume_scale = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal',
                                   bg=self.colors['background'], fg=self.colors['text'],
                                   font=('SF Pro Display', 10))
            volume_scale.set(self.volume_level)
            volume_scale.pack(fill='x', padx=10, pady=5)
            
            def update_volume(val):
                self.set_volume(int(float(val)))
            
            volume_scale.config(command=update_volume)
            
            # Яркость
            brightness_frame = tk.Frame(settings_frame, bg=self.colors['card'])
            brightness_frame.pack(fill='x', pady=5)
            
            tk.Label(brightness_frame, text="Яркость:", bg=self.colors['card'],
                    font=('SF Pro Display', 12)).pack(side='left', padx=10, pady=5)
            
            brightness_scale = tk.Scale(brightness_frame, from_=0, to=100, orient='horizontal',
                                       bg=self.colors['background'], fg=self.colors['text'],
                                       font=('SF Pro Display', 10))
            brightness_scale.set(self.brightness_level)
            brightness_scale.pack(fill='x', padx=10, pady=5)
            
            def update_brightness(val):
                self.set_brightness(int(float(val)))
            
            brightness_scale.config(command=update_brightness)
            
            # Раскладка клавиатуры
            keyboard_frame = tk.Frame(settings_frame, bg=self.colors['card'])
            keyboard_frame.pack(fill='x', pady=5)
            
            keyboard_label = tk.Label(keyboard_frame, text=f"Раскладка: {self.settings.get('keyboard_layout', 'en')}",
                                    bg=self.colors['card'], font=('SF Pro Display', 12))
            keyboard_label.pack(side='left', padx=10, pady=5)
            
            def toggle_keyboard_layout():
                current_layout = self.settings.get('keyboard_layout', 'en')
                new_layout = 'ru' if current_layout == 'en' else 'en'
                self.settings['keyboard_layout'] = new_layout
                self.save_settings()
                keyboard_label.config(text=f"Раскладка: {new_layout}")
            
            keyboard_btn = tk.Button(keyboard_frame, text="Сменить", 
                                    command=toggle_keyboard_layout,
                                    bg=self.colors['primary'], fg='white')
            keyboard_btn.pack(side='right', padx=10, pady=5)
        
        self.create_window("Центр уведомлений", notification_content, 600, 500, source_position=source_position)
    
    def open_volume_control(self, source_position=None):
        def volume_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="Управление громкостью", 
                    font=('SF Pro Display', 16, 'bold'), bg=self.colors['background']).pack(pady=10)
            
            volume_scale = tk.Scale(frame, from_=0, to=100, orient='horizontal',
                                   bg=self.colors['background'], fg=self.colors['text'],
                                   font=('SF Pro Display', 12))
            volume_scale.set(self.volume_level)
            volume_scale.pack(fill='x', padx=20, pady=10)
            
            def update_volume(val):
                self.set_volume(int(float(val)))
            
            volume_scale.config(command=update_volume)
            
            test_btn = tk.Button(frame, text="Тест звука", 
                                command=self.play_test_sound,
                                bg=self.colors['primary'], fg='white')
            test_btn.pack(pady=10)
        
        self.create_window("Громкость", volume_content, 400, 200, source_position=source_position)
    
    def open_brightness_control(self, source_position=None):
        def brightness_content(parent):
            frame = tk.Frame(parent, bg=self.colors['background'])
            frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(frame, text="Управление яркостью", 
                    font=('SF Pro Display', 16, 'bold'), bg=self.colors['background']).pack(pady=10)
            
            brightness_scale = tk.Scale(frame, from_=0, to=100, orient='horizontal',
                                       bg=self.colors['background'], fg=self.colors['text'],
                                       font=('SF Pro Display', 12))
            brightness_scale.set(self.brightness_level)
            brightness_scale.pack(fill='x', padx=20, pady=10)
            
            def update_brightness(val):
                self.set_brightness(int(float(val)))
            
            brightness_scale.config(command=update_brightness)
        
        self.create_window("Яркость", brightness_content, 400, 200, source_position=source_position)
    
    def play_test_sound(self):
        try:
            # Проверяем, инициализирован ли mixer
            if pygame.mixer.get_init():
                # Создаем короткий звуковой сигнал
                sound = pygame.mixer.Sound(buffer=bytes([128]*4096))
                sound.play()
            else:
                # Если mixer не инициализирован, используем системный звук
                os.system("aplay -q /usr/share/sounds/speech-dispatcher/test.wav 2>/dev/null || echo -e '\a'")
        except:
            self.add_notification("🔊 Тестовый звук воспроизведен")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        os_system = O1SOperatingSystem()
        os_system.run()
    except KeyboardInterrupt:
        print("\nO1S завершена пользователем")
    except Exception as e:
        print(f"Ошибка запуска O1S: {e}")
