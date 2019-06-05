from collections import defaultdict
from enum import Enum
import os.path
import re

from distancealgo import EditDistance

class SuggestRule(Enum):
    EDITDIST = 0  #Edit distance rule
    PREFIX = 1  #Prefix rule
    SUBSTR = 2  #Sub string rule


class SuggestObj(object):
    """Symmetric Delete spelling correction algorithm
    **Attributes**:
    * _words: Dictionary of unique correct spelling words, and the\
        frequency count for each word.
        below the count threshold for being considered correct spellings.
    * _deletes: Dictionary that contains a mapping of lists of\
        suggested correction words to the hashCodes of the original\
        words and the deletes derived from them. Collisions of\
        hashCodes is tolerated, because suggestions are ultimately\
        verified via an edit distance function. A list of suggestions\
        might have a single suggestion, or multiple suggestions.
            checking
    """

    #Constructor
    def __init__(self, max_dictionary_edit_distance=2, prefix_length=7):
        if max_dictionary_edit_distance < 0:
            raise ValueError("max_dictionary_edit_distance cannot be "
                             "negative")
        if (prefix_length < 1
                or prefix_length <= max_dictionary_edit_distance):
            raise ValueError("prefix_length cannot be less than 1 or "
                             "smaller than max_dictionary_edit_distance")

        self.words = dict()
        self.deletes_dict = defaultdict(list)
        self.max_dictionary_edit_distance = max_dictionary_edit_distance
        self.prefix_length = prefix_length
        self.max_word_length = 0

    #Add entry to word dict
    def create_dictionary_entry(self, key, count):
        #Dont do anything if count less than 0
        if count <= 0:
            return False
          
        self.words[key] = count

        if len(key) > self.max_word_length:
            self.max_word_length = len(key)

        # create deletes
        edits = self.edits_prefix(key)
        for delete in edits:
            self.deletes_dict[delete].append(key)
        return True
    
    #Load the corpus from a givn path
    def load_corpus(self, corpus, term_index, count_index,
                        encoding=None):
        if not os.path.exists(corpus):
            return False
        with open(corpus, "r", encoding=encoding) as infile:
            for line in infile:
                line_parts = line.rstrip().split("\t")
                if len(line_parts) >= 2:
                    key = line_parts[term_index]
                    #Assuming all counts are int, will throw exception other wise. Handle?
                    count = int(line_parts[count_index])
                    if count is not None:
                        self.create_dictionary_entry(key, count)
        return True

    def prefix_list(self,prefix):
        suggestions = list()
        prefix_words = list()
        for word in self.words.keys():
            if word.startswith(prefix):
                prefix_words.append(word)
            if len(prefix_words) > 25:
                break
        for word in prefix_words:
            suggestions.append(SuggestItem(word, len(word)-len(prefix),
                                         self.words[word],SuggestRule.PREFIX))

        # if len(suggestions) > 1:
        #     suggestions.sort()
        return suggestions[0:25]

    def sub_string(self,sub_str):
        suggestions = list()
        sub_str_words = list()
        for word in self.words.keys():
            if sub_str in word[1:len(word)]:
                sub_str_words.append(word)
            if len(sub_str_words) > 25:
                break
        for word in sub_str_words:
            suggestions.append(SuggestItem(word, len(word)-len(sub_str),
                                         self.words[word],SuggestRule.SUBSTR))

        # if len(suggestions) > 1:
        #     suggestions.sort()
        return suggestions[0:25]
    
    #Lokkup function for the phrase from dictionary with given edit dist
    def lookup(self, phrase, max_edit_distance=None):
        if max_edit_distance is None:
            max_edit_distance = self.max_dictionary_edit_distance
        if max_edit_distance > self.max_dictionary_edit_distance:
            raise ValueError("Distance too large")
        suggestions = list()
        phrase_len = len(phrase)

        #Exit function
        def exit_now():
            return suggestions

        #Exit when word is too big
        if phrase_len - max_edit_distance > self.max_word_length:
            return exit_now()

        #Exact match with ED 0
        suggestion_count = 0
        if phrase in self.words:
            suggestion_count = self.words[phrase]
            suggestions.append(SuggestItem(phrase, 0, suggestion_count,SuggestRule.EDITDIST))
        
        #Exit after exact match
        if max_edit_distance == 0:
            return exit_now()

        considered_deletes = set()
        considered_suggestions = set()
        
        #Already chacked for exact match
        considered_suggestions.add(phrase)

        max_edit_distance_2 = max_edit_distance
        candidate_pointer = 0
        candidates = list()

        # add original prefix
        phrase_prefix_len = phrase_len
        if phrase_prefix_len > self.prefix_length:
            phrase_prefix_len = self.prefix_length
            candidates.append(phrase[: phrase_prefix_len])
        else:
            candidates.append(phrase)
        distance_comparer = EditDistance() #DamerauOsa algo
        while candidate_pointer < len(candidates):
            candidate = candidates[candidate_pointer]
            # print(candidate)
            candidate_pointer += 1
            candidate_len = len(candidate)
            len_diff = phrase_prefix_len - candidate_len

            #Exit loop, distance has gone over edit distance
            if len_diff > max_edit_distance_2:
                continue

            if candidate in self.deletes_dict:
                dict_suggestions = self.deletes_dict[candidate]
                # print("dict suggestions for {} : --- {} ".format(candidate, dict_suggestions))
                for suggestion in dict_suggestions:
                    #Already added in exact match
                    if suggestion == phrase:
                        continue
                    suggestion_len = len(suggestion)
                   
                    #Edit distance should be less than max, it should not be for same delete string, 
                    #is in suggestion not smaller than considering word,
                    #suggestion and considering word should not be same. the last two happens cause of hash collision
                    if (abs(suggestion_len - phrase_len) > max_edit_distance_2
                            or suggestion_len < candidate_len or (suggestion_len == candidate_len and suggestion != candidate)):
                        continue
                    suggestion_prefix_len = min(suggestion_len,
                                                self.prefix_length)
                    if (suggestion_prefix_len > phrase_prefix_len
                            and suggestion_prefix_len - candidate_len > max_edit_distance_2):
                        continue

                    #Idea of symspell algo, meet in the middle to calculate truw edit distance by using only delete edits
                    distance = 0
                    min_distance = 0
                    if candidate_len == 0:
                        #suggestions with no common chars. only the ones less that max_edit_dist
                        distance = max(phrase_len, suggestion_len)
                        if (distance > max_edit_distance_2
                                or suggestion in considered_suggestions):
                            continue
                    elif suggestion_len == 1:
                        distance = (phrase_len
                                    if phrase.index(suggestion[0]) < 0
                                    else phrase_len - 1)
                        if (distance > max_edit_distance_2
                                or suggestion in considered_suggestions):
                            continue
                    # number of edits in prefix ==maxediddistance AND
                    # no identical suffix, then
                    # editdistance>max_edit_distance and no need for
                    # Levenshtein calculation
                    # (phraseLen >= prefixLength) &&
                    # (suggestionLen >= prefixLength)
                    else:
                        # handles the shortcircuit of min_distance
                        # assignment when first boolean expression
                        # evaluates to False
                        if self.prefix_length - max_edit_distance == candidate_len:
                            min_distance = (min(phrase_len, suggestion_len) -
                                            self.prefix_length)
                        else:
                            min_distance = 0
                        # pylint: disable=C0301,R0916
                        if (self.prefix_length - max_edit_distance == candidate_len
                                and (min_distance > 1
                                     and phrase[phrase_len + 1 - min_distance :] != suggestion[suggestion_len + 1 - min_distance :])
                                or (min_distance > 0
                                    and phrase[phrase_len - min_distance] != suggestion[suggestion_len - min_distance]
                                    and (phrase[phrase_len - min_distance - 1] != suggestion[suggestion_len - min_distance]
                                         or phrase[phrase_len - min_distance] != suggestion[suggestion_len - min_distance - 1]))):
                            continue
                        else:
                            considered_suggestions.add(suggestion)
                            distance = distance_comparer.compare(
                                phrase, suggestion, max_edit_distance_2)
                            if distance < 0:
                                continue
                    # do not process higher distances than those already found
                    if distance <= max_edit_distance_2:
                        suggestion_count = self.words[suggestion]
                        si = SuggestItem(suggestion, distance,
                                         suggestion_count, SuggestRule.EDITDIST)
                        suggestions.append(si)
                        if len(suggestions) > 25:
                            break
          
            #Deleted edits from considering word. adds everything until max distance
            if (len_diff < max_edit_distance
                    and candidate_len <= self.prefix_length):
                #No edits with distance smaller than already added ones
                for i in range(candidate_len):
                    delete = candidate[: i] + candidate[i + 1 :]
                    if delete not in considered_deletes:
                        considered_deletes.add(delete)
                        candidates.append(delete)

        if len(suggestions) > 1:
            suggestions.sort()
        exit_now()
        return suggestions[0:25]

    #Only does deletion, no transpose, insert or replace. based on the meet in the middle technique of symspell algorithm
    def edits_delete(self, word, edit_distance, delete_words):
        edit_distance += 1
        word_len = len(word)
        if word_len > 1:
            for i in range(word_len):
                delete = word[: i] + word[i + 1 :]
                if delete not in delete_words:
                    delete_words.add(delete)
                    # recurse until max_edit distance
                    if edit_distance < self.max_dictionary_edit_distance:
                        self.edits_delete(delete, edit_distance, delete_words)
        return delete_words

    def edits_prefix(self, key):
        hash_set = set()
        if len(key) <= self.max_dictionary_edit_distance:
            hash_set.add("")
        if len(key) > self.max_dictionary_edit_distance:
            key = key[: self.prefix_length]
        hash_set.add(key)
        return self.edits_delete(key, 0, hash_set)

#Return object for lookup, contains term, frequenzy, edit distance, rule which suggested it
class SuggestItem(object):

    #Constructor
    def __init__(self, term, distance, count, suggest_rule):
        self.term = term
        self.distance = distance
        self.count = count
        self.suggest_rule = suggest_rule

    #Equal function for ordering
    def __eq__(self, other):
        if self.distance == other.distance:
            return self.count == other.count
        else:
            return self.distance == other.distance
    
    #Hascode for unique elements
    def __hash__(self):
        return hash(('term', self.term,'count', self.count))
    
    #Less than for sorting
    def __lt__(self, other):
        # if self._distance == 0:
        #     return True
        # if self._suggest_rule==SuggestRule.PREFIX and other._suggest_rule!=SuggestRule.PREFIX:
        #     return True
        # elif self._suggest_rule!=SuggestRule.PREFIX and other._suggest_rule==SuggestRule.PREFIX:
        #     return False
        if self.distance == other.distance:
            return self.count > other.count
        else:
            return self.distance < other.distance
    #to string
    def __str__(self):
        return "{}, {}, {}, {}".format(self.term, self.distance, self.count, self.suggest_rule)