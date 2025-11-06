"""Radar LFS amb visualització millorada"""
import socket
import struct
import time
import json
import math
from pathlib import Path

def clear_screen():
    """Clear screen - funciona millor en Windows"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("=== LFS RADAR - Versió Millorada ===")
    print("Iniciant...")
    
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
    
    packet_count = 0
    radar_history = []
    last_update = 0
    update_interval = 0.5  # Actualitzar cada 0.5 segons (més lent)
    
    # Variables per mostrar
    current_speed = 0.0
    current_pos = [0.0, 0.0, 0.0]
    status_msg = "Esperant dades..."
    
    print(f"Escoltant al port {outsim_port}")
    print("Assegura't que LFS estigui en vista cockpit i conduint!")
    print("Prem Ctrl+C per aturar\n")
    
    try:
        while True:
            try:
                # Receive data
                data, addr = sock.recvfrom(96)
                packet_count += 1
                current_time = time.time()
                
                # Process packet
                if len(data) >= 64:
                    try:
                        # Basic position decode
                        pos_x, pos_y, pos_z = struct.unpack('<fff', data[4:16])
                        
                        # Check if valid
                        if all(not math.isnan(v) and not math.isinf(v) for v in [pos_x, pos_y, pos_z]):
                            current_pos = [pos_x, pos_y, pos_z]
                            
                            # Try velocity for speed
                            try:
                                vel_x, vel_y, vel_z = struct.unpack('<fff', data[16:28])
                                if all(not math.isnan(v) and not math.isinf(v) for v in [vel_x, vel_y, vel_z]):
                                    speed_ms = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2)
                                    current_speed = speed_ms * 3.6
                            except:
                                pass
                            
                            radar_history.append((pos_x, pos_y))
                            if len(radar_history) > 20:
                                radar_history.pop(0)
                            
                            status_msg = "Connectat ✅"
                        
                    except:
                        status_msg = "Error de decodificació ⚠️"
                
                # Update display only every 0.5 seconds
                if current_time - last_update >= update_interval:
                    last_update = current_time
                    
                    # Clear and redraw
                    clear_screen()
                    
                    # Header
                    print("╔═══════════════════════════════════════════════════════════════════════════╗")
                    print("║                           🏎️  LFS RADAR                                 ║")
                    print("╠═══════════════════════════════════════════════════════════════════════════╣")
                    print(f"║ Status: {status_msg:<25} Paquets: {packet_count:>8}         ║")
                    print(f"║ Velocitat: {current_speed:>6.1f} km/h                                        ║")
                    print(f"║ Posició: X={current_pos[0]:>7.1f} Y={current_pos[1]:>7.1f} Z={current_pos[2]:>5.1f}           ║")
                    print("╠═══════════════════════════════════════════════════════════════════════════╣")
                    
                    # Create radar
                    radar_size = 15
                    radar_center = radar_size // 2
                    radar = [['·' for _ in range(radar_size)] for _ in range(radar_size)]
                    scale = 30.0
                    
                    # Plot positions
                    for i, (hx, hy) in enumerate(radar_history[-10:]):
                        radar_x = int(hx / scale) + radar_center
                        radar_y = int(-hy / scale) + radar_center
                        
                        if 0 <= radar_x < radar_size and 0 <= radar_y < radar_size:
                            if i == len(radar_history[-10:]) - 1:
                                radar[radar_y][radar_x] = '🚗'  # Current
                            else:
                                radar[radar_y][radar_x] = '•'   # Trail
                    
                    radar[radar_center][radar_center] = '⭕'  # Center
                    
                    # Display radar
                    print("║                                RADAR                                      ║")
                    for row in radar:
                        line = "║ " + " ".join(f"{cell:>2}" for cell in row) + "  ║"
                        print(line)
                    
                    print("╠═══════════════════════════════════════════════════════════════════════════╣")
                    print(f"║ Llegenda: ⭕=Centre  🚗=Tu  •=Trajecte  Escala: {scale:.0f}m/cel          ║")
                    print("║ Controls: Ctrl+C per aturar                                              ║")
                    print("╚═══════════════════════════════════════════════════════════════════════════╝")
                    
            except socket.timeout:
                if time.time() - last_update >= update_interval:
                    last_update = time.time()
                    clear_screen()
                    print("╔═══════════════════════════════════════════════════════════════════════════╗")
                    print("║                           🏎️  LFS RADAR                                 ║")
                    print("╠═══════════════════════════════════════════════════════════════════════════╣")
                    print("║ ⚠️  ESPERANT DADES - Comprova que LFS estigui en vista cockpit          ║")
                    print("║                      i que estiguis conduint                             ║")
                    print("╚═══════════════════════════════════════════════════════════════════════════╝")
                continue
                
    except KeyboardInterrupt:
        print("\n\n🏁 Radar aturat per l'usuari!")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
