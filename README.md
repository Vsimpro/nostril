# Nostril 
Malware that uses the Nostr-protocol as a communication channel.

> [!CAUTION]
> ### WARNING
> The code in this profile has been written for research purposes and ethical use only. Run any code associated only on machines YOU OWN and in Sandboxed environments. <br>

## Inside:

In this repo you will find 2 sets of proof of concept code.

### dropper

Showcases basic interactions with the Nostr network, and a PowerShell- based Implant generator. Pushes a "payload" into the network, and once the PowerShell script is ran, executes the payload with `iex` after fetching it. Supports multiple Nostr-relays.

1. `Main.py` : CLI tool to push the payload into the network, and generate the implant/dropper
2. `Scrape.py` : Script to enumerate Nostr relays to find suitable candidates.

### C2

A botnet proof-of-concept kit, that supports multiple Nostr-relays as a one way communication channel from the operator to the bots.
1. `Connection.py` : library for required functions for interacting with the network
2. `Implant.py`    : The bot that connects to the Nostr network, and executes the commands.
3. `Tui.py`        : The basic user interface, wraps over `connection.py` 


## Documentation

Any further information can be either found as comments on code, or from this blog post: [Nostril](https://vs1m.pro/posts/nostril/)
