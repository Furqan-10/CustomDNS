from dnslib import DNSRecord, QTYPE

qname = "google.com"  # Example query
real_dns = DNSRecord.question(qname)
response = real_dns.send("8.8.8.8", 53, timeout=2)

if response:
    print("Response from 8.8.8.8 received:")
    print(response)
else:
    print("No response from 8.8.8.8.")

