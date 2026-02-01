import asyncio
import struct
from enum import IntEnum
from typing import Optional


class PacketType(IntEnum):
    SERVERDATA_AUTH = 3
    SERVERDATA_AUTH_RESPONSE = 2
    SERVERDATA_EXECCOMMAND = 2
    SERVERDATA_RESPONSE_VALUE = 0


class RCONError(Exception):
    """Base RCON exception."""
    pass


class RCONAuthError(RCONError):
    """Authentication failed."""
    pass


class RCONConnectionError(RCONError):
    """Connection error."""
    pass


class RCONClient:
    """Async RCON client for Source engine servers (CS2)."""

    def __init__(self, host: str, port: int, password: str, timeout: float = 10.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._request_id = 0
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """Connect and authenticate with the RCON server."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise RCONConnectionError(f"Connection to {self.host}:{self.port} timed out")
        except OSError as e:
            raise RCONConnectionError(f"Failed to connect to {self.host}:{self.port}: {e}")

        # Authenticate
        response = await self._send_packet(PacketType.SERVERDATA_AUTH, self.password)
        if response is None:
            raise RCONAuthError("Authentication failed: no response")

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._writer:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except Exception:
                pass
            self._writer = None
            self._reader = None

    async def execute(self, command: str) -> str:
        """Execute an RCON command and return the response."""
        if not self._writer:
            raise RCONConnectionError("Not connected")

        async with self._lock:
            response = await self._send_packet(PacketType.SERVERDATA_EXECCOMMAND, command)
            return response or ""

    async def _send_packet(self, packet_type: PacketType, body: str) -> Optional[str]:
        """Send a packet and receive the response."""
        self._request_id += 1
        request_id = self._request_id

        # Build packet: size (4) + id (4) + type (4) + body + null (1) + null (1)
        body_encoded = body.encode("utf-8")
        packet_body = struct.pack("<ii", request_id, packet_type) + body_encoded + b"\x00\x00"
        packet = struct.pack("<i", len(packet_body)) + packet_body

        self._writer.write(packet)
        await self._writer.drain()

        # Read response
        try:
            response_data = await asyncio.wait_for(
                self._read_packet(),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            raise RCONConnectionError("Response timed out")

        if response_data is None:
            return None

        resp_id, resp_type, resp_body = response_data

        # Auth response: -1 means failure
        if packet_type == PacketType.SERVERDATA_AUTH:
            if resp_id == -1:
                raise RCONAuthError("Authentication failed: invalid password")

        return resp_body

    async def _read_packet(self) -> Optional[tuple[int, int, str]]:
        """Read a single RCON packet."""
        # Read size (4 bytes)
        size_data = await self._reader.read(4)
        if len(size_data) < 4:
            return None

        size = struct.unpack("<i", size_data)[0]

        # Read rest of packet
        packet_data = await self._reader.read(size)
        if len(packet_data) < size:
            return None

        # Parse: id (4) + type (4) + body + null + null
        request_id, packet_type = struct.unpack("<ii", packet_data[:8])
        body = packet_data[8:-2].decode("utf-8", errors="replace")

        return request_id, packet_type, body

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


async def execute_rcon(host: str, port: int, password: str, command: str) -> str:
    """Execute a single RCON command (connects, runs, disconnects)."""
    async with RCONClient(host, port, password) as client:
        return await client.execute(command)
