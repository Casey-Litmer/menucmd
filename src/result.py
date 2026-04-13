
#==================================================================================
#Result Type

class Result():
    def __init__(self, n: int, expand: bool = False):
        self.__n__ = n
        self.__attr__ = None
        self.__expand__ = expand

    def __getitem__(self, n: int):
        r = type(self)(n, expand=self.__expand__)
        r.__attr__ = self.__attr__
        return r

    def __repr__(self):
        return f"<class Result[{self.__n__}]>" + (".expand()" if self.__expand__ else "")

    def __eq__(self, other):
        """Compare by attribute if both self and other have attributes"""
        if not isinstance(other, Result) or self.__expand__ != other.__expand__:
            return False

        if self.__attr__ is not None and other.__attr__ is not None:
            return self.__attr__ == other.__attr__
        else:
            return self.__n__ == other.__n__

    def expand(self):
        """Type to replace and expand in place.   *result <=> result.expand()"""
        r = type(self)(self.__n__, expand=True)
        r.__attr__ = self.__attr__
        return r

    def __getattr__(self, tag):
        """Index by attribute first.  If no attribute, index by index"""
        new_result = type(self)(self.__n__, expand=self.__expand__)
        new_result.__attr__ = tag
        return new_result
