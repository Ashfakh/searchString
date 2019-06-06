import os

from suggestutils import SuggestObj, SuggestRule  # import the module

from scorealgo import ScoreSuggestions

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

        #SUggestion based on PREFIX rule
        suggestions1 = suggest_obj.prefix_list(input_term)
        #SUggestion based on SUBSTR rule
        suggestions2 = suggest_obj.sub_string(input_term)
        #SUggestion based on ED rule
        suggestions3 = suggest_obj.lookup(input_term,
                                   max_edit_distance_lookup)

        suggestions=suggestions1+suggestions2+suggestions3

        for suggestion in suggestions:
            print("Suggestions are : "+str(suggestion))

        suggestion_set = set(suggestions)
        suggestion_set = list(suggestion_set)
        suggestion_set.sort()
        
        #Get n suggestions
        suggestion_limit=25
        scoreObj = ScoreSuggestions(suggestion_limit)

        scored_set = scoreObj.getScoredList(suggestion_set)

        print("scored_set is --")
        for suggestion in scored_set:
            print(str(suggestion))


if __name__ == "__main__":
    init()