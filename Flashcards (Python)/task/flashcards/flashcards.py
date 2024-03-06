# Write your code here

import argparse
import io
import json
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--import_from")
parser.add_argument("--export_to")

memory = io.StringIO()


class LoggerOut:
    def __init__(self):
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        memory.write(f"{message}")

    def flush(self):
        pass


class LoggerIn:
    def __init__(self):
        self.terminal = sys.stdin

    def readline(self):
        entry = self.terminal.readline()
        memory.write(f"> {entry}")
        return entry


sys.stdout = LoggerOut()
sys.stdin = LoggerIn()

cmd_add = "add"
cmd_rem = "remove"
cmd_import = "import"
cmd_export = "export"
cmd_ask = "ask"
cmd_exit = "exit"
cmd_log = "log"
cmd_hardest = "hardest card"
cmd_reset = "reset stats"


class Card:
    def __init__(self):
        self.term = ""
        self.definition = ""
        self.mistakes = 0

    def count_mistakes(self):
        self.mistakes += 1

    def to_dict(self):
        return {
            "term": self.term,
            "definition": self.definition,
            "mistakes": self.mistakes
        }

    def from_dict(self, data):
        self.term = data["term"]
        self.definition = data["definition"]
        self.mistakes = data["mistakes"]


cards = {}


def filter_by_definition(definition):
    return list(filter(lambda c: c.definition == definition, cards.values()))


def add_card():
    card = Card()
    print("The card:")
    card.term = enter_term()
    print("The definition of the card:")
    card.definition = enter_definition()
    print(f'The pair ("{card.term}":"{card.definition}") has been added.')
    cards[card.term] = card
    action()


def enter_term():
    term = input()
    if term in cards:
        print(f'The term "{term}" already exists. Try again:')
        return enter_term()
    else:
        return term


def enter_definition():
    definition = input()
    existing = filter_by_definition(definition)
    if len(existing) > 0:
        print(f'The definition "{definition}" already exists. Try again:')
        return enter_definition()
    else:
        return definition


def remove_card():
    print("Which card?")
    term = input()
    if term not in cards:
        print(f'Can\'t remove "{term}": there is no such card."')
    else:
        cards.pop(term)
        print(f'The card has been removed.')
    action()


def import_cards():
    print("File name:")
    filename = input()
    import_cards_from_file(filename)


def import_cards_from_file(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            for card in data:
                new_card = Card()
                new_card.from_dict(card)
                cards[new_card.term] = new_card
            print(f"{len(data)} cards have been loaded.")
    except FileNotFoundError:
        print("File not found.")
    action()


def export_cards():
    print("File name:")
    filename = input()
    export_cards_to_file(filename)
    action()


def export_cards_to_file(filename):
    data = [c.to_dict() for c in cards.values()]
    with open(filename, 'w') as file:
        json.dump(data, file)
    print(f"{len(data)} cards have been saved.")


def ask_cards():
    print("How many times to ask?")
    number = int(input())
    card_list = list(cards.values())
    for i in range(number):
        card = card_list[i % len(card_list)]
        print(f'Print the definition of "{card.term}":')
        answer = input()
        if answer == card.definition:
            print("Correct!")
        else:
            existing = filter_by_definition(answer)
            if len(existing) > 0:
                other = existing[0]
                print(
                    f'Wrong. The right answer is "{card.definition}", but your definition is correct for "{other.term}".')
            else:
                print(f'Wrong. The right answer is "{card.definition}".')
            card.count_mistakes()
    action()


def save_log():
    print("File name:")
    filename = input()
    content = memory.getvalue()
    with open(filename, 'w') as file:
        file.write(content)
    print("The log has been saved.")
    action()


def hardest_cards():
    max_mistakes = max((card.mistakes for card in cards.values()), default=0)
    if max_mistakes <= 0:
        print("There are no cards with errors.")
    else:
        hardest = [f'"{card.term}"' for card in cards.values() if card.mistakes == max_mistakes]
        if len(hardest) > 1:
            print(f"The hardest card are {','.join(hardest)}. You have {max_mistakes} errors answering them.")
        else:
            print(f"The hardest card is {hardest[0]}. You have {max_mistakes} errors answering it.")
    action()


def reset_stats():
    for card in cards.values():
        card.mistakes = 0
    print("Card statistics have been reset.")
    action()


def action():
    print("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")
    cmd = input()
    if cmd == cmd_add:
        add_card()
    elif cmd == cmd_rem:
        remove_card()
    elif cmd == cmd_import:
        import_cards()
    elif cmd == cmd_export:
        export_cards()
    elif cmd == cmd_ask:
        ask_cards()
    elif cmd == cmd_log:
        save_log()
    elif cmd == cmd_hardest:
        hardest_cards()
    elif cmd == cmd_reset:
        reset_stats()
    else:
        if args.export_to:
            export_cards_to_file(args.export_to)
        print("Bye bye!")


args = parser.parse_args()
if args.import_from:
    import_cards_from_file(args.import_from)
else:
    action()
