import time, json

from pynostr.key           import PrivateKey
from pynostr.event         import Event
from pynostr.relay_manager import RelayManager
from pynostr.filters       import FiltersList, Filters


def push( user_content : str, relay : str, private_key ) -> tuple:
    """
    Pushes content into a Nostr relay.                                          \n
    
    Parameters:
        user_content (str) : The content we want to push into the relay,        \n
        relay        (str) : The (Nostr) relay we want to push into,            \n
        private_key        : The private key we use for authentication/signing  \n
    
    Returns:
        (tuple)                           \n
        [1]    Public Key of the message  \n
        [2]    OK_Notice, if any          \n
        [3]    General_Notice, if any     \n
    """
    if relay == None or relay == "": 
        raise TypeError( "RELAY must be a non-empty string" )
    
    # Connect to the Relay
    relay_manager = RelayManager()
    relay_manager.add_relay( relay )

    # Prepare an event
    event = Event(
        content = user_content
    )
    
    event.sign(private_key.hex())
    
    # Push the event
    relay_manager.publish_event(event)
    relay_manager.run_sync()

    time.sleep(2)

    # Check everythings ok.
    ok_notice      = None
    general_notice = None 
    while relay_manager.message_pool.has_ok_notices():
        ok_notice = relay_manager.message_pool.get_ok_notice()
        #print(ok_notice)
        
    while relay_manager.message_pool.has_notices():
        general_notice = relay_manager.message_pool.get_notice()
        #print(general_notice)


    return event.pubkey, ok_notice, general_notice


def pull( public_key : str, relay : str ) -> list:
    """
    Pulls content from a Nostr relay with a public key.                       \n
    
    Parameters:
        public_key (str) : The public key of which we want the messages from  \n
        relay      (str) : The relaty we want to fetch messages from          \n
    
    Returns:
        list: the message contents as a dict, if any.
    """
    
    messages : list[ str ] = []
    
    if public_key == None or public_key == "": 
        raise TypeError( "PUBLIC_KEY must be a non-empty string" )
    
    if relay == None or relay == "": 
        raise TypeError( "RELAY must be a non-empty string" )
    
    
    # Subscribe to the relay    
    relay_manager = RelayManager()
    relay_manager.add_relay( relay )

    filters = FiltersList([
        Filters(
            authors = [ public_key ],
            kinds   = [ 1 ],
            limit   = 5
        )
    ])

    # Add a new subscription schema
    sub_id = "arbit_sub"
    relay_manager.add_subscription_on_all_relays(sub_id, filters)
    relay_manager.run_sync()

    time.sleep(2)

    # Get events. 
    while relay_manager.message_pool.has_events():
        raw_msg = relay_manager.message_pool.get_event()
        message = raw_msg.event.to_dict()#[ "content" ]
        messages.append( message )
        
    return messages