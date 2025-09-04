from __future__ import annotations
from data_structures.abstract_set import Set, T
from data_structures.referential_array import ArrayR


class ArraySet(Set[T]):
    """
    Array-based implementation of the set ADT.
    """

    def __init__(self, capacity: int = 1) -> None:
        if capacity <= 0:
            raise ValueError("Capacity should be larger than 0.")

        self.__array = ArrayR(capacity)
        self.__length = 0

    def add(self, item: T) -> None:
        """
        Adds an element to the set. Note that an element already present
        in the set should not be added.
        :raises Exception: if the set is full.
        """
        if item not in self:
            if self.is_full():
                raise Exception("The set is full.")

            self.__array[self.__length] = item
            self.__length += 1

    def remove(self, item: T) -> None:
        """
        Removes an element from the set.
        :raises KeyError: if no such element is found.
        :complexity:
            Best case O(1) when the items is found at the beginning. 
            Worst case O(N) where N is the number of items in the set, happens when item
            is found at the end of the set or not found at all.
        """
        for i in range(self.__length):
            if item == self.__array[i]:
                self.__array[i] = self.__array[self.__length - 1]
                self.__length -= 1
                break
        else:
            raise KeyError(item)
    
    def values(self) -> ArrayR[T]:
        """
        Returns the elements of the set as an array.
        :complexity: O(N) where N is the number of items in the set.
        """
        res = ArrayR(self.__length)
        for i in range(self.__length):
            res[i] = self.__array[i]
        return res

    def clear(self) -> None:
        """ Makes the set empty.
        We do this by simply setting the size to 0, which means the next items will
        write over the existing array.
        """
        self.__length = 0

    def is_empty(self) -> bool:
        """ True if the set is empty. """
        return len(self) == 0

    def is_full(self) -> bool:
        """ True if the set is full and no element can be added. """
        return len(self) == len(self.__array)

    def union(self, other: ArraySet[T]) -> ArraySet[T]:
        """
        Creates a new set equal to the union of this set and the other one.
        I.e. the result set should contain all elements in self and other.
        :complexity: O(N * M) where N is the number of items in self and M is the number of items in other.
        """
        res = ArraySet(len(self.__array) + len(other.__array))

        for i in range(len(self)):
            res.__array[i] = self.__array[i]
        res.__length = self.__length

        for j in range(len(other)):
            if other.__array[j] not in self:
                res.__array[res.__length] = other.__array[j]
                res.__length += 1

        return res

    def intersection(self, other: ArraySet[T]) -> ArraySet[T]:
        """ The intersection of this set with the other one.
        The result set should contain the elements that are present
        in both self and other.
        :complexity: O(N * M) where N is the number of items in self and M is the number of items in other.
        """
        res = ArraySet(min(len(self.__array), len(other.__array)))

        for i in range(len(self)):
            if self.__array[i] in other:
                res.__array[res.__length] = self.__array[i]
                res.__length += 1

        return res

    def difference(self, other: ArraySet[T]) -> ArraySet[T]:
        """ Creates the result of self - other.
        The result set should contain the elements that are present
        in self but not in other.
        :complexity: O(N * M) where N is the number of items in self and M is the number of items in other.
        """
        res = ArraySet(len(self.__array))

        for i in range(len(self)):
            if self.__array[i] not in other:
                res.__array[res.__length] = self.__array[i]
                res.__length += 1

        return res

    def __contains__(self, item: T) -> bool:
        """ True if the set contains the item. """
        for i in range(self.__length):
            if item == self.__array[i]:
                return True
        return False

    def __len__(self) -> int:
        """ Returns the number of elements in the set. """
        return self.__length

    def __str__(self):
        """ Returns a string representation of the set. """
        return f'<ArraySet {Set.__str__(self)}>'
