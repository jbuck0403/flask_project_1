CHANGELOG 1

- make unown error messages load smoothly
- disallow access to login and account creation if logged in
- update welcome screen to unown letters

CHANGELOG 2

- turn pokedex into a class to call from any route
- change userName functionality
- added db interaction error rollbacks
- updated error messages for account page
- change password functionality

CHANGELOG 3

- delete account functionality

CHANGELOG 4

- added ability to pick an account favorite pokemon that displays in the top right
- added "Are you sure?" button after logout button
- cleaned up account management ui/ux

CHANGELOG 5

- added catch functionality - store a team of up to 6 pokemon in the db per user
- added display team page

CHANGELOG 6

- added ability to remove pokemon from team

CHANGELOG 7

- simplified unown error messages into Pokedex.unownErrorMessage method

CHANGELOG 8

- can no longer change your password to the same password
- can no longer change your user name to the same user name

CHANGELOG 9

- added shake animation to buttons
- smoothed choppy sprite loading with fade animations

CHANGELOG 10

- fixed error adding pokemon with no base exp to db
- fixed error where Pokedex was not displaying second type

CHANGELOG 11

- added moves table and search move page

CHANGELOG 12

- added bridge tables to show relationships between pokemon and learnable moves
- added code for when a new pokemon is added to the db to auto-populate moves db with all moves that pokemon can learn
