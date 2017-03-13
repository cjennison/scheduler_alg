from __future__ import print_function
import random

# It is reasonable to assume that there are cases when no party is eligible for a
# position on a timeslot. This happens when all adjacent players are
# already on the timeslot.
# Remedies:
#   RANDOM - Pick the player with the lowest hours at random (All Shifts Full, but spot hours)
#   IGNORE - Do nothing and allow the slot to remain open (Extra Shift Positions Possible, most fair shifts)
NONE_ELIGIBLE_CONDITION = "IGNORE"  # "RANDOM"/"IGNORE"
RANDOM_BLOCK_START_REQ = 5  # when to start running RANDOM assignment (only for NONE_ELIGIBLE_CONDITION = RANDOM)

# number of times to run game
ROTATIONS = 50

# If evaluating using timeslot count - set to zero
# If evaluating using pointed priority per timeslot model - set to specified start value
START_PRIORITY = 0

MAX_Y_DIMENSION = 4
MAX_X_DIMENSION = 4

# Arbitrary players (or employees)
PLAYERS = [1, 2, 3]

# optional to allow a zero shift
ALLOW_ZERO_SHIFT = True
FIND_SHIFT_ALTERNATIVE = True

# An arbitrary unit of time
class Timeslot:
    x = None
    y = None
    slots_available = None
    players = None

    def __init__(self, i, j, slots_available):
        self.x = i
        self.y = j
        self.slots_available = slots_available
        self.players = []

    def is_full(self):
        return len(self.players) >= self.slots_available

    def add_player(self, player):
        self.players.append(player)


# the scheduler
class Board:
    board = None
    x_max = None
    y_max = None

    def generate_board(self, rows, cols):
        board = []
        self.x_max = rows
        self.y_max = cols
        for x in range(0, rows):
            column = []
            for y in range(0, cols):
                min_shift = 1
                if ALLOW_ZERO_SHIFT:
                    min_shift = 0
                column.append(Timeslot(x, y, random.randint(min_shift, 3)))
            board.append(column)

        self.board = board

    def get_timeslot(self, x, y):
        if x > self.x_max - 1 or x < 0 or y > self.y_max - 1 or y < 0:
            return None
        return self.board[x][y]

    def get_dimensions(self):
        return {"x": self.x_max, "y": self.y_max}

    def print_board(self):
        for y in range(0, self.y_max):
            for x in range(0, self.x_max):
                slot = self.board[x][y]
                print("[ %d (%s) ]" % (slot.slots_available, slot.players), end="")
            print()


# schedule manager
class Game:
    game_board = None
    players = None
    player_timeslots = {}
    round_number = 0;

    def set_players(self, players):
        self.players = players

    def set_board(self, board):
        self.game_board = board

    def prepare_game(self, random_set, positions):
        # TODO Allow for predetermined schedule

        # set player timeslot keys
        for player in self.players:
            self.player_timeslots[player] = []

        # Set a player in a random Y timeslot for each day
        dimensions = self.game_board.get_dimensions()
        random.shuffle(self.players)
        for x in range(0, dimensions["x"]):
            # choose random y between 0 and dimensions(y)
            rand_y = random.randint(0, dimensions["y"] - 1)
            slot = self.game_board.get_timeslot(x, rand_y)

            # dont allow for 0 slots to be chosen
            while slot.slots_available == 0:
                rand_y = random.randint(0, dimensions["y"] - 1)
                slot = self.game_board.get_timeslot(x, rand_y)

            player = self.players[x % len(self.players)]

            self.player_timeslots[player].append([x, rand_y])

            # rotate around player list for each day number mod the number of players we have (18 mod 4 = 2)
            slot.add_player(player)

            # if predetermined
            ## todo

    def check_win_condition(self):
        # We win if an only if every slot has been filled
        dimensions = self.game_board.get_dimensions()
        for x in range(0, dimensions["x"]):
            for y in range(0, dimensions["y"]):
                slot = self.game_board.get_timeslot(x, y)
                slot_full = slot.is_full()
                if not slot_full:
                    print("Slot not full: %d %d %s" % (x, y, slot.players))
                    return False

        # All slots full - return true
        return True

    def get_next_none_zero_shift(self, x, y, dir):
        slot = self.game_board.get_timeslot(x, y);
        i = 1;
        if dir is "down":
            i *= 1
        if dir is "up":
            i *= -1

        while slot is not None and slot.slots_available is 0:
            slot = self.game_board.get_timeslot(x, y+i);
            if dir is "down":
                i += 1
            if dir is "up":
                i += -1

        return slot;

    def get_eligible_players_for_slot(self, x, y):
        # eligible players are within one move from this timeslot
        up_slot = self.game_board.get_timeslot(x, y - 1)
        right_slot = self.game_board.get_timeslot(x + 1, y)
        down_slot = self.game_board.get_timeslot(x, y + 1)
        left_slot = self.game_board.get_timeslot(x - 1, y)

        if FIND_SHIFT_ALTERNATIVE:
            if up_slot and up_slot.slots_available is 0:
                print("Zero Shift Found . . .", up_slot.x, up_slot.y)
                up_slot = self.get_next_none_zero_shift(x, y-1, "up")
                if up_slot:
                    print("Zero Shift Alternative", up_slot.x, up_slot.y)

            if down_slot and down_slot.slots_available is 0:
                print("Zero Shift Found . . .", down_slot.x, down_slot.y)
                down_slot = self.get_next_none_zero_shift(x, y+1, "down")
                if down_slot:
                    print("Zero Shift Alternative", down_slot.x, down_slot.y)


        # get the slot in question
        main_slot = self.game_board.get_timeslot(x, y)

        player_collection = []

        # collect players
        if up_slot:
            player_collection.append(up_slot.players)
        if right_slot:
            player_collection.append(right_slot.players)
        if down_slot:
            player_collection.append(down_slot.players)
        if left_slot:
            player_collection.append(left_slot.players)

        # flatten and unique-ify the collection of eligible blocks
        player_list = list(set([item for sublist in player_collection for item in sublist]))

        # remove players who already are in this slot
        existing_players = main_slot.players
        for player in existing_players:
            if player in player_list:
                print("Remove Player From Eligible", player)
                player_list.remove(player)

        return player_list

    def get_priority_player(self, eligible_players):

        active_scores = {}

        # count the number of timeslots per player
        for player in eligible_players:
            if not active_scores.has_key(player):
                active_scores[player] = START_PRIORITY
            active_scores[player] = active_scores[player] + len(self.player_timeslots[player])

        # return the player with the lowest score
        lowest = eligible_players[0]
        lowest_score = active_scores[lowest]
        for player in eligible_players:
            if active_scores[player] < lowest_score:
                lowest_score = active_scores[player]
                lowest = player

        return lowest

    def place_player_at_timeslot(self, player, x, y):
        slot = self.game_board.get_timeslot(x, y)
        self.player_timeslots[player].append([x,y])
        slot.add_player(player)

    def get_random_priority(self, x, y):
        # get all players priorities
        active_scores = {}
        for player in self.players:
            if not active_scores.has_key(player):
                active_scores[player] = START_PRIORITY
            active_scores[player] += len(self.player_timeslots[player])

        # find the set of lowest players
        lowest_score = active_scores[PLAYERS[0]]
        low_players = []
        for player in self.players:
            if active_scores[player] < lowest_score:
                lowest_score = active_scores[player]
                low_players = [player]
            if active_scores[player] == lowest_score:
                low_players.append(player)

        low_players = list(set(low_players))
        print("Lowest Scoring Players", low_players)

        # remove players who are in this block already
        slot = self.game_board.get_timeslot(x, y);
        existing_players = slot.players;
        for player in existing_players:
            if player in low_players:
                print("Remove Player From Random Eligible", player)
                low_players.remove(player)

        if len(low_players) == 0:
            return None;

        return random.choice(low_players)

    def run_round(self):
        # rounds are full systems from 0,0 to max_x, max_y
        self.round_number += 1
        dimensions = self.game_board.get_dimensions()

        # go up and down -> left to right
        for y in range(0, dimensions["y"]):
            for x in range(0, dimensions["x"]):
                slot = self.game_board.get_timeslot(x, y)
                if not slot.is_full():
                    # if the slot is not full - place a player
                    elg_players = self.get_eligible_players_for_slot(x, y)

                    # If there are obvious eligible players
                    if len(elg_players) > 0:
                        print("Eligible Players", elg_players)
                        winner = self.get_priority_player(elg_players)
                        self.place_player_at_timeslot(winner, x, y)
                        print("Winner:", winner)
                    else:
                        # otherwise defer to a different method
                        print("No Eligible Players: Running - ", NONE_ELIGIBLE_CONDITION)
                        if NONE_ELIGIBLE_CONDITION is "RANDOM" and self.round_number >= RANDOM_BLOCK_START_REQ:
                            winner = self.get_random_priority(x, y);
                            print("Winner:", winner)
                            if winner:
                                self.place_player_at_timeslot(winner, x, y)

    def get_player_scores(self):
        # get all players priorities
        active_scores = {}
        for player in self.players:
            if not active_scores.has_key(player):
                active_scores[player] = START_PRIORITY
            active_scores[player] += len(self.player_timeslots[player])

        return active_scores

    def play(self):
        print("Running Scheduler - ")
        self.game_board.print_board()

        # Arbitrary number of rounds, run until satisfied
        for x in range(0, ROTATIONS):
            self.run_round()

        print("Board Full?", self.check_win_condition())
        print("Final Score", self.get_player_scores())


def main():
    # Start and generate a board
    game_board = Board()
    game_board.generate_board(MAX_X_DIMENSION, MAX_Y_DIMENSION)

    # Start the game, set the players, and prep
    game = Game()
    game.set_board(game_board)
    game.set_players(PLAYERS)
    game.prepare_game(True, None)

    # execute
    game.play()

    game_board.print_board()

main()
