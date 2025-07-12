from django.db import transaction
from .models import Tournament, TournamentParticipant, TournamentMatch


def generate_bracket(tournament: Tournament):
    """
    Generate matches for the given tournament based on its bracket_type.
    Supports: single_elim, double_elim. Extensible for more formats.
    """
    participants = list(TournamentParticipant.objects.filter(tournament=tournament, status='approved'))
    if not participants:
        raise ValueError("No approved participants for this tournament.")
    import random
    random.shuffle(participants)  # Randomly pair teams/participants
    bracket_type = tournament.bracket_type
    with transaction.atomic():
        # Clear existing matches
        TournamentMatch.objects.filter(tournament=tournament).delete()
        if bracket_type == 'single_elim':
            _generate_single_elim(tournament, participants)
        elif bracket_type == 'double_elim':
            _generate_double_elim(tournament, participants)
        else:
            raise NotImplementedError(f"Bracket type '{bracket_type}' not implemented.")

def _generate_single_elim(tournament, participants):
    """Generate a single elimination bracket."""
    import math
    n = len(participants)
    rounds = math.ceil(math.log2(n))
    matches = []
    # Pad with byes if needed
    byes = (2 ** rounds) - n
    seeds = participants + [None] * byes
    # First round
    for i in range(0, len(seeds), 2):
        match = TournamentMatch.objects.create(
            tournament=tournament,
            round_number=1,
            bracket='winner',
            match_type=tournament.match_type,
            player1=seeds[i],
            player2=seeds[i+1] if i+1 < len(seeds) else None,
        )
        matches.append(match)
    # Future rounds (empty, to be filled as winners progress)
    prev_round = matches
    for r in range(2, rounds+1):
        next_round = []
        for i in range(0, len(prev_round), 2):
            match = TournamentMatch.objects.create(
                tournament=tournament,
                round_number=r,
                bracket='winner',
                match_type=tournament.match_type,
            )
            # Link previous matches to this one
            prev_round[i].next_match = match
            prev_round[i].save()
            if i+1 < len(prev_round):
                prev_round[i+1].next_match = match
                prev_round[i+1].save()
            next_round.append(match)
        prev_round = next_round

def _generate_double_elim(tournament, participants):
    # Placeholder: implement double elimination logic here
    # For now, just call single elim as a fallback
    _generate_single_elim(tournament, participants)
    # TODO: Add loser bracket logic
