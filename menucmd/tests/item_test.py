from menucmd.src.menu_item import Item
from macrolibs.typemacros import list_union, hashable_repr

item1 = Item(key='a', message='hello', funcs=[])
item2 = Item(key='b', message='hello2', funcs=[])

print(list_union([], [item1, item2]))

print('')

print(hashable_repr(item1))
print(hashable_repr(item2))