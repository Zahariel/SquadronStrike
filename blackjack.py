import math
import random
from collections import Counter

suit = [2,3,4,5,6,7,8,9,10,10,10,10,11]
base_deck = suit * 4

def blackjack_eval(cards):
    basic_sum = sum(cards)
    if basic_sum <= 21:
        return basic_sum
    for card in cards:
        if card == 11:
            basic_sum -= 10
            if basic_sum <= 21:
                return basic_sum
    return basic_sum


def deal_hand(threshold):
    deck = list(base_deck)
    random.shuffle(deck)

    hand = []
    while True:
        hand.append(deck.pop())
        score = blackjack_eval(hand)
        if score >= threshold: return score, len(hand)


def trials(threshold, count=100000):
    successes = 0
    cards_per_successful_hand = Counter()
    cards_per_busted_hand = Counter()
    cards_in_successful_hands = Counter()
    cards_in_busted_hands = Counter()
    cards_since_success = 0
    cards_since_bust = 0
    for i in range(count):
        score, cards = deal_hand(threshold)
        cards_since_success += cards
        cards_since_bust += cards
        if score <= 21:
            successes += 1
            cards_per_successful_hand[cards_since_success] += 1
            cards_in_successful_hands[cards] += 1
            cards_since_success = 0
        else:
            cards_in_busted_hands[cards] += 1
            cards_per_busted_hand[cards_since_bust] += 1
            cards_since_bust = 0

    return successes, cards_per_successful_hand, cards_per_busted_hand, cards_in_successful_hands, cards_in_busted_hands

def do_statistics(distribution, limit=30):
    total = sum(distribution.values())
    rescaled = dict(sorted((key, f"{(num * 100) // successes}%") for key, num in distribution.items() if key < limit))
    average = sum(key * num for key, num in distribution.items()) / total
    variance = sum((key - average)**2 * num for key, num in distribution.items()) / total
    stddev = math.sqrt(variance)
    return average, stddev, rescaled


for threshold in [17,18,19,20,21]:
    TRIALS = 100000
    successes, cards_until_success, cards_until_bust, cards_in_successful_hands, cards_in_busted_hands = trials(threshold, TRIALS)

    total_success_cards_avg, total_success_cards_stddev, total_success_cards_raw = do_statistics(cards_until_success)
    total_bust_cards_avg, total_bust_cards_stddev, total_bust_cards_raw = do_statistics(cards_until_bust)
    success_cards_avg, success_cards_stddev, success_cards_raw = do_statistics(cards_in_successful_hands)
    bust_cards_avg, bust_cards_stddev, bust_cards_raw = do_statistics(cards_in_busted_hands)

    print(f"{threshold}: {(successes * 100) // TRIALS}% successful hands")
    print(f"    total cards until success: {total_success_cards_avg:.2f} +/- {total_success_cards_stddev:.2f} (raw: {total_success_cards_raw})")
    print(f"    total cards until bust:    {total_bust_cards_avg:.2f} +/- {total_bust_cards_stddev:.2f} (raw: {total_bust_cards_raw})")
    print(f"    cards in successful hands: {success_cards_avg:.2f} +/- {success_cards_stddev:.2f} (raw: {success_cards_raw})")
    print(f"    cards in busted hands:     {bust_cards_avg:.2f} +/- {bust_cards_stddev:.2f} (raw: {bust_cards_raw})")

