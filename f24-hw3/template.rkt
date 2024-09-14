;; The first three lines of this file were inserted by DrRacket. They record metadata
;; about the language level of this file in a form that our tools can easily process.
#reader(lib "htdp-beginner-reader.ss" "lang")((modname master) (read-case-sensitive #t) (teachpacks ()) (htdp-settings #(#t constructor repeating-decimal #f #t none #f () #f)))

(require 2htdp/image)
;; Purpose: Recipe recipe practice, now with structured data.

;;! Instructions
;;! 1. Do not create, modify or delete any line that begins with ";;!", such
;;!    as these lines. These are markers that we use to segment your file into
;;!    parts to facilitate grading.
;;! 2. You must follow the _design recipe_ for every problem. In particular,
;;!    every function you define must have at least three check-expects (and
;;!    more if needed).
;;! 3. You must follow the Style Guide:
;;!    https://pages.github.khoury.northeastern.edu/2500/2023F/style.html
;;! 4. You must submit working code. In DrRacket, ensure you get on errors
;;!    when you click Run. After you submit on Gradescope, you'll get instant
;;!    feedback on whether or Gradescope can run your code, and your code must
;;!    run on Gradescope to receive credit from the autograder.

;;! Problem 1

;; Consider the following data definition and interpretation.

(define-struct time (hours minutes seconds))
;;! A Time is a (make-time Number Number Number)
;;! Represents the time of day where:
;;! – hours is between 0 and 23
;;! – minutes is between 0 and 59
;;! – seconds is between 0 and 59

;;! Part A
;; Complete the two remaining parts of the data design for Time.
;;!! Please begin your response AFTER this line 

;;! Part B
;; Design a function called tick that adds one second to a Time.
;;!! Please begin your response AFTER this line: 

;;! Part C
;; Design a function called time->image that draws an analog clock face with
;; three hands. (The hour hand is shortest and the minute and second hand should
;; be different.)
;;
;; See the link below for a refresher on how an analog clock works
;; https://en.wikipedia.org/wiki/Clock_face
;; Note: The hour hand does not need to base it's position on the minute hand
;; for this assignment
;;!!

;;! Problem 2

;;! Part A
;; You are a feared restaurant critic whose ratings can make or break the
;; restaurants in Boston. Design a data definition called Review
;; that represents your review of a single restauant. A Review holds the
;; restaurant's name, its cuisine, the dish you ordered, its price, your
;; rating (1--5), and whether or not you saw any rats.
;;!!

;;! Part B
;; Design a function called update-rating that takes a Review and a new rating,
;; and updates the review with the new rating.
;;!!

;;! Part C
;; Design a function called rat-sighting that takes a Review and marks it as
;; a restaurant with rats. It also decreases its rating by 1 star, only if
;; the restaurant was not previously known to have rats.
;;!!

;;! Problem 3

;; You are in the robot part business, making essential parts for robots.
;; The only parts you make are LIDAR sensors, depth cameras, accelerometers,
;; electric motors, and batteries. For every part, you track the kind of
;; part, the price of the item, and the number of items in stock.

;;! Part A
;; Design data definitions called PartType and Stock to represent
;; a single type of item in stock.
;;!!

;;! Part B
;; Design a function called discount that takes an Stock and a discount
;; value, and reduces the price by the given value. However, if the price
;; is lower than $10, do not apply the discount. You can assume that the
;; discount is less than the original price.
;;!!

;;! Part C
;; Design a function called greater-value? that takes two Stocks and
;; produces #true iff the value (quantity * price) of the first is greater than
;; or equal to the value of the second.
;; Note: To receive full credit, you will need to write a helper function that
;; follows the template.
;;!!