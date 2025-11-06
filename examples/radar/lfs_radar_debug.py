"""🕵️ LFS RADAR DEBUG - Trobar el format correcte"""
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

def find_config_file():
    """Find config.json by searching upward from current file."""
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        config_path = parent / "config.json"
        if config_path.exists():
            return config_path
    return Path("config.json")  # Fallback to current directory

def main():
    os.system('color')
    
    # Load config
    config_path = find_config_file()
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
    last_update = 0
    update_interval = 2.0  # Més lent per llegir bé
    
    print(colored("🕵️ LFS RADAR DEBUG MODE", Colors.CYAN + Colors.BOLD))
    print(colored("Buscant el format correcte del paquet OutSim...", Colors.WHITE))
    print("-" * 80)
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(96)
                packet_count += 1
                current_time = time.time()
                
                # Debug cada 2 segons
                if current_time - last_update >= update_interval:
                    last_update = current_time
                    
                    os.system('cls')
                    print(colored("🕵️ LFS OUTSIM DEBUG DETECTIVE", Colors.CYAN + Colors.BOLD))
                    print(colored("="*80, Colors.CYAN))
                    print(f"Paquets rebuts: {packet_count} | Mida paquet: {len(data)} bytes")
                    print()
                    
                    if len(data) >= 64:
                        print(colored("📦 DESCODIFICACIÓ MÚLTIPLE (provant tots els offsets):", Colors.YELLOW + Colors.BOLD))
                        print()
                        
                        # PROVA TOTS ELS OFFSETS POSSIBLES PER VELOCITAT I POSICIÓ
                        candidates = []
                        
                        for offset in range(0, len(data) - 11, 4):  # Cada 4 bytes (float)
                            try:
                                if offset + 12 <= len(data):
                                    val1, val2, val3 = struct.unpack('<fff', data[offset:offset+12])
                                    
                                    # Criteri per velocitat (valors raonables 0-200 km/h en m/s)
                                    speed_ms = math.sqrt(val1**2 + val2**2 + val3**2) if all(not math.isnan(v) and not math.isinf(v) for v in [val1, val2, val3]) else 0
                                    speed_kmh = speed_ms * 3.6
                                    
                                    # Criteri per posició (valors raonables -1000 a 1000m)
                                    pos_reasonable = all(not math.isnan(v) and not math.isinf(v) and abs(v) < 1000 for v in [val1, val2, val3])
                                    
                                    candidates.append({
                                        'offset': offset,
                                        'values': [val1, val2, val3],
                                        'speed_kmh': speed_kmh,
                                        'pos_reasonable': pos_reasonable,
                                        'changing': any(abs(v) > 0.1 for v in [val1, val2, val3])
                                    })
                            except:
                                pass
                        
                        # Mostrar candidats més probables
                        print(colored("🎯 CANDIDATS PER VELOCITAT (0-100 km/h raonables):", Colors.GREEN + Colors.BOLD))
                        for i, cand in enumerate(candidates):
                            if 0 < cand['speed_kmh'] < 100 and cand['changing']:
                                print(f"Offset {cand['offset']:2d}: X={cand['values'][0]:7.2f} Y={cand['values'][1]:7.2f} Z={cand['values'][2]:7.2f} -> {cand['speed_kmh']:6.1f} km/h")
                        
                        print()
                        print(colored("📍 CANDIDATS PER POSICIÓ (valors que canvien):", Colors.BLUE + Colors.BOLD))
                        for i, cand in enumerate(candidates):
                            if cand['pos_reasonable'] and cand['changing'] and cand['speed_kmh'] < 5:  # Posició no és velocitat
                                print(f"Offset {cand['offset']:2d}: X={cand['values'][0]:8.2f} Y={cand['values'][1]:8.2f} Z={cand['values'][2]:8.2f}")
                        
                        print()
                        print(colored("🔬 TOTS ELS VALORS FLOAT DEL PAQUET:", Colors.WHITE))
                        for i in range(0, min(len(data), 64), 4):
                            try:
                                if i + 4 <= len(data):
                                    val = struct.unpack('<f', data[i:i+4])[0]
                                    if not (math.isnan(val) or math.isinf(val)):
                                        print(f"Byte {i:2d}-{i+3:2d}: {val:12.3f}", end="  ")
                                        if (i // 4) % 4 == 3:  # Nova línia cada 4 floats
                                            print()
                            except:
                                pass
                        
                        print("\n")
                        print(colored("💡 INSTRUCCIONS:", Colors.YELLOW))
                        print("1. Condueix i observa quins offsets canvien")
                        print("2. La velocitat hauria de ser proporcional al velocímetre de LFS")
                        print("3. La posició hauria de canviar quan et moguis pel circuit")
                        print("4. Prem Ctrl+C quan trobis els offsets correctes")
                        
                    else:
                        print(colored("❌ Paquet massa petit", Colors.RED))
                    
            except socket.timeout:
                print(colored("⏳ Esperant dades...", Colors.YELLOW))
                continue
                
    except KeyboardInterrupt:
        print(colored("\n🏁 Debug finalitzat!", Colors.GREEN + Colors.BOLD))
        print("Ara pots crear la versió final amb els offsets correctes!")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
