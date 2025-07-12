
import requests
import json
import time
import os

# --- Configuration ---
# Ensure the DJANGO_SETTINGS_MODULE is set if running outside of manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_rpg.settings')

BASE_URL = 'http://localhost:8000'
LOGIN_URL = f'{BASE_URL}/accounts/login/'
STATE_URL = f'{BASE_URL}/api/dungeons/state/'
SEARCH_URL = f'{BASE_URL}/api/dungeons/search/'
START_URL = f'{BASE_URL}/api/dungeons/start/'
PROGRESS_URL_TEMPLATE = f'{BASE_URL}/api/dungeons/progress/{{run_id}}/'
ABANDON_URL = f'{BASE_URL}/api/dungeons/abandon/'
ADMIN_SKIP_TIMER_URL_TEMPLATE = f'{BASE_URL}/api/dungeons/admin/skip_timer/{{run_id}}/'

# --- User Credentials (IMPORTANT: CHANGE THESE TO A VALID, APPROVED, ADMIN TEST USER) ---
EMAIL = 'frajanwer9@gmail.com'
PASSWORD = 'Aser2486'

def run_test():
    """
    Runs a full integration test of the dungeon API flow.
    """
    session = requests.Session()

    # 1. Login to get session and CSRF cookies
    print("--- 1. Logging in... ---")
    
    # First, GET the login page to receive a CSRF token cookie
    try:
        login_page_resp = session.get(LOGIN_URL)
        login_page_resp.raise_for_status()
        if 'csrftoken' not in login_page_resp.cookies:
            print("Error: Could not retrieve CSRF token from login page.")
            return
        csrf_token = login_page_resp.cookies['csrftoken']
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server at {LOGIN_URL}. Is it running?")
        print(e)
        return

    # Second, POST credentials to log in
    login_data = {
        'username': EMAIL,  # Django's AuthenticationForm uses 'username' field
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    headers = {
        'Referer': LOGIN_URL
    }
    
    login_resp = session.post(LOGIN_URL, data=login_data, headers=headers)

    if not (login_resp.ok and 'sessionid' in session.cookies):
        print(f"Login failed for user {EMAIL}. Please check credentials and ensure the user is approved.")
        print(f"Status Code: {login_resp.status_code}")
        print(f"Response: {login_resp.text[:200]}...")
        return

    print(f"Login successful for {EMAIL}.")
    
    # Update headers with the new CSRF token for subsequent POST requests
    headers['X-CSRFToken'] = session.cookies['csrftoken']

    # 2. Check initial state and attempt to reset if necessary
    print("\n--- 2. Checking initial dungeon state... ---")
    state_resp = session.get(STATE_URL, headers=headers)
    state = state_resp.json()
    print(json.dumps(state, indent=2))

    if state.get('status') not in ['idle', 'cooldown']:
        print(f"Player is not idle (current state: {state.get('status')}). Attempting to abandon run...")
        abandon_resp = session.post(ABANDON_URL, headers=headers)
        print(f"Abandon response: {json.dumps(abandon_resp.json(), indent=2)}")
        time.sleep(2)  # Give the server a moment to process
        state_resp = session.get(STATE_URL, headers=headers)
        state = state_resp.json()
        print(f"New state: {json.dumps(state, indent=2)}")

    if state.get('status') == 'cooldown':
        cooldown_time = state.get('cooldown_for', 0)
        print(f"Player is on cooldown for {cooldown_time} seconds. Please wait and try again.")
        return

    if state.get('status') != 'idle':
        print("Could not get player to an idle state. Aborting test.")
        return

    # 3. Start dungeon search
    print("\n--- 3. Starting dungeon search... ---")
    search_resp = session.post(SEARCH_URL, headers=headers)
    print(json.dumps(search_resp.json(), indent=2))

    # 4. Poll state until a dungeon is found
    print("\n--- 4. Polling for dungeon state... ---")
    while True:
        state_resp = session.get(STATE_URL, headers=headers)
        state = state_resp.json()
        
        status = state.get('status')
        print(f"Current state: {status}")

        if status == 'found':
            print("Dungeon found!")
            print(json.dumps(state, indent=2))
            break
        elif status == 'searching':
            wait_time = state.get('search_completes_in', 5)
            print(f"Searching... completes in {wait_time} seconds. Waiting...")
            # Wait a bit longer than the expected time to be safe
            time.sleep(wait_time + 1)
        else:
            print(f"Unexpected state ({status}) while searching. Aborting.")
            print(json.dumps(state, indent=2))
            return

    # 5. Start the dungeon run
    print("\n--- 5. Starting dungeon run... ---")
    start_resp = session.post(START_URL, headers=headers)
    state = start_resp.json()
    print(json.dumps(state, indent=2))

    if state.get('status') != 'on_hold':
        print("Failed to start the run. Aborting.")
        return

    run_id = state.get('run', {}).get('id')
    if not run_id:
        print("Could not get a run ID from the state. Aborting.")
        return

    # 6. Progress through all floors
    while state.get('status') == 'on_hold':
        current_floor = state.get('run', {}).get('current_floor')
        total_floors = state.get('run', {}).get('total_floors')
        print(f"\n--- 6. Progressing Floor {current_floor}/{total_floors} ---")
        
        progress_url = PROGRESS_URL_TEMPLATE.format(run_id=run_id)
        energy_to_spend = 1

        # This simulates the frontend flow: a POST request is sent when the user is 'on_hold'.
        # This should start the timer and change the state to 'in_progress'.
        print(f"Attempting to start floor {current_floor}...")
        progress_resp = session.post(progress_url, headers=headers, json={'energy_spent': energy_to_spend})
        state = progress_resp.json()
        print("Start floor response:")
        print(json.dumps(state, indent=2))

        if state.get('status') != 'in_progress':
            print(f"Failed to start floor timer. Current state is {state.get('status')}. Aborting.")
            break

        # Skip the floor timer using the admin endpoint
        completes_in = state.get('run', {}).get('completes_in', 0)
        if completes_in > 0:
            print(f"Floor is in progress. Skipping timer via admin endpoint...")
            admin_skip_url = ADMIN_SKIP_TIMER_URL_TEMPLATE.format(run_id=run_id)
            skip_resp = session.post(admin_skip_url, headers=headers)

            if not skip_resp.ok:
                print("!!! ERROR: Failed to skip timer. Ensure the test user is an admin. !!!")
                print(json.dumps(skip_resp.json(), indent=2))
                break
            
            print("Timer skipped successfully.")
            # Give the server a moment to process the skip before polling again
            time.sleep(1)

        # After waiting, we need to check the state again. The backend requires a second POST to resolve the floor.
        # This is a point of interest in your API design. The frontend polling would normally hide this,
        # but a script must do it explicitly.
        print(f"Timer finished. Attempting to resolve floor {current_floor}...")
        progress_resp = session.post(progress_url, headers=headers, json={'energy_spent': energy_to_spend})
        state = progress_resp.json()
        print("Resolve floor response:")
        print(json.dumps(state, indent=2))

        battle_report = state.get('run', {}).get('battle_report', {})
        if battle_report:
            result = 'Victory' if battle_report.get('win') else 'Defeat'
            print(f"Battle Report: {result}")
            print(f"  - Win Rate: {battle_report.get('calculated_win_rate', 0):.2%}")
            print(f"  - Your Roll: {battle_report.get('roll', 0):.2f}")
            if battle_report.get('rewards'):
                rewards = battle_report['rewards']
                print("  - Rewards:")
                print(f"    - XP: {rewards.get('xp', 0)}")
                print(f"    - Currency: {rewards.get('currency', 0)}")
                print(f"    - Items: {rewards.get('items', [])}")

    print("\n--- 7. Dungeon run finished. ---")
    print(f"Final Status: {state.get('status')}")
    print(json.dumps(state, indent=2))


if __name__ == "__main__":
    if EMAIL == 'your_test_email@example.com':
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! PLEASE EDIT `test_dungeon_flow.py` AND SET YOUR ADMIN TEST USER'S    !!!")
        print("!!! EMAIL AND PASSWORD BEFORE RUNNING. THE USER MUST BE A STAFF/ADMIN. !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        run_test()
