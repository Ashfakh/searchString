# searchString
A python rest module and libraries which employ DamerauOsa Algo and custom scoring to return strings

# Rules
Prefix - Words having the search string as a prefix is returned.
SubStr - Words having the search string as a sub string is returned
EditDist - Words which falls within certain edit distance is returned

# Scoring
Scoring depends on exact match, prefix length, frequency, Phoenetic match. 

# Algorithm
Implements a version of DamerauOsa algorithm which only considers delete edits, other edits (insert, transpose, replace) are derived from deletes using a meat in the middle technique. 1000x faster than normal spell correction algos
  reference : https://medium.com/@wolfgarbe/1000x-faster-spelling-correction-algorithm-2012-8701fcd87a5f

# Package
Modularised packages which are parametrised, currently considering the dictionary for an edit distance upto two.

# Usage
Libraries:
  Flask
  Jellyfish (Phonetic matching)
  Numpy
  Gunicorn (For deployment)
    
Can deploy in local using Heroku Cli
Or normal terminal usage by running python run.py

# API

Returns search result based on a string upto 25 (parametrised) results
  <host>/search?word=<word>
  
Deployed on:
https://search-string-heroku.herokuapp.com/search?word=yoo
