

def append_milo(lst: list = []):
    lst.append("milo xui")
    print("значение списка", lst)


append_milo()
print()
print("атрибуты", append_milo.__defaults__)
print()
append_milo()
print()
print("атрибуты", append_milo.__defaults__)