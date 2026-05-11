import json, requests 
from datetime import datetime, timezone


def encoded_timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%%3A%M%%3A%S.%f")[:-3] + "Z"

#
#   This is a poor way to scrape these. Lets find a better one?
#
def main() -> list:
    """
    Uses 'nostr.watch' to scrape public Nostr relays. 
    
    Returns:
        list : List of Nostr relays as 'str'
    """
    
    links        = {}
    deduplicated = []
    
    # Generate url
    url      = f"https://nostr.watch/seed/operators-0.json?v={ encoded_timestamp() }"
    
    # Get the payload from nostr.watch
    response = requests.get( url ).text
    json_response = json.loads(response)
    
    # Parse through the JSON to find the wss:// links 
    for object in json_response:
        tags = object["tags"]
        
        if tags == []:
            continue
        
        # Any JSON inconsistencies can be skipped.
        try:
            for tag in tags:
                _url = tag[1] 
                # Some tags are not links.
                if  not ("ws"  in _url) and \
                    not ("://" in _url):
                    continue
                
                # Skip TOR
                if ".onion" in _url:
                    continue
                    
                if _url not in links:
                    links[ _url ] = 0
                    continue
                 
        except Exception as e:
            pass
    
    # Turn the links dict into a list
    for link in links:
        deduplicated.append( link )
        
    return deduplicated
