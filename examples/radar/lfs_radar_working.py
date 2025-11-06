"""🏎️ LFS RADAR DEFINITIU - Sense Errors de Sintaxi"""
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
    config_path = Path(__file__).parent.parent.parent / "config.json"
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
    update_interval = 1.0  # 1 segon sense parpelleig
    
    # Data variables
    current_speed = 0.0
    max_speed = 0.0
    current_pos = [0.0, 0.0, 0.0]
    current_vel = [0.0, 0.0, 0.0]
    status_msg = "🔄 Iniciant..."
    
    # Clear inicial
    os.system('cls')
    
    try:
        while True:
            data_received = False
            
            try:
                # Receive data
                data, addr = sock.recvfrom(96)
                packet_count += 1
                current_time = time.time()
                data_received = True
                
                if len(data) >= 64:
                    try:
                        # FORMAT OUTSIM CORRECTE segons documentació LFS:
                        time_ms = struct.unpack('<I', data[0:4])[0]
                        
                        # Angular velocity (4-16)
                        ang_vel_x, ang_vel_y, ang_vel_z = struct.unpack('<fff', data[4:16])
                        
                        # Heading, Pitch, Roll (16-28)
                        heading, pitch, roll = struct.unpack('<fff', data[16:28])
                        
                        # Acceleration (28-40)
                        accel_x, accel_y, accel_z = struct.unpack('<fff', data[28:40])
                        
                        # Velocity (40-52) - VELOCITAT AQUÍ
                        vel_x, vel_y, vel_z = struct.unpack('<fff', data[40:52])
                        
                        # Position (52-64) - POSICIÓ AQUÍ
                        pos_x, pos_y, pos_z = struct.unpack('<fff', data[52:64])
                        
                        # Validar dades
                        pos_valid = all(not (math.isnan(v) or math.isinf(v)) for v in [pos_x, pos_y, pos_z])
                        vel_valid = all(not (math.isnan(v) or math.isinf(v)) for v in [vel_x, vel_y, vel_z])
                        
                        if pos_valid and vel_valid:
                            # Calcular velocitat
                            speed_ms = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2)
                            current_speed = speed_ms * 3.6  # km/h
                            
                            if current_speed > max_speed:
                                max_speed = current_speed
                            
                            current_pos = [pos_x, pos_y, pos_z]
                            current_vel = [vel_x, vel_y, vel_z]
                            
                            # Radar history
                            radar_history.append((pos_x, pos_y))
                            if len(radar_history) > 15:
                                radar_history.pop(0)
                            
                            status_msg = colored("✅ FUNCIONANT", Colors.GREEN + Colors.BOLD)
                            
                        else:
                            status_msg = colored("⚠️ DADES INVÀLIDES", Colors.YELLOW)
                        
                    except Exception as e:
                        status_msg = colored("❌ ERROR FORMAT", Colors.RED)
                
                # Update display
                if current_time - last_update >= update_interval:
                    last_update = current_time
                    
                    clear_screen_smooth()
                    
                    # Header
                    print(colored("╔" + "═" * 75 + "╗", Colors.CYAN + Colors.BOLD))
                    print(colored("║" + " 🏎️  LFS RADAR DEFINITIU ".center(75) + "║", Colors.CYAN + Colors.BOLD))
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    
                    # Status amb colors nets
                    status_text = status_msg.replace(Colors.END, "")
                    print(colored(f"║ Status: {status_text:<25} Paquets: {packet_count:>8} ║", Colors.CYAN))
                    
                    # Velocitat amb colors
                    if current_speed < 30:
                        speed_color = Colors.GREEN
                    elif current_speed < 80:
                        speed_color = Colors.YELLOW
                    else:
                        speed_color = Colors.RED
                    
                    speed_text = colored(f"{current_speed:6.1f}", speed_color + Colors.BOLD)
                    max_text = colored(f"{max_speed:6.1f}", Colors.MAGENTA + Colors.BOLD)
                    
                    print(colored(f"║ Velocitat: {speed_text} km/h   Màxima: {max_text} km/h            ║", Colors.CYAN))
                    
                    # Coordenades
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║ 📍 POSICIÓ AL CIRCUIT:                                           ║", Colors.WHITE + Colors.BOLD))
                    
                    x_text = colored(f"{current_pos[0]:8.1f}m", Colors.RED + Colors.BOLD)
                    y_text = colored(f"{current_pos[1]:8.1f}m", Colors.GREEN + Colors.BOLD)  
                    z_text = colored(f"{current_pos[2]:8.1f}m", Colors.BLUE + Colors.BOLD)
                    
                    print(colored(f"║  X={x_text}  Y={y_text}  Z={z_text}               ║", Colors.CYAN))
                    print(colored("║  ↑Lateral     ↑Longitudinal   ↑Vertical                        ║", Colors.WHITE))
                    
                    # Radar
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║" + " 🗺️  RADAR DE TRAJECTE ".center(75) + "║", Colors.WHITE + Colors.BOLD))
                    
                    # Crear radar 15x15
                    radar_size = 15
                    radar_center = radar_size // 2
                    radar = [['  ' for _ in range(radar_size)] for _ in range(radar_size)]
                    scale = 25.0
                    
                    # Dibuixar trajecte
                    for i, (hx, hy) in enumerate(radar_history[-10:]):
                        radar_x = int(hx / scale) + radar_center
                        radar_y = int(-hy / scale) + radar_center
                        
                        if 0 <= radar_x < radar_size and 0 <= radar_y < radar_size:
                            if i == len(radar_history[-10:]) - 1:
                                radar[radar_y][radar_x] = colored('██', Colors.RED + Colors.BOLD)
                            elif i >= len(radar_history[-10:]) - 3:
                                radar[radar_y][radar_x] = colored('▓▓', Colors.YELLOW)
                            else:
                                radar[radar_y][radar_x] = colored('░░', Colors.BLUE)
                    
                    # Centre
                    radar[radar_center][radar_center] = colored('++', Colors.WHITE + Colors.BOLD)
                    
                    # Mostrar radar
                    for row in radar:
                        line = "║ " + "".join(cell if cell.strip() else '··' for cell in row) + " ║"
                        print(line)
                    
                    # Llegenda
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored(f"║ {colored('██', Colors.RED)}=TU  {colored('▓▓', Colors.YELLOW)}=Recent  {colored('░░', Colors.BLUE)}=Antic  {colored('++', Colors.WHITE)}=Centre  Escala:{scale:.0f}m   ║", Colors.CYAN))
                    
                    # Controls
                    print(colored("╠" + "═" * 75 + "╣", Colors.CYAN + Colors.BOLD))
                    print(colored("║ ⌨️  Controls: Ctrl+C per aturar | Vista cockpit necessària      ║", Colors.WHITE))
                    print(colored("╚" + "═" * 75 + "╝", Colors.CYAN + Colors.BOLD))
                    
                    # Espais per netejar
                    for i in range(5):
                        print(" " * 80)
                    
            except socket.timeout:
                if not data_received and time.time() - last_update >= update_interval:
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
        print(colored(f"📊 Paquets: {packet_count} | Velocitat màxima: {max_speed:.1f} km/h", Colors.WHITE))
        print(colored("Gràcies per usar LFS Radar! 🚗💨", Colors.CYAN))
    finally:
        sock.close()

if __name__ == "__main__":
    main()
