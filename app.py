import requests, random, os, sys, re, time, json, glob, shutil, threading, webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from urllib.parse import quote
import winreg, psutil, pystray
from PIL import Image, ImageTk
from io import BytesIO
import pygame

# ========= Storage Path =========
def get_storage_path(filename: str) -> Path:
    app_name = "ValorantTool"
    appdata = Path(os.getenv("APPDATA")) / app_name
    appdata.mkdir(parents=True, exist_ok=True)
    return appdata / filename

BACKUP_FILE = get_storage_path("optimizer_backup.json")
CACHE_DIR = get_storage_path("cache")
CACHE_FILE = get_storage_path("agents_cache.json")
CACHE_TTL = 86400
os.makedirs(CACHE_DIR, exist_ok=True)

def is_cache_expired(path, max_age=CACHE_TTL):
    return not os.path.exists(path) or (time.time() - os.path.getmtime(path)) > max_age

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ICON_PNG = resource_path("setting_files/logo.png")
ICON_ICO = resource_path("setting_files/logo.ico")
SPIKE_DEFUSE_SOUND = resource_path("setting_files/audio/defuse_sound.mp3")
SPIKE_ACTIVE_SOUND = resource_path("setting_files/audio/spike_sound.mp3")

# --- Global flag to show tray message only once ---
tray_message_shown = False

# ========= UI =========
def run_tray(root):
    def on_quit(icon,item):
        icon.stop()
        root.destroy()
        os._exit(0)

    def show_window(icon,item):
        icon.stop()
        root.after(0, root.deiconify)

    menu = pystray.Menu(pystray.MenuItem("Open", show_window), pystray.MenuItem("Quit", on_quit))
    tray_icon = Image.open(ICON_PNG)
    icon = pystray.Icon("app", tray_icon, "Valorant Tool", menu)
    icon.run()

def hide_window(root):
    root.withdraw()
    if not tray_message_shown:
        messagebox.showinfo(
            "Valorant Tool",
            "The application is still running in the system tray.\nRight-click the icon to quit."
        )
        tray_message_shown = True

    threading.Thread(target=run_tray,args=(root,),daemon=True).start()

class SettingManager:
    def __init__(self, parent):
        self.parent = parent

        button_style = {
            "font": ("Segoe UI", 11, "bold"),
            "bg": "#ff4655",
            "fg": "#ffffff",
            "activebackground": "#ff6b7d",
            "activeforeground": "#ffffff",
            "bd": 0,
            "relief": "flat",
            "width": 25,
            "height": 2
        }

        tk.Label(parent, text="VALORANT Settings Manager",
                font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

        # Nút chức năng
        tk.Button(parent, text="Add Mature Content", command=self.showMatureContent, **button_style).pack(pady=5)

        tk.Button(parent, text="Delete VNGLogo", command=self.removeVNGLogo, **button_style).pack(pady=5)

        tk.Button(parent, text="Valorant Optimizer", command=self.optimize_settings, **button_style).pack(pady=5)

        tk.Button(parent, text="Restore Valorant Optimizer", command=self.restore_settings, **button_style).pack(pady=5)


    def save_backup(self, data): 
        with open(BACKUP_FILE,"w") as f: json.dump(data,f)

    def load_backup(self):
        return json.load(open(BACKUP_FILE)) if os.path.exists(BACKUP_FILE) else {}

    def get_current_settings(self):
        settings = {}
        try:
            paths = {
                r"SOFTWARE\Microsoft\GameBar": ["AllowAutoGameMode","AutoGameModeEnabled","ShowStartupPanel","GameDVR_Enabled"],
                r"System\GameConfigStore": ["GameDVR_Enabled","GameDVR_FSEBehaviorMode","GameDVR_HonorUserFSEBehaviorMode","GameDVR_EFSEFeatureFlags"],
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR": ["AppCaptureEnabled","HistoricalCaptureEnabled"]
            }
            for k,v in paths.items():
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, k, 0, winreg.KEY_READ) as key:
                    for name in v:
                        try: settings[name]=winreg.QueryValueEx(key,name)[0]
                        except FileNotFoundError: pass
        except Exception as e: print("Backup error:",e)
        return settings

    def showMatureContent(self):
        try:
            source_folder = resource_path("setting_files/mature_content")

            for filename in os.listdir(source_folder):
                source_file = os.path.join(source_folder, filename)
                if os.path.isfile(source_file):
                    shutil.copy(source_file, destination_folder)

            messagebox.showinfo("Success", "Add Mature Content success!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def removeVNGLogo(self):
        try:
            pattern = os.path.join(destination_folder, "VNGLogo-WindowsClient.*")
            files_to_delete = glob.glob(pattern)

            if not files_to_delete:
                messagebox.showinfo("Notice", "No VNGLogo files found to delete.")
                return

            for file_path in files_to_delete:
                os.remove(file_path)

            messagebox.showinfo("Success", "Delete VNGLogo success!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def optimize_settings(self):
        try:
            if not os.path.exists(BACKUP_FILE): self.save_backup(self.get_current_settings())
            # Disable GameMode / DVR / GameBar
            set_registry = lambda k,n,v: winreg.SetValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER,k,0,winreg.KEY_SET_VALUE),n,0,winreg.REG_DWORD,v)
            set_registry(r"SOFTWARE\Microsoft\GameBar","AllowAutoGameMode",0)
            set_registry(r"SOFTWARE\Microsoft\GameBar","AutoGameModeEnabled",0)
            set_registry(r"SOFTWARE\Microsoft\GameBar","ShowStartupPanel",0)
            set_registry(r"SOFTWARE\Microsoft\GameBar","GameDVR_Enabled",0)
            set_registry(r"System\GameConfigStore","GameDVR_Enabled",0)
            set_registry(r"System\GameConfigStore","GameDVR_FSEBehaviorMode",2)
            set_registry(r"System\GameConfigStore","GameDVR_HonorUserFSEBehaviorMode",1)
            set_registry(r"System\GameConfigStore","GameDVR_EFSEFeatureFlags",0)
            set_registry(r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR","AppCaptureEnabled",0)
            set_registry(r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR","HistoricalCaptureEnabled",0)
            # High Priority Valorant
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and "VALORANT-Win64-Shipping.exe" in proc.info['name']:
                    psutil.Process(proc.pid).nice(psutil.HIGH_PRIORITY_CLASS)
                    break
            # Clear temp
            for d in [os.environ.get("TEMP"), r"C:\Windows\Temp"]:
                if d and os.path.exists(d):
                    try: shutil.rmtree(d,ignore_errors=True); os.makedirs(d,exist_ok=True)
                    except: pass
            messagebox.showinfo("Success","Optimize complete!")
        except Exception as e: messagebox.showerror("Error",str(e))

    def restore_settings(self):
        try:
            data= self.load_backup()
            if not data: return
            paths = {
                r"SOFTWARE\Microsoft\GameBar": ["AllowAutoGameMode","AutoGameModeEnabled","ShowStartupPanel","GameDVR_Enabled"],
                r"System\GameConfigStore": ["GameDVR_Enabled","GameDVR_FSEBehaviorMode","GameDVR_HonorUserFSEBehaviorMode","GameDVR_EFSEFeatureFlags"],
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR": ["AppCaptureEnabled","HistoricalCaptureEnabled"]
            }
            for k,v in paths.items():
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, k, 0, winreg.KEY_SET_VALUE) as key:
                    for name in v:
                        if name in data: winreg.SetValueEx(key,name,0,winreg.REG_DWORD,data[name])
            messagebox.showinfo("Success","✅ Restore successfully!")
        except Exception as e:
            messagebox.showerror("Restore Error",str(e))

class RandomAgent:
    def __init__(self, parent, notebook, root):
        self.parent = parent
        self.notebook = notebook
        self.root = root
        self.agent_widgets = []
        self.loaded = False
        self.random_running = False

        tk.Label(parent, text="Random Valorant Agent",
                 font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

        # canvas + scrollbar
        self.canvas = tk.Canvas(parent, bg="#1e1e2f", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#1e1e2f")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.frame_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self.resize_canvas)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Label loading
        self.loading_label = tk.Label(self.scrollable_frame,
                                      text="Loading all agents...",
                                      fg="white", bg="#1e1e2f", font=("Arial", 14))
        self.loading_label.pack(pady=20)
        notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def get_agents_list(self):
        url = "https://valorant-api.com/v1/agents"
        if os.path.exists(CACHE_FILE) and not is_cache_expired(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        agents = [a for a in data['data'] if a['isPlayableCharacter']]
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(agents, f, ensure_ascii=False, indent=2)
        return agents

    def open_agent_page(self, agent_name):
        agent_slug = agent_name.lower().replace(" ", "-")
        webbrowser.open(f"https://playvalorant.com/en-us/agents/{agent_slug}/")

    def safe_filename(self, name: str) -> str:
        return re.sub(r'[\\/:"*?<>|]+', "_", name)

    def load_image_from_url(self, url, name, size=(80,80)):
        safe_name = self.safe_filename(name)
        cache_path = os.path.join(CACHE_DIR, f"{safe_name}.png")
        try:
            if os.path.exists(cache_path):
                img = Image.open(cache_path).resize(size, Image.LANCZOS)
            else:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                with open(cache_path, "wb") as f: f.write(response.content)
                img = Image.open(BytesIO(response.content)).resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print("⚠️ Error loading image:", e)
            return None

    def resize_canvas(self, event):
        self.canvas.itemconfig(self.frame_window, width=event.width)

    def load_images(self):
        agent_list = self.get_agents_list()
        self.loading_label.pack_forget()

        # tính số cột
        self.scrollable_frame.update_idletasks()
        frame_width = self.scrollable_frame.winfo_width() or self.canvas.winfo_width()
        item_width = 120
        cols = max(1, frame_width // item_width)

        row, col = 0, 0
        self.agent_widgets = []

        placeholder = ImageTk.PhotoImage(Image.new("RGB", (80, 80), "#333333"))

        for item in agent_list:
            name, url = item['displayName'], item['displayIcon']

            frame = tk.Frame(self.scrollable_frame, bg="#1e1e2f", padx=4, pady=4)
            frame.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

            lbl_img = tk.Label(frame, image=placeholder, bd=0,
                               highlightthickness=3, highlightbackground="#1e1e2f")
            lbl_img.image = placeholder
            lbl_img.pack()

            lbl_txt = tk.Label(frame, text=name, fg="white", bg="#1e1e2f")
            lbl_txt.pack()

            self.agent_widgets.append((frame, lbl_img, lbl_txt, url, name))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        for c in range(cols):
            self.scrollable_frame.grid_columnconfigure(c, weight=1)

        # nút random
        btn_random = tk.Button(self.scrollable_frame, text="🎲 Random Agent",
                               font=("Segoe UI", 12, "bold"),
                               bg="#ff4655", fg="white",
                               activebackground="#ff6b7d", activeforeground="white",
                               relief="flat", padx=10, pady=5,
                               command=self.start_random_animation)
        btn_random.grid(row=row+1, column=0, columnspan=cols, pady=20)

        self.loaded = True

        # thread load ảnh dần
        def worker():
            for frame, lbl_img, lbl_txt, url, name in self.agent_widgets:
                photo = self.load_image_from_url(url, name)
                if photo:
                    self.canvas.after(0, lambda lbl=lbl_img, p=photo: self.update_image(lbl, p))
        threading.Thread(target=worker, daemon=True).start()

    def update_image(self, label, photo):
        label.configure(image=photo)
        label.image = photo

    def start_random_animation(self):
        if self.random_running:
            return

        self.random_running = True
        target_index = random.randint(0, len(self.agent_widgets) - 1)
        cycles = len(self.agent_widgets) * 1
        steps = cycles + target_index
        delay = 50

        def highlight(step, delay):
            for frame, lbl_img, lbl_txt, url, name in self.agent_widgets:
                lbl_img.config(highlightbackground="#1e1e2f")

            if step < steps:
                index = random.randint(0, len(self.agent_widgets) - 1)
                frame, lbl_img, lbl_txt, url, name = self.agent_widgets[index]
                lbl_img.config(highlightbackground="#ff4655")

                new_delay = delay + (step // len(self.agent_widgets)) * 20
                self.root.after(new_delay, lambda: highlight(step+1, new_delay))
            else:
                frame, lbl_img, lbl_txt, url, name = self.agent_widgets[target_index]
                lbl_img.config(highlightbackground="#ff4655")
                self.random_running = False
                self.show_random_result(lbl_txt.cget("text"), lbl_img)

        highlight(0, delay)

    def show_random_result(self, agent_name, lbl_img):
        popup = tk.Toplevel(self.root)
        popup.title("Random Result")
        popup.configure(bg="#1e1e2f")
        popup.geometry("300x200")

        x = self.root.winfo_x() + (self.root.winfo_width() // 2 - 150)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2 - 150)
        popup.geometry(f"300x200+{x}+{y}")

        img = lbl_img.image
        lbl_img_popup = tk.Label(popup, image=img, bg="#1e1e2f")
        lbl_img_popup.image = img
        lbl_img_popup.pack(pady=10)

        lbl_img_popup.bind("<Button-1>", lambda e: self.open_agent_page(agent_name))
        lbl_img_popup.config(cursor="hand2")

        lbl_txt = tk.Label(popup, text=f"You got: {agent_name} 🎉",
                           font=("Segoe UI", 14, "bold"),
                           fg="#ff4655", bg="#1e1e2f")
        lbl_txt.pack(pady=10)

        btn_close = tk.Button(popup, text="OK", command=popup.destroy,
                              font=("Segoe UI", 11, "bold"),
                              bg="#ff4655", fg="white",
                              activebackground="#ff6b7d", relief="flat", padx=10, pady=5)
        btn_close.pack(pady=10)

        popup.transient(self.root)
        popup.grab_set()

    def on_tab_changed(self,event):
        tab = event.widget.tab("current")["text"]
        if tab == "Random Agent" and not self.loaded:
            self.root.after(100, self.load_images)
    
class SupportWeb:
    def __init__(self, parent):
        self.parent = parent
        self.urls = {
            1: "https://lineupsvalorant.com/",
            2: "https://strats.gg/valorant/lineups/",
            3: "https://www.vcrdb.net/"
        }

        tk.Label(parent, text="Lineup Agent",
                font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

        tk.Button(parent, text="lineupsvalorant.com", command = lambda: self.open_page(1),
                                bg="#1e91ff", fg="white", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=25, height=2).pack(pady=5)

        tk.Button(parent, text="strats.gg", command = lambda: self.open_page(2),
                                bg="#1e91ff", fg="white", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=25, height=2).pack(pady=5)

        tk.Label(parent, text="Tracker Player",
                font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

        self.play_name_entry = tk.Entry(parent, font=("Segoe UI", 11), width=40)
        self.play_name_entry.insert(0, "DeathProof#1606")
        self.play_name_entry.pack(pady=5)

        tk.Button(
            parent, text="Tracking", 
            command=lambda : self.open_tracker_page(self.play_name_entry.get()), 
            bg="#1e91ff", fg="white", 
            font=("Segoe UI", 11, "bold"),
            bd=0, relief="flat", width=15, height=1
        ).pack(pady=5)

        tk.Label(parent, text="Crosshair Collection",
                font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

        tk.Button(parent, text="vcrdb.net", command = lambda: self.open_page(3),
                                bg="#1e91ff", fg="white", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=25, height=2).pack(pady=5)

    def open_page(self, choice):
        webbrowser.open(self.urls.get(choice, "https://google.com"))

    def open_tracker_page(self, player_name):
        webbrowser.open(f"https://tracker.gg/valorant/profile/riot/{quote(player_name)}/overview")

### Spike Training
# ================= Spike Settings =================
SPIKE_TIMER = 45.0   # seconds
DEFUSE_TIME = 7.0    # seconds

class SpikeSimulator:
    def __init__(self, parent):
        self.parent = parent
        self.time_left = SPIKE_TIMER
        self.running = False
        self.timer_id = None
        self.show_timer = True  # ✅ mặc định hiển thị đúng với nút
        self.start_time = None

        # init pygame mixer cho âm thanh (bọc try/except)
        try:
            pygame.mixer.init()
        except pygame.error as e:
            print("⚠️ Pygame audio init failed:", e)

        # UI
        self.frame = tk.LabelFrame(parent, text="💣 Spike Simulator", font=("Arial", 12, "bold"), fg="white", bg="#0f1923")
        self.frame.pack(fill="x", pady=10, padx=10)

        self.timer_label = tk.Label(self.frame, text="Spike not planted", font=("Arial", 20), fg="white", bg="#0f1923")
        self.timer_label.pack(pady=10)

        btn_frame = tk.Frame(self.frame, bg="#0f1923")
        btn_frame.pack(pady=5)

        self.plant_btn = tk.Button(btn_frame, text="🔴 Plant", font=("Arial", 14), bg="#ff4655", fg="white", command=self.plant_spike, cursor="hand2")
        self.plant_btn.grid(row=0, column=0, padx=10)

        self.defuse_btn = tk.Button(btn_frame, text="🟢 Defuse", font=("Arial", 14), bg="#00ffae", fg="black", state="disabled", command=self.defuse_spike, cursor="hand2")
        self.defuse_btn.grid(row=0, column=1, padx=10)

        self.reset_btn = tk.Button(btn_frame, text="🔄 Reset", font=("Arial", 14), bg="#ffaa00", fg="black", state="disabled", command=self.reset, cursor="hand2")
        self.reset_btn.grid(row=0, column=2, padx=10)

        self.toggle_btn = tk.Button(self.frame, text="👁️ Hide Timer", font=("Arial", 12), bg="#1f51ff", fg="white", command=self.toggle_timer, cursor="hand2")
        self.toggle_btn.pack(pady=5)

        self.result_label = tk.Label(self.frame, text="", font=("Arial", 14), fg="white", bg="#0f1923")
        self.result_label.pack(pady=10)

        notes_frame = tk.LabelFrame(parent, text="📘 Notes", font=("Arial", 12, "bold"), fg="white", bg="#0f1923")
        notes_frame.pack(fill="x", pady=10, padx=10)

        notes_text = (
            "💣 Spike explodes after 45 seconds once planted.\n"
            "🟢 Full defuse time: 7 seconds.\n"
            "🟡 Half defuse (hold 3.5s): You can resume defusing from halfway if interrupted.\n"
            "⚠️ Always try to get a half first, then finish depending on the situation.\n"
            "💭 If little time remains, consider if 7s defuse + travel time is realistic.\n"
            "💼 If not, save your weapon and armor for the next round."
        )

        tk.Label(notes_frame, text=notes_text, font=("Arial", 11), justify="left", anchor="w", fg="#dddddd", bg="#0f1923", wraplength=500).pack(padx=10, pady=5, fill="x")

    def play_spike_audio(self):
        try:
            pygame.mixer.music.load(SPIKE_ACTIVE_SOUND)
            pygame.mixer.music.play()
        except Exception as e:
            print("⚠️ Audio error:", e)

    def play_defuse_audio(self):
        try:
            pygame.mixer.music.load(SPIKE_DEFUSE_SOUND)
            pygame.mixer.music.play()
        except Exception as e:
            print("⚠️ Audio error:", e)

    def stop_audio(self):
        pygame.mixer.music.stop()

    def update_timer(self):
        if not self.running:
            return

        elapsed = time.time() - self.start_time
        self.time_left = SPIKE_TIMER - elapsed

        if self.time_left >= 0:
            text = f"⏳ {self.time_left:.1f}s" if self.show_timer else "⏳ ???"
            self.timer_label.config(text=text)
            self.timer_id = self.parent.after(100, self.update_timer)
        else:
            # ✅ Dừng khi nổ
            self.running = False
            self.defuse_btn.config(state="disabled")
            self.reset_btn.config(state="normal")
            self.timer_label.config(text="💥 Spike exploded!")
            messagebox.showinfo("Result", "💥 Spike exploded!")

    def plant_spike(self):
        if self.timer_id:
            self.parent.after_cancel(self.timer_id)

        self.play_spike_audio()
        self.start_time = time.time()
        self.time_left = SPIKE_TIMER
        self.running = True
        self.defuse_btn.config(state="normal")
        self.reset_btn.config(state="disabled")
        self.result_label.config(text="")
        self.update_timer()

    def defuse_spike(self):
        if not self.running:
            return

        elapsed = time.time() - self.start_time
        remaining = SPIKE_TIMER - elapsed

        # ✅ Hiển thị thời gian còn lại trước khi nổ
        self.result_label.config(text=f"🕒 Remaining time before explosion: {remaining:.1f}s")

        self.stop_audio()
        self.play_defuse_audio()

        if remaining > DEFUSE_TIME:
            self.running = False
            if self.timer_id:
                self.parent.after_cancel(self.timer_id)
            self.defuse_btn.config(state="disabled")
            self.reset_btn.config(state="normal")
            self.result_label.config(text=f"✅ Defuse successful! ({remaining:.1f}s left)")
        else:
            self.running = False
            if self.timer_id:
                self.parent.after_cancel(self.timer_id)
            self.defuse_btn.config(state="disabled")
            self.reset_btn.config(state="normal")
            self.result_label.config(text=f"❌ Too late! Spike exploded")


    def toggle_timer(self):
        self.show_timer = not self.show_timer
        self.toggle_btn.config(text="👁️ Hide Timer" if self.show_timer else "👁️ Show Timer")

    def reset(self):
        if self.timer_id:
            self.parent.after_cancel(self.timer_id)
        self.time_left = SPIKE_TIMER
        self.running = False
        self.timer_label.config(text="Spike not planted")
        self.result_label.config(text="")
        self.defuse_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")
        self.stop_audio()

# ========= Entry UI =========
def open_main_ui(root, folder):
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("Error","Invalid folder!")
        return
    global destination_folder; destination_folder = folder

    destination_folder = folder
    root.withdraw()  # ẩn cửa sổ chọn folder

    main_ui = tk.Toplevel(root)
    main_ui.title("VALORANT Tool (VLT)")
    main_ui.geometry("900x700")
    main_ui.iconbitmap(ICON_ICO)
    main_ui.protocol("WM_DELETE_WINDOW", lambda: hide_window(main_ui))

    # ... bạn có thể copy giao diện Notebook và các tab từ file gốc vào đây,
    style = ttk.Style()
    style.theme_use('clam')  # theme dễ tùy chỉnh
    # Tab chưa chọn
    style.configure('TNotebook.Tab',
                    background='#2e2e3f',  # màu tab chưa chọn
                    foreground='white',
                    font=('Segoe UI', 11, 'bold'),
                    padding=[10,5])
    # Tab đang chọn
    style.map('TNotebook.Tab',
            background=[('selected', '#ff4655')],
            foreground=[('selected', 'white')])

    main_ui.configure(bg="#1e1e2f")

    notebook = ttk.Notebook(main_ui)
    notebook.pack(expand=True, fill='both')

    # ---------- Tab 1: Settings Manager ----------
    tab1 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab1, text="Settings Manager")
    SettingManager(tab1)

    # ---------- Tab 2: Random Agent ----------
    tab2 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab2, text="Random Agent")
    RandomAgent(tab2, notebook, main_ui)

    # ---------- Tab 3: Support Manager ----------
    tab3 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab3, text="Support Tool")
    SupportWeb(tab3)

    # ---------- Tab 4: Spike Defuse Training ----------
    tab4 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab4, text="Spike Defuse Training")
    SpikeSimulator(tab4)

    # Hover effect cho tất cả nút
    def on_enter(e):
        if e.widget['bg'] == "#ff4655":
            e.widget['bg'] = "#ff6b7d"
        else:
            e.widget['bg'] = "#1ea1ff"

    def on_leave(e):
        if e.widget['bg'] in ["#ff6b7d", "#ff4655"]:
            e.widget['bg'] = "#ff4655"
        else:
            e.widget['bg'] = "#1e91ff"

    root.bind_class("Button", "<Enter>", on_enter, add="+")
    root.bind_class("Button", "<Leave>", on_leave, add="+")

    main_ui.mainloop()
# ========= Start =========
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chọn Destination Folder")
    root.geometry("500x250")
    root.iconbitmap(ICON_ICO)
    root.configure(bg="#1e1e2f")

    folder_var = tk.StringVar(value=r"D:\Riot Games\VALORANT\live\ShooterGame\Content\Paks")

    tk.Label(root, text="Chọn hoặc nhập Destination Folder:", fg="#ffffff", bg="#1e1e2f", font=("Segoe UI", 12, "bold")).pack(pady=5)
    tk.Entry(root, textvariable=folder_var, width=50, font=("Segoe UI", 11)).pack(pady=5)
    tk.Button(root, text="📂 Browse", command=lambda: folder_var.set(filedialog.askdirectory()), bg="#ff4655", fg="#ffffff", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=12, height=1).pack(pady=5)
    tk.Button(root, text="Xác nhận", command=lambda : open_main_ui(root,folder_var.get()), bg="#ff4655", fg="#ffffff", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=12, height=1).pack(pady=5)
    tk.Label(root, text="Bạn có thể tìm Destination Folder ở setting game Valorant trong RiotClient", 
            fg="#ffffff", bg="#1e1e2f", font=("Segoe UI", 10, "italic")).pack(pady=(15,5))

    root.mainloop()
