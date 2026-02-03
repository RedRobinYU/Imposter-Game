import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os

DATA_FILE = "topics.json"

# ------------------------
# THEME COLORS
# ------------------------
BG = "#121212"
PANEL = "#1e1e1e"
TEXT = "#f0f0f0"
MUTED = "#9a9a9a"
GREEN = "#4CAF50"
RED = "#e53935"
GRAY = "#2a2a2a"

# ------------------------
# LOAD / SAVE DATA
# ------------------------
def load_topics():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_topics():
    with open(DATA_FILE, "w") as f:
        json.dump(topics, f, indent=2)

topics = load_topics()
players = []

roles = {}
viewed_players = set()
current_topic = ""
current_word = ""
current_hint = ""
starter_player = ""
starter_announced = False

# Toggles
show_topic = True          # GLOBAL (affects everyone)
show_hint_to_imposter = True

# ------------------------
# GUI SETUP
# ------------------------
root = tk.Tk()
root.title("Imposter Game")
root.geometry("360x640")
root.configure(bg=BG)

main = tk.Frame(root, padx=12, pady=12, bg=BG)
main.pack(fill="both", expand=True)

# ------------------------
# FONT SCALING
# ------------------------
def player_font_size():
    count = max(len(players), 1)
    if count <= 4:
        return 18
    elif count <= 7:
        return 14
    else:
        return 11

# ------------------------
# PLAYER FUNCTIONS
# ------------------------
def add_player():
    name = simpledialog.askstring("Add Player", "Player name:")
    if name and name not in players:
        players.append(name)
        update_players()

def remove_player():
    name = simpledialog.askstring("Remove Player", "Player name:")
    if name in players:
        players.remove(name)
        update_players()

def update_players():
    size = player_font_size()
    player_list.config(font=("Arial", size))
    player_list.delete(0, tk.END)
    for p in players:
        label = p + (" ✔" if p in viewed_players else "")
        player_list.insert(tk.END, label)

# ------------------------
# WORD MANAGEMENT
# ------------------------
def add_word():
    topic = simpledialog.askstring("Add Topic", "Topic name:")
    if not topic:
        return
    if topic not in topics:
        topics[topic] = {}

    word = simpledialog.askstring("Add Word", "Word:")
    hint = simpledialog.askstring("Add Hint", "Vague hint (association, NOT definition):")

    if word and hint:
        topics[topic][word] = hint
        save_topics()

def remove_word():
    topic = simpledialog.askstring("Remove Word", "Topic:")
    if topic not in topics:
        return
    word = simpledialog.askstring("Remove Word", "Word:")
    if word in topics[topic]:
        del topics[topic][word]
        save_topics()

# ------------------------
# TOGGLES
# ------------------------
def toggle_topic():
    global show_topic
    show_topic = not show_topic
    update_toggle_buttons()

def toggle_hint():
    global show_hint_to_imposter
    show_hint_to_imposter = not show_hint_to_imposter
    update_toggle_buttons()

def update_toggle_buttons():
    topic_btn.config(
        text=f"Show Topic to Players: {'ON' if show_topic else 'OFF'}",
        bg=GREEN if show_topic else GRAY
    )
    hint_btn.config(
        text=f"Imposter sees Hint: {'ON' if show_hint_to_imposter else 'OFF'}",
        bg=GREEN if show_hint_to_imposter else GRAY
    )

# ------------------------
# GAME LOGIC
# ------------------------
def start_game():
    global roles, viewed_players, current_topic, current_word
    global current_hint, starter_player, starter_announced

    if len(players) < 3:
        messagebox.showerror("Error", "At least 3 players required.")
        return

    if not topics:
        messagebox.showerror("Error", "No topics available.")
        return

    imposter_count = simpledialog.askinteger(
        "Imposters",
        "How many imposters?",
        minvalue=1,
        maxvalue=len(players) - 1
    )
    if not imposter_count:
        return

    current_topic = random.choice(list(topics.keys()))
    current_word, current_hint = random.choice(list(topics[current_topic].items()))

    imposters = set(random.sample(players, imposter_count))
    roles.clear()
    for p in players:
        roles[p] = "imposter" if p in imposters else "crewmate"

    viewed_players = set()
    starter_player = random.choice(players)
    starter_announced = False

    update_players()

    messagebox.showinfo(
        "Game Ready",
        "Game ready!\n\nPass the phone.\nTap your name to see your role."
    )

# ------------------------
# PRIVACY + ROLE SCREENS
# ------------------------
def confirm_player(name):
    confirm = tk.Toplevel(root)
    confirm.geometry("360x640")
    confirm.configure(bg=BG)
    confirm.grab_set()

    tk.Label(confirm, text=name, font=("Arial", 28, "bold"),
             bg=BG, fg=TEXT).pack(pady=80)

    tk.Label(
        confirm,
        text="Is this you?\nMake sure no one else is looking 👀",
        font=("Arial", 16),
        bg=BG,
        fg=MUTED,
        wraplength=300,
        justify="center"
    ).pack(pady=40)

    tk.Button(
        confirm,
        text="YES – SHOW MY ROLE",
        font=("Arial", 16, "bold"),
        bg=GREEN,
        fg="white",
        pady=10,
        command=lambda: (confirm.destroy(), show_role(name))
    ).pack(fill="x", padx=30, pady=10)

    tk.Button(
        confirm,
        text="NO – GO BACK",
        font=("Arial", 14),
        bg=GRAY,
        fg=TEXT,
        command=confirm.destroy
    ).pack(pady=10)

def show_role(name):
    global starter_announced

    if name in viewed_players:
        return

    win = tk.Toplevel(root)
    win.geometry("360x640")
    win.configure(bg=BG)
    win.grab_set()

    tk.Label(win, text=name, font=("Arial", 26, "bold"),
             bg=BG, fg=TEXT).pack(pady=30)

    if roles[name] == "imposter":
        tk.Label(win, text="YOU ARE THE IMPOSTER",
                 font=("Arial", 22, "bold"),
                 bg=BG, fg=RED).pack(pady=20)

        text = ""
        if show_topic:
            text += f"Topic: {current_topic}\n\n"
        if show_hint_to_imposter:
            text += f"Hint:\n{current_hint}"

        if not text:
            text = "No extra info.\nBlend in 😈"

        tk.Label(win, text=text, font=("Arial", 18),
                 bg=BG, fg=TEXT,
                 wraplength=300, justify="center").pack(pady=30)

    else:
        if show_topic:
            tk.Label(win, text=f"Topic:\n{current_topic}",
                     font=("Arial", 20),
                     bg=BG, fg=TEXT).pack(pady=15)

        tk.Label(win, text=f"WORD:\n{current_word}",
                 font=("Arial", 26, "bold"),
                 bg=BG, fg=TEXT,
                 wraplength=300, justify="center").pack(pady=30)

    def close_and_check():
        global starter_announced
        win.destroy()
        viewed_players.add(name)
        update_players()

        if not starter_announced and len(viewed_players) == len(players):
            starter_announced = True
            messagebox.showinfo(
                "Discussion Start",
                f"{starter_player} goes first!"
            )

    tk.Button(
        win,
        text="DONE (PASS PHONE)",
        font=("Arial", 16, "bold"),
        bg=GREEN,
        fg="white",
        pady=10,
        command=close_and_check
    ).pack(fill="x", padx=30, pady=40)

def reveal_role(event):
    sel = player_list.curselection()
    if not sel:
        return
    confirm_player(players[sel[0]])

# ------------------------
# UI LAYOUT
# ------------------------
tk.Label(main, text="Players (tap your name)",
         font=("Arial", 16, "bold"),
         bg=BG, fg=TEXT).pack(pady=(0, 6))

player_list = tk.Listbox(
    main,
    height=8,
    bg=PANEL,
    fg=TEXT,
    selectbackground=GREEN,
    selectforeground="white",
    activestyle="none"
)
player_list.pack(fill="x", pady=(0, 8))
player_list.bind("<<ListboxSelect>>", reveal_role)

def styled_button(text, cmd):
    return tk.Button(main, text=text, command=cmd,
                     bg=GRAY, fg=TEXT, pady=6)

styled_button("Add Player", add_player).pack(fill="x", pady=2)
styled_button("Remove Player", remove_player).pack(fill="x", pady=2)

topic_btn = tk.Button(main, command=toggle_topic, fg="white")
topic_btn.pack(fill="x", pady=2)

hint_btn = tk.Button(main, command=toggle_hint, fg="white")
hint_btn.pack(fill="x", pady=2)

update_toggle_buttons()

styled_button("Add Word + Hint", add_word).pack(fill="x", pady=2)
styled_button("Remove Word", remove_word).pack(fill="x", pady=2)

tk.Button(
    main,
    text="START GAME",
    font=("Arial", 16, "bold"),
    bg=GREEN,
    fg="white",
    pady=10,
    command=start_game
).pack(fill="x", pady=10)

update_players()
root.mainloop()
