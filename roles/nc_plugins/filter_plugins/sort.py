#!/usr/bin/python
import re
import collections

from functools import cmp_to_key


def natural_sort(a_list):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(a_list, key=alphanum_key)


def version_sort(a_list):
    def compare(str1, str2):
        pattern = re.compile('([0-9]+|[.-_])')
        split1 = list(filter(None, re.split(pattern, str1)))
        split2 = list(filter(None, re.split(pattern, str2)))
        for i in range(min(len(split1), len(split2))):
            if len(split1[i]) > 0 and len(split2[i]) > 0:
                c1 = split1[i][0]
                c2 = split2[i][0]
                comp = 0
                if c1.isdigit() and c2.isdigit():
                    comp = int(split1[i]) - int(split2[i])
                if c1.isdigit() and not c2.isdigit():
                    comp = 1
                if not c1.isdigit() and c2.isdigit():
                    comp = -1
                if comp == 0:
                    if split1[i] < split2[i]:
                        comp = -1
                    if split1[i] > split2[i]:
                        comp = 1
                if comp != 0:
                    return comp
        return len(split1) - len(split2)

    return sorted(a_list, key=cmp_to_key(compare))


def split_list(a_list, delimiter='', return_last=True):
    if delimiter == '':
        return a_list
    if isinstance(a_list, collections.Iterable) and type(a_list) is not str:
        a_list = list(a_list)
    if type(a_list) is not list:
        a_list = [a_list]

    result = a_list
    skip = return_last
    pattern = re.compile("^.*" + delimiter + ".*$")
    for i in list(a_list):
        matched = pattern.search(i)
        if matched:
            skip = bool(not skip)
        if skip:
            result.remove(i)
    return result


def regexp_sort(a_list, include_mask=[], exclude_mask=[]):
    if isinstance(a_list, collections.Iterable) and type(a_list) is not str:
        a_list = list(a_list)
    if type(a_list) is not list:
        a_list = [a_list]

    if isinstance(include_mask, collections.Iterable) and type(include_mask) is not str:
        include_mask = list(include_mask)
    if type(include_mask) is not list:
        include_mask = [include_mask]

    if isinstance(exclude_mask, collections.Iterable) and type(exclude_mask) is not str:
        exclude_mask = list(exclude_mask)
    if type(exclude_mask) is not list:
        exclude_mask = [exclude_mask]

    initial = a_list
    for e in list(exclude_mask):
        pattern = re.compile("^.*" + e + ".*$")
        matched = list(filter(pattern.match, initial))
        initial = [x for x in initial if x not in matched]

    result = []
    for i in list(include_mask):
        pattern = re.compile("^.*" + i + ".*$")
        matched = list(filter(pattern.match, initial))
        result.extend(matched)
        initial = [x for x in initial if x not in matched]
    result.extend(initial)
    return result


class FilterModule(object):
    def filters(self):
        return {
            'natural_sort': natural_sort,
            'version_sort': version_sort,
            'split_list':   split_list,
            'regexp_sort':  regexp_sort
        }
