from dnslib import DNSRecord, QTYPE, RR, A
from socketserver import UDPServer, BaseRequestHandler
import socket
import subprocess
import os
import time

def start_dnsproxy():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    batch_file = os.path.join(script_dir, "proxy.bat")
    
    if not os.path.exists(batch_file):
        print(f"[X] Error: Batch file not found at {batch_file}")
        return
    
    print("[*] Starting DNS proxy server...")
    process = subprocess.Popen(batch_file, shell=True)
    
    time.sleep(2)
    
    if process.poll() is None:
        print("[*] DNS Proxy Server started successfully.")
    else:
        print("[X] Error: Failed to start DNS Proxy Server.")

if __name__ == "__main__":
    start_dnsproxy()


# Blocked domains and fake IP response
BLOCKED_DOMAINS = ["youtube.com"]
BLOCK_RESPONSE_IP = "127.0.0.1"

class DNSRequestHandler(BaseRequestHandler):
    def handle(self):
        data, sock = self.request

        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).strip(".")
            print(f"[+] DNS Query received for: {qname}, ID: {request.header.id}")

            # Blocked domain check
            if any(qname.lower().endswith(blocked) for blocked in BLOCKED_DOMAINS):
                print(f"[!] Blocking domain: {qname}")
                reply = request.reply()
                reply.add_answer(RR(qname, QTYPE.A, rdata=A(BLOCK_RESPONSE_IP), ttl=60))
                sock.sendto(reply.pack(), self.client_address)
                print(f"[+] Sent fake DNS response to {self.client_address}")
            else:
                print(f"[+] Forwarding request for: {qname} to 8.8.8.8")
                # Forward original request raw bytes
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as forward_sock:
                    forward_sock.settimeout(5)
                    forward_sock.sendto(data, ("8.8.8.8", 53))
                    response_data, _ = forward_sock.recvfrom(512)

                # Send the raw response back to the client
                sock.sendto(response_data, self.client_address)
                print(f"[+] Successfully forwarded and responded to {qname}")

        except Exception as e:
            print(f"[X] Error processing request: {e}")
            try:
                # Send a fallback response
                fallback = DNSRecord.parse(data).reply()
                fallback.add_answer(RR("error.local", QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
                sock.sendto(fallback.pack(), self.client_address)
            except:
                pass


# Bind the DNS server to all interfaces on port 53
server = UDPServer(("0.0.0.0", 5354), DNSRequestHandler)
print("[*] Starting DNS server on port 5354...")
server.serve_forever() 