import random

class Gamble():
    @staticmethod
    def GambleWon(win_chance: int) -> bool:
        '''
            Rolls a random number, returns true if the @user won the gambling game.
            :param win_chance: Winning chance (E.g -> 5% = 5)
            :return: True if @user won, False if not
        '''
        roll = random.randint(1, 100)
        return roll <= win_chance

    @staticmethod
    def SimulateSlots(slots: list, n_slots: list):
        selectedSlots = []
        for loop in range(n_slots):
            selectedSlots.append(random.choice(slots))
        return selectedSlots

    @staticmethod
    def slotsOutput(simulated_slots: list):
        results = set(simulated_slots)
        return len(results)