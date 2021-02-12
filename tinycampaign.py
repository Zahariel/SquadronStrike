import functools
import operator
import random
from collections import Counter, defaultdict

DEBUG = False
TRIALS = 10000
def debug(*a, **kw):
    if DEBUG:
        print(*a, **kw)

vp_rewards = [0, 1, 1, 2, 4, 6]
vp_keep = [0, 0, 1, 1, 1, 1]

# full deck
#44/66
# card_values = {
#     0: 44,
#     1: 22,
#     2: 23,
#     3: 11,
#     4: 10,
# }

#40/70
# card_values = {
#     0: 40,
#     1: 23,
#     2: 24,
#     3: 13,
#     4: 10,
# }

#30/80
card_values = {
    0: 30,
    1: 26,
    2: 26,
    3: 16,
    4: 12,
}

choice_weights = {
    0: 70,
    1: 30,
    2: 30,
    3: 30,
    4: 30,
}

# ok, now run the game
class Player:
    def __init__(self):
        self.scenarios = []
        self.war = None

class War:
    def __init__(self):
        self.scenarios = []
        self.players = dict()

def play_campaign(player_count=4, war_threshold=10):
    deck = functools.reduce(operator.add, ([size] * amount for size, amount in card_values.items()))

    random.shuffle(deck)

    thirds = len(deck)//3
    deck.insert(random.randint(2*thirds - 5, 2*thirds), -1)
    deck.insert(random.randint(-5, -1), -1)


    players = [Player() for i in range(player_count)]
    wars = []
    vp_chip_count = 19*player_count + 1

    deck_used = 0
    player = 0
    game_ending = 0
    wars_started = 0
    scenarios_played = Counter()
    turns_by_scenario_count = Counter()

    def draw_chips(amount, keep):
        nonlocal vp_chip_count
        if vp_chip_count == 0: return
        draw = min(random.sample(range(vp_chip_count), amount))
        vp_chip_count -= keep
        if draw == 0:
            debug(f"the end of game chip is drawn!")
            nonlocal game_ending
            game_ending += 1
            vp_chip_count = 0

    def draw_rewards(escalation):
        nonlocal vp_chip_count
        if vp_chip_count == 0: return
        draw_chips(vp_rewards[escalation], vp_keep[escalation])
        loser_escalation = random.choice([escalation-2, escalation-2, escalation-1])
        if loser_escalation > 0:
            draw_chips(vp_rewards[loser_escalation], vp_keep[escalation])

    while deck_used < len(deck) and game_ending < 2:
        # draw phase
        cards_drawn = list(deck[deck_used:deck_used+2])
        deck_used += 2
        if -1 in cards_drawn:
            debug(f"player {player} advances the end of the game!")
            cards_drawn.remove(-1)
            game_ending += 1
        # if the current player is at war, they can't play events or possibly low-tier scenarios
        active_player = players[player]
        if active_player.war:
            escalation = active_player.war.scenarios[0]
            cards_drawn = [card for card in cards_drawn if card >= escalation]
        # if we still have cards to play, play one of them
        if len(cards_drawn) > 0:
            weights = [choice_weights[card] for card in cards_drawn]

            card_played, = random.choices(cards_drawn, weights)
            debug(f"player {player} plays {card_played}")
            if card_played > 0:
                if active_player.war:
                    active_player.war.scenarios.append(card_played)
                    active_player.war.scenarios.sort()
                    debug(f"    into a current war, which is now {active_player.war.scenarios}")
                else:
                    active_player.scenarios.append(card_played)
                    debug(f"    to his own row, which is now {active_player.scenarios}")
                    # check for new wars breaking out
                    for other in range(len(players)):
                        if other == player: continue
                        if players[other].war: continue
                        if len(players[other].scenarios) == 0: continue
                        if sum(active_player.scenarios) + sum(players[other].scenarios) >= war_threshold:
                            war = War()
                            active_player.war = war
                            players[other].war = war
                            war.scenarios = active_player.scenarios + players[other].scenarios
                            war.scenarios.sort()
                            active_player.scenarios = []
                            players[other].scenarios = []
                            war.players = {player: [], other: []}
                            wars.append(war)
                            debug(f"    starting a war with player {other}, containing {war.scenarios}!")
                            wars_started += 1
        else:
            debug(f"player {player} was forced to discard both cards")

        # scenario phase
        # play a scenario in each war
        turns_by_scenario_count[len(wars)] += 1
        for war in wars:
            scenario = war.scenarios[0]
            winner = random.choice(list(war.players.keys()))
            debug(f"players {war.players} play a scenario worth {scenario}, which player {winner} wins")
            scenarios_played[scenario] += 1
            war.players[winner].append(scenario)
            draw_rewards(scenario + (1 if game_ending else 0))
            del war.scenarios[0]
            if sum(war.players[winner]) >= war_threshold:
                debug(f"player {winner} wins the war!")
                # this newest one is guaranteed to be the biggest scenario
                draw_chips(scenario, scenario)
            if len(war.scenarios) == 0:
                # the war is over
                for player in war.players:
                    players[player].war = None
                wars.remove(war)
                debug(f"the war ends for lack of scenarios")

        # pass to the next player
        player += 1
        player %= len(players)
    debug(f"{wars_started} wars started, containing {scenarios_played}")
    return wars_started, scenarios_played, turns_by_scenario_count

count = Counter()
scenarios_played = defaultdict(Counter)
scenarios_per_turn = defaultdict(Counter)
battle_turns = Counter()
for i in range(TRIALS):
    wars, scenarios, per_turn = play_campaign()
    count[wars] += 1
    scenarios_played[wars] += scenarios
    scenarios_per_turn[wars] += per_turn
    battle_turns[wars] += sum(count for num, count in per_turn.items() if num != 0)

for wars, scenarios in sorted(scenarios_played.items()):
    scenarios_per_campaign = {level: f"{number / count[wars]:.2f}" for level, number in sorted(scenarios.items())}
    scenarios_per_war = {level: f"{number / (wars * count[wars]):.2f}" for level, number in sorted(scenarios.items())}
    total_turns = sum(scenarios_per_turn[wars].values())
    spt = {num: f"{(count * 100) // total_turns}%" for num, count in scenarios_per_turn[wars].items()}
    print(f"{wars} wars: {count[wars]} campaigns")
    print(f"    turns with battles: {battle_turns[wars]/count[wars]}")
    print(f"    scenarios per campaign by escalation: {scenarios_per_campaign}")
    print(f"    scenarios per war by escalation: {scenarios_per_war}")
    print(f"    scenarios played per turn: {spt}")

