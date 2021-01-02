meow = False
max_cats = 0
max_restaurant = ''
while not meow:
    data = input()
    if data == 'MEOW':
        meow = True
        continue
    the_space: int = data.find(' ')
    name = data[0:the_space]
    cats = int(data[the_space+1:])
    if cats > max_cats:
        max_cats = cats
        max_restaurant = name

print(max_restaurant)
