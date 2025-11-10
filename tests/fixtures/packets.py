"""
Sample InSim packet fixtures for testing

Reference: https://en.lfsmanual.net/wiki/InSim.txt
"""

import struct
import pytest


@pytest.fixture
def sample_isi_packet():
    """
    Sample IS_ISI (InSim Init) packet
    
    Structure: Size(1), Type(1), ReqI(1), Zero(1), UDPPort(2), Flags(2), 
               InSimVer(1), Prefix(1), Interval(2), Admin(16), IName(16)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_ISI
    """
    size = 44  # Total packet size
    packet_type = 1  # ISP_ISI
    req_i = 1  # Request ID
    zero = 0
    udp_port = 0  # 0 for TCP
    flags = 1  # IPS_MCI flag for Multi Car Info
    insim_ver = 9  # INSIM_VERSION
    prefix = ord('!')  # Command prefix character
    interval = 1000  # Update interval in ms
    admin = b'admin'.ljust(16, b'\x00')  # Admin password (16 bytes)
    iname = b'TestApp'.ljust(16, b'\x00')  # App name (16 bytes)
    
    packet = struct.pack(
        '=4B2H2BH16s16s',
        size, packet_type, req_i, zero,
        udp_port, flags,
        insim_ver, prefix, interval,
        admin, iname
    )
    
    return packet


@pytest.fixture
def sample_ver_packet():
    """
    Sample IS_VER (Version) packet
    
    Structure: Size(1), Type(1), ReqI(1), Zero(1), Version(8), Product(6), InSimVer(2)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_VER
    """
    size = 20  # Total packet size
    packet_type = 2  # ISP_VER
    req_i = 1  # Request ID
    zero = 0
    version = b'0.7E'.ljust(8, b'\x00')  # LFS version
    product = b'S3'.ljust(6, b'\x00')  # Product (S1, S2, S3, Demo)
    insim_ver = 9  # INSIM_VERSION
    
    packet = struct.pack(
        '=4B8s6sH',
        size, packet_type, req_i, zero,
        version, product, insim_ver
    )
    
    return packet


@pytest.fixture
def sample_mci_packet():
    """
    Sample IS_MCI (Multi Car Info) packet with one car
    
    Structure: Size(1), Type(1), ReqI(1), NumC(1), followed by CompCar structures
    
    Each CompCar: Node(2), Lap(2), PLID(1), Position(1), Info(1), Sp3(1),
                  X(4), Y(4), Z(4), Speed(2), Direction(2), Heading(2),
                  AngVel(2)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_MCI
    """
    size = 32  # 4 + 28 for one CompCar
    packet_type = 38  # ISP_MCI
    req_i = 0
    num_c = 1  # Number of cars
    
    # CompCar data
    node = 10  # Current node
    lap = 2  # Current lap
    plid = 1  # Player ID
    position = 1  # Race position
    info = 0  # Car info flags
    sp3 = 0  # Spare
    x = 100000  # X position (in game units, 65536 per meter)
    y = 200000  # Y position
    z = 5000  # Z position (height)
    speed = 15000  # Speed (m/s * 32768)
    direction = 16384  # Direction (0-65535, 0 = world Y axis forward)
    heading = 16384  # Car heading
    angvel = 100  # Angular velocity
    
    # Pack header
    header = struct.pack('=4B', size, packet_type, req_i, num_c)
    
    # Pack CompCar
    compcar = struct.pack(
        '=3H4B3i4H',
        node, lap, plid, position, info, sp3,
        x, y, z,
        speed, direction, heading, angvel
    )
    
    packet = header + compcar
    
    return packet


@pytest.fixture
def sample_nlp_packet():
    """
    Sample IS_NLP (Node and Lap) packet with one player
    
    Structure: Size(1), Type(1), ReqI(1), NumP(1), followed by NodeLap structures
    
    Each NodeLap: Node(2), Lap(2), PLID(1), Position(1), Sp2(2)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_NLP
    """
    size = 12  # 4 + 8 for one NodeLap
    packet_type = 37  # ISP_NLP
    req_i = 0
    num_p = 1  # Number of players
    
    # NodeLap data
    node = 15  # Current node
    lap = 3  # Current lap
    plid = 1  # Player ID
    position = 2  # Race position
    sp2 = 0  # Spare
    
    # Pack header
    header = struct.pack('=4B', size, packet_type, req_i, num_p)
    
    # Pack NodeLap
    nodelap = struct.pack('=2H2BH', node, lap, plid, position, sp2)
    
    packet = header + nodelap
    
    return packet


@pytest.fixture
def sample_lap_packet():
    """
    Sample IS_LAP (Lap time) packet
    
    Structure: Size(1), Type(1), ReqI(1), PLID(1), LTime(4), ETime(4),
               LapsDone(2), Flags(2), Sp0(1), Penalty(1), NumStops(1), Sp3(1)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_LAP
    """
    size = 20
    packet_type = 24  # ISP_LAP
    req_i = 0
    plid = 1  # Player ID
    ltime = 90000  # Lap time in ms (90 seconds)
    etime = 270000  # Total race time in ms (4.5 minutes)
    laps_done = 3  # Number of laps completed
    flags = 0  # Lap flags
    sp0 = 0  # Spare
    penalty = 0  # Penalty value
    num_stops = 1  # Number of pit stops
    sp3 = 0  # Spare
    
    packet = struct.pack(
        '=4B2I3H4B',
        size, packet_type, req_i, plid,
        ltime, etime,
        laps_done, flags, sp0,
        penalty, num_stops, sp3
    )
    
    return packet


@pytest.fixture
def sample_mso_packet():
    """
    Sample IS_MSO (Message Out) packet
    
    Structure: Size(1), Type(1), ReqI(1), Zero(1), UCID(1), PLID(1), UserType(1), TextStart(1),
               Msg(up to 128 chars)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_MSO
    """
    message = b'Test message from server'
    text_start = 0
    size = 8 + len(message) + 1  # Header + message + null terminator
    # Round up to multiple of 4
    size = ((size + 3) // 4) * 4
    
    packet_type = 11  # ISP_MSO
    req_i = 0
    zero = 0
    ucid = 1  # User ID
    plid = 1  # Player ID
    user_type = 2  # User type (MSO_USER)
    
    # Create message with null terminator and padding
    msg_data = message + b'\x00'
    padding_needed = size - 8 - len(msg_data)
    if padding_needed > 0:
        msg_data += b'\x00' * padding_needed
    
    packet = struct.pack(
        f'=8B{len(msg_data)}s',
        size, packet_type, req_i, zero,
        ucid, plid, user_type, text_start,
        msg_data
    )
    
    return packet


@pytest.fixture
def sample_sta_packet():
    """
    Sample IS_STA (State) packet
    
    Structure: Size(1), Type(1), ReqI(1), Zero(1), ReplaySpeed(4), Flags(2),
               InGameCam(1), ViewPLID(1), NumP(1), NumConns(1), NumFinished(1), RaceInProg(1),
               QualMins(1), RaceLaps(1), Sp2(1), Sp3(1), Track(6), Weather(1), Wind(1)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_STA
    """
    size = 28
    packet_type = 5  # ISP_STA (using ISP_STA = 5)
    req_i = 0
    zero = 0
    replay_speed = 1  # Normal speed (0 = not replaying)
    flags = 1  # State flags
    in_game_cam = 0  # In-game camera type
    view_plid = 255  # Viewed player ID (255 = none)
    num_p = 8  # Number of players
    num_conns = 8  # Number of connections
    num_finished = 0  # Number of finished players
    race_in_prog = 1  # Race in progress flag
    qual_mins = 0  # Qualification minutes
    race_laps = 10  # Number of race laps
    sp2 = 0  # Spare
    sp3 = 0  # Spare
    track = b'BL1'.ljust(6, b'\x00')  # Track code
    weather = 1  # Weather (0=sunny, 1=cloudy, 2=rain)
    wind = 0  # Wind (0=none, 1=weak, 2=strong)
    
    packet = struct.pack(
        '=4BfH10B6s2B',
        size, packet_type, req_i, zero,
        replay_speed, flags,
        in_game_cam, view_plid, num_p, num_conns,
        num_finished, race_in_prog, qual_mins, race_laps,
        sp2, sp3,
        track, weather, wind
    )
    
    return packet


@pytest.fixture
def sample_tiny_packet():
    """
    Sample IS_TINY (Tiny) packet - used for keepalive and control
    
    Structure: Size(1), Type(1), ReqI(1), SubT(1)
    
    Reference: https://en.lfsmanual.net/wiki/InSim.txt#IS_TINY
    """
    size = 4
    packet_type = 3  # ISP_TINY
    req_i = 0
    subt = 0  # TINY_NONE (keepalive)
    
    packet = struct.pack('=4B', size, packet_type, req_i, subt)
    
    return packet


@pytest.fixture
def sample_invalid_packet():
    """
    Invalid packet with wrong size
    """
    # Create a packet with size field that doesn't match actual size
    size = 100  # Claims to be 100 bytes
    packet_type = 1  # ISP_ISI
    req_i = 0
    zero = 0
    
    # But only create 8 bytes
    packet = struct.pack('=4B', size, packet_type, req_i, zero)
    
    return packet


@pytest.fixture
def sample_telemetry_data():
    """
    Sample processed telemetry data dictionary
    """
    return {
        'timestamp': 1234567890.123,
        'plid': 1,
        'speed': 150.5,  # km/h
        'rpm': 7500,
        'gear': 4,
        'position_x': 100.5,
        'position_y': 200.3,
        'position_z': 5.2,
        'heading': 90.0,  # degrees
        'lap': 3,
        'node': 15,
        'race_position': 2,
    }


@pytest.fixture
def sample_telemetry_list():
    """
    List of sample telemetry data points
    """
    return [
        {
            'timestamp': 1234567890.0 + i,
            'plid': 1,
            'speed': 100.0 + i * 10,
            'rpm': 5000 + i * 500,
            'gear': min(3 + i // 2, 6),
            'lap': 1,
            'node': 5 + i,
        }
        for i in range(10)
    ]
