import os
from app.suggestutils import SuggestObj, SuggestRule  # import the module
from app.scorealgo import ScoreSuggestions
from flask import Flask
from flask import request
import json


app = Flask(__name__)

max_edit_distance_dictionary = 2
prefix_length = 7
suggest_obj = SuggestObj(max_edit_distance_dictionary, prefix_length)
def init():
    # load corpus
    print("loading dictionary")
    dictionary_path = os.path.join(os.path.dirname(__file__),
                                   "dict.txt")
    term_index = 0
    count_index = 1
    if not suggest_obj.load_corpus(dictionary_path, term_index, count_index):
        print("Dictionary file not found")
        return
# init()


@app.route("/search")
def hello():
    if 'word' in request.args:
        return search(suggest_obj,request.args['word']) 
    return "param word has to be present"

def search(suggest_obj,input_word):
    print(suggest_obj)
    max_edit_distance_lookup = 2
    
    #SUggestion based on PREFIX rule
    suggestions1 = suggest_obj.prefix_list(input_word)
    #SUggestion based on SUBSTR rule
    suggestions2 = suggest_obj.sub_string(input_word)
    #SUggestion based on ED rule
    suggestions3 = suggest_obj.lookup(input_word,max_edit_distance_lookup)
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
    return getjson(scored_set)

def getjson(suggestions):
    data = {}
    suggestions_list = list()
    for suggestion in suggestions:
        suggestions_list.append(suggestion.term)
    data['suggestions'] = suggestions_list
    return json.dumps(data)

if __name__ == "__main__":
    print("yaaay")
    init()
    app.run(debug=True)