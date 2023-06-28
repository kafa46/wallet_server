import collections

def sorted_dict_by_key(unsorted_dict: dict):
    '''사전(dict)은 원소의 순서가 보장되지 않음
        -> 같은 사전이라도 순서가 달라지면 hash 값은 엄청난 차이
        -> 사전의 key 값에 따라 일정하게 정렬하여
           동일한 dict은 동일한 hash 값을 보장
    '''
    return collections.OrderedDict(
        sorted(unsorted_dict.items(), key=lambda keys: keys[0])
    )