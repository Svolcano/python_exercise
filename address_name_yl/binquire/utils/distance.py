#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def levenshtein(s, t):
    """ same as edit_distance_similarity
    """
    ''' From Wikipedia article; Iterative with two matrix rows. '''
    if s == t:
        return 0
    elif len(s) == 0:
        return len(t)
    elif len(t) == 0:
        return len(s)
    v0 = [None] * (len(t) + 1)
    v1 = [None] * (len(t) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s)):
        v1[0] = i + 1
        for j in range(len(t)):
            cost = 0 if s[i] == t[j] else 2
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]

    return v1[len(t)] / (len(s) + len(t))


def lcs(S, T):
    """ The Longest Common Subsequence
    :param S: S is a source string
    :param T: T is a target string
    :return: max Subsequence string length
    """
    m = len(S)
    n = len(T)
    counter = [[0] * (n + 1) for x in range(m + 1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i + 1][j + 1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i - c + 1:i + 1])
                elif c == longest:
                    lcs_set.add(S[i - c + 1:i + 1])

    return max(lcs_set, key=len)


def jaccard_similarity(str1, str2):
    # http://love-python.blogspot.tw/2012/07/python-code-to-compute-jaccard-index.html

    set_1 = set(str1)
    set_2 = set(str2)
    n = len(set_1.intersection(set_2))
    if n == float(len(set_1) + len(set_2) - n):
        return 1
    else:
        return n / float(len(set_1) + len(set_2) - n)