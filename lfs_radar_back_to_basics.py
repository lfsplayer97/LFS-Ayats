"""🏎️ LFS RADAR - Tornant als Bàsics però PRO"""
import socket
import struct
import time
import json
import math
import os
from pathlib import Path

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

def colored(text, color):
    return f"{color}{text}{Colors.END}"

def clear_screen_smooth():
    """Clear suau sense parpelleig"""
    print('\033[H', end='')

def main():
    os.system('color')
    
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
    update_interval = 1.0  # 1 segon
    
    # Data variables
    current_speed = 0.0
    max_speed = 0.0
    current_pos = [0.0, 0.0, 0.0]
    status_msg = "🔄 Iniciant..."
    
    # Clear inicial
    os.system('cls')
    
    try:
        while True:
            try:
                # Receive data
                data, addr = sock.recvfrom(96)
                packet_count += 1
                current_time = time.time()
                
                if len(data) >= 64:
                    try:
                        # TORNEM AL FORMAT SIMPLE QUE FUNCIONAVA
                        time_ms = struct.unpack('<I', data[0:4])[0]
                        
                        # Posició a offset 4 (com abans)
                        pos_x, pos_y, pos_z = struct.unpack('<fff', data[4:16])
                        
                        # Velocitat a offset 16 (com abans)
                        vel_x, vel_y, vel_z = struct.unpack('<fff', data[16:28])
                        
                        # Validar que no són NaN
                        pos_valid = all(not (math.isnan(v) or math.isinf(v)) for v in [pos_x, pos_y, pos_z])
                        vel_valid = all(not (math.isnan(v) or math.isinf(v)) for v in [vel_x, vel_y, vel_z])
                        
                        if pos_valid:
                            current_pos = [pos_x, pos_y, pos_z]
                            
                            # Calcular velocitat
                            if vel_valid:
                                speed_ms = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2)
                                current_speed = speed_ms * 3.6
                                
                                if current_speed > max_speed:
                                    max_speed = current_speed
                            
                            # Actualitzar radar
                            radar_history.append((pos_x, pos_y))
                            if len(radar_history) > 20:
                                radar_history.pop(0)
                            
                            status_msg = colored("✅ FUNCIONANT", Colors.GREEN + Colors.BOLD)
                        else:
                            status_msg = colored("⚠️ DADES INVÀLIDES", Colors.YELLOW)
                        
                    except Exception as e:
                        status_msg = colored("❌ ERROR", Colors.RED)
                
                # Update display
                if current_time - last_update >= update_interval:
                    last_update = current_time
                    
                    clear_screen_smooth()
                    
                    # Header PRO
                    print(colored("╔" + "═" * 75 + "╗", Colors.CYAN + Colors.BOLD))
                    print(colored("║" + " 🏎️  LFS RADAR ULTIMATE ".center(75) + "║", Colors.CYAN + Colors.BOLD))
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    
                    # Status
                    status_clean = status_msg.replace(Colors.END, "").replace(Colors.GREEN + Colors.BOLD, "").replace(Colors.YELLOW, "").replace(Colors.RED, "")
                    print(colored(f"║ Status: {status_clean:<25} Paquets: {packet_count:>8} ║", Colors.CYAN))
                    
                    # Velocitat amb colors
                    if current_speed < 30:
                        speed_color = Colors.GREEN
                    elif current_speed < 80:
                        speed_color = Colors.YELLOW
                    else:
                        speed_color = Colors.RED
                    
                    print(colored(f"║ Velocitat: {colored(f'{current_speed:6.1f}', speed_color + Colors.BOLD)} km/h   Màxima: {colored(f'{max_speed:6.1f}', Colors.MAGENTA + Colors.BOLD)} km/h            ║", Colors.CYAN))
                    
                    # Coordenades amb colors
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║ 📍 POSICIÓ AL CIRCUIT:                                           ║", Colors.WHITE + Colors.BOLD))
                    
                    x_text = f"{current_pos[0]:8.1f}m"
                    y_text = f"{current_pos[1]:8.1f}m"
                    z_text = f"{current_pos[2]:8.1f}m"
                    
                    print(colored(f"║  X={colored(x_text, Colors.RED + Colors.BOLD)}  Y={colored(y_text, Colors.GREEN + Colors.BOLD)}  Z={colored(z_text, Colors.BLUE + Colors.BOLD)}               ║", Colors.CYAN))
                    print(colored("║  ↑Lateral     ↑Longitudinal   ↑Vertical                        ║", Colors.WHITE))
                    
                    # RADAR VISUAL COM ABANS
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║" + " 🗺️  RADAR DE TRAJECTE ".center(75) + "║", Colors.WHITE + Colors.BOLD))
                    
                    # Radar 21x21 com a l'inici
                    radar_size = 21
                    radar_center = radar_size // 2
                    radar = [['.' for _ in range(radar_size)] for _ in range(radar_size)]
                    scale = 20.0  # metres per cel·la
                    
                    # Dibuixar trajecte
                    for i, (hx, hy) in enumerate(radar_history[-15:]):
                        radar_x = int(hx / scale) + radar_center
                        radar_y = int(-hy / scale) + radar_center  # Y invertida
                        
                        if 0 <= radar_x < radar_size and 0 <= radar_y < radar_size:
                            if i == len(radar_history[-15:]) - 1:
                                radar[radar_y][radar_x] = colored('X', Colors.RED + Colors.BOLD)  # TU
                            else:
                                radar[radar_y][radar_x] = colored('·', Colors.YELLOW)  # Trajecte
                    
                    # Centre
                    radar[radar_center][radar_center] = colored('O', Colors.WHITE + Colors.BOLD)
                    
                    # Mostrar radar amb format net
                    for row in radar:
                        line = "║ " + " ".join(cell if isinstance(cell, str) and '\033' in cell else cell for cell in row) + " ║"
                        print(line)
                    
                    # Llegenda
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored(f"║ {colored('X', Colors.RED + Colors.BOLD)}=TU  {colored('·', Colors.YELLOW)}=Trajecte  {colored('O', Colors.WHITE + Colors.BOLD)}=Centre  Escala: {scale:.0f}m per cel·la     ║", Colors.CYAN))
                    
                    # Info extra
                    print(colored(f"║ Historial: {len(radar_history)} punts de trajecte                        ║", Colors.WHITE))
                    
                    # Controls
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║ ⌨️  Controls: Ctrl+C per aturar | Vista cockpit necessària      ║", Colors.WHITE))
                    print(colored("╚" + "═" * 75 + "╝", Colors.CYAN + Colors.BOLD))
                    
                    # Espais per netejar residus
                    for _ in range(3):
                        print(" " * 80)
                    
            except socket.timeout:
                if time.time() - last_update >= update_interval:
                    last_update = time.time()
                    clear_screen_smooth()
                    print(colored("╔" + "═" * 75 + "╗", Colors.RED + Colors.BOLD))
                    print(colored("║" + " ⚠️  ESPERANT DADES DE LFS ".center(75) + "║", Colors.RED + Colors.BOLD))
                    print(colored("║" + " Comprova: LFS obert + Practice + Vista cockpit ".center(75) + "║", Colors.YELLOW))
                    print(colored("╚" + "═" * 75 + "╝", Colors.RED + Colors.BOLD))
                continue
                
    except KeyboardInterrupt:
        clear_screen_smooth()
        print(colored("\n🏁 RADAR ATURAT!", Colors.GREEN + Colors.BOLD))
        print(colored(f"📊 Estadístiques:", Colors.CYAN + Colors.BOLD))
        print(colored(f"   • Paquets processats: {packet_count}", Colors.WHITE))
        print(colored(f"   • Velocitat màxima: {max_speed:.1f} km/h", Colors.WHITE))
        print(colored(f"   • Punts de trajecte: {len(radar_history)}", Colors.WHITE))
        print(colored("Gràcies per usar LFS Radar Ultimate! 🚗💨", Colors.CYAN))
    finally:
        sock.close()

if __name__ == "__main__":
    main()
