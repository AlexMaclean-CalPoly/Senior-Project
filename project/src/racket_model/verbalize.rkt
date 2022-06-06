#lang racket


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
     (let ([g? (group-syntax? sexp)])
       (format "~a of ~a next"
               (verbalize f)
               (string-join (map (λ (a) (verbalize a g?)) args) " and ")))]
    [_ ""]))

(define (group-syntax? sexp)
  (match sexp
    [(cons (or 'match 'let 'cond 'struct) _) #t]
    [_ #f]))

(define (verbalize-all file)
  (define sexp (safe-read file))
  (cond
    [(equal? sexp eof) ""]
    [else (format "~a\n~a" (verbalize sexp) (verbalize-all file))]))


(define (safe-read file)
  (with-handlers
      ([exn:fail? (lambda (exn) (begin (read file) (safe-read file)))])
    (read file)))

(define (main)
  (for ([p (directory-list "./output" #:build? #t)])
    (with-handlers
      ([exn:fail? (lambda (exn) (displayln exn))])
    (when (string-suffix? (path->string p) ".rkt")
      (define f (open-input-file p))
      (displayln p)
      (define text (verbalize-all f))
      (define outfile (open-output-file (path-replace-extension p #".txt") #:exists 'replace))
      (display text outfile)
      (close-input-port f)
      (close-output-port outfile)
      ))

    )
  )

(main)
