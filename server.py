
"""Run: pip install -r requirements.txt && python server.py"""

import asyncio
import json
import secrets
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread

from websockets.asyncio.server import serve
from core import Room

rooms = {}
members = {}


async def connection(ws):
    client_id = secrets.token_hex(8)
    room_id = None

    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                await ws.send(json.dumps({
                    'type': 'error',
                    'message': 'invalid JSON'
                }))
                continue

            action = msg.get('type')

            if action == 'join':
                requested = str(msg.get('room', '')).strip()[:40]

                if not requested or not all(
                    c.isalnum() or c in '_-' for c in requested
                ):
                    await ws.send(json.dumps({
                        'type': 'error',
                        'message': 'invalid room'
                    }))
                    continue

                if room_id:
                    await ws.send(json.dumps({
                        'type': 'error',
                        'message': 'already joined'
                    }))
                    continue

                try:
                    room = rooms.setdefault(requested, Room())
                    result = room.join(
                        client_id,
                        str(msg.get('name', 'Guest'))
                    )
                except ValueError:
                    await ws.send(json.dumps({
                        'type': 'error',
                        'message': 'invalid name'
                    }))
                    continue

                room_id = requested
                members.setdefault(room_id, set()).add(ws)

                await ws.send(json.dumps(
                    result,
                    ensure_ascii=False
                ))

                await broadcast_users(room_id)

            elif action == 'edit' and room_id:
                result = rooms[room_id].update(
                    msg.get('code'),
                    msg.get('revision')
                )

                if result['type'] == 'update':
                    await broadcast(room_id, result)
                else:
                    await ws.send(json.dumps(
                        result,
                        ensure_ascii=False
                    ))

            else:
                await ws.send(json.dumps({
                    'type': 'error',
                    'message': 'join room first'
                }))

    finally:
        if room_id:
            members.get(room_id, set()).discard(ws)
            rooms[room_id].leave(client_id)
            await broadcast_users(room_id)


async def broadcast(room_id, data):
    packet = json.dumps(data, ensure_ascii=False)

    for peer in tuple(members.get(room_id, ())):
        try:
            await peer.send(packet)
        except Exception:
            pass


async def broadcast_users(room_id):
    if room_id in rooms:
        await broadcast(room_id, {
            'type': 'users',
            'users': list(rooms[room_id].users.values())
        })


def start_http():
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(
                *args,
                directory=str(Path(__file__).parent),
                **kwargs
            )

    server = ThreadingHTTPServer(
        ('127.0.0.1', 8000),
        Handler
    )
    server.serve_forever()


async def main():
    Thread(
        target=start_http,
        daemon=True
    ).start()

    print('CodeTogether запущен!')
    print('Откройте http://127.0.0.1:8000')

    async with serve(
        connection,
        '127.0.0.1',
        8765,
        max_size=200000
    ):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())

