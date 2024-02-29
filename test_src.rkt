#lang htdp/isl+


(define all-unique?
  (λ (l)
    (if (empty? l)
        #t
        (and (not (member? (first l) (rest l))) (all-unique? (rest l))))))

;;! Begin Problem 1: Data Design

(define-struct player [name strength endurance])
; A Player is a (make-player String PosInt PosInt)
; The String is the player's name, the first PosInt is their strength score, the second is their \
; endurance score

; A MatchType is one of:
; - "best-of-3", representing a best of 3 match
; - "best-of-5", representing a best of 5 match

(define-struct match [type team1 team2])
; A Match is a (make-match MatchType [ListOf Player] [ListOf Player])
; The type is the type of match, and each list is the list of players on one of the teams

;;! End Problem 1

;;! Begin Problem 2: 

; validate-match: Match -> Boolean
; Returns true if and only if a match is valid blah blah blah...
(define (validate-match m)
  (let ([l1 (length (match-team1 m))]
        [l2 (length (match-team2 m))])
    (and (>= l1 1) (>= l2 1) (<= l1 10) (<= l2 10)
         (all-unique? (map player-name (append (match-team1 m) (match-team2 m)))))))

;;! End Problem 2

;;! Begin Problem 3: 

(define (prop-diff m p) 
  (- (foldr + 0 (map p (match-team1 m)))
     (foldr + 0 (map p (match-team2 m)))))

; strength-diff: Match -> PosInt
; The strength difference between two teams...
(define (strength-diff m) (prop-diff m player-strength))

;;! End Problem 3

;;! Begin Problem 4: 

; A MatchResult is one of:
; - "invalid"
; - "draw"
; - "team-1-wins"
; - "team-2-wins"

(define (play-match m)
  (let ([sd (strength-diff m)]
        [se (endurance-diff m)])
    (cond [(not (validate-match m)) "invalid"]
          [(>= sd 100) "team-1-wins"]
          [(<= sd -100) "team-2-wins"]
          [(> se 0) "team-1-wins"]
          [(< se 0) "team-2-wins"]
          [else "draw"])))

(define (endurance-diff m) (prop-diff m player-endurance))


;;! End Problem 4




