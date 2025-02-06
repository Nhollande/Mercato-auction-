import random
import numpy as np
import time
from itertools import combinations


# Étape 1 : Générer les valeurs des objets
def generate_object_values():
    # Divise 20 en trois parties pour créer les sous-ensembles
    def split_into_three(total):
        parts = []
        sum_part = 0
        for _ in range(2):
            sum_part = sum(par for par in parts)
            if sum_part == 20:
                part = 0
                parts.append(part)
            else:
                part = random.randint(0, total - sum_part)
                parts.append(part)
        parts.append(total-sum_part)
        random.shuffle(parts)
        return parts

    first_set = split_into_three(20)
    second_set = split_into_three(20)
    object_values = first_set + second_set
    random.shuffle(object_values)  # Mélanger l'ordre
    return object_values


# Étape 2 : Générer les estimations pour l'ordinateur et Bob
def generate_estimations(object_values):
    v = [round(np.random.normal(loc=p, scale=5)) for p in object_values]  # Estimations pour l'ordinateur
    w = [round(np.random.normal(loc=p, scale=5)) for p in object_values]  # Estimations pour Bob
    for i in range(6):
        v[i] = max(v[i], 0)
        w[i] = max(w[i], 0)
    return v, w


# Étape 3 : Stratégie de Bob
def select_bob_items(mid, v):
    # Recherche des meilleures combinaisons de 3 objets
    best_combination = None
    best_mid_sum = 0

    for combination in combinations(range(6), 3):
        mid_sum = sum(mid[i] for i in combination)
        v_sum = sum(v[i] for i in combination)

        # Vérifie les contraintes : somme des estimations adverses <= 17
        if v_sum <= 17 and mid_sum > best_mid_sum:
            best_mid_sum = mid_sum
            best_combination = combination
        if not best_combination:
            for combination_2 in combinations(range(6), 2):
                mid_sum = sum(mid[i] for i in combination_2)
                v_sum = sum(v[i] for i in combination_2)

                # Vérifie les contraintes : somme des estimations adverses <= 17
                if v_sum <= 18 and mid_sum > best_mid_sum:
                    best_mid_sum = mid_sum
                    best_combination = combination_2
            if not best_combination:
                for combination_1 in combinations(range(6), 1):
                    mid_sum = sum(mid[i] for i in combination_1)
                    v_sum = sum(v[i] for i in combination_1)

                    # Vérifie les contraintes : somme des estimations adverses <= 17
                    if v_sum <= 19 and mid_sum > best_mid_sum:
                        best_mid_sum = mid_sum
                        best_combination = combination_1
                    if not best_combination:
                        best_combination = [0]
    return best_combination


# Étape 4 : Jeu d'enchères
def auction_game():
    start_time = time.time()  # Début de la mesure du temps
    print("Bienvenue dans le jeu d'enchères !")

    # Générer les valeurs des objets
    object_values = generate_object_values()
    print("Les objets ont été générés avec leurs valeurs (secrètes).")

    # Générer les estimations
    v, w = generate_estimations(object_values)
    mid = [(v[i] + w[i]) / 2 for i in range(6)]

    print("Les estimations ont été générées pour l'ordinateur et Bob.")
    print(f"Estimations de l'ordinateur (v) : {v}")
    print(f"Estimations de Bob (w) : {w}")
    print(f"Estimations moyennes (mid) : {mid}")

    # Initialisation des budgets et scores
    computer_budget = 20
    bob_budget = 20
    computer_score = 0
    bob_score = 0

    # Stratégie de Bob
    bob_items = select_bob_items(mid, v)
    print(f"Bob a choisi de cibler les objets {bob_items} en fonction de sa stratégie.")

    # Boucle sur chaque objet
    for i in range(6):
        print(f"\nObjet {i + 1} : enchères ouvertes !")

        # Estimations et enchères
        computer_estimation = v[i]
        bob_estimation = mid[i]

        # Ordinateur enchérit
        computer_bid = min(computer_estimation, computer_budget)

        # Bob enchérit uniquement sur les objets qu'il a ciblés
        if i in bob_items:
            bob_bid = min(v[i]+1, computer_budget+1)
        else:
            bob_bid = 0

        # Résultat de l'enchère
        if bob_bid > computer_bid:
            print(f"Bob remporte l'objet {i + 1} !")
            bob_score += object_values[i]
            bob_budget -= bob_bid
        else:
            print(f"L'ordinateur remporte l'objet {i + 1}.")
            computer_score += object_values[i]
            computer_budget -= computer_bid

        print(f"Budget de Bob : {bob_budget}. Budget de l'ordinateur : {computer_budget}.")

    # Fin du jeu
    end_time = time.time()  # Fin de la mesure du temps
    elapsed_time = end_time - start_time

    print("\nLe jeu est terminé. Révélation des scores !")
    print(f"Valeur totale des objets acquis par Bob : {bob_score}")
    print(f"Valeur totale des objets acquis par l'ordinateur : {computer_score}")
    print(f"Temps total d'exécution : {elapsed_time:.2f} secondes")

    # Déterminer le gagnant
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
    run_games(300)
