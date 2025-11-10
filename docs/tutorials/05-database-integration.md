# Tutorial 5: Integració amb Base de Dades

Aquest tutorial t'ensenyarà a emmagatzemar sessions de telemetria en una base de dades per consultes històriques i anàlisi a llarg termini.

## Objectius

- ✅ Configurar PostgreSQL o SQLite
- ✅ Emmagatzemar sessions i telemetria
- ✅ Consultar dades històriques
- ✅ Optimitzar rendiment de consultes
- ✅ Exportar i importar dades

## Prerequisits

- Tutorials anteriors completats
- SQLite (inclòs amb Python) o PostgreSQL instal·lat

## Temps Estimat: 45 minuts

## Pas 1: Configuració de la Base de Dades

### Opció A: SQLite (Recomanat per començar)

```python
"""
Integració amb Base de Dades
Emmagatzematge persistent de telemetria.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.database import Base, Session, Lap, TelemetryPoint
from src.connection import InSimClient
from src.telemetry import TelemetryCollector
from src.utils import setup_logger

logger = setup_logger("db_integration", "INFO")


def setup_sqlite_database(db_path: str = "data/telemetry.db"):
    """
    Configura base de dades SQLite.
    
    Args:
        db_path: Camí al fitxer de base de dades
        
    Returns:
        Sessió de base de dades
    """
    logger.info(f"Configurant SQLite: {db_path}")
    
    # Crear engine
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    
    # Crear taules
    Base.metadata.create_all(engine)
    logger.info("✓ Taules creades")
    
    # Crear sessió
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    return db_session
```

### Opció B: PostgreSQL (Producció)

```python
def setup_postgresql_database(
    host: str = "localhost",
    port: int = 5432,
    database: str = "lfs_telemetry",
    user: str = "lfs_user",
    password: str = "password"
):
    """
    Configura base de dades PostgreSQL.
    
    Args:
        host: Host del servidor PostgreSQL
        port: Port (per defecte 5432)
        database: Nom de la base de dades
        user: Usuari
        password: Contrasenya
        
    Returns:
        Sessió de base de dades
    """
    logger.info(f"Connectant a PostgreSQL: {host}:{port}/{database}")
    
    # Connection string
    conn_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    
    # Crear engine
    engine = create_engine(conn_string, echo=False)
    
    # Crear taules
    Base.metadata.create_all(engine)
    logger.info("✓ Connexió establerta i taules creades")
    
    # Crear sessió
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    return db_session
```

## Pas 2: Models de Dades

Els models ja estan definits a `src/database/models.py`, però aquí tens un resum:

```python
# Exemple de model Session
class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    track = Column(String(50))
    car = Column(String(50))
    driver = Column(String(50))
    laps = relationship("Lap", back_populates="session")


# Exemple de model Lap
class Lap(Base):
    __tablename__ = 'laps'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    lap_number = Column(Integer)
    lap_time = Column(Float)
    telemetry_points = relationship("TelemetryPoint", back_populates="lap")
```

## Pas 3: Guardar Sessions

```python
from src.database.repository import TelemetryRepository


def save_session_to_database(
    db_session,
    telemetry_data: List[Dict],
    track: str = "Unknown",
    car: str = "Unknown",
    driver: str = "Unknown"
):
    """
    Guarda una sessió completa a la base de dades.
    
    Args:
        db_session: Sessió de SQLAlchemy
        telemetry_data: Dades de telemetria
        track: Nom del circuit
        car: Model del cotxe
        driver: Nom del pilot
    """
    logger.info("Guardant sessió a la base de dades...")
    
    repo = TelemetryRepository(db_session)
    
    # Crear sessió
    session = repo.create_session(
        start_time=datetime.now(),
        track=track,
        car=car,
        driver=driver
    )
    
    logger.info(f"✓ Sessió creada: ID {session.id}")
    
    # Separar en voltes
    laps = extract_laps(telemetry_data)
    
    # Guardar cada volta
    for lap_idx, lap_data in enumerate(laps):
        lap_time = calculate_lap_time(lap_data)
        
        lap = repo.create_lap(
            session_id=session.id,
            lap_number=lap_idx + 1,
            lap_time=lap_time
        )
        
        # Guardar punts de telemetria
        for point in lap_data:
            repo.create_telemetry_point(
                lap_id=lap.id,
                timestamp=datetime.fromisoformat(point['timestamp']),
                speed=point.get('speed', 0),
                rpm=point.get('rpm', 0),
                gear=point.get('gear', 0),
                pos_x=point.get('pos_x', 0),
                pos_y=point.get('pos_y', 0),
                pos_z=point.get('pos_z', 0)
            )
        
        logger.info(f"  Volta {lap_idx + 1}: {len(lap_data)} punts guardats")
    
    # Actualitzar end_time de la sessió
    repo.update_session(session.id, end_time=datetime.now())
    
    logger.info(f"✓ Sessió guardada: {len(laps)} voltes")
    
    return session.id
```

## Pas 4: Consultar Dades Històriques

```python
def query_best_laps(db_session, track: str = None, limit: int = 10):
    """
    Consulta les millors voltes.
    
    Args:
        db_session: Sessió de base de dades
        track: Filtrar per circuit (opcional)
        limit: Nombre màxim de resultats
        
    Returns:
        Llista de millors voltes
    """
    logger.info("Consultant millors voltes...")
    
    repo = TelemetryRepository(db_session)
    
    best_laps = repo.get_best_laps(track=track, limit=limit)
    
    logger.info(f"\n🏆 Top {limit} Millors Voltes:")
    for idx, lap in enumerate(best_laps, 1):
        logger.info(f"{idx}. Volta {lap.lap_number} - "
                   f"Temps: {lap.lap_time:.3f}s - "
                   f"Circuit: {lap.session.track} - "
                   f"Pilot: {lap.session.driver}")
    
    return best_laps


def query_session_statistics(db_session, session_id: int):
    """
    Obté estadístiques d'una sessió.
    
    Args:
        db_session: Sessió de base de dades
        session_id: ID de la sessió
    """
    logger.info(f"Consultant estadístiques de la sessió {session_id}...")
    
    repo = TelemetryRepository(db_session)
    
    session = repo.get_session(session_id)
    
    if not session:
        logger.error(f"Sessió {session_id} no trobada")
        return
    
    logger.info(f"\n📊 Sessió #{session.id}")
    logger.info(f"   Circuit: {session.track}")
    logger.info(f"   Cotxe: {session.car}")
    logger.info(f"   Pilot: {session.driver}")
    logger.info(f"   Inici: {session.start_time}")
    logger.info(f"   Fi: {session.end_time}")
    logger.info(f"   Total voltes: {len(session.laps)}")
    
    if session.laps:
        lap_times = [lap.lap_time for lap in session.laps]
        logger.info(f"   Millor volta: {min(lap_times):.3f}s")
        logger.info(f"   Pitjor volta: {max(lap_times):.3f}s")
        logger.info(f"   Mitjana: {np.mean(lap_times):.3f}s")


def compare_sessions(db_session, session_id1: int, session_id2: int):
    """
    Compara dues sessions.
    
    Args:
        db_session: Sessió de base de dades
        session_id1: ID primera sessió
        session_id2: ID segona sessió
    """
    logger.info(f"\n=== Comparant Sessions {session_id1} vs {session_id2} ===")
    
    repo = TelemetryRepository(db_session)
    
    s1 = repo.get_session(session_id1)
    s2 = repo.get_session(session_id2)
    
    if not s1 or not s2:
        logger.error("Una o ambdues sessions no existeixen")
        return
    
    # Comparar millors voltes
    best_lap1 = min(s1.laps, key=lambda l: l.lap_time) if s1.laps else None
    best_lap2 = min(s2.laps, key=lambda l: l.lap_time) if s2.laps else None
    
    if best_lap1 and best_lap2:
        diff = best_lap2.lap_time - best_lap1.lap_time
        logger.info(f"\n⏱️  Millors Voltes:")
        logger.info(f"   Sessió {session_id1}: {best_lap1.lap_time:.3f}s")
        logger.info(f"   Sessió {session_id2}: {best_lap2.lap_time:.3f}s")
        logger.info(f"   Diferència: {abs(diff):.3f}s")
```

## Pas 5: Optimització de Consultes

```python
# Afegir índexs per millorar rendiment
from sqlalchemy import Index

# A models.py, afegir índexs:
Index('idx_session_track', Session.track)
Index('idx_lap_time', Lap.lap_time)
Index('idx_telemetry_timestamp', TelemetryPoint.timestamp)


def batch_insert_telemetry(db_session, telemetry_points: List[Dict], 
                          batch_size: int = 1000):
    """
    Inserció per lots per millor rendiment.
    
    Args:
        db_session: Sessió de base de dades
        telemetry_points: Llista de punts
        batch_size: Mida del lot
    """
    logger.info(f"Inserint {len(telemetry_points)} punts en lots...")
    
    for i in range(0, len(telemetry_points), batch_size):
        batch = telemetry_points[i:i + batch_size]
        db_session.bulk_insert_mappings(TelemetryPoint, batch)
        db_session.commit()
        
        logger.info(f"  Inserits {i + len(batch)}/{len(telemetry_points)} punts")
    
    logger.info("✓ Inserció completada")
```

## Pas 6: Exportació i Importació

```python
def export_session_to_json(db_session, session_id: int, 
                          output_file: str):
    """Exporta sessió a JSON."""
    repo = TelemetryRepository(db_session)
    session = repo.get_session(session_id, include_telemetry=True)
    
    data = {
        'session_id': session.id,
        'track': session.track,
        'car': session.car,
        'driver': session.driver,
        'laps': []
    }
    
    for lap in session.laps:
        lap_data = {
            'lap_number': lap.lap_number,
            'lap_time': lap.lap_time,
            'telemetry': [
                {
                    'timestamp': str(point.timestamp),
                    'speed': point.speed,
                    'rpm': point.rpm,
                    'gear': point.gear,
                    'pos_x': point.pos_x,
                    'pos_y': point.pos_y,
                    'pos_z': point.pos_z
                }
                for point in lap.telemetry_points
            ]
        }
        data['laps'].append(lap_data)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"✓ Sessió exportada: {output_file}")


def import_session_from_json(db_session, json_file: str):
    """Importa sessió des de JSON."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Crear sessió
    session = Session(
        start_time=datetime.now(),
        track=data['track'],
        car=data['car'],
        driver=data['driver']
    )
    db_session.add(session)
    db_session.flush()
    
    # Afegir voltes
    for lap_data in data['laps']:
        lap = Lap(
            session_id=session.id,
            lap_number=lap_data['lap_number'],
            lap_time=lap_data['lap_time']
        )
        db_session.add(lap)
        db_session.flush()
        
        # Afegir telemetria
        for point_data in lap_data['telemetry']:
            point = TelemetryPoint(
                lap_id=lap.id,
                **point_data
            )
            db_session.add(point)
    
    db_session.commit()
    logger.info(f"✓ Sessió importada: ID {session.id}")
```

## Pas 7: Funció Principal

```python
def main():
    """Funció principal."""
    logger.info("=== Integració amb Base de Dades ===\n")
    
    # 1. Configurar base de dades
    db_session = setup_sqlite_database("data/telemetry.db")
    
    # 2. Carregar dades d'exemple
    telemetry_data = load_session_data("data/session_20240115_143022.json")
    
    # 3. Guardar a base de dades
    session_id = save_session_to_database(
        db_session,
        telemetry_data,
        track="Blackwood GP",
        car="XF GTI",
        driver="YourName"
    )
    
    # 4. Consultar dades
    query_best_laps(db_session, limit=5)
    query_session_statistics(db_session, session_id)
    
    # 5. Exportar
    export_session_to_json(db_session, session_id, "session_export.json")
    
    logger.info("\n✓ Tutorial completat!")


if __name__ == "__main__":
    main()
```

## Consells de Producció

### 1. Configuració PostgreSQL

```bash
# Crear base de dades
sudo -u postgres psql
CREATE DATABASE lfs_telemetry;
CREATE USER lfs_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE lfs_telemetry TO lfs_user;
```

### 2. Migrations amb Alembic

```bash
# Inicialitzar Alembic
alembic init alembic

# Generar migració
alembic revision --autogenerate -m "Initial schema"

# Aplicar migració
alembic upgrade head
```

### 3. Backups Regulars

```bash
# Backup SQLite
cp data/telemetry.db data/telemetry_backup_$(date +%Y%m%d).db

# Backup PostgreSQL
pg_dump lfs_telemetry > backup_$(date +%Y%m%d).sql
```

## Exercicis

1. **Anàlisi Temporal**: Crea consultes per veure progressió al llarg del temps
2. **Estadístiques Globals**: Implementa queries per rànquings globals
3. **Càrrega Lazy**: Optimitza càrrega de relacions

## Recursos

- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

---

Ara pots emmagatzemar i consultar històrics! 💾
