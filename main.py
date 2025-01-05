
import os
from sites import anitaku, AnimeHeaven
import subprocess

# Clear the terminal screen
def cls():
    os.system('clear')

# Let user choose where they want to download from
def chooseSite():
    cls()  # Clear screen
    print('Choose where you want to download from:')
    print('\t0 - GogoAnime')
    print('\t1 - AnimeHeaven.me')

    # Valid choices
    validC = [
            {'choice': '0', 'script': anitaku.GogoAnime()},
            {"choice":"1","script": AnimeHeaven.AnimeHeaven()}
    ]

    while True:  # Loop until a valid choice is made
        choice = input(": ")
        selected = next((site for site in validC if site['choice'] == choice), None)

        if selected:
            selected["script"].main()
            break  # Exit the loop if a valid choice is made
        else:
            print("Invalid choice. Please try again.")

# Example usage
if __name__ == "__main__":
    cls()  # Clear screen at start
    chooseSite()  # Let the user choose a site
