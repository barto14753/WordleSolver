import string
from matplotlib.pyplot import close
from numpy import place
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
from english_words import english_words_lower_set as en_words
import random
from nltk.corpus import words



WEBSITE = "https://www.devangthakkar.com/wordle_archive/?"
ALPHABET = string.ascii_uppercase
WORD_LEN = 5
LEVELS = 6

# COLORS
GOOD_PLACE = 0
GOOD_APPEAR = 1
WRONG_APPEAR = 2
WRONG_WORD = 3

STATS = [0 for i in range(LEVELS+1)]


def open():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver

def enter(driver):
    button = driver.find_element(By.XPATH, "//*[@id=\"root\"]/div/div/div[3]/div[3]/button[1]")
    button.click()

def reset(driver):
    button = driver.find_element(By.XPATH, "//*[@id=\"root\"]/div/div/div[3]/div[3]/button[9]")
    for i in range(WORD_LEN):
        button.click()

def get_element(driver, level, letter):
    index = WORD_LEN*level + letter + 1
    return driver.find_element(By.XPATH, "//*[@id=\"root\"]/div/div/div[2]/div/span[" + str(index) + "]")
    
def recognize_element(element):
    classes = element.get_attribute("class").split(" ")
    if "nm-inset-n-gray" in classes:
        return WRONG_APPEAR
    elif "nm-inset-yellow-500" in classes:
        return GOOD_APPEAR
    elif "nm-inset-n-green" in classes:
        return GOOD_PLACE
    elif "nm-inset-background" in classes:
        return WRONG_WORD
    else:
        return -1


def close_popup(driver):
    button = driver.find_element(By.XPATH, "/html/body/div[4]/div/div/div/button")
    button.click()

def make_move(driver, letter):
    div = driver.find_element(By.XPATH, "//div[text()=\"" + letter + "\"]")
    button = div.find_element(By.XPATH, "./..")
    button.click()

def get_init_words():
    w = []
    for word in words.words():
        if len(word) == WORD_LEN:
            w.append(word.lower())
    return w


def valid_placed(word, placed):
    word = list(word)
    for letter, index in placed:
        if word[index] != letter:
            return False
    return True

def valid_showed(word, showed):
    word = list(word)
    for letter in showed:
        if not letter in word:
            return False
    return True


def valid_used(word, used):
    word = list(word)
    for letter in used:
        if letter in word:
            return False
    return True

def valid_tried(word, tried):
    word = list(word)
    for letter, index in tried:
        if word[index] == letter:
            return False
    return True


def get_words(words, placed, showed, tried, used):
    result = []
    for word in words:
        if valid_placed(word, placed) and valid_showed(word, showed) and valid_used(word, used) and valid_tried(word,tried):
            result.append(word)
    return result

def count_showed(word, showed, used):
    s = 0
    w = list(word)
    for letter in w:
        if letter not in showed and letter not in used and w.count(letter) == 1:
            s += 1
    return s


def get_random_word(words, showed, used):
    w = [(count_showed(word, showed, used), word) for word in words]
    return max(w)[1]

def make_moves(driver, word):
    for letter in word:
        sleep(0.1)
        make_move(driver, letter.upper())
    enter(driver)

def evaluate(driver, word, level, placed, showed, tried, used):
    word = list(word)
    for i in range(WORD_LEN):
        el = get_element(driver, level, i)
        rec = recognize_element(el)
        if rec == WRONG_WORD:
            reset(driver)
            return level, placed, showed, tried, used
        elif rec == GOOD_PLACE and not (word[i], i) in placed:
            placed.append((word[i], i))
            if not word[i] in showed:
                showed.append(word[i])
            if word[i] in used:
                used.remove(word[i])
        elif rec == GOOD_APPEAR and not word[i] in showed:
            showed.append(word[i])
            tried.append((word[i], i))
            if word[i] in used:
                used.remove(word[i])
        elif rec == WRONG_APPEAR and not word[i] in used and not word[i] in showed:
            used.append(word[i])

    return level+1, placed, showed, tried, used


def main(driver, nr):
    level = 0
    words = get_init_words()
    placed = []
    showed = []
    used = []
    tried = []

    words = get_words(words, placed, showed, tried, used)
    
    driver.get(WEBSITE + str(nr))

    if nr == 1:
        close_popup(driver)

    el = get_element(driver, 0, 0)
    print(recognize_element(el))

    while level < LEVELS and len(placed) < WORD_LEN:
        # print("\nLevel " + str(level))
        # print(len(words), placed, showed, used)

        words = get_words(words, placed, showed, tried, used)

        word = get_random_word(words, showed, used)
        words.remove(word)
        # print(word)
        make_moves(driver, word)

        level, placed, showed, tried, used = evaluate(driver, word, level, placed, showed, tried, used)


    if len(placed) == WORD_LEN:
        STATS[level] = STATS[level] + 1


if __name__ == "__main__":
    driver = open()
    for i in range(1,100):
        main(driver, i)
        print(STATS)
