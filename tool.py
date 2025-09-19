import requests
import random
from PIL import Image, ImageTk
from io import BytesIO
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import os
import glob
import shutil
import webbrowser
from urllib.parse import quote


# Biến toàn cục
destination_folder = ""
lang_var = None  # khai báo trước
main_ui_window = None  # window chính
agent_image_label = None
loaded_once = False

choice_map = {
    "en_US": "en_US",
    "ja_JP": "ja_JP",
    "ko_KR": "ko_KR",
}


# --- Hàm chức năng ---
def showMatureContent():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        source_folder = os.path.join(current_dir, "setting_files/mature_content")

        for filename in os.listdir(source_folder):
            source_file = os.path.join(source_folder, filename)
            if os.path.isfile(source_file):
                shutil.copy(source_file, destination_folder)

        messagebox.showinfo("Success", "Add Mature Content success!")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def removeVNGLogo():
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
        messagebox.showerror("Lỗi", str(e))


# def changeLanguage():
#     try:
#         choice = lang_var.get()
#         if choice not in choice_map:
#             messagebox.showwarning("Cảnh báo", "Vui lòng chọn ngôn ngữ hợp lệ!")
#             return

#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         source_folder = os.path.join(current_dir, "setting_files/language", choice_map[choice])

#         for filename in os.listdir(source_folder):
#             source_file = os.path.join(source_folder, filename)
#             if os.path.isfile(source_file):
#                 shutil.copy(source_file, destination_folder)

#         messagebox.showinfo("Hoàn tất", f"Đã chuyển ngôn ngữ sang {choice_map[choice]}!")
#     except Exception as e:
#         messagebox.showerror("Lỗi", str(e))


# --- Hàm lấy agent ---
def get_agents_list():
    url = "https://valorant-api.com/v1/agents"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Lỗi khi lấy dữ liệu: {response.status_code}")
    
    data = response.json()
    agents = [agent for agent in data['data'] if agent['isPlayableCharacter']]
    if not agents:
        raise Exception("Không tìm thấy agent nào")
    
    return agents

def load_agent_image():
    size = (80, 80)
    agentList = get_agents_list()

    photos = []
    for item in agentList:
        url = item['displayIcon']
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = img.resize(size)
        photo = ImageTk.PhotoImage(img)
        photos.append((item['displayName'], photo))  # nên hiển thị tên agent thay vì basename của URL
    return photos

# --- Hàm mở trang agent ---
def open_agent_page(agent_name):
    # Chuyển tên agent thành lowercase, thay khoảng trắng bằng "-"
    agent_slug = agent_name.lower().replace(" ", "-")
    url = f"https://playvalorant.com/en-us/agents/{agent_slug}/"

    webbrowser.open(url)

def open_lineup_page(page_number):
    url = "https://lineupsvalorant.com/"

    if page_number == 1:
        url = "https://lineupsvalorant.com/"
    else:
        url = "https://strats.gg/valorant/lineups"

    webbrowser.open(url)

def open_tracker_page(player_name):
    encode_name = quote(player_name);
    url = f"https://tracker.gg/valorant/profile/riot/{encode_name}/overview"
    webbrowser.open(url)

def update_edpi(*args):
    try:
        dpi = int(dpi_var.get())
        sens = float(sens_var.get())
        edpi = dpi * sens
        edpi_label.config(text=f"eDPI: {edpi:.2f}")
        
        # Recommendation based on eDPI
        if 200 <= edpi <= 400:
            recommend_label.config(text="✅ Within the eDPI range pros usually use (200 – 400)")
        elif edpi < 200:
            recommend_label.config(text="⬇️ Low eDPI, mouse movement may feel slow")
        else:
            recommend_label.config(text="⬆️ High eDPI, mouse movement may feel too fast")
    except ValueError:
        edpi_label.config(text="eDPI: ---")
        recommend_label.config(text="")


# --- Giao diện chính ---
def main_ui():
    global lang_var, main_ui_window, agent_image_label, name_label, role_label, dpi_var, sens_var, edpi_label, recommend_label
    main_ui_window = tk.Tk()
    main_ui_window.title("VALORANT Settings Manager")
    # Full screen window
    main_ui_window.geometry("900x700")

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

    main_ui_window.configure(bg="#1e1e2f")

    notebook = ttk.Notebook(main_ui_window)
    notebook.pack(expand=True, fill='both')

    # ---------- Tab 1: Settings Manager ----------
    tab1 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab1, text="Settings Manager")

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

    tk.Label(tab1, text="VALORANT Settings Manager",
             font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

    # Nút chức năng
    btn_mature = tk.Button(tab1, text="Add Mature Content", command=showMatureContent, **button_style)
    btn_mature.pack(pady=5)

    btn_remove_logo = tk.Button(tab1, text="Delete VNGLogo", command=removeVNGLogo, **button_style)
    btn_remove_logo.pack(pady=5)

    # ---------- Tab 2: Random Agent ----------
    tab2 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab2, text="Random Agent")

    tk.Label(tab2, text="Random Valorant Agent",
             font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

    # tạo canvas + scrollbar
    canvas = tk.Canvas(tab2, bg="#1e1e2f", highlightthickness=0)
    scrollbar = tk.Scrollbar(tab2, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1e1e2f")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((canvas.winfo_width() // 2, 0),
                     window=scrollable_frame, anchor="n")    
    canvas.configure(yscrollcommand=scrollbar.set)

    def resize_canvas(event):
        canvas.itemconfig(frame_window, width=event.width)

    frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
    canvas.bind("<Configure>", resize_canvas)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Label loading
    loading_label = tk.Label(scrollable_frame, text="Loading all agents...", fg="white", bg="#1e1e2f", font=("Arial", 14))
    loading_label.pack(pady=20)

    # Thêm ảnh vào giao diện
    def load_images_into_tab2():
        agent_list = load_agent_image()  # [(name, PhotoImage), ...]

        # xóa label loading
        loading_label.pack_forget()

        # lấy chiều rộng frame hiện tại
        scrollable_frame.update_idletasks()
        frame_width = scrollable_frame.winfo_width()
        if frame_width <= 1:  # khi chưa render thì lấy width của canvas
            frame_width = canvas.winfo_width()

        # ảnh giả định rộng khoảng 120px (ảnh + text + padding)
        item_width = 120
        cols = max(1, frame_width // item_width)

        row, col = 0, 0
        tab2.agent_widgets = []  # lưu lại widget để random highlight

        for name, photo in agent_list:
            frame = tk.Frame(scrollable_frame, bg="#1e1e2f", padx=4, pady=4)
            frame.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

            lbl_img = tk.Label(frame, image=photo, bd=0, highlightthickness=3, highlightbackground="#1e1e2f")

            lbl_img.image = photo
            lbl_img.pack()

            lbl_txt = tk.Label(frame, text=name, fg="white", bg="#1e1e2f")
            lbl_txt.pack()

            tab2.agent_widgets.append((frame, lbl_img, lbl_txt))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        # căn đều các cột
        for c in range(cols):
            scrollable_frame.grid_columnconfigure(c, weight=1)

        # thêm nút Random
        btn_random = tk.Button(scrollable_frame, text="🎲 Random Agent",
                            font=("Segoe UI", 12, "bold"),
                            bg="#ff4655", fg="white",
                            activebackground="#ff6b7d", activeforeground="white",
                            relief="flat", padx=10, pady=5,
                            command=lambda: start_random_animation(tab2.agent_widgets))
        btn_random.grid(row=row+1, column=0, columnspan=cols, pady=20)

        tab2.loaded = True  # đánh dấu đã load

    def start_random_animation(widgets):
        if getattr(tab2, "random_running", False):
            return

        tab2.random_running = True
        target_index = random.randint(0, len(widgets) - 1)

        # Chạy ít nhấn 2 vòng
        cycles = len(widgets) * 1
        steps = cycles + target_index
        delay = 50  # tốc độ ban đầu (ms)

        def highlight(step, delay):
            # reset border
            for frame, lbl_img, lbl_txt in widgets:
                lbl_img.config(highlightbackground="#1e1e2f")

            if step < steps:
                # highlight random
                index = random.randint(0, len(widgets) - 1)
                f, lbl_img, lbl_txt = widgets[index]
                lbl_img.config(highlightbackground="#ff4655")

                # tăng delay khi gần cuối
                new_delay = delay + (step // len(widgets)) * 20
                main_ui_window.after(new_delay, lambda: highlight(step+1, new_delay))
            else:
                # highlight target duy nhất
                f, lbl_img, lbl_txt = widgets[target_index]
                lbl_img.config(highlightbackground="#ff4655")
                tab2.random_running = False
                show_random_result(lbl_txt.cget("text"), lbl_img)

        highlight(0, delay)

    def show_random_result(agent_name, lbl_img):
        # popup hiển thị kết quả
        popup = tk.Toplevel(main_ui_window)
        popup.title("Random Result")
        popup.configure(bg="#1e1e2f")
        popup.geometry("300x200")

        # canh giữa màn hình chính
        x = main_ui_window.winfo_x() + (main_ui_window.winfo_width() // 2 - 150)
        y = main_ui_window.winfo_y() + (main_ui_window.winfo_height() // 2 - 150)
        popup.geometry(f"300x200+{x}+{y}")

        # lấy ảnh từ label (đã có sẵn)
        img = lbl_img.image
        lbl_img_popup = tk.Label(popup, image=img, bg="#1e1e2f")
        lbl_img_popup.image = img
        lbl_img_popup.pack(pady=10)

        lbl_img_popup.bind("<Button-1>", lambda e: open_agent_page(agent_name))
        lbl_img_popup.config(cursor="hand2")  # "hand2" là biểu tượng tay

        # text kết quả
        lbl_txt = tk.Label(popup, text=f"You got: {agent_name} 🎉",
                        font=("Segoe UI", 14, "bold"),
                        fg="#ff4655", bg="#1e1e2f")
        lbl_txt.pack(pady=10)

        # nút đóng
        btn_close = tk.Button(popup, text="OK", command=popup.destroy,
                            font=("Segoe UI", 11, "bold"),
                            bg="#ff4655", fg="white",
                            activebackground="#ff6b7d", relief="flat", padx=10, pady=5)
        btn_close.pack(pady=10)

        # popup luôn nằm trên cùng
        popup.transient(main_ui_window)
        popup.grab_set()

    # ---------- Tab 3: Support Manager ----------
    tab3 = tk.Frame(notebook, bg="#1e1e2f")
    notebook.add(tab3, text="Support Tool")

    tk.Label(tab3, text="Lineup Agent",
             font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

    open_lineup_first = tk.Button(tab3, text="lineupsvalorant.com", command = lambda: open_lineup_page(1),
                             bg="#1e91ff", fg="white", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=25, height=2)
    open_lineup_first.pack(pady=5)

    open_lineup_second = tk.Button(tab3, text="strats.gg", command = lambda: open_lineup_page(2),
                             bg="#1e91ff", fg="white", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=25, height=2)
    open_lineup_second.pack(pady=5)

    tk.Label(tab3, text="Tracker Player",
             font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

    play_name = tk.Entry(tab3, font=("Segoe UI", 11), width=40)
    play_name.insert(0, "DeathProof#1606")  # Giá trị mặc định
    play_name.pack(pady=5)

    tracker_btn = tk.Button(
        tab3, text="Tracking", 
        command=lambda : open_tracker_page(play_name.get()), 
        bg="#1e91ff", fg="white", 
        font=("Segoe UI", 11, "bold"),
        bd=0, relief="flat", width=15, height=1
    )
    tracker_btn.pack(pady=5)

    tk.Label(tab3, text="eDPI Calculator",
            font=("Segoe UI", 18, "bold"), fg="#ff4655", bg="#1e1e2f").pack(pady=10)

    # Biến liên kết
    dpi_var = tk.StringVar(value="800")
    sens_var = tk.StringVar(value="0.5")

    dpi_var.trace_add("write", update_edpi)
    sens_var.trace_add("write", update_edpi)

    # Label & Entry DPI
    tk.Label(tab3, text="DPI:", font=("Segoe UI", 11)).pack(pady=5)
    tk.Entry(tab3, textvariable=dpi_var, font=("Segoe UI", 11)).pack(pady=5)

    # Label & Entry Sensitivity
    tk.Label(tab3, text="Sensitivity:", font=("Segoe UI", 11)).pack(pady=5)
    tk.Entry(tab3, textvariable=sens_var, font=("Segoe UI", 11)).pack(pady=5)

    # Label hiển thị kết quả eDPI
    edpi_label = tk.Label(tab3, text="eDPI: ---", font=("Segoe UI", 12, "bold"), fg="#1e91ff")
    edpi_label.pack(pady=10)

    # Label gợi ý
    recommend_label = tk.Label(tab3, text="", font=("Segoe UI", 10), fg="gray")
    recommend_label.pack()

    # Gọi update lần đầu
    update_edpi()

    # ---------- Tab 4: Crosshair Sample ----------


    # ---------- Tab 5: Zalopay VP Calculator ----------

    # Hover effect cho tất cả nút
    def on_enter(e):
        e.widget['bg'] = "#ff6b7d" if e.widget['bg'] == "#ff4655" else "#1ea1ff"

    def on_leave(e):
        e.widget['bg'] = "#ff4655" if e.widget['bg'] in ["#ff6b7d","#ff4655"] else "#1e91ff"

    for btn in [btn_mature, btn_remove_logo, open_lineup_first, open_lineup_second, tracker_btn]:
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)


    def on_tab_changed(event):
        tab = event.widget.tab("current")["text"]
        if tab == "Random Agent" and not hasattr(tab2, "loaded"):
            # giữ cho UI render "Loading..." trước khi load ảnh
            main_ui_window.after(100, load_images_into_tab2)

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    main_ui_window.mainloop()

# --- Giao diện 1: Nhập folder ---
def open_main_ui():
    global destination_folder
    folder = folder_var.get()
    if not folder or not os.path.isdir(folder):
        messagebox.showerror("Lỗi", "Vui lòng chọn folder hợp lệ!")
        return

    destination_folder = folder
    folder_window.destroy()
    main_ui()


def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)


folder_window = tk.Tk()
folder_window.title("Chọn Destination Folder")
folder_window.geometry("500x250")  # tăng chiều cao
folder_window.resizable(False, False)
folder_window.configure(bg="#1e1e2f")

folder_var = tk.StringVar(value=r"D:\Riot Games\VALORANT\live\ShooterGame\Content\Paks")  # giá trị mặc định

# Gợi ý cho người dùng
tk.Label(folder_window, text="Bạn có thể tìm Destination Folder ở setting game Valorant trong RiotClient", 
         fg="#ffffff", bg="#1e1e2f", font=("Segoe UI", 10, "italic")).pack(pady=(15,5))

tk.Label(folder_window, text="Chọn hoặc nhập Destination Folder:", fg="#ffffff", bg="#1e1e2f", font=("Segoe UI", 12, "bold")).pack(pady=5)
tk.Entry(folder_window, textvariable=folder_var, width=50, font=("Segoe UI", 11)).pack(pady=5)
tk.Button(folder_window, text="📂 Browse", command=browse_folder, bg="#ff4655", fg="#ffffff", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=12, height=1).pack(pady=5)
tk.Button(folder_window, text="Xác nhận", command=open_main_ui, bg="#ff4655", fg="#ffffff", font=("Segoe UI", 11, "bold"), bd=0, relief="flat", width=12, height=1).pack(pady=5)

# Hover effect
def on_enter(e):
    e.widget['bg'] = "#ff6b7d"

def on_leave(e):
    e.widget['bg'] = "#ff4655"

for btn in folder_window.winfo_children():
    if isinstance(btn, tk.Button):
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

folder_window.mainloop()
