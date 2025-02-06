import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool
import time


def generate_object_values(moyenne):
    def split_into_three(total):
        parts = []
        sum_part = 0
        for _ in range(2):
            if sum_part == total:
                part = 0
                parts.append(part)
            else:
                part = random.randint(0, total - sum_part)
                parts.append(part)
            sum_part += part
        parts.append(total - sum_part)
        random.shuffle(parts)
        return parts

    first_set = split_into_three(moyenne)
    second_set = split_into_three(moyenne)
    object_values = first_set + second_set
    random.shuffle(object_values)
    return object_values


def generate_estimations(object_values, variance=10):
    v = [min(max(0, round(np.random.normal(loc=p, scale=variance))), 99) for p in object_values]
    w = [min(max(0, round(np.random.normal(loc=p, scale=variance))), 99) for p in object_values]
    return v, w


def calculate_dp_bob(values, budget, opponent_budget):
    """
    Calcul du tableau DP pour maximiser le score en fonction des budgets propres et adverses,
    ainsi que de la mise actuelle.
    Inclut la condition finale :
      - Si Bob a un budget strictement supérieur, il remporte le dernier objet.
      - Si l'ordinateur a un budget supérieur ou égal, il remporte le dernier objet.
    """
    n = len(values)
    dp = [[[[0 for _ in range(opponent_budget + 1)] for _ in range(budget + 1)] for _ in range(budget + 1)] for _ in
          range(n + 1)]

    for i in range(n - 1, -1, -1):
        for b in range(budget + 1):
            for o in range(opponent_budget + 1):
                for current_bid in range(min(b, o) + 1):
                    # Option 1: Continuer à surenchérir
                    if b > current_bid:
                        dp[i][b][o][current_bid] = max(
                            dp[i+1][b][o][current_bid + 1],
                            dp[i + 1][b - current_bid][o][0] + values[i]
                        )

    # Ajouter la condition finale pour le dernier objet
    for b in range(budget + 1):
        for o in range(opponent_budget + 1):
            if b > o:  # Bob remporte l'objet
                dp[n - 1][b][o][0] += values[n - 1]
            elif o >= b:  # L'ordinateur remporte l'objet
                dp[n - 1][b][o][0] += 0  # Pas d'ajout au score de Bob

    return dp

def calculate_dp_ordi(values, budget, opponent_budget):
    """
    Calcul du tableau DP pour maximiser le score en fonction des budgets propres et adverses,
    ainsi que de la mise actuelle.
    Inclut la condition finale :
      - Si Bob a un budget strictement supérieur, il remporte le dernier objet.
      - Si l'ordinateur a un budget supérieur ou égal, il remporte le dernier objet.
    """
    n = len(values)
    dp = [[[[0 for _ in range(opponent_budget + 1)] for _ in range(budget + 1)] for _ in range(budget + 1)] for _ in
          range(n + 1)]

    for i in range(n - 1, -1, -1):
        for b in range(budget + 1):
            for o in range(opponent_budget + 1):
                for current_bid in range(min(b, o) + 1):
                    # Option 1: Continuer à surenchérir
                    if b > current_bid:
                        dp[i][b][o][current_bid] = max(
                            dp[i + 1][b][o][current_bid + 1],
                            dp[i + 1][b - current_bid][o][0] + values[i]
                        )

    # Ajouter la condition finale pour le dernier objet
    for b in range(budget + 1):
        for o in range(opponent_budget + 1):
            if b >= o:  # Bob remporte l'objet
                dp[n - 1][b][o][0] += values[n - 1]
            elif o > b:  # L'ordinateur remporte l'objet
                dp[n - 1][b][o][0] += 0  # Pas d'ajout au score de Bob


    return dp


def auction_game_ascending(bob_budget=100, computer_budget=100, moyenne=100, variance=10):
    # Générer les valeurs des objets et les estimations
    object_values = generate_object_values(moyenne)
    v, w = generate_estimations(object_values, variance)
    mid = [(v[i] + w[i]) / 2 for i in range(6)]

    print("Début de la partie.")
    print(f"Valeurs secrètes des objets : {object_values}")
    print(f"Estimations de l'ordinateur (v) : {v}")
    print(f"Estimations de Bob (w) : {w}")
    print(f"Estimations moyennes (mid) : {mid}")

    # Calculer les DP pour l'ordinateur et Bob
    dp_computer = calculate_dp_ordi(v, computer_budget, bob_budget)
    dp_bob = calculate_dp_bob(mid, bob_budget, computer_budget)

    # Initialisation des scores et budgets
    bob_score = 0
    computer_score = 0

    for i in range(6):
        current_bid = 1
        while True:
            # Ordinateur décide s'il surenchérit
            computer_can_bid = (computer_budget >= current_bid and
                                dp_computer[i+1][computer_budget - current_bid][bob_budget][0] + v[i] >
                                dp_computer[i + 1][computer_budget][bob_budget][0])

            # Bob décide s'il surenchérit
            bob_can_bid = (bob_budget >= current_bid and
                           dp_bob[i+1][bob_budget - current_bid][computer_budget][0] + mid[i] >
                           dp_bob[i + 1][bob_budget][computer_budget][0])

            if not bob_can_bid :
                # Bob se couche, l'ordinateur remporte l'objet
                computer_score += object_values[i]
                computer_budget -= current_bid
                print(f"L'ordinateur remporte l'objet {i + 1} avec une enchère de {current_bid}.")
                break
            elif not computer_can_bid:
                # L'ordinateur se couche, Bob remporte l'objet
                bob_score += object_values[i]
                bob_budget -= current_bid
                print(f"Bob remporte l'objet {i + 1} avec une enchère de {current_bid}.")
                break
            else:
                # Les deux surenchérissent
                current_bid += 1

        print(f"Score actuel de Bob : {bob_score}, Budget restant : {bob_budget}")
        print(f"Score actuel de l'ordinateur : {computer_score}, Budget restant : {computer_budget}")

    # Résultats finaux
    print("\nLe jeu est terminé.")
    print(f"Score final de Bob : {bob_score}")
    print(f"Score final de l'ordinateur : {computer_score}")

    if bob_score > computer_score:
        print("Bob a gagné la partie !")
        return True
    else:
        print("L'ordinateur a gagné la partie.")
        return False


if __name__ == "__main__":
    auction_game_ascending(bob_budget=100, computer_budget=100, moyenne=100, variance=10)