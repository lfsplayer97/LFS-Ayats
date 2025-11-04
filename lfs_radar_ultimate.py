"""🏎️ LFS RADAR ULTIMATE - La versió més PRO! 🏎️"""
import socket
import struct
import time
import json
import math
import os
from pathlib import Path

class Colors:
    """Colors per terminal Windows/PowerShell"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

def colored(text, color):
    """Aplica color al text"""
    return f"{color}{text}{Colors.END}"

def clear_screen_smooth():
    """Clear screen sense parpelleig"""
    # Mover cursor a l'inici sense borrar
    print('\033[H', end='')

def main():
    # Enable colors in Windows PowerShell
    os.system('color')
    
    print(colored("🏎️ LFS RADAR ULTIMATE - Carregant... 🏎️", Colors.BOLD + Colors.CYAN))
    time.sleep(1)
    
    # Load config
    config_path = Path(__file__).parent / "config.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
        outsim_port = config["outsim"]["port"]
    except:
        outsim_port = 30000
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', outsim_port))
    sock.settimeout(1.0)
    
    # Variables
    packet_count = 0
    radar_history = []
    last_update = 0
    update_interval = 0.8  # Més lent per evitar parpelleig
    
    # Data variables
    current_speed = 0.0
    max_speed = 0.0
    current_pos = [0.0, 0.0, 0.0]
    status_msg = "🔄 Iniciant..."
    total_distance = 0.0
    last_pos = None
    
    # Clear screen inicial
    os.system('cls' if os.name == 'nt' else 'clear')
    
    try:
        while True:
            try:
                # Receive data
                data, addr = sock.recvfrom(96)
                packet_count += 1
                current_time = time.time()
                
                # Process packet - MÚLTIPLES INTENTS PER TROBAR LA VELOCITAT
                if len(data) >= 64:
                    try:
                        # INTENT 1: Posició a offset 4
                        pos_x, pos_y, pos_z = struct.unpack('<fff', data[4:16])
                        
                        # Validar posició
                        if all(not math.isnan(v) and not math.isinf(v) for v in [pos_x, pos_y, pos_z]):
                            # Calcular distància recorreguda
                            if last_pos:
                                dist = math.sqrt((pos_x - last_pos[0])**2 + (pos_y - last_pos[1])**2)
                                total_distance += dist
                            last_pos = [pos_x, pos_y, pos_z]
                            
                            current_pos = [pos_x, pos_y, pos_z]
                            
                            # INTENT 1: Velocitat directa de diferents offsets
                            speed_found = False
                            
                            # Prova offset 16 (velocitat)
                            try:
                                vel_x, vel_y, vel_z = struct.unpack('<fff', data[16:28])
                                if all(not math.isnan(v) and not math.isinf(v) for v in [vel_x, vel_y, vel_z]):
                                    speed_ms = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2)
                                    current_speed = speed_ms * 3.6
                                    speed_found = True
                            except:
                                pass
                            
                            # INTENT 2: Velocitat a offset 40
                            if not speed_found:
                                try:
                                    vel_x, vel_y, vel_z = struct.unpack('<fff', data[40:52])
                                    if all(not math.isnan(v) and not math.isinf(v) for v in [vel_x, vel_y, vel_z]):
                                        speed_ms = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2)
                                        current_speed = speed_ms * 3.6
                                        speed_found = True
                                except:
                                    pass
                            
                            # INTENT 3: Calcular velocitat per diferència de posició
                            if not speed_found and len(radar_history) > 0:
                                try:
                                    last_radar_pos = radar_history[-1]
                                    time_diff = 0.1  # Assumim 100ms entre paquets
                                    dist_diff = math.sqrt((pos_x - last_radar_pos[0])**2 + (pos_y - last_radar_pos[1])**2)
                                    current_speed = (dist_diff / time_diff) * 3.6  # Convert to km/h
                                except:
                                    pass
                            
                            # Actualitzar velocitat màxima
                            if current_speed > max_speed:
                                max_speed = current_speed
                            
                            # Actualitzar trajecte
                            radar_history.append((pos_x, pos_y))
                            if len(radar_history) > 25:  # Més història
                                radar_history.pop(0)
                            
                            status_msg = colored("✅ CONNECTAT", Colors.GREEN + Colors.BOLD)
                        
                    except Exception as e:
                        status_msg = colored(f"⚠️ ERROR: {str(e)[:20]}", Colors.YELLOW)
                
                # Update display només quan toca (sense parpelleig)
                if current_time - last_update >= update_interval:
                    last_update = current_time
                    
                    # Clear suau
                    clear_screen_smooth()
                    
                    # 🏁 HEADER SÚPER PRO
                    print(colored("╔" + "═" * 77 + "╗", Colors.CYAN + Colors.BOLD))
                    print(colored("║" + f"🏎️  LFS RADAR ULTIMATE v2.0".center(77) + "║", Colors.CYAN + Colors.BOLD))
                    print(colored("╠" + "═" * 77 + "╣", Colors.CYAN + Colors.BOLD))
                    
                    # 📊 INFORMACIÓ PRINCIPAL
                    status_line = f"║ Status: {status_msg:<30} Paquets: {colored(str(packet_count), Colors.BOLD + Colors.WHITE):>8} ║"
                    print(status_line.replace(Colors.END, Colors.END + Colors.CYAN))
                    
                    # 🚀 VELOCITATS AMB COLORS
                    speed_color = Colors.GREEN if current_speed < 50 else Colors.YELLOW if current_speed < 100 else Colors.RED
                    speed_text = colored(f"{current_speed:>6.1f}", speed_color + Colors.BOLD)
                    max_speed_text = colored(f"{max_speed:>6.1f}", Colors.MAGENTA + Colors.BOLD)
                    
                    print(colored(f"║ Velocitat: {speed_text} km/h   Màxima: {max_speed_text} km/h   Distància: {total_distance:>6.1f}m ║", Colors.CYAN).replace(Colors.END, Colors.END + Colors.CYAN))
                    
                    # 🌍 COORDENADES AMB EXPLICACIÓ
                    print(colored("╠" + "═" * 77 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║ 📍 POSICIÓ AL CIRCUIT:                                                 ║", Colors.CYAN + Colors.BOLD))
                    
                    x_color = Colors.RED + Colors.BOLD
                    y_color = Colors.GREEN + Colors.BOLD  
                    z_color = Colors.BLUE + Colors.BOLD
                    
                    x_text = colored(f"{current_pos[0]:>8.1f}m", x_color)
                    y_text = colored(f"{current_pos[1]:>8.1f}m", y_color)
                    z_text = colored(f"{current_pos[2]:>8.1f}m", z_color)
                    
                    print(colored(f"║ X{x_text}  Y{y_text}  Z{z_text}                    ║", Colors.CYAN).replace(Colors.END, Colors.END + Colors.CYAN))
                    print(colored("║ ↑Esquerra/Dreta  ↑Endavant/Enrere  ↑Amunt/Avall                      ║", Colors.WHITE))
                    
                    # 🗺️ RADAR SÚPER VISUAL
                    print(colored("╠" + "═" * 77 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║" + "🗺️  RADAR DE CIRCUIT".center(77) + "║", Colors.CYAN + Colors.BOLD))
                    
                    # Create radar més gran
                    radar_size = 19
                    radar_center = radar_size // 2
                    radar = [['  ' for _ in range(radar_size)] for _ in range(radar_size)]
                    scale = 25.0
                    
                    # Plot trajecte amb colors degradats
                    for i, (hx, hy) in enumerate(radar_history[-15:]):
                        radar_x = int(hx / scale) + radar_center
                        radar_y = int(-hy / scale) + radar_center
                        
                        if 0 <= radar_x < radar_size and 0 <= radar_y < radar_size:
                            if i == len(radar_history[-15:]) - 1:
                                # Posició actual - SÚPER VISIBLE
                                radar[radar_y][radar_x] = colored('🚗', Colors.RED + Colors.BOLD + Colors.BG_YELLOW)
                            elif i >= len(radar_history[-15:]) - 3:
                                # Trajecte recent
                                radar[radar_y][radar_x] = colored('██', Colors.YELLOW)
                            else:
                                # Trajecte antic
                                radar[radar_y][radar_x] = colored('▓▓', Colors.BLUE)
                    
                    # Centre SÚPER VISIBLE
                    radar[radar_center][radar_center] = colored('⊕⊕', Colors.WHITE + Colors.BOLD + Colors.BG_RED)
                    
                    # Display radar amb marcs
                    for i, row in enumerate(radar):
                        if i == 0 or i == radar_size - 1:
                            border = "═" * (radar_size * 2)
                            print(colored(f"║╔{border}╗║", Colors.CYAN))
                        else:
                            line = "".join(cell if cell != '  ' else '··' for cell in row)
                            print(colored(f"║║{line}║║", Colors.CYAN))
                    
                    # LLEGENDA AMB COLORS
                    print(colored("╠" + "═" * 77 + "╣", Colors.CYAN + Colors.BOLD))
                    llegenda = f"║ {colored('🚗', Colors.RED + Colors.BOLD)}=TU  {colored('██', Colors.YELLOW)}=Trajecte Recent  {colored('▓▓', Colors.BLUE)}=Trajecte Antic  {colored('⊕⊕', Colors.WHITE + Colors.BOLD)}=Centre"
                    print(llegenda.ljust(85).replace(Colors.END, Colors.END + Colors.CYAN) + "║")
                    print(colored(f"║ Escala: {scale:.0f}m per cel·la | Historial: {len(radar_history)} punts" + " " * 28 + "║", Colors.WHITE))
                    
                    # CONTROLS
                    print(colored("╠" + "═" * 77 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║ ⌨️  CONTROLS: Ctrl+C per aturar | Mantén vista cockpit a LFS          ║", Colors.WHITE + Colors.BOLD))
                    print(colored("╚" + "═" * 77 + "╝", Colors.CYAN + Colors.BOLD))
                    
            except socket.timeout:
                if time.time() - last_update >= update_interval:
                    last_update = time.time()
                    clear_screen_smooth()
                    print(colored("╔" + "═" * 77 + "╗", Colors.RED + Colors.BOLD))
                    print(colored("║" + "⚠️  ESPERANT DADES DE LFS".center(77) + "║", Colors.RED + Colors.BOLD))
                    print(colored("║" + "Comprova: Vista cockpit + Conduint".center(77) + "║", Colors.YELLOW))
                    print(colored("╚" + "═" * 77 + "╝", Colors.RED + Colors.BOLD))
                continue
                
    except KeyboardInterrupt:
        clear_screen_smooth()
        print(colored("\n🏁 RADAR ATURAT!", Colors.GREEN + Colors.BOLD))
        print(colored(f"📊 Estadístiques finals:", Colors.CYAN + Colors.BOLD))
        print(colored(f"   • Paquets processats: {packet_count}", Colors.WHITE))
        print(colored(f"   • Velocitat màxima: {max_speed:.1f} km/h", Colors.WHITE))
        print(colored(f"   • Distància total: {total_distance:.1f} m", Colors.WHITE))
        print(colored("Gràcies per usar LFS Radar Ultimate! 🚗💨", Colors.CYAN + Colors.BOLD))
    finally:
        sock.close()

if __name__ == "__main__":
    main()
