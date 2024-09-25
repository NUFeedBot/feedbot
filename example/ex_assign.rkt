#lang htdp/isl+

;;! Problem 1

;; Your school is going to hold a tug-of-war challenge, but they need to keep
;; track of who is participating. There should be a data definition for a
;; Player, who each have a name (a string), and a strength and endurance score
;; which are positive integers. There are should be a data definition for
;; a Match, which consist of some number of players divided into two teams. Each
;; match must also have a type, either best-of-3 or best-of-5.

;;!! Write your code below:

;;! Problem 2

;; Design a function `validate-match` that returns true if and only if a match
;; is valid. For a valid match, there must be exactly two teams and they must
;; each have at least one but at most ten players. Additionally, no players may
;; be present multiple times (i.e. there can't be two players with the same
;; name).

;;!! Write your code below:


;;! Problem 3

;;! Part A

;; Design a function `strength-diff` that returns the absolute value of the
;; difference in total strength between two teams in a match. The total strength
;; is the sum of the strength scores of all players on a team.

;;!! Write your code below:


;;! Part B

;; Using the following data definition for a match result, design a function
;; `play-match` that returns the appropriate result for a match.

;; A MatchResult is one of:
;; - "invalid"
;; - "draw"
;; - "team-1-wins"
;; - "team-2-wins"

;; The result is determined as follows:
;;
;; - If the game is not valid (as defined in `validate-match`), the result is
;; invalid
;;
;; - If one team's strength score exceeds the other by 100 or more, that team
;; wins
;;
;; - If not, then the team with the highest total endurance score wins
;;
;; - If the stength and endurance scores are exactly the same, the game is a
;; draw

;;!! Write your code below: