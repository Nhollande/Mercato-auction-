from multiprocessing import Pool
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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


def calculate_max_score(mid, v, bob_budget, computer_budget):
    n = len(mid)
    dp = [[[0 for _ in range(computer_budget + 1)] for _ in range(bob_budget + 1)] for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for b_budget in range(bob_budget + 1):
            for c_budget in range(computer_budget + 1):
                if b_budget > min(c_budget, v[i]):
                    option1 = dp[i + 1][b_budget - (min(c_budget, v[i], b_budget) + 1)][c_budget] + mid[i]
                else:
                    option1 = float('-inf')
                if c_budget >= min(c_budget, v[i]):
                    option2 = dp[i + 1][b_budget][c_budget - min(c_budget, v[i])]
                else:
                    option2 = float('-inf')
                dp[i][b_budget][c_budget] = max(option1, option2)
    return dp


def auction_game(bob_budget=100, computer_budget=100, moyenne=100, variance=10):
    object_values = generate_object_values(moyenne)
    v, w = generate_estimations(object_values, variance)
    mid = [(v[i] + w[i]) / 2 for i in range(6)]
    dp = calculate_max_score(mid, v, bob_budget, computer_budget)
    bob_score = 0
    computer_score = 0
    for i in range(6):
        computer_bid = min(v[i], computer_budget, bob_budget)
        bob_decision = dp[i][bob_budget][computer_budget]
        if (bob_decision == dp[i + 1][bob_budget - (min(computer_budget, v[i], bob_budget) + 1)][computer_budget] + mid[i]) and \
                bob_budget >= min(computer_budget, v[i]) + 1:
            bob_score += object_values[i]
            bob_budget -= min(computer_budget, v[i], bob_budget) + 1
        else:
            computer_score += mid[i]
            computer_budget -= min(v[i], computer_budget, bob_budget)
    return bob_score > computer_score


def simulate_single_combination(params):
    n_games, bob_budget, computer_budget, moyenne, variance = params
    bob_wins = 0
    for _ in range(n_games):
        if auction_game(bob_budget=bob_budget, computer_budget=computer_budget, moyenne=moyenne, variance=variance):
            bob_wins += 1
    return (variance, computer_budget, bob_wins)


def generate_results_table_parallel(n_games=20, bob_budget=100, budget_range=(100, 200, 10), variance_range=(0, 50, 5)):
    budgets = range(*budget_range)
    variances = range(*variance_range)
    combinations = [(n_games, bob_budget, budget, 100, variance) for budget in budgets for variance in variances]

    # Utiliser multiprocessing pour paralléliser les simulations
    with Pool() as pool:
        results = pool.map(simulate_single_combination, combinations)

    # Organiser les résultats dans un DataFrame
    results_table = pd.DataFrame(index=variances, columns=budgets)
    for variance, budget, bob_wins in results:
        results_table.at[variance, budget] = bob_wins

    return results_table


if __name__ == "__main__":
    start_time = time.time()
    results_table = generate_results_table_parallel(n_games=1000, bob_budget=100, budget_range=(100, 205, 5),
                                                    variance_range=(0, 34, 1))
    end_time = time.time()

    print(f"\nTemps total d'exécution : {end_time - start_time:.2f} secondes")

    # Afficher le tableau sous forme de heatmap
    plt.figure(figsize=(10, 8))
    plt.title("Nombre de victoires de Bob (Exécution parallèle)")
    plt.xlabel("Budget de l'ordinateur")
    plt.ylabel("Variance")
    plt.imshow(results_table.astype(float), cmap="viridis", aspect="auto", origin="lower",
               extent=[100, 200, 0, 33])
    plt.colorbar(label="Victoires de Bob")
    plt.xticks(range(100, 205, 5))
    plt.yticks(range(0, 34, 1))
    plt.show()

    # Afficher le tableau des résultats
    print("\nTableau des résultats :")
    print(results_table)
