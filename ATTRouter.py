from requests import Session, head
from bs4 import BeautifulSoup
from hashlib import md5
import logging
from threading import Thread
import sys
from time import sleep

class ATTRouter(Session):
    def __init__(self, access_code, router_internal_ip="192.168.1.254"):
        super().__init__()
        
        self.router_internal_ip = router_internal_ip
        self.base_url = f"http://{router_internal_ip}/cgi-bin/"
        
        logging.basicConfig(level=logging.INFO, format='[%(module)s] %(message)s')
        self.logger = logging.getLogger(__name__)

        self.logger.info(f"ROUTER INTERNAL IP -- {router_internal_ip}")
        self.logger.info(f"PASSWORD -- {access_code}\n")
        
        result = self._login(access_code)
        if b"Access Code Required" not in result.content:
            self.logger.info("Login success.")
        else:
            raise Exception("Could not log in to router.")

    def router_request(self, method, endpoint, data=None):
        return self.request(method, self.base_url + endpoint, data=data)

    def _retrieve_nonce(self, response_content):
        return BeautifulSoup(response_content, features="html.parser").body.find('input', attrs={'name':'nonce'}).attrs['value']
    
    def _login(self, access_code):
        self.logger.info("Retrieving nonce...")
        login_page = self.router_request("GET", "login.ha")
        nonce = self._retrieve_nonce(login_page.content)
        self.logger.info(f"NONCE -- {nonce}\n")

        password_stars = "*" * len(access_code)
        
        self.logger.info("Computing password hash...")
        password_hash = md5((access_code + nonce).encode('utf-8')).hexdigest()
        self.logger.info(f"PASSWORD HASH -- {password_hash}\n")

        login_data = {
            "nonce": nonce,
            "password": password_stars,
            "hashpassword": password_hash
        }

        self.logger.info("Logging in...")
        return self.router_request("POST", "login.ha", data=login_data)

    def _request_reboot(self, nonce):
        try:
            self.router_request("POST", "restart.ha", data={"Restart":"Restart", "nonce":nonce})
        except:
            pass

    def reboot(self):
        animator = RebootingAnimator()
        animator.start()

        restart_page = self.router_request("GET", "restart.ha")
        if b"Access Code Required" in restart_page.content:
            raise Exception("You are not logged in.")
        nonce = self._retrieve_nonce(restart_page.content)
        Thread(target=self._request_reboot, args=(nonce,), daemon=True).start()

        sleep(10)
        while True:
            try:
                head("https://google.com", timeout=5.0)
            except Exception:
                continue
            else:
                break

        animator.stop()

        self.logger.info("Reboot complete!")


class RebootingAnimator(Thread):
    def __init__(self):
        super().__init__()
        self.running = False

    def stop(self):
        self.running = False
        sleep(0.5)
        print("")

    def _icon_generator(self):
        icons = ["-", "\\", "|", "/"]
        index = 0
        while True:
            yield icons[index % len(icons)]
            index += 1

    def run(self):
        self.running = True
        gen = self._icon_generator()
        print("")
        while self.running:
            sys.stdout.write(f"\r[ATTRouter] Rebooting... {next(gen)} ")
            sys.stdout.flush()
            sleep(0.1)
