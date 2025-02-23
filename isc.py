from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from src.services.game_stats import GameStats

# Paramètres
PSEUDO = "joselonm"
MOT_DE_PASSE = "HFZ2KWFO7C"
URL = "https://www.isc.ro/"
JOUEUR_RECHERCHE = "20067s"
ADVERSAIRE = "joselonm"
LANGUE_CHOISIE = "Français"
N_LAST = 10  # Number of historical games to examine
NTH_MATCH = 5  # Which match to find (1=oldest match, 2=second oldest, etc.)

# Configuration du navigateur
driver = webdriver.Chrome()
driver.implicitly_wait(10)

def login(driver):
    """Handles the login process, including language selection."""
    try:
        driver.get(URL)
        # Language Selection
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='gwt-DialogBox']//div[@class='Caption' and text()='Select language']"))
        )
        driver.find_element(By.XPATH, "//input[@name='language' and @id='gwt-uid-3']").click()
        driver.find_element(By.XPATH, "//button[contains(@class, 'gwt-Button') and text()='OK']").click()

        # Login
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[1]/input[1]"))
        )
        username_field.send_keys(PSEUDO)
        driver.find_element(By.XPATH, "/html/body/div[5]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/div[1]/input[1]").send_keys(MOT_DE_PASSE)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div[1]/table[1]/tbody[1]/tr[2]/td[2]/div[1]/div[1]/table[1]/tbody[1]/tr[1]/td[3]/button[1]"))
        ).click()
        
        # Wait for welcome message in results div, getting fresh content each time
        WebDriverWait(driver, 30).until(
            lambda d: "Bienvenue à l'Internet Scrabble Club" in d.find_element(
                By.XPATH, "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]"
            ).text
        )
        print("Login successful!")
    except Exception as e:
        print(f"Login failed: {e}")
        raise

def wait_for_command_complete(driver, command):
    """Wait for a command to complete by checking for its appearance in results."""
    try:
        WebDriverWait(driver, 10).until(
            lambda d: command in d.find_element(
                By.XPATH, "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]"
            ).text
        )
          # Small additional wait to ensure response is complete
    except Exception as e:
        print(f"Warning: Timeout waiting for command '{command}' to complete")

def send_examine_commands(driver, joueur, n_last):
    """Send EXAMINE commands from index 0 (newest) to n_last-1 (oldest)."""
    command_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//select[@class='gwt-ListBox']/../following-sibling::td/input[@type='text']"))
    )
    
    for i in range(n_last):
        command = f"EXAMINE HISTORY {joueur} {i}"
        print(f"Sending command: {command}")
        command_input.clear()
        command_input.send_keys(command + Keys.ENTER)
        # Wait for each command to complete before sending the next
        wait_for_command_complete(driver, command)

def filter_interface_text(lines):
    """Remove interface elements and headers from the text."""
    return [
        line for line in lines 
        if not any(skip in line for skip in [
            '____',  # ASCII art header
            'Tentative de connexion',
            'Validation',
            'Bienvenue',
        ])
    ]

def extract_games_from_history(history_text, joueur, adversaire):
    """Extract games between the specified players."""
    all_games = []
    for line in history_text.splitlines():
        if line.startswith("Analyses de partie:"):
            all_games.append(line)
    
    print(f"Found {len(all_games)} games in history. {len(all_games)}")
    matches_found = []
    for i, game in enumerate(all_games):
        if (f"{joueur} vs {adversaire}" in game or
            f"{adversaire} vs {joueur}" in game):
            matches_found.append((game, i))
            print(f"Found match: {game} (EXAMINE index: {i})")
    
    matches_found.reverse()
    
    if matches_found:
        print("\nMatches between players (from oldest to newest):")
        for idx, (match, examine_idx) in enumerate(matches_found, 1):
            print(f"Match {idx}: {match} (EXAMINE index: {examine_idx})")
    
    return matches_found

def analyze_game_history(driver, joueur, adversaire, nth_match):
    """Find the nth match between players (1=oldest match between them)."""
    try:
        results_div = WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]")
        )
        history_text = results_div.text
        print("Extracting matches between players...")
        matches = extract_games_from_history(history_text, joueur, adversaire)
        
        if not matches:
            return None, None, None, history_text
            
        if nth_match <= len(matches):
            game_header, examine_index = matches[nth_match - 1]
            return True, game_header, examine_index, history_text
        else:
            game_header, examine_index = matches[0]
            return False, game_header, examine_index, history_text

    except Exception as e:
        print(f"Error analyzing game history: {e}")
        return None, None, None, None

def examine_specific_game(driver, joueur, match_index):
    """Re-examine a specific game by its index before getting the move list."""
    try:
        command_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//select[@class='gwt-ListBox']/../following-sibling::td/input[@type='text']"))
        )
        command = f"EXAMINE HISTORY {joueur} {match_index}"
        print(f"Re-examining specific game: {command}")
        command_input.clear()
        command_input.send_keys(command + Keys.ENTER)
        # Wait for the examine command to complete
        wait_for_command_complete(driver, command)
        time.sleep(0.5)  # Additional wait to ensure game data is fully loaded
        return True
    except Exception as e:
        print(f"Error examining specific game: {e}")
        return False

def extract_move_list(driver):
    """Get the move list for the current game, filtering out connection messages."""
    try:
        command_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//select[@class='gwt-ListBox']/../following-sibling::td/input[@type='text']"))
        )
        command_input.clear()
        command_input.send_keys("LIST" + Keys.ENTER)
        print("Sent command: LIST")

        # Wait for the LIST command to appear
        wait_for_command_complete(driver, "LIST")
        
        # Get the full results div text for debugging
        results_div = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]")
        print("\n=== Full Results Div Content ===\n" + results_div.text + "\n===========================\n")
        
        # Wait specifically for move list content
        move_list_div = WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]") 
            if "________________________________________" in d.find_element(By.XPATH, "/html/body/div[4]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]").text 
            else None
        )
        
        if not move_list_div:
            return None
            
        full_text = move_list_div.text
        lines = full_text.splitlines()
        move_list_start = -1
        move_list_end = -1
        
        # Find where the actual move list starts (after LIST command)
        for i, line in enumerate(lines):
            if line.strip() == "LIST":
                move_list_start = i + 1
                break
        
        # Find where the move list ends (at the final score line)
        score_pattern = re.compile(r'\d+\s+points\s+\d+\s+points')
        for i in range(move_list_start, len(lines)):
            if score_pattern.search(lines[i]):
                move_list_end = i + 1  # Include the score line
                break
        
        if move_list_start >= 0 and move_list_end >= 0:
            return "\n".join(lines[move_list_start:move_list_end])
        return None

    except Exception as e:
        print(f"Error extracting move list: {e}")
        return None

# --- Main Execution ---
try:
    print("--- START OF SCRIPT ---")
    login(driver)
    
    print(f"Examining last {N_LAST} games of {JOUEUR_RECHERCHE}...")
    send_examine_commands(driver, JOUEUR_RECHERCHE, N_LAST)
    
    nth_match_found, results_line, examine_index, history = analyze_game_history(driver, JOUEUR_RECHERCHE, ADVERSAIRE, NTH_MATCH)
    
    if results_line:  # We found at least one match
        print(f"Found match with {ADVERSAIRE}")
        print(f"Results line: {results_line}")
        
        if examine_specific_game(driver, JOUEUR_RECHERCHE, examine_index):
            move_list = extract_move_list(driver)
        else:
            move_list = None
        
        match_data = {
            "found": True,
            "nth_match_found": nth_match_found,
            "results_line": results_line,
            "move_list": move_list,
            "message": f"{'Requested' if nth_match_found else 'Oldest available'} match found with {ADVERSAIRE}"
        }
        
    else:
        print(f"No matches found with {ADVERSAIRE}")
        match_data = {
            "found": False,
            "nth_match_found": False,
            "results_line": None,
            "move_list": None,
            "message": f"No matches found with {ADVERSAIRE}"
        }
    
    print(match_data)

    # Compute statistics
    game_stats = GameStats()
    if match_data['move_list']:
        game_stats.parse_move_list(match_data['move_list'])
        stats = game_stats.get_statistics()

        print("\n--- Game Statistics ---")
        for player, data in stats.items():
            print(f"Player: {data.get('player_name', player)}")
            print(f"  Rating: {data.get('rating', 'N/A')}")
            print(f"  Total Score: {data.get('total_score', 0)}")
            print(f"  Median Score: {data.get('median_score', 0):.2f}")  # Show median first
            print(f"  Average Score: {data.get('average_score', 0):.2f}")
            print(f"  Highest Score: {data.get('highest_score', 0)}")
            
            print("  Top Scoring Moves:")
            for move in data.get('highest_scoring_moves', []):
                print(f"    - {move}")
                
            bingos = data.get('bingos', {})
            print(f"  Bingos ({bingos.get('count', 0)}):")
            if bingos.get('words'):
                for word in bingos['words']:
                    print(f"    - {word}")
                    
            high_value = data.get('high_value_plays', {})
            print(f"  High Value Plays ({high_value.get('count', 0)}):")
            if high_value.get('details'):
                for play in high_value['details']:
                    print(f"    - {play}")
                    
            special = data.get('special_moves', {})
            print(f"  Special Moves:")
            print(f"    - Passes: {special.get('passes', 0)}")
            print(f"    - Changes: {special.get('changes', 0)}")
            
            multipliers = data.get('multiplier_plays', {})
            print(f"  Multiplier Achievements:")
            print(f"    - Quadruples: {len(multipliers.get('quadruples', []))}")
            print(f"    - Nonuples: {len(multipliers.get('nonuples', []))}")
            print(f"    - Legendres: {len(multipliers.get('legendres', []))}")
    else:
        print("No move list available to compute statistics.")

except Exception as e:
    import traceback
    print(f"GLOBAL ERROR: {traceback.format_exc()}")

finally:
    print("--- END OF SCRIPT ---")
    driver.quit()