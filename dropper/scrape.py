import hashlib

from pynostr.key        import PrivateKey
from src.interact_nodes import pull, push
from src.get_nodes      import main as get_nodes


PRIVATE_KEY = PrivateKey()
PUBLIC_KEY  = PRIVATE_KEY.public_key.hex()


def log( msg ):
    with open( "relays.txt", "a+" ) as file:
        file.write( f"{msg}\n" )


def shahify( string ):
    return hashlib.sha256(string.encode()).hexdigest()


def main():
    relays = get_nodes()[:10]
    for relay in relays:
    
        # Push a SHA of the relay url into the relay
        push( 
            user_content = shahify( relay ),
            relay        = relay,
            private_key  = PRIVATE_KEY,    
        )
        
        # Check the relay -- if the SHA name of the relay is returned,
        # it's open for free to use, 
        # and doesn't mess with the integrity of the message
        msg = pull( 
            relay      = relay,
            public_key = PUBLIC_KEY,
        )
        
        if shahify( relay ) == msg:
            print( f"[>>>] Relay: {relay}, msg: {msg}, with: {PUBLIC_KEY}" )
            log( relay )

if __name__ == "__main__":
    main()

