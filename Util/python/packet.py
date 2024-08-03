import zerohertzLib as zz
from scapy.all import IP, TCP, UDP, sniff

logger = zz.logging.Logger("PACKET")


def packet_handler(packet):
    if IP in packet:
        logs = ""
        ip_layer = packet[IP]
        logs += f"\n[IP Packet] {ip_layer.src} -> {ip_layer.dst}"
        if TCP in packet:
            tcp_layer = packet[TCP]
            logs += f"\n[TCP] Source Port: {tcp_layer.sport}, Destination Port: {tcp_layer.dport}\nSequence Number: {tcp_layer.seq}, Acknowledgment Number: {tcp_layer.ack}"
        elif UDP in packet:
            udp_layer = packet[UDP]
            logs += f"\n[UDP] Source Port: {udp_layer.sport}, Destination Port: {udp_layer.dport}"
        logs += "\n" + packet.show(True)
        logger.info(logs)


if __name__ == "__main__":
    logger.info("Starting packet capture...")
    sniff(prn=packet_handler, filter="tcp or udp", count=10)
