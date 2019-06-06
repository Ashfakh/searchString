from enum import Enum

import numpy as np

#Removes common suffix and prefix and gets start and corresponding lengths
def prefix_suffix_remove(str1, str2):
    len1 = len(str1)
    len2 = len(str2)
    
    #remove suffix
    while len1 != 0 and str1[len1 - 1] == str2[len2 - 1]:
        len1 -= 1
        len2 -= 1
    #remove prefix
    start = 0
    while start != len1 and str1[start] == str2[start]:
        start += 1
    if start != 0:
        len1 -= start
        # length without  prefix and suffix
        len2 -= start
    return len1, len2, start

class EditDistance():
    #Edit distance algo

    #Constructor
    def __init__(self):
        self._distance_comparer = DamerauOsa()
        
    #COmpare to strings to find edit distances
    #Uses initilized distance comparotor - DamerauOsa Algo
    # base string and string to compare as arguments. max distance is the limit
    def compare(self, str1, str2, max_distance):
        return self._distance_comparer.distance(str1, str2,
                                                max_distance)

class DamerauOsa():

    #Constructor
    def __init__(self):
        self._base_char = 0
        self._base_char_1_costs = np.zeros(0, dtype=np.int32)
        self._base_prev_char_1_costs = np.zeros(0, dtype=np.int32)

    #distance function
    def distance(self, str1, str2, max_distance):

        #Null check
        if str1 is None or str2 is None:
            if  str1 is None:
                if str2 is None:
                    return 0
                else:
                    return len(str2) if len(str2) <= max_distance else -1
            return len( str1) if len( str1) <= max_distance else -1
        
        if max_distance <= 0:
            return 0 if str1 == str2 else -1

        # bound on maxness. 
        max_distance = int(min(2 ** 31 - 1, max_distance))

        #str 1 sould be shorter, increase speed as inner loop will be used mostly
        if len(str1) > len(str2):
            str2, str1 = str1, str2

        if len(str2) - len(str1) > max_distance:
            return -1
        
        # remove common suffix and prefix
        len_1, len_2, start = prefix_suffix_remove(str1, str2)

        #Limiting on len 2
        if len_1 == 0:
            return len_2 if len_2 <= max_distance else -1
        

        if len_2 > len(self._base_char_1_costs):
            self._base_char_1_costs = np.zeros(len_2, dtype=np.int32)
            self._base_prev_char_1_costs = np.zeros(len_2, dtype=np.int32)
        
        # returns till max distance
        if max_distance < len_2:
            return self._distance_max(str1, str2, len_1, len_2,
                                      start, max_distance,
                                      self._base_char_1_costs,
                                      self._base_prev_char_1_costs)
        #return all distance
        return self._distance(str1, str2, len_1, len_2, start,
                              self._base_char_1_costs,
                              self._base_prev_char_1_costs)
    
    #Implemntation of DamerauOsa without bound, reference : https://github.com/softwx/SoftWx.Match
    def _distance(self, str1, str2, len_1, len_2, start,
                  char_1_costs, prev_char_1_costs):
        char_1_costs = np.asarray([j + 1 for j in range(len_2)])
        char_1 = " "
        current_cost = 0
        for i in range(len_1):
            prev_char_1 = char_1
            char_1 = str1[start + i]
            char_2 = " "
            left_char_cost = above_char_cost = i
            next_trans_cost = 0
            for j in range(len_2):
                this_trans_cost = next_trans_cost
                next_trans_cost = prev_char_1_costs[j]
                # cost of diagonal (substitution)
                prev_char_1_costs[j] = current_cost = left_char_cost
                # left now equals current cost (which will be diagonal
                # at next iteration)
                left_char_cost = char_1_costs[j]
                prev_char_2 = char_2
                char_2 = str2[start + j]
                if char_1 != char_2:
                    # substitution if neither of two conditions below
                    if above_char_cost < current_cost:
                        current_cost = above_char_cost
                    if left_char_cost < current_cost:
                        current_cost = left_char_cost
                    current_cost += 1
                    if (i != 0 and j != 0
                            and char_1 == prev_char_2
                            and prev_char_1 == char_2
                            and this_trans_cost + 1 < current_cost):
                        # transposition
                        current_cost = this_trans_cost + 1
                char_1_costs[j] = above_char_cost = current_cost
        return current_cost

    #Implemntation of DamerauOsa with bound, reference : https://github.com/softwx/SoftWx.Match
    def _distance_max(self, str1, str2, len_1, len_2, start,
                      max_distance, char_1_costs, prev_char_1_costs):
        char_1_costs = np.asarray([j + 1 if j < max_distance
                                   else max_distance + 1
                                   for j in range(len_2)])
        len_diff = len_2 - len_1
        j_start_offset = max_distance - len_diff
        j_start = 0
        j_end = max_distance
        char_1 = " "
        current_cost = 0
        for i in range(len_1):
            prev_char_1 = char_1
            char_1 = str1[start + i]
            char_2 = " "
            left_char_cost = above_char_cost = i
            next_trans_cost = 0
            # no need to look beyond window of lower right diagonal -
            # max_distance cells (lower right diag is i - len_diff) and
            # the upper left diagonal + max_distance cells (upper left
            # is i)
            j_start += 1 if i > j_start_offset else 0
            j_end += 1 if j_end < len_2 else 0
            for j in range(j_start, j_end):
                this_trans_cost = next_trans_cost
                next_trans_cost = prev_char_1_costs[j]
                # cost of diagonal (substitution)
                prev_char_1_costs[j] = current_cost = left_char_cost
                # left now equals current cost (which will be diagonal
                # at next iteration)
                left_char_cost = char_1_costs[j]
                prev_char_2 = char_2
                char_2 = str2[start + j]
                if char_1 != char_2:
                    # substitution if neither of two conditions below
                    if above_char_cost < current_cost:
                        current_cost = above_char_cost
                    if left_char_cost < current_cost:
                        current_cost = left_char_cost
                    current_cost += 1
                    if (i != 0 and j != 0 and char_1 == prev_char_2
                            and prev_char_1 == char_2
                            and this_trans_cost + 1 < current_cost):
                        # transposition
                        current_cost = this_trans_cost + 1
                char_1_costs[j] = above_char_cost = current_cost
            if char_1_costs[i + len_diff] > max_distance:
                return -1
        return current_cost if current_cost <= max_distance else -1