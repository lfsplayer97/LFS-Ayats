"""
Example REST API client for LFS-Ayats.

Demonstrates how to interact with the LFS-Ayats REST API including:
- REST API calls (sessions, laps, statistics)
- WebSocket telemetry streaming
- Error handling
- Pagination

Usage:
    python examples/api_client_example.py

Requirements:
    pip install requests websockets
"""

import asyncio
import json
import requests
import websockets
from typing import List, Dict, Any


# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
WEBSOCKET_URL = "ws://localhost:8000/api/v1/telemetry/live"


class LFSAyatsClient:
    """Client for LFS-Ayats REST API."""

    def __init__(self, base_url: str = API_BASE_URL):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API
        """
        self.base_url = base_url

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health.

        Returns:
            Health status response
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def get_status(self) -> Dict[str, Any]:
        """
        Get system status.

        Returns:
            System status response
        """
        response = requests.get(f"{self.base_url}/status")
        response.raise_for_status()
        return response.json()

    def list_sessions(
        self,
        circuit: str = None,
        vehicle: str = None,
        driver: str = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        List telemetry sessions.

        Args:
            circuit: Filter by circuit name
            vehicle: Filter by vehicle name
            driver: Filter by driver name
            limit: Maximum results
            offset: Pagination offset

        Returns:
            Paginated session list
        """
        params = {"limit": limit, "offset": offset}
        if circuit:
            params["circuit"] = circuit
        if vehicle:
            params["vehicle"] = vehicle
        if driver:
            params["driver"] = driver

        response = requests.get(f"{self.base_url}/sessions", params=params)
        response.raise_for_status()
        return response.json()

    def get_session(self, session_id: int) -> Dict[str, Any]:
        """
        Get session details.

        Args:
            session_id: Session ID

        Returns:
            Session details
        """
        response = requests.get(f"{self.base_url}/sessions/{session_id}")
        response.raise_for_status()
        return response.json()

    def create_session(
        self, circuit: str, vehicle: str, driver: str
    ) -> Dict[str, Any]:
        """
        Create a new session.

        Args:
            circuit: Circuit name
            vehicle: Vehicle name
            driver: Driver name

        Returns:
            Created session details
        """
        data = {"circuit": circuit, "vehicle": vehicle, "driver": driver}
        response = requests.post(f"{self.base_url}/sessions", json=data)
        response.raise_for_status()
        return response.json()

    def delete_session(self, session_id: int) -> None:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete
        """
        response = requests.delete(f"{self.base_url}/sessions/{session_id}")
        response.raise_for_status()

    def get_lap(self, lap_id: int) -> Dict[str, Any]:
        """
        Get lap details.

        Args:
            lap_id: Lap ID

        Returns:
            Lap details
        """
        response = requests.get(f"{self.base_url}/{lap_id}")
        response.raise_for_status()
        return response.json()

    def get_lap_telemetry(
        self, lap_id: int, sample_rate: int = None
    ) -> Dict[str, Any]:
        """
        Get lap telemetry data.

        Args:
            lap_id: Lap ID
            sample_rate: Optional downsampling rate (Hz)

        Returns:
            Telemetry data
        """
        params = {}
        if sample_rate:
            params["sample_rate"] = sample_rate

        response = requests.get(
            f"{self.base_url}/{lap_id}/telemetry", params=params
        )
        response.raise_for_status()
        return response.json()

    def compare_laps(self, lap_ids: List[int]) -> Dict[str, Any]:
        """
        Compare multiple laps.

        Args:
            lap_ids: List of lap IDs to compare (2-5)

        Returns:
            Comparison results
        """
        params = [("lap_ids", lap_id) for lap_id in lap_ids]
        response = requests.get(f"{self.base_url}/compare", params=params)
        response.raise_for_status()
        return response.json()

    def get_best_laps(
        self, circuit: str = None, vehicle: str = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get best laps.

        Args:
            circuit: Filter by circuit
            vehicle: Filter by vehicle
            limit: Maximum results

        Returns:
            List of best laps
        """
        params = {"limit": limit}
        if circuit:
            params["circuit"] = circuit
        if vehicle:
            params["vehicle"] = vehicle

        response = requests.get(f"{self.base_url}/stats/best-laps", params=params)
        response.raise_for_status()
        return response.json()

    def get_driver_stats(self, driver_name: str) -> Dict[str, Any]:
        """
        Get driver statistics.

        Args:
            driver_name: Driver name

        Returns:
            Driver statistics
        """
        response = requests.get(f"{self.base_url}/stats/driver/{driver_name}")
        response.raise_for_status()
        return response.json()

    def get_circuit_stats(self, circuit_name: str) -> Dict[str, Any]:
        """
        Get circuit statistics.

        Args:
            circuit_name: Circuit name

        Returns:
            Circuit statistics
        """
        response = requests.get(f"{self.base_url}/stats/circuit/{circuit_name}")
        response.raise_for_status()
        return response.json()

    def export_lap_csv(self, lap_id: int, filename: str) -> None:
        """
        Export lap data as CSV.

        Args:
            lap_id: Lap ID
            filename: Output filename
        """
        response = requests.get(f"{self.base_url}/export/csv/{lap_id}")
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

    def export_lap_json(self, lap_id: int, filename: str) -> None:
        """
        Export lap data as JSON.

        Args:
            lap_id: Lap ID
            filename: Output filename
        """
        response = requests.get(f"{self.base_url}/export/json/{lap_id}")
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

    async def stream_telemetry(
        self, callback, duration: int = None
    ):
        """
        Stream live telemetry via WebSocket.

        Args:
            callback: Function to call with telemetry data
            duration: Optional duration in seconds (None = indefinite)
        """
        async with websockets.connect(WEBSOCKET_URL) as websocket:
            start_time = asyncio.get_event_loop().time()

            while True:
                if duration and (asyncio.get_event_loop().time() - start_time) > duration:
                    break

                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    if data.get("type") == "telemetry":
                        callback(data["data"])
                    elif data.get("type") == "error":
                        print(f"WebSocket error: {data.get('error')}")
                        break

                except websockets.exceptions.ConnectionClosed:
                    print("WebSocket connection closed")
                    break


def main():
    """Demonstrate API usage."""
    print("=" * 60)
    print("LFS-Ayats API Client Example")
    print("=" * 60)

    # Create client
    client = LFSAyatsClient()

    # 1. Health check
    print("\n1. Health Check")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}")
    except requests.exceptions.ConnectionError:
        print("   ERROR: Cannot connect to API server")
        print("   Please start the API server first:")
        print("   uvicorn src.api.main:app --reload")
        return

    # 2. System status
    print("\n2. System Status")
    status = client.get_status()
    print(f"   Connected to LFS: {status['connected']}")
    print(f"   Uptime: {status['uptime']:.1f}s")
    print(f"   Sessions: {status['sessions_count']}")

    # 3. List sessions
    print("\n3. List Sessions")
    sessions = client.list_sessions(limit=5)
    print(f"   Total sessions: {sessions['total']}")
    print(f"   Showing: {len(sessions['items'])} sessions")
    for session in sessions["items"][:3]:
        print(f"   - Session {session['id']}: {session['driver']} @ {session['circuit']}")

    # 4. Create a test session
    print("\n4. Create Test Session")
    try:
        new_session = client.create_session(
            circuit="Blackwood GP",
            vehicle="XF GTI",
            driver="APITestDriver",
        )
        print(f"   Created session ID: {new_session['id']}")
        print(f"   Driver: {new_session['driver']}")
        print(f"   Circuit: {new_session['circuit']}")
    except Exception as e:
        print(f"   Error creating session: {e}")

    # 5. Get best laps
    print("\n5. Get Best Laps")
    try:
        best_laps = client.get_best_laps(limit=5)
        print(f"   Found {len(best_laps)} best laps")
        for lap_stats in best_laps[:3]:
            lap = lap_stats["lap"]
            print(f"   - {lap_stats['driver']}: {lap['lap_time']:.2f}s @ {lap_stats['circuit']}")
    except Exception as e:
        print(f"   No best laps available yet: {e}")

    # 6. WebSocket telemetry streaming (demo)
    print("\n6. WebSocket Telemetry Streaming")
    print("   (Would stream telemetry for 5 seconds)")
    print("   Uncomment the code below to test WebSocket streaming")

    # Uncomment to test WebSocket streaming:
    # def telemetry_callback(data):
    #     print(f"   Speed: {data['speed']:.1f} km/h, RPM: {data['rpm']}, Gear: {data['gear']}")
    #
    # try:
    #     asyncio.run(client.stream_telemetry(telemetry_callback, duration=5))
    # except Exception as e:
    #     print(f"   WebSocket error: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("Visit http://localhost:8000/api/docs for interactive API documentation")
    print("=" * 60)


if __name__ == "__main__":
    main()
