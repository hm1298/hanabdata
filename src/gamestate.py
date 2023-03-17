
class GameState:

    def __init__(self, data, turn):

        # Game/Seed/Variant info

        self.data = data
        self.deck = data["deck"]
        
        for i, card in enumerate(self.deck):
            card["order"] = i

        self.players = data["players"]
        self.actions = data["actions"]
        self.suit_count = 1 + max([card["suitIndex"] for card in self.deck])
        try: 
            self.variant = data["options"]["variant"]
        except:
            self.variant = "No Variant"
        self.player_count = len(self.players)
        self.hand_size = _get_hand_size(self.data)

        # Turn-dependent game info
        
        self.clue_token_count = 8
        self.turn = 0
        self.discard_pile = []
        self.play_stacks = [[] for _ in range(self.suit_count)]
        self.score = 0
        self.hands = _get_starting_hands(self.deck, self.player_count, self.hand_size)
        self.current_player_index = 0
        self.strike_count = 0
        self.draw_pile_size = len(self.deck) - self.player_count * self.hand_size
        
        # progress to current turn
        for i in range(turn):
            self.implement_action(self.actions[i])
            



    # Helper for plays, bombs, and discards
    def _remove_from_hand(self, player_index, order):
        
        found = False
        for i, card in enumerate(self.hands[player_index]):
            if card["order"] == order:
                found = True
                break

        if not found:
            print(f'could not find card {order}!')
            return self.deck[order]

        remains = self.hands[player_index][0:i] + self.hands[player_index][i + 1:]
        self.hands[player_index] = remains
        return card
        

    def _draw_card(self):
        if self.draw_pile_size == 0:
            return
        card = self.deck[- self.draw_pile_size]
        self.hands[self.current_player_index] = [card] + self.hands[self.current_player_index]
        self.draw_pile_size -= 1

    def _get_type(self, action):
        i = action["type"]
        if i == 3:
            return "rank"
        if i == 2:
            return "color"
        if i == 1: 
            return "discard"
        if i == 4 or i == 5: 
            return "vtk"
        card = self.deck[action["target"]]
        if len(self.play_stacks[card["suitIndex"]]) == card["rank"] - 1:
            return "play"
        return "bomb"

    def _increment_clue_count(self):
        if self.variant[0:12] == "clue starved":
            inc = 0.5
        else: 
            inc = 1
        self.clue_token_count = min(8, self.clue_token_count + inc)


    # function to call when the game progresses

    def implement_action(self, action):
        action_type = self._get_type(action)

        if action_type == "rank":
            self.clue_token_count -= 1

        elif action_type == "color":
            self.clue_token_count -= 1
            
        elif action_type == "discard":
            card = self._remove_from_hand(self.current_player_index, action["target"])
            self._increment_clue_count()
            self.discard_pile.append(card)
            self._draw_card()
            
        elif action_type == "play":
            card = self._remove_from_hand(self.current_player_index, action["target"])
            self.play_stacks[card["suitIndex"]].append(card)
            self._draw_card()
            self.score += 1

            if self.deck[action["target"]]["rank"] == 5:
                self._increment_clue_count()

        elif action_type == "bomb": 
            card = self._remove_from_hand(self.current_player_index, action["target"])
            self.discard_pile.append(card)
            self.strike_count += 1
            self._draw_card()
        if action_type != "vtk":
            self.current_player_index = (self.current_player_index + 1) % self.player_count
            self.turn += 1

    # Replay state at prior turn

    def review_turn(self, turn_count):
        if turn_count >= len(self.actions) or turn_count < 0:
            return False

        return GameState(self.data, turn_count)

    # print

    def __repr__(self):
        hands_repr = []
        for hand in self.hands:
            hand_repr = []
            for card in hand:
                rank = card["rank"]
                suit = "RYGBKM"[card["suitIndex"]]
                hand_repr.append(suit + str(rank))
            hands_repr.append(hand_repr)



        return (
            f"turn: {self.turn}\n" +  
            f"hands: {hands_repr}\n"
        )
    
def _get_hand_size(data):
    player_count = len(data["players"])
    if player_count < 4:
        x = 5
    elif player_count < 6:
        x = 4
    else: 
        x = 3

    if "options" in data:
        if "oneExtraCard" in data["options"]:
            x += 1
        if "oneLessCard" in data["options"]:
            x -= 1
    return x

def _get_starting_hands(deck, player_count, hand_size):
    hands = []
    pile = iter(deck)
    for _ in range(player_count):
        hand = []
        for __ in range(hand_size):
            hand.append(next(pile))
        hands.append([card for card in reversed(hand)])
    return hands