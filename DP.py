
import random
import numpy as np
import time
import numpy as np


# Étape 1 : Générer les valeurs des objets
def generate_object_values():
    # Divise 100 en trois parties pour créer les sous-ensembles
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
        parts.append(total-sum_part)
        random.shuffle(parts)
        return parts

    first_set = split_into_three(100)
    second_set = split_into_three(100)
    object_values = first_set + second_set
    random.shuffle(object_values)  # Mélanger l'ordre
    return object_values

# Étape 2 : Générer les estimations pour l'ordinateur et Bob
def generate_estimations(object_values):
    v = [round(np.random.normal(loc=p, scale=10)) for p in object_values]
    w = [round(np.random.normal(loc=p, scale=10)) for p in object_values]
    for i in range(6):
        v[i] = max(v[i], 0)
        w[i] = max(w[i], 0)
    return v, w


# Étape 3 : Calcul du score maximal estimé via programmation dynamique
def calculate_max_score(mid, v, bob_budget, computer_budget):
    n = len(mid)

    # Tableau pour stocker les résultats intermédiaires
    dp = [[[0 for _ in range(computer_budget + 1)] for _ in range(bob_budget + 1)] for _ in range(n + 1)]

    # Remplissage en partant du dernier objet
    for i in range(n - 1, -1, -1):
        for b_budget in range(bob_budget + 1):
            for c_budget in range(computer_budget + 1):
                # Option 1 : Bob achète l'objet, si possible
                if b_budget >= min(c_budget, v[i]) + 1:
                    option1 = dp[i + 1][b_budget - (min(c_budget, v[i]) + 1)][c_budget] + mid[i]
                else:
                    option1 = float('-inf')  # Impossible d'acheter

                # Option 2 : Bob laisse l'objet à l'ordinateur, si possible

                option2 = dp[i + 1][b_budget][c_budget - min(c_budget, v[i])]


                # Prendre le maximum des deux options
                dp[i][b_budget][c_budget] = max(option1, option2)

    return dp


# Étape 4 : Jeu avec stratégie optimale pour Bob
def auction_game():
    # Générer les valeurs des objets et les estimations
    object_values = generate_object_values()
    v, w = generate_estimations(object_values)
    mid = [(v[i] + w[i]) / 2 for i in range(6)]

    bob_budget = 100
    computer_budget = 100

    print("Début de la partie.")
    print(f"Valeurs secrètes des objets (non connues par les joueurs) : {object_values}")
    print(f"Estimations de l'ordinateur (v) : {v}")
    print(f"Estimations de Bob (w) : {w}")
    print(f"Estimations moyennes (mid) : {mid}")

    # Calculer le score maximal pour Bob
    dp = calculate_max_score(mid, v, bob_budget, computer_budget)

    # Lecture des décisions optimales pour chaque enchère
    bob_score = 0
    computer_score = 0
    for i in range(6):
        computer_bid = min(v[i], computer_budget)
        bob_decision = dp[i][bob_budget][computer_budget]

        if bob_decision == dp[i + 1][bob_budget - (min(computer_budget, v[i]) + 1)][computer_budget] + mid[i]:
            print(bob_decision)
            # Bob achète l'objet
            bob_score += object_values[i]
            bob_budget -= min(computer_budget, v[i]) + 1
            print(f"Bob remporte l'objet {i + 1}.")
        else:
            print(bob_decision)
            # L'ordinateur remporte l'objet
            computer_score += object_values[i]
            computer_budget -= min(v[i],computer_budget)
            print(f"L'ordinateur remporte l'objet {i + 1}.")

        print(f"Score estimé de Bob : {bob_score}, Budget restant : {bob_budget}")
        print(f"Score estimé de l'ordinateur : {computer_score}, Budget restant : {computer_budget}")

    # Fin du jeu
    print("\nLe jeu est terminé. Révélation des scores réels !")
    print(f"Valeur totale des objets acquis par Bob : {bob_score}")
    print(f"Valeur totale des objets acquis par l'ordinateur : {computer_score}")

    if bob_score > computer_score:
        print("Félicitations à Bob ! Il a gagné la partie !")
        return True
    elif bob_score <= computer_score:
        print("L'ordinateur a gagné cette fois-ci.")
        return False


def run_games(n_games=300):
    start_time = time.time()
    bob_wins = 0

    for _ in range(n_games):
        if auction_game():
            bob_wins += 1

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nNombre de parties jouées : {n_games}")
    print(f"Nombre de victoires de Bob : {bob_wins}")
    print(f"Temps total d'exécution : {elapsed_time:.2f} secondes")


# Point d'entrée principal
if __name__ == "__main__":
    run_games(500)

