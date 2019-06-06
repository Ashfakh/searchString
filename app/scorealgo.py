#Scoring Algo

from app.suggestutils import SuggestRule  # import the module
import jellyfish

class ScoreSuggestions(object):

    #Constructor
    def __init__(self, limit):
        self.limit = limit

    def getScoredList(self,suggestions,phrase):
        return sorted(suggestions, key=lambda s: self.scoring(s,phrase))[0:self.limit]

    #TODO: Improve scoring
    def scoring(self,suggestion,phrase):
        score = 0;
        if(suggestion.distance == 0):
            score += 2000;
        if(suggestion.suggest_rule == SuggestRule.PREFIX):
            score += 500;
        if(suggestion.distance == 1):
            score += 300;
        if(suggestion.distance == 2):
            score += 100;
        if(suggestion.distance > 2):
            score += (100 - suggestion.distance*10)
        score += suggestion.count/100000000
        if(suggestion.count < 100000):
            score -= 10000000/suggestion.count
        if(jellyfish.metaphone(suggestion.term) == jellyfish.metaphone(phrase)):
            score += 50
        # print(jellyfish.metaphone(suggestion.term))
        # print(jellyfish.metaphone(phrase))
        # if(suggestion.count>10000000000):
        #     score += 200
        # if(suggestion.count>1000000000 and suggestion.count< 10000000000):
        #     score += 150
        # if(suggestion.count>100000000 and suggestion.count< 1000000000):
        #     score += 100
        # if(suggestion.count>10000000 and suggestion.count< 100000000):
        #     score += 50
        # if(suggestion.count>1000000 and suggestion.count< 10000000):
        #     score += 25
        # if(suggestion.count>100000 and suggestion.count< 1000000):
        #     score += 25
        print(str(suggestion)+ "score is : " + str(score))
        return score*-1