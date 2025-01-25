import random
from multiprocessing import Pool, cpu_count
from main import valid_words, raiting_word, SIZE_WORD, get_next_possibility_word, BEST_WORD
from collections import Counter
import sys
import os


class Wordle:
    def __init__(self):
        self.word: str = random.choice(valid_words)
    
    def get_configuration(self, assumption_word: str) -> list[int]:
        assert(assumption_word in valid_words)

        res = []
        for i in range(SIZE_WORD):
            if assumption_word[i] == self.word[i]:
                res.append(2)
            elif assumption_word[i] in self.word:
                res.append(1)
            else:
                res.append(0)

        return res


def simulate_single_game(_):
    wordle = Wordle()
    possibility_word = valid_words
    attempts = 0  # Счетчик ходов

    while True:

        if attempts != 0:
            rat_word_pair = []
            for word in valid_words:
                rating = raiting_word(word, possibility_word)
                rat_word_pair.append((rating, word))

            rat_word_pair = sorted(rat_word_pair, reverse=True)

            assumption_word = rat_word_pair[0][1]
        else:
            assumption_word = BEST_WORD
        
        conf = wordle.get_configuration(assumption_word)

        attempts += 1

        if conf == [2] * SIZE_WORD:
            return attempts

        next_possibility_word = get_next_possibility_word(possibility_word, conf, assumption_word)
        possibility_word = next_possibility_word


def simulate_games_parallel(num_games: int = 100):
    num_workers = min(cpu_count(), num_games)
    print(f"Using {num_workers} parallel workers.")

    attempts_list = []

    with Pool(processes=num_workers) as pool:
        for idx, attempts in enumerate(pool.imap_unordered(simulate_single_game, range(num_games)), start=1):
            attempts_list.append(attempts)

            avg_attempts = sum(attempts_list) / len(attempts_list)
            os.system("clear")
            print(f"\nProgress: {idx}/{num_games} games completed.")
            print(f"Average attempts so far: {avg_attempts:.2f}")
            plot_attempts_distribution(attempts_list)

    os.system("clear")
    print(f"\nSimulated {num_games} games.")
    print(f"Final average attempts to guess: {sum(attempts_list) / len(attempts_list):.2f}")
    plot_attempts_distribution(attempts_list)



def plot_attempts_distribution(attempts_list):
    counter = Counter(attempts_list)
    total_attempts = len(attempts_list)
    
    distribution = {key: value / total_attempts for key, value in sorted(counter.items())}
    
    print("\nAttempts Distribution:")
    max_bar_length = 50
    for attempt, proportion in distribution.items():
        bar_length = int(proportion * max_bar_length)
        bar = "#" * bar_length
        print(f"{attempt:>2} | {bar} ({proportion:.2%})")



if __name__ == "__main__":
    _, num_simulations = sys.argv
    num_simulations = int(num_simulations)
    simulate_games_parallel(num_simulations)
