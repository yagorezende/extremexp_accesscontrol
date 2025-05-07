import asyncio
from ip_city_crosscheck import checkIpCity

async def main():
    ip_examples = [
        "62.103.147.55",
        "195.46.24.91"
    ]

    for ip in ip_examples:
        print(f"Checking IP: {ip} for city: Athens\n")
        result = await checkIpCity(ip, "athens", {"debug": True})
        print("\nResult:", result["ok"])
        print("-" * 40, "\n")

if __name__ == "__main__":
    asyncio.run(main())
