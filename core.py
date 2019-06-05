import os

from suggestutils import SuggestObj, SuggestRule  # import the module


#TODO: Improve scoring
def scoring(suggestion):
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
        return score*-1

def init():

    max_edit_distance_dictionary = 2
    prefix_length = 7

    suggest_obj = SuggestObj(max_edit_distance_dictionary, prefix_length)
    # load corpus
    dictionary_path = os.path.join(os.path.dirname(__file__),
                                   "dict.txt")
    term_index = 0
    count_index = 1
    if not suggest_obj.load_corpus(dictionary_path, term_index, count_index):
        print("Dictionary file not found")
        return
    while True:
        print("Enter lookup word: ")
        #Take input
        input_term = input()
   
        max_edit_distance_lookup = 2

        #SUggestion based on ED rule
        suggestions1 = suggest_obj.lookup(input_term,
                                   max_edit_distance_lookup)
        #SUggestion based on SUBSTR rule
        suggestions2 = suggest_obj.sub_string(input_term)

        #SUggestion based on PREFIX rule
        suggestions3 = suggest_obj.prefix_list(input_term)

        suggestions=suggestions3+suggestions2+suggestions1

        # print(suggestions)


    # display suggestion term, term frequency, and edit distance
        # for suggestion in suggestions:
        # 	print(str(suggestion))
            # print("{}, {}, {}".format(suggestion.term, suggestion.distance,
            #                       suggestion.count))
        suggestion_set = set(suggestions)
        print(len(suggestion_set))
        suggestion_set = list(suggestion_set)
        suggestion_set.sort()

        scored_set = sorted(suggestion_set, key=lambda s: scoring(s))
        # print("suggestion_set is --")
        # for suggestion in suggestion_set:
        #     print(str(suggestion))

        print("scored_set is --")
        for suggestion in scored_set:
            print(str(suggestion) +" -- Score is -- "+ str(scoring(suggestion)))




if __name__ == "__main__":
    init()