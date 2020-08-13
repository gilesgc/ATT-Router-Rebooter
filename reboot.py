from ATTRouter import ATTRouter
from argparse import ArgumentParser

def main():
    args = parse_args()
    ip_address = args.ip_address
    access_code = args.access_code if args.access_code is not None else input("Please enter your router access code: ")
    
    router = ATTRouter(access_code, router_internal_ip=ip_address)

    if not args.skip_confirm:
        input("\nPress enter to reboot.")

    router.reboot()

    if not args.skip_confirm:
        input("\nPress enter to exit.")

def parse_args():
    parser = ArgumentParser(description='Reboot an AT&T router remotely')
    parser.add_argument('--ip-address', '-i', type=str, default="192.168.1.254", help="The router's internal IP address")
    parser.add_argument('--access-code', '-a', type=str, help="The router's access code")
    parser.add_argument('--skip-confirm', '-s', type=int, nargs='?', const=1, default=0, help="Skip the 'Press enter to ...' confirmations")
    return parser.parse_args()
    
if __name__ == "__main__":
    main()
