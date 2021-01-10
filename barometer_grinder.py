#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import random
from time import sleep
import stem.process
from stem import Signal
from stem.util import term
from stem.control import Controller
from stem.util.system import pid_by_name
import requests
from time import strftime
from fake_useragent import UserAgent
import signal
import simplejson as json
import atexit
import argparse
from fake_useragent import FakeUserAgentError


parser = argparse.ArgumentParser(
    description='Stemmer automatisk på Barometerlisten. Forbinder via Tor '
    'og skifter IP og user-agent for hver stemme. '
    'Denne bot er et Proof of Concept. Forfatteren kan ikke '
    'stilles til ansvar for eventuelt misbrug.')

parser.add_argument(
    "-s",
    "--stemmer",
    help="Antal stemmer der skal afgives (default: 5000)",
    type=int,
    default=5000)

parser.add_argument(
    "-a",
    "--amok",
    help="Fuck at være realistisk. Bare klø på uden pauser."
    "(Bruger stadig Tor og skifter IP)",
    action="store_true")
args = parser.parse_args()


def kill_tor():
    try:
        tor_process.kill()
    except NameError:
        pass


def interrupt_handler(signal, frame):

    printtime()
    print term.format('Afslutter.\n', term.Color.BLUE)
    kill_tor()

    sys.exit(0)


signal.signal(signal.SIGINT, interrupt_handler)
atexit.register(kill_tor)

ua = UserAgent()

SOCKS_PORT = 7000
CONTROL_PORT = random.randint(9000, 9999)

# SOCKS5 proxy for HTTP/HTTPS
proxies = {
    'http': "socks5://127.0.0.1:%s" % SOCKS_PORT,
    'https': "socks5://127.0.0.1:%s" % SOCKS_PORT
}


def printtime():
    print strftime('[%H:%M:%S]'),


def make_headers():
    user_agent = str(ua.random)

    headers = {
        "User-Agent": user_agent,
        "Accept": "*/*",
        "Accept-Language": "en-GB,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Content-Type": "application/json",
        "Referer": "https://www.dr.dk/p3/artikel/barometerlisten/",
        "Cookie": "",
        "Connection": "keep-alive",
    }
    return headers


def welcome():
    print term.format("""
 ▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄       ▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌     ▐░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░▌░▌   ▐░▐░▌▐░█▀▀▀▀▀▀▀▀▀  ▀▀▀▀█░█▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌
▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌▐░▌ ▐░▌▐░▌▐░▌               ▐░▌     ▐░▌          ▐░▌       ▐░▌
▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░▌ ▐░▐░▌ ▐░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌
▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀█░█▀▀ ▐░▌       ▐░▌▐░▌   ▀   ▐░▌▐░█▀▀▀▀▀▀▀▀▀      ▐░▌     ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀ 
▐░▌       ▐░▌▐░▌       ▐░▌▐░▌     ▐░▌  ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌               ▐░▌     ▐░▌          ▐░▌     ▐░▌  
▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░▌      ▐░▌ ▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄      ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌ 
▐░░░░░░░░░░▌ ▐░▌       ▐░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░▌       ▐░▌
 ▀▀▀▀▀▀▀▀▀▀   ▀         ▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀ 
                                                                                                                     
 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄                            
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌      v0.4          
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀ ▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌                 
▐░▌          ▐░▌       ▐░▌     ▐░▌     ▐░▌▐░▌    ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌                           
▐░▌ ▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌     ▐░▌     ▐░▌ ▐░▌   ▐░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌    
▐░▌▐░░░░░░░░▌▐░░░░░░░░░░░▌     ▐░▌     ▐░▌  ▐░▌  ▐░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌         by  
▐░▌ ▀▀▀▀▀▀█░▌▐░█▀▀▀▀█░█▀▀      ▐░▌     ▐░▌   ▐░▌ ▐░▌▐░▌       ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀         Cyber_Charl3s          
▐░▌       ▐░▌▐░▌     ▐░▌       ▐░▌     ▐░▌    ▐░▌▐░▌▐░▌       ▐░▌▐░▌          ▐░▌     ▐░▌     
▐░█▄▄▄▄▄▄▄█░▌▐░▌      ▐░▌  ▄▄▄▄█░█▄▄▄▄ ▐░▌     ▐░▐░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌   
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌      ▐░░▌▐░░░░░░░░░░▌ ▐░░░░░░░░░░░▌▐░▌       ▐░▌ 
 ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀   ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  
                                                                                            
                                                                                            
                                                                                            
                                                                                            
""", term.Color.GREEN,
                      term.Attr.BOLD)

    print term.format("▩"*50, term.Color.GREEN,
                      term.Attr.BOLD),
    print term.format("GØR DIG FUCKING BERØMT!", term.Color.YELLOW,
                      term.Attr.BOLD),
    print term.format("▩"*50, term.Color.GREEN,
                      term.Attr.BOLD),
    print """
    """


welcome()

# Start an instance of Tor. This prints
# Tor's bootstrap information as it starts. Likely will not
# work with another Tor instance running.


def print_bootstrap_lines(line):
    if 'Bootstrapped ' in line:
        print term.format(line, term.Color.BLUE)


print ""
printtime()
print term.format('Starter Tor med SOCKS-port ' + str(SOCKS_PORT) +
                  " og kontrolport " + str(CONTROL_PORT) + ':', term.Attr.BOLD)

tor_process = \
    stem.process.launch_tor_with_config(config={
                                        'SocksPort': str(SOCKS_PORT),
                                        'ControlPort': str(CONTROL_PORT)},
                                        init_msg_handler=print_bootstrap_lines)


def newnym():
    with Controller.from_port(port=CONTROL_PORT) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)


def wait(min, max):
    if not args.amok:
        sleeptime = random.randint(min, max)
        printtime()
        print term.format(
            "Venter tilfældigt antal (%s) sekunder for at virke realistisk...",
            term.Color.BLUE) % (sleeptime)

        while sleeptime > 0:
            print term.format("(%s sekunder tilbage)    ",
                              term.Color.YELLOW) % (sleeptime)
            sleep(1)
            sys.stdout.write("\033[F")  # Cursor up one line
            sleeptime -= 1

        printtime()
        print term.format("Starter igen                 ", term.Color.BLUE)


def change_ip():

    # Get current WAN IP
    printtime()
    print term.format('Finder nuværende aktiv IP adresse.', term.Color.BLUE)
    res = requests.get('http://ipecho.net/plain', proxies=proxies)
    old_ip = res.text.rstrip()
    printtime()
    print term.format('Skifter IP adresse. Nuvaerende IP: %s' % old_ip,
                      term.Color.BLUE)

    # Send newnym signal to Tor
    newnym()

    # Check IP for change every second
    not_changed_count = 0
    while True:
        res = requests.get('http://ipecho.net/plain', proxies=proxies)
        if res.text.rstrip() != old_ip:
            printtime()
            print term.format(
                "IP addresse skiftet. Ny IP: %s" % res.text.rstrip(),
                term.Color.GREEN)
            break
        else:
            printtime()
            print term.format(
                'IP ikke skiftet endnu. Tjekker igen om 1 sekund.',
                term.Color.BLUE)
            sleep(1)
            not_changed_count += 1

        if not_changed_count > 4:
            print term.format(
                'Der sker ikke en skid. Beder Tor om en ny IP igen og venter lidt...',
                term.Color.YELLOW)
            newnym()

            sleeptime = 10
            while sleeptime > 0:
                print term.format("(%s sekunder tilbage)    ",
                                  term.Color.YELLOW) % (sleeptime)
                sleep(1)
                sys.stdout.write("\033[F")  # Cursor up one line
                sleeptime -= 1


def socks_error():
    printtime()
    print term.format('Proxy fejl: %s', term.Color.RED) % (e)

    printtime()
    print term.format('Sender NEWNYM signal til Tor.', term.Color.BLUE)

    printtime()
    print term.format('Prøver igen.', term.Color.BLUE)

    newnym()


def vote():
    print ""
    printtime()
    print term.format(32 * "▩" + " STEMMER " + 33 * "▩", term.Attr.BOLD)

    headers = make_headers()
    url = "https://www.dr.dk/tjenester/radio/radio/ChartList/chartvote"
    # url = "https://httpbin.org/everything" # Debug URL

    printtime()
    print term.format("Bruger user-agent: \"%s\" ", term.Color.BLUE) % (
        headers["User-Agent"][:50] + "...")

    printtime()
    print term.format('Stemme sendt. Venter på svar fra serveren...',
                      term.Color.BLUE)
    req = requests.post(
        url, headers=headers, proxies=proxies, data=json.dumps(vote_post_data))
    if "Registered" not in req.text:
        printtime()
        print term.format('FEJL I SERVERSVAR: %s' % req.text, term.Color.RED,
                          term.Attr.BOLD)
        tor_process.kill()
        sys.exit()


def get_choice():

    print term.format("\nBAROMETERLISTEN " + "▩" * 70 + "\n", term.Color.BLUE,
                      term.Attr.BOLD)

    for choice_number, track in enumerate(chart["Items"]):
        print term.format("\t(" + str(choice_number + 1) + ")\t",
                          term.Color.BLUE),
        print term.format(track["Title"], term.Color.WHITE)

    while True:
        try:
            print term.format("\nVælg det nummer du vil stemme på:",
                              term.Attr.BOLD),
            value = int(raw_input())
        except ValueError:
            print term.format(
                "Fejl! Skriv tallet til venstre for det nummer du vil stemme på.\n",
                term.Color.RED)
            continue

        if value not in range(1, 11):
            print term.format("Vælg et tal mellem 1 og 10!\n", term.Color.RED)
            continue
        else:
            break
    return value


chart_request = requests.get(
    "https://www.dr.dk/mu-online/api/1.4/list/barometerlisten?limit=10",
    proxies=proxies)
chart = json.loads(chart_request.text)

track_choice = get_choice() - 1
title = chart["Items"][track_choice]["Title"].encode("utf-8")
clipid = chart["Items"][track_choice]["Urn"]

vote_post_data = {"chartId": "barometerlisten", "clipId": clipid}

for i in range(1, args.stemmer + 1):
    try:
        vote()

        printtime()
        print term.format("Stemt på \"%s\""
                          " %i gang%s siden start." % (title, i,
                                                       "e" [i == 1:]),
                          term.Color.GREEN, term.Attr.BOLD)
        if i == args.stemmer:
            sys.exit()

        wait(10, 500)
    except requests.ConnectionError as e:
        error = e
        socks_error()

    try:
        change_ip()
    except requests.ConnectionError as e:
        error = e
        socks_error()

tor_process.kill()  # stops tor
