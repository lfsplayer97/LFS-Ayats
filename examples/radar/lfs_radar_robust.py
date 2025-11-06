"""Radar LFS robust amb protecció contra errors"""
import socket
import struct
import time
import json
import math
from pathlib import Path

def is_valid_float(value):
    """Comprova si un valor float és vàlid (no NaN, no infinit)"""
    return not (math.isnan(value) or math.isinf(value))

def safe_int_convert(value, default=0):
    """Converteix un valor a int de forma segura"""
    try:
        if is_valid_float(value):
            return int(value)
        else:
            return default
    except:
        return default

def main():
    print("[INFO] Starting LFS Radar (Robust Version)...")
    
    # Load config
    config_path = Path(__file__).parent.parent.parent / "config.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
        outsim_port = config["outsim"]["port"]
    except:
        outsim_port = 30000  # Default
    
    print(f"[INFO] Listening for OutSim on port {outsim_port}")
    print("[INFO] Make sure LFS is running in cockpit view and you're driving!")
    print("[INFO] Press Ctrl+C to stop")
    
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', outsim_port))
    sock.settimeout(1.0)
    
    packet_count = 0
    radar_history = []
    last_valid_pos = (0.0, 0.0)
    
    try:
        while True:
            try:
                # Receive OutSim packet
                data, addr = sock.recvfrom(96)
                packet_count += 1
                
                if len(data) >= 64:
                    try:
                        # Try different interpretations of the packet
                        # Version 1: Simple format
                        time_ms = struct.unpack('<I', data[0:4])[0]
                        
                        # Try to find position data in different offsets
                        pos_found = False
                        pos_x, pos_y, pos_z = 0.0, 0.0, 0.0
                        vel_x, vel_y, vel_z = 0.0, 0.0, 0.0
                        
                        # Try position at offset 52 (standard OutSim)
                        if len(data) >= 64:
                            try:
                                pos_x, pos_y, pos_z = struct.unpack('<fff', data[52:64])
                                if all(is_valid_float(v) for v in [pos_x, pos_y, pos_z]):
                                    pos_found = True
                            except:
                                pass
                        
                        # If not found, try position at offset 4
                        if not pos_found and len(data) >= 16:
                            try:
                                pos_x, pos_y, pos_z = struct.unpack('<fff', data[4:16])
                                if all(is_valid_float(v) for v in [pos_x, pos_y, pos_z]):
                                    pos_found = True
                            except:
                                pass
                        
                        # Try velocity at offset 40
                        if len(data) >= 52:
                            try:
                                vel_x, vel_y, vel_z = struct.unpack('<fff', data[40:52])
                                if not all(is_valid_float(v) for v in [vel_x, vel_y, vel_z]):
                                    vel_x = vel_y = vel_z = 0.0
                            except:
                                vel_x = vel_y = vel_z = 0.0
                        
                        # If position is valid, use it
                        if pos_found and all(is_valid_float(v) for v in [pos_x, pos_y, pos_z]):
                            last_valid_pos = (pos_x, pos_y)
                            
                            # Calculate speed
                            speed = math.sqrt(vel_x**2 + vel_y**2 + vel_z**2) if all(is_valid_float(v) for v in [vel_x, vel_y, vel_z]) else 0.0
                            speed_kmh = speed * 3.6
                            
                            # Add to radar history
                            radar_history.append((pos_x, pos_y))
                            if len(radar_history) > 30:  # Keep last 30 positions
                                radar_history.pop(0)
                        else:
                            # Use last known valid position
                            pos_x, pos_y = last_valid_pos
                            pos_z = 0.0
                            speed_kmh = 0.0
                        
                        # Create radar display
                        radar_size = 21
                        radar_center = radar_size // 2
                        radar = [['.' for _ in range(radar_size)] for _ in range(radar_size)]
                        
                        # Scale factor
                        scale = 20.0  # meters per radar cell
                        
                        # Draw position history
                        for i, (hx, hy) in enumerate(radar_history[-10:]):  # Only last 10 positions
                            if is_valid_float(hx) and is_valid_float(hy):
                                radar_x = safe_int_convert(hx / scale + radar_center)
                                radar_y = safe_int_convert(-hy / scale + radar_center)  # Flip Y
                                
                                if 0 <= radar_x < radar_size and 0 <= radar_y < radar_size:
                                    if i == len(radar_history[-10:]) - 1:
                                        radar[radar_y][radar_x] = 'X'  # Current
                                    else:
                                        radar[radar_y][radar_x] = '·'  # Trail
                        
                        # Mark center
                        radar[radar_center][radar_center] = 'O'
                        
                        # Clear screen and display
                        print("\033[2J\033[H", end="")
                        print("=== LFS Radar (Robust) ===")
                        print(f"Packets: {packet_count:6d} | Data size: {len(data)} bytes")
                        print(f"Speed: {speed_kmh:6.1f} km/h")
                        print(f"Position: X={pos_x:7.1f} Y={pos_y:7.1f} Z={pos_z:7.1f}")
                        if pos_found:
                            print("Status: ✅ Position data valid")
                        else:
                            print("Status: ⚠️ Using last known position")
                        print()
                        print("Radar (O=origin, X=you, ·=trail):")
                        
                        for row in radar:
                            print(' '.join(row))
                        
                        print()
                        print(f"Scale: {scale:.0f}m per cell | History: {len(radar_history)} points")
                        print("Controls: Ctrl+C to exit")
                        
                    except struct.error as e:
                        print(f"[WARNING] Packet decode error: {e}")
                        continue
                    except Exception as e:
                        print(f"[WARNING] Processing error: {e}")
                        continue
                        
            except socket.timeout:
                print(f"\r[WAITING] No OutSim data - Check LFS is in cockpit view and driving", end="")
                continue
                
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
