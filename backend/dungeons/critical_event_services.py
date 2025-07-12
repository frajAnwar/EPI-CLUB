
import random

class CriticalEventService:
    EVENTS = {
        "fork_in_the_road": {
            "name": "A Fork in the Road",
            "description": "You arrive at a crossroads. The path to the left is short but looks treacherous, teeming with enemies. The path to the right is longer but appears quiet and safe.",
            "choices": [
                {
                    "id": "fork_left",
                    "text": "Take the short, dangerous path.",
                    "effects": [
                        {"type": "FLOOR_MODIFIER", "stat": "EncounterCount", "operation": "ADD", "value": 2, "target": "NEXT_FLOOR_ONLY"},
                        {"type": "PLAYER_MODIFIER", "stat": "Anima", "operation": "SUBTRACT", "value": 1, "target": "IMMEDIATE"}
                    ]
                },
                {
                    "id": "fork_right",
                    "text": "Take the long, safe path.",
                    "effects": [
                        {"type": "FLOOR_MODIFIER", "stat": "EncounterCount", "operation": "SUBTRACT", "value": 1, "target": "NEXT_FLOOR_ONLY"}
                    ]
                }
            ]
        },
        "captured_merchant": {
            "name": "The Captured Merchant",
            "description": "You find a wealthy merchant trapped in a cage. He promises you a rare artifact in exchange for his freedom, but freeing him will surely alert the floor's guardian.",
            "choices": [
                {
                    "id": "free_merchant",
                    "text": "Free the merchant.",
                    "effects": [
                        {"type": "LOOT_MODIFIER", "item_id": "rare_artifact_of_power", "operation": "ADD", "value": 1, "target": "IMMEDIATE"},
                        {"type": "ENCOUNTER_MODIFIER", "stat": "GuardianPower", "operation": "MULTIPLY", "value": 1.5, "target": "NEXT_FLOOR_GUARDIAN_ONLY"}
                    ]
                },
                {
                    "id": "ignore_merchant",
                    "text": "Ignore him and move on.",
                    "effects": []
                }
            ]
        }
    }

    @staticmethod
    def get_random_event():
        """Returns a random critical event, or None."""
        if random.random() < 0.25:  # 25% chance to trigger an event
            event_key = random.choice(list(CriticalEventService.EVENTS.keys()))
            return {"id": event_key, **CriticalEventService.EVENTS[event_key]}
        return None
