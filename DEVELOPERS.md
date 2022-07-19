# Development for the development of bCNC

lorem ipsum

## Use pep8 

### Line width
Line width is a maximum of 79 characters per line. 


### Disabled Codes:
W503 - linbreak before logic operation (this is disables since lines shall start with the operator. It is mutual exclusiv with W502)

## String formating

prefer the usage of f-strings. 

good:
``` 
w = world
print(f"Hello {w}" )
```
bad:
```
print("Hello %s" % w)
print("Hello {}".format(w))
```


