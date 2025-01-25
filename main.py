import re
from colorama import Fore, init
import os
from tqdm import tqdm
import math
from multiprocessing import Pool, cpu_count


init(autoreset=True)

SIZE_WORD = 5


def wordle_dict():

    DICT_NAME = "100000-russian-words.txt"

    def is_valid_word(word: str):
        return len(word) == SIZE_WORD and word.isalpha() and word.islower()

    with open(DICT_NAME, 'r', encoding='utf-8') as file:
        words = file.read().split()


    return [word.replace("ё", "е") for word in words if is_valid_word(word)]


valid_words = wordle_dict()


def is_valid_word_for_configuration(word, conf, assumption_word):
    for i in range(SIZE_WORD):
        if assumption_word[i] == word[i]:
            if conf[i] != 2:
                return False

        elif assumption_word[i] in word:
            if conf[i] != 1:
                return False
        
        elif assumption_word[i] not in word:
            if conf[i] != 0:
                return False
    
    return True

def get_configuration(word, correct_word):
    conf = [0] * SIZE_WORD
    for i in range(SIZE_WORD):
        if word[i] == correct_word[i]:
            conf[i] = 2
        elif word[i] in correct_word[i]:
            conf[i] = 1
        else:
            conf[i] = 0
    return conf

def raiting_word(word: str, possibility_word: list[str]) -> int:
    arr = [0] * 243

    for poss_word in possibility_word:
        conf = get_configuration(word, poss_word)
        arr[sum(conf[i] * 3 ** i for i in range(SIZE_WORD))] += 1

    rat = 0

    for x in arr:
        if x != 0:
            px = x / sum(arr)
            rat += px * math.log2(1 / px + 1)

    return rat, word in possibility_word


def get_next_possibility_word(possibility_word, conf, assumption_word):
    next_possibility_word = []
    for word in possibility_word:
        if is_valid_word_for_configuration(word, conf, assumption_word):
            next_possibility_word.append(word)
    return next_possibility_word


def print_configuration(assumption_word, conf):
    for i in range(SIZE_WORD):
        if conf[i] == 0:
            print(Fore.BLACK + assumption_word[i], end=' ')  
        elif conf[i] == 1:
            print(Fore.YELLOW + assumption_word[i], end=' ')  
        elif conf[i] == 2:
            print(Fore.GREEN + assumption_word[i], end=' ')  
    print()  

def print_history(history):
    print("\nHistory of guesses:")
    print("Guess # | Word    | Configuration")
    for idx, (word, conf) in enumerate(history, 1):
        print(f"{idx:7} | {word}  | ", end="")
        print_configuration(word, conf)

def calculate_ratings_in_parallel(valid_words, possibility_word, pool):
    tasks = [(word, possibility_word) for word in valid_words]
    results = list(tqdm(pool.imap_unordered(worker_raiting_word, tasks), total=len(valid_words), desc="Processing words", ncols=100))
    return results

def worker_raiting_word(args):
    word, possibility_word = args
    return raiting_word(word, possibility_word), word


def best_word():
    with Pool(processes=min(cpu_count(), len(valid_words))) as pool:
        print("\nCalculating best word ratings...")
        rat_word_pair = calculate_ratings_in_parallel(valid_words, valid_words, pool)
        os.system("clear")
    
    return rat_word_pair[0][1]

BEST_WORD = "карта"

def main():
    possibility_word = valid_words
    history = []

    with Pool(processes=min(cpu_count(), len(valid_words))) as pool:
        while True:
            rat_word_pair = []

            print("\nCalculating word ratings...")
            rat_word_pair = calculate_ratings_in_parallel(valid_words, possibility_word, pool)
            
            rat_word_pair = sorted(rat_word_pair, reverse=True)

            os.system("clear")

            print("\nTop 10 possibility words and rated words:")
            print(f"{'Possibility Word'.ljust(25)} {'Rated Word - Rating'.rjust(30)}")
            print("-" * 60)
            
            for i in range(10):
                possibility_display = (possibility_word[i] if i < len(possibility_word) else "").ljust(25)
                rated_display = f"{rat_word_pair[i][1]} - Rating: {rat_word_pair[i][0]}".rjust(30)
                print(f"{possibility_display} {rated_display}")
            
            print(f"\nNumber of possible words left: {len(possibility_word)}")

            print_history(history)

            assumption_word = input(f"\nEnter your guess ({SIZE_WORD}-letter word): ").strip()

            if assumption_word not in valid_words:
                print(f"Invalid word! Please enter a valid {SIZE_WORD}-letter word.")
                continue

            conf_input = input("Enter configuration (e.g., 20100): ").strip()
            if not re.fullmatch(r"[012]{5}", conf_input):
                print(f"Invalid configuration! Please enter a string of {SIZE_WORD} digits (0, 1, 2).")
                continue
            
            conf = list(map(int, conf_input))
            history.append((assumption_word, conf))

            if conf == [2] * SIZE_WORD:
                print("\nCongratulations! You guessed the word correctly!")
                break

            next_possibility_word = []

            for word in possibility_word:
                if is_valid_word_for_configuration(word, conf, assumption_word):
                    next_possibility_word.append(word)

            possibility_word = next_possibility_word

            if not possibility_word:
                print("\nNo possible words left! Check your inputs.")
                break


if __name__ == "__main__":
    main()
