"""
Minesweeper game with graphic interface. 
The menu is text-based in the terminal window.  
"""
import json
import math
import random
import time
import sweeperlib as lib

state = {
    "user_field": [],       # this is what player can see on window
    "reveal_field": [],     #this is what the full field look like
    "unopened_safe": [],    #list of unopened safe tile (coordinates)
    "lose": False,
    "win": False,
    "mines": 0,
    "first_click": False,
    "available_tile": []    #list of available tile for generate mines (coordinates)
}

TILE_WIDTH = 40             #size of a tile
PER_PAGE = 10               #number of results per page
FONT_SIZE = 20              #text font size
result = {
    "time": None,           #when the game played
    "duration": 0,          #how long the game last (in seconds)
    "outcomes": None,       #win or lose game
    "mine_left": 0,         #mines not marked by flags if game lose. 0 mine left if game win
    "turn": 0               #number of mouse click use in game
}

def reset():
    """
    Reset game state
    """
    state["user_field"] = []
    state["reveal_field"] = []
    state["unopened_safe"] = []
    state["lose"] = False
    state["win"] = False
    state["mines"] = 0
    state["first_click"] = False
    state["available_tile"] = []
    result["turn"] = 0

def field_value(prompt):
    """
    Value prompt. Only the incorrect value is prompted again.
    """
    while True:
        try:
            number = int(input(prompt))
        except ValueError:
            print("Please input an integer.")
            continue
        if number < 1:
            print("Field value must be bigger or equal to 1")
        else:
            break
    return number

def game_setup(cols, rows):
    """
    This function set up the basic game list: user_field, reveal_field, 
    unopened_safe tiles, available_tile 
    """
    #This function based on course excersise:'Mine time'
    for row in range(rows):
        state["user_field"].append([])
        state["reveal_field"].append([])
        for col in range(cols):
            state["user_field"][-1].append(" ")
            state["reveal_field"][-1].append(0)
    for x in range(cols):
        for y in range(rows):
            state["unopened_safe"].append((x, y))
            state["available_tile"].append((x, y))

def tile_surround(selected_x, selected_y, field):
    """
    Check if the selected position is at the corner, edge or center. 
    Give the coordinates of surrounding tiles. 
    """
    if selected_x == 0:
        range_j = [0, 1]
    elif selected_x == len(field[0]) -1:
        range_j = [-1, 0]
    else:
        range_j = [-1, 0, 1]

    if selected_y == 0:
        range_i = [0, 1]
    elif selected_y == len(field) -1:
        range_i = [-1, 0]
    else:
        range_i = [-1, 0, 1]

    surround_coordinate = []
    for i in range_i:
        for j in range_j:
            surround_coordinate.append((selected_x + j, selected_y + i))
    return surround_coordinate

def place_mines(field_mine, available_tile, mines_number):
    """
    Places N mines to a field in random tiles.
    """
    mine_tile = random.sample(available_tile, mines_number)
    for i in range(mines_number):
        col = mine_tile[i][0]
        row = mine_tile[i][1]
        field_mine[row][col] = "x"
        state["unopened_safe"].remove(mine_tile[i])

def count_mines(mine_field):
    """
    Counts the mines surrounding one tile and assign number of mines surround as tile value.
    If the tile has mine, the function will pass that tile.
    """
    for rows in range(len(mine_field)):
        for cols in range(len(mine_field[0])):
            if mine_field[rows][cols] == "x":
                for (col, row) in tile_surround(cols, rows, mine_field):
                    if mine_field[row][col] == "x":
                        pass
                    else:
                        mine_field[row][col] += 1

def floodfill(start_x, start_y):
    """
    Marks previously unknown connected areas as safe, starting from the given
    x, y coordinates.
    """
    #How to remove duplicate value in a list was taken from
    #https://www.w3schools.com/python/python_howto_remove_duplicates.asp
    floodfill_list = [(start_x, start_y)]
    reveal_field = state["reveal_field"]
    user_field = state["user_field"]
    if reveal_field[start_y][start_x] == "x":
        pass
    else:
        while len(floodfill_list) > 0:
            (fill_x, fill_y) = floodfill_list[0]
            state["unopened_safe"].remove((fill_x, fill_y))
            user_field[fill_y][fill_x] = reveal_field[fill_y][fill_x]
            open_tiles = tile_surround(fill_x, fill_y, user_field)
            for (col, row) in open_tiles:
                if reveal_field[row][col] != 'x' and user_field[row][col] == " ":
                    floodfill_list.append((col, row))
                    floodfill_list = list( dict.fromkeys(floodfill_list))
                elif reveal_field[row][col] == "x":
                    break
            del floodfill_list[0]

def close_game(mouse_x, mouse_y, mouse_button, modifiers):
    """
    Close game window and return to main menu
    """
    lib.close()

def handle_mouse(mouse_x, mouse_y, mouse_button, modifiers):
    """
    This function is called when a mouse button is clicked inside the game window.
    """
    tile_x = mouse_x // TILE_WIDTH
    tile_y = mouse_y // TILE_WIDTH
    mines = state["mines"]
    available_tile = state["available_tile"]
    #What right clicks do
    if mouse_button == lib.MOUSE_RIGHT:
        result["turn"] += 1
        if state["user_field"][tile_y][tile_x] == " ":
            state["user_field"][tile_y][tile_x] = "f"
        elif state["user_field"][tile_y][tile_x] == "f":
            state["user_field"][tile_y][tile_x] = " "
    #What left clicks do
    elif mouse_button == lib.MOUSE_LEFT:
        #Generate mines. The first clicked tile and its 8 surrounding tiles will not contain mine.
        if not state["first_click"]:
            first_tiles = tile_surround(tile_x, tile_y, state["user_field"])
            result["turn"] += 1
            for tiles in first_tiles:
                available_tile.remove(tiles)
            place_mines(state["reveal_field"], available_tile, mines)
            count_mines(state["reveal_field"])
            state["first_click"] = True
        #open tiles
        if state["user_field"][tile_y][tile_x] == " ":
            result["turn"] += 1
            state["user_field"][tile_y][tile_x] = state["reveal_field"][tile_y][tile_x]
            floodfill(tile_x, tile_y)
    #Game lose
    if state["user_field"][tile_y][tile_x] == "x":
        state["lose"] = True
        result["outcomes"] = "Lose"
        for i in range(len(state["reveal_field"])):
            for j in range(len(state["reveal_field"][0])):
                if state["reveal_field"][i][j] == "x" and state["user_field"][i][j] == "f":
                    mines -= 1
                result["mine_left"] = mines
        lib.set_mouse_handler(close_game)
    #Game win
    if len(state["unopened_safe"]) == 0:
        state["win"] = True
        result["mine_left"] = 0
        result["outcomes"] = "Win"
        lib.set_mouse_handler(close_game)

def draw_field():
    """
    A handler function that draws a field represented by a two-dimensional list
    into a game window. This function is called whenever the game engine requests
    a screen update.
    """
    field = state["user_field"]
    lib.clear_window()
    lib.begin_sprite_draw()
    row = len(field)
    col = len(field[0])
    for i in range(row):
        for j in range(col):
            key = field[i][j]
            x_range = int(j*TILE_WIDTH)
            y_range = int(i*TILE_WIDTH)
            lib.prepare_sprite(key, x_range, y_range)
    lib.draw_sprites()
    close_text = "Click again to return to menu."
    middle_position = row*TILE_WIDTH/2
    if state["lose"]:
        lib.draw_background()
        lib.draw_text("Game over.", 0, middle_position+FONT_SIZE,(0, 0, 0, 255),"serif", FONT_SIZE)
        lib.draw_text(close_text, 0, middle_position-FONT_SIZE,(0, 0, 0, 255),"serif", FONT_SIZE)
    elif state["win"]:
        lib.draw_background()
        lib.draw_text("Game win.", 0, middle_position+FONT_SIZE,(0, 0, 0, 255),"serif", FONT_SIZE)
        lib.draw_text(close_text, 0, middle_position-FONT_SIZE,(0, 0, 0, 255),"serif", FONT_SIZE)

def create_window(field):
    """
    Loads the game graphics, creates a game window, and sets a draw handler
    """
    row = len(field)
    col = len(field[0])
    lib.load_sprites('sprites')
    lib.create_window(col * TILE_WIDTH, row * TILE_WIDTH)
    lib.set_draw_handler(draw_field)

def load_result(filename):
    """
    Loads game statistics. If no statistics found, return an empty list
    """
    #This function was based on example on course material 4
    try:
        with open(filename) as source:
            statistics = json.load(source)
    except (IOError, json.JSONDecodeError):
        statistics = []
    return statistics

def save_result(results, filename):
    """
    Save result of the last game into file.
    """
    #This function was based on example on course material 4
    try:
        with open(filename, "w") as target:
            json.dump(results, target)
    except IOError:
        print("Unable to open the target file. Saving failed.")

def start_game():
    """
    Start game and call other neccessary functions. 
    """
    print ("Game setting")
    # check if user input is properly or not.
    while True:
        width = field_value("Input width:")
        height = field_value("Input height:")
        mine = field_value("Input mines:")
        if mine > (width * height):
            print("Too many mines for a small field!")
        else:
            #game start here
            state["mines"] = mine
            game_setup(width, height)
            create_window(state["user_field"])
            result["time"] = time.strftime("%a, %d %b,%y - %H:%M:%S", time.localtime())
            start_time = time.time()
            lib.set_mouse_handler(handle_mouse)
            lib.start()
            if state["lose"] or state["win"]:
                end_time = time.time()
                result["duration"] = int(end_time - start_time)
                statistics = load_result("result.json")
                statistics.append(result)
                save_result(statistics, "result.json")
            else:
                print("Game break!")
            print(" ")
            break

def show(results):
    """
    Break results into pages. Press enter to move to next page 
    """
    #This function was based on example on course material 4
    pages = math.ceil(len(results) / PER_PAGE)
    for i in range(pages):
        start = i * PER_PAGE
        end = (i + 1) * PER_PAGE
        format_page(results[start:end], i)
        if i < pages - 1:
            input("   -- press enter to continue --")

def format_page(lines, page_n):
    """
    Format how results are printeed
    """
    #This function was based on example on course material 4
    print("Statistics:")
    for i, results in enumerate(lines, page_n * PER_PAGE + 1):
        print(
            f"{i:2}. "
            f"{results['outcomes']} on {results['time']} for {results['duration']} seconds"
            f" with {results['turn']} clicks. There are {results['mine_left']} mines left."
        )

def menu():
    """
    Game main menu. User can choose play new game, see game statistics or quit.
    """
    #This function was based on example on course material 4
    print("This is minesweeper game.")
    while True:
        print("Main menu:")
        print("(N)ew game")
        print("(Q)uit")
        print("(S)tatistics")
        choice = input("Make your choice: ").strip().lower()
        if choice == "n":
            reset()
            start_game()
        elif choice == "s":
            results = load_result("result.json")
            if results == []:
                print("No records saved.")
            else:
                show(results)
            print(" ")
        elif choice == "q":
            break
        else:
            print("The chosen feature is not available.")

if __name__ == "__main__":
    menu()
    