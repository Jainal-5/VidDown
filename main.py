
import os
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
import subprocess

# Clear the terminal screen
def cls():
    os.system('clear')

# Let user choose where they want to download from
def chooseSite():
    cls()  # Clear screen
    print('Choose where you want to download from:')
    print('\t0 - Anitaku.pe')

    # Valid choices
    validC = [{'choice': '0', 'script': 'sites/anitaku.py'}]

    while True:  # Loop until a valid choice is made
        choice = input(": ")
        selected = next((site for site in validC if site['choice'] == choice), None)

        if selected:
            subprocess.run(['python',selected['script']])
            break  # Exit the loop if a valid choice is made
        else:
            print("Invalid choice. Please try again.")

# Example usage
if __name__ == "__main__":
    cls()  # Clear screen at start
    chooseSite()  # Let the user choose a site
