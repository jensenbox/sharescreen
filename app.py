"""This module sets up a FastAPI application for screen sharing and viewing.

It includes the following endpoints:
- `/`: Generates a new room ID and provides share and view links.
- `/share/{room_id}`: Renders a page for sharing the screen in a specific room.
- `/view/{room_id}`: Renders a page for viewing the screen in a specific room.
- `/ws/{room_id}`: WebSocket endpoint for real-time communication in a specific room.

The module also configures the templates directory and mounts static files.

Dependencies:
- FastAPI
- Jinja2
- Loguru
- Starlette

Usage:
    Run the FastAPI application to start the server and access the endpoints.
"""

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket
from loguru import logger
from starlette.websockets import WebSocketDisconnect


connections = {}

# Initialize FastAPI app
app = FastAPI()

# Configure templates directory
templates = Jinja2Templates(directory="templates")

# Mount static files (for CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Endpoint to generate a new room ID and links
@app.get("/", response_class=HTMLResponse)
async def generate_room(request: Request) -> templates.TemplateResponse:
    """Endpoint to generate a new room ID and links.

    This endpoint generates a unique room ID and creates share and view links
    for screen sharing. It then renders an HTML page with these links.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: The rendered HTML response containing the share and view links.
    """
    room_id = str(uuid.uuid4())
    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost:8088')}"

    share_link = f"{base_url}/share/{room_id}"
    view_link = f"{base_url}/view/{room_id}"
    return templates.TemplateResponse(
        "share.html",
        {
            "request": request,
            "title": "Screen Sharing Links",
            "share_link": share_link,
            "view_link": view_link,
        },
    )


# Endpoint for screen sharing page
@app.get("/share/{room_id}", response_class=HTMLResponse, name="share")
async def share_screen(request: Request, room_id: str) -> templates.TemplateResponse:
    """Endpoint for sharing the screen in a specific room.

    This endpoint renders an HTML page that allows users to share their screen
    in the specified room.

    Args:
        request (Request): The HTTP request object.
        room_id (str): The unique identifier for the room.

    Returns:
        TemplateResponse: The rendered HTML response for sharing the screen.
    """
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "title": f"Sharing Room {room_id}",
            "content": f"""
        <p>Sharing screen for room <strong>{room_id}</strong>.</p>
        <p>Screen sharing functionality coming soon.</p>
        """,
        },
    )


# Endpoint for viewing screen
@app.get("/view/{room_id}", response_class=HTMLResponse, name="view")
async def view_screen(request: Request, room_id: str) -> templates.TemplateResponse:
    """Endpoint for viewing the screen in a specific room.

    This endpoint renders an HTML page that allows users to view the screen
    being shared in the specified room.

    Args:
        request (Request): The HTTP request object.
        room_id (str): The unique identifier for the room.

    Returns:
        TemplateResponse: The rendered HTML response for viewing the screen.
    """
    return templates.TemplateResponse(
        "base.html",
        {
            "request": request,
            "title": f"Viewing Room {room_id}",
            "content": f"""
        <p>Viewing screen for room <strong>{room_id}</strong>.</p>
        <p>Screen viewing functionality coming soon.</p>
        """,
        },
    )


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str) -> None:
    """WebSocket endpoint for handling real-time communication in a specific room.

    This endpoint accepts WebSocket connections and manages a list of connections
    for each room. It receives messages from the connected WebSocket and broadcasts
    them to all other connections in the same room.

    Args:
        websocket (WebSocket): The WebSocket connection instance.
        room_id (str): The unique identifier for the room.

    Raises:
        Exception: If an error occurs during message handling or connection management.
    """
    await websocket.accept()
    if room_id not in connections:
        connections[room_id] = []
    connections[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for connection in connections[room_id]:
                if connection != websocket:
                    await connection.send_text(data)
    except (WebSocketDisconnect, ConnectionError) as e:
        logger.info(f"WebSocket disconnected: {e}")
    finally:
        connections[room_id].remove(websocket)
