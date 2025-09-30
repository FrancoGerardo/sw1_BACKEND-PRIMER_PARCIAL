from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # Diccionario para almacenar conexiones por sala
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Diccionario para almacenar usuarios por sala
        self.room_users: Dict[str, List[dict]] = {}
        # Diccionario para almacenar XML de cada sala
        self.room_xmls: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, room: str, username: str):
        """Conectar un usuario a una sala"""
        await websocket.accept()
        
        if room not in self.active_connections:
            self.active_connections[room] = []
            self.room_users[room] = []
        
        self.active_connections[room].append(websocket)
        
        # Agregar usuario a la sala
        user_info = {"username": username, "websocket": websocket}
        self.room_users[room].append(user_info)
        
        print(f"Usuario {username} conectado a la sala {room}")
        
        # Notificar a otros usuarios
        await self.broadcast_user_list(room)

    def disconnect(self, websocket: WebSocket, room: str, username: str):
        """Desconectar un usuario de una sala"""
        if room in self.active_connections:
            if websocket in self.active_connections[room]:
                self.active_connections[room].remove(websocket)
            
            # Remover usuario de la lista
            self.room_users[room] = [
                user for user in self.room_users[room] 
                if user["websocket"] != websocket
            ]
            
            print(f"Usuario {username} desconectado de la sala {room}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Enviar mensaje a un WebSocket específico"""
        try:
            await websocket.send_text(message)
        except:
            pass  # Ignorar errores de conexión cerrada

    async def broadcast_to_room(self, message: str, room: str, exclude_websocket: WebSocket = None):
        """Transmitir mensaje a todos los usuarios de una sala"""
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                if connection != exclude_websocket:
                    try:
                        await connection.send_text(message)
                    except:
                        # Remover conexión si está cerrada
                        if connection in self.active_connections[room]:
                            self.active_connections[room].remove(connection)

    async def broadcast_diagram_change(self, room: str, xml_content: str):
        """Transmitir cambios del diagrama a otros usuarios"""
        self.room_xmls[room] = xml_content
        message = json.dumps({
            "type": "draw_component",
            "xml": xml_content
        })
        await self.broadcast_to_room(message, room)

    async def broadcast_user_list(self, room: str):
        """Transmitir lista de usuarios a todos en la sala"""
        if room in self.room_users:
            users = [user["username"] for user in self.room_users[room]]
            message = json.dumps({
                "type": "reload_users_room",
                "users": users
            })
            await self.broadcast_to_room(message, room)

    async def send_save_response(self, websocket: WebSocket, success: bool, message: str):
        """Enviar respuesta de guardado"""
        response = {
            "type": "save_response",
            "success": success,
            "message": message
        }
        await self.send_personal_message(json.dumps(response), websocket)

# Instancia global del manager
manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, room: str, username: str):
    """Endpoint principal de WebSocket"""
    await manager.connect(websocket, room, username)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "draw_component":
                # Transmitir cambios del diagrama a otros usuarios
                xml_content = message.get("xml", "")
                await manager.broadcast_diagram_change(room, xml_content)
            
            elif message.get("type") == "save_component":
                # Procesar guardado (aquí podrías integrar con la base de datos)
                await manager.send_save_response(
                    websocket, 
                    True, 
                    "Diagrama guardado exitosamente"
                )
            
            elif message.get("type") == "login":
                # Usuario se conecta a la sala
                await manager.broadcast_user_list(room)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, room, username)
        # Notificar a otros usuarios que alguien se desconectó
        await manager.broadcast_user_list(room)
