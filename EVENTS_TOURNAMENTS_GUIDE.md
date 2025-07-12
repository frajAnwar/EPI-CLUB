# Events & Tournaments Guide

## For Admins

### Creating Events and Tournaments
- Go to the admin dashboard.
- Create a new event (fill in name, description, dates, etc.).
- To add a tournament, use the tournament creation form and select the parent event.
- Select the game for the tournament; team size will be enforced based on the game.

### Managing Team Applications
- View all team applications for a tournament in the admin dashboard.
- Approve teams to allow them to participate.
- Reject teams if they do not meet requirements (rejection is permanent).
- Only team leaders can apply, and the team must have the correct number of members.

### Attendance and Rewards
- After the tournament, view all approved teams and their members.
- Mark which members attended (checkboxes).
- Enter XP/currency values and grant rewards to attended members (confirmation required).
- Each member can only receive a reward once per tournament.

---

## For Team Leaders

- Create a team and add members (team size must match the game for the tournament).
- Go to the event page and apply your team to the tournament (only leaders can apply).
- Check your application status in the event/tournament page.

---

## For Team Members

- Join a team to participate in tournaments.
- Ask your team leader to apply your team to the tournament.
- Check with your leader or in the event page to see if your team is participating.
- After the event, check if you received attendance rewards.

---

## Developer Notes

- All critical flows are covered by backend and frontend tests.
- API endpoints:
  - `POST /events/` (admin only): create event
  - `POST /tournaments/` (admin only): create tournament (with event)
  - `POST /tournaments/{id}/apply/`: team leader applies team
  - `POST /tournaments/{id}/applications/{participant_id}/approve/`: admin approves team
  - `POST /tournaments/{id}/applications/{participant_id}/reward/`: admin grants reward to member
- Run backend tests: `python manage.py test events.tests_event_tournament`
- Run frontend tests: `npm test`

---

For more details, see inline help text in the UI or contact the project maintainer.
