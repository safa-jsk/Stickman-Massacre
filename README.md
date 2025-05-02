## 🕹️ Last One Standing

**Last One Standing** is a 3D arena survival shooter built using **PyOpenGL + GLUT**. Play as a futuristic fighter battling waves of enemies and bosses in an ever-escalating war for survival.

---

## Project Members

1. **Md. Saadat Rahman**  
   GitHub: [MD-SAADAT-RAHMAN](https://github.com/MD-SAADAT-RAHMAN)

2. **Mohammad Jabir Safa Khandoker**  
   GitHub: [safa-jsk](https://github.com/safa-jsk)

3. **Md. Fahim Muntasir**  
   GitHub: [srab0n](https://github.com/srab0n)

---

### 🚀 Features

- 🔫 **Bullet & Melee Combat**: Use both ranged shots and close-range attacks
- 👹 **Boss Battles**: Challenging bosses spawn every few levels with powerful attacks
- 🧪 **Loot System**: Randomly spawning power-ups (Health, Double Damage, Shield)
- 🧠 **Cheat Mode**: Toggle cheat mode to nuke enemies, gain infinite power, and test mechanics
- 🧱 **Colorful Arena**: Grid-based floor with dynamic colored boundaries
- 🎮 **First-person-style Controls**: WASD for movement, mouse for attacking, arrow keys for camera
- 💥 **Special Effects**: Boss bomb pulse, damage scaling, power-up timers

---

### 🧰 Requirements

- Python 3.x
- `PyOpenGL`
- `PyOpenGL_accelerate` (recommended for performance)

Install with:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

---

### 🎮 Controls

| Key / Mouse   | Action                            |
| ------------- | --------------------------------- |
| `W A S D`     | Move/Turn                         |
| `Mouse Left`  | Melee attack                      |
| `Mouse Right` | Fire bullet                       |
| `Arrow Keys`  | Rotate/Zoom camera                |
| `Shift`       | Sprint toggle                     |
| `Enter`       | Start the game from launch screen |
| `Space`       | Pause/Resume                      |
| `C`           | Toggle Cheat Mode                 |
| `X`           | Nuke all enemies (cheat mode)     |
| `R`           | Restart game                      |
| `P`           | Trigger boss attack (debug)       |

---

### 📺 Launch Screen

- 3D scene with player model on the left and boss on the right
- Game title: **"LAST ONE STANDING"**
- Press `Enter` to begin

---

### 🔧 Game Structure

- `draw_start_screen()` handles the launch view
- `show_screen()` draws main gameplay
- `idle()` is the update loop (AI, movement, damage, boss logic)
- `draw_player()` and `draw_boss()` render 3D character models
- `spawn_enemy()`, `spawn_loot()` manage procedural generation

---

### 🛠️ Notes

- Boss health scales up with level
- Bullet and melee attacks can be boosted with power-ups
- Loot effects are time-limited (or hit-limited, like shield)
- Cheat mode changes game balance and enables testing tools

---

### 📂 File Structure

- `main.py` — Main game logic (single file architecture)
