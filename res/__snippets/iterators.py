#!/usr/bin/python3
"""
Infinite iterator from min to max by step with restart possibilities.
"""


class Infinite:
    """
    Infinite iterator object over a definite sequence.
    """
    def __init__(self, min: int = 1, max: int = 5, step: int = 1, from_minimum: bool = True):
        """
        :param min: start of the iterator
        :param max: upper bound of the iterator
        :param step: step between two values
        :param from_minimum: when the maximum is reached continue from minimum? True (1, 3, 5, 1, 3, ...),
                                                                                False (1, 3, 5, 2, 4, 1, 3, ...)
        """
        self.min = min
        self.max = max
        self.step = step
        self.from_minimum = from_minimum

    def __iter__(self):
        self.n = self.min
        return self

    def __next__(self):
        result = self.n
        if self.n + self.step <= self.max:
            self.n += self.step
        else:
            if self.from_minimum:
                self.n = self.min
            else:
                self.n = self.n + self.step - self.max + self.min - 1
        return result


class InfiniteList:
    """
    Infinite iterator object over a supplied list.
    """
    def __init__(self, iter_list: list = 1, step: int = 1, from_start: bool = True):
        """
        :param iter_list: list of values to iterate over
        :param step: step between two values
        :param from_start: when the end of list is reached continue from start? True (1, 3, 5, 1, 3, ...),
                                                                                False (1, 3, 5, 2, 4, 1, 3, ...)
        """
        self.iter_list = iter_list
        self.length = len(self.iter_list)
        self.step = step
        self.from_start = from_start

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        result = self.iter_list[self.n]
        if self.n + self.step < self.length:
            self.n += self.step
        else:
            if self.from_start:
                self.n = 0
            else:
                self.n = self.n + self.step - self.length
        return result


class Fibonacci:
    """
    Infinite iterator object over Fibonacci sequence.
    """
    def __init__(self, number: int = -1):
        """
        :param number: the number of Fibonacci numbers to return. if number = -1, then infinite
        :return:
        """
        self.number = number

    def __iter__(self, number: int = -1):
        self.n = 0
        self.m = 1
        self.c = 0
        return self

    def __next__(self):
        self.c += 1
        if self.c == self.number:
            raise StopIteration
        fib = self.n
        self.n = self.m
        self.m += fib
        return fib


class TwoToPowerOfN:
    """
    Infinite iterator object over 2^n sequence.
    """
    def __init__(self, number: int = -1):
        """
        :param number: the number of numbers to return. if number = -1, then infinite
        :return:
        """
        self.number = number

    def __iter__(self, number: int = -1):
        self.n = 0
        self.c = 0
        return self

    def __next__(self):
        self.c += 1
        if self.c == self.number:
            raise StopIteration
        two = 2 ** self.n
        self.n += 1
        return two


# test
if __name__ == '__main__':
    # c = Infinite(0, 10, 2, False)
    # c = InfiniteList([1, 2, 3, 4, 5], 2, False)
    # c = Fibonacci()
    # c = Fibonacci(20)
    c = TwoToPowerOfN(30)
    for i in c:
        print(i)
