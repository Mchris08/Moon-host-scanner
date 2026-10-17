import asyncio, socket, ssl, json, aiohttp, ipaddress
from datetime import datetime

# Zimbabwe ISP prefixes for filtering
ZIM_PREFIXES = ["41.220.", "197.221.", "196.44.", "196.43.", "41.190.", "41.191."]

def is_zim_ip(ip: str) -> bool:
    return any(ip.startswith(p) for p in ZIM_PREFIXES)

async def fetch_public_proxies():
    """Fetches publicly listed proxies (ProxyScrape)."""
    url = "https://raw.githubusercontent.com/proxyscrape/free-proxy-list/main/proxies/countries/zw/data.txt"
    proxies = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    for line in text.splitlines():
                        if ":" in line:
                            ip, port = line.strip().split(":")[:2]
                            if is_zim_ip(ip):
                                proxies.append({"host": ip, "port": int(port)})
    except Exception as e:
        print(f"Fetch error: {e}")
    return proxies

async def check_tcp(host, port, timeout=3):
    try:
        _, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def scan_host(proxy):
    """Tests the proxy to see if it's alive."""
    host, port = proxy["host"], proxy["port"]
    alive = await check_tcp(host, port)
    return {
        "host": host,
        "port": port,
        "score": 80 if alive else 0,
        "grade": "A" if alive else "F",
        "tunnel_ready": alive,
        "is_zimbabwe": True,
        "status": "working" if alive else "dead"
    }

async def run_bulk_scan():
    """Main function called by the route."""
    proxies = await fetch_public_proxies()
    # If no Zim proxies found in public list, use some test IPs
    if not proxies:
        proxies = [
            {"host": "41.220.16.208", "port": 80},
            {"host": "197.221.240.176", "port": 80}
        ]
    
    tasks = [scan_host(p) for p in proxies]
    results = await asyncio.gather(*tasks)
    
    working_hosts = [r for r in results if r["status"] == "working"]
    return working_hosts
