#lang racket

(define f (open-input-file "output/0a98082deb09707a710455ad72e139da970fae0a482c5db466d7c9e11947956b.rkt"))



(define (verbalize sexp [group? #f])
  (match sexp
    [(? string?) (format "string of ~a next" sexp)]
    [(or (? number?) (? symbol?) (? boolean?) (? keyword?)) (~a sexp)]
    [(? regexp?)
     (let ([rstr (~a sexp)])
     (format "regexp of string of ~a next next"
             (substring rstr 4 (string-length rstr))))]
    [(? pregexp?)
     (let ([rstr (~a sexp)])
     (format "pregexp of string of ~a next next"
             (substring rstr 4 (string-length rstr))))]
    ['() "group of next"]
    [(? list?)
     #:when group?
     (format "group of ~a next" (string-join (map verbalize sexp) " and "))]
    [(cons f (? list? args))
     (format "~a of ~a next"
             (verbalize f)
             (string-join (map verbalize args) " and "))]
    [_ ""]))

(define (verbalize-all file)
  (define sexp (safe-read file))
  (cond
    [(equal? sexp eof) ""]
    [else (format "~a\n~a" (verbalize sexp) (verbalize-all file))]))


(define (safe-read file)
  (with-handlers
      ([exn:fail? (lambda (exn) (begin (read file) (safe-read file)))])
    (read file)))

(verbalize-all f)