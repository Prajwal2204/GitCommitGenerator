a = 2
b = 4
print(a+b)
print("Hello world")

def areaOfRectangle(length, breadth):
    return length * breadth

def areaOfTriangle(base, height):
    return 0.5 * base * height

def main():
    print("Inside main function")
    print("Area of rectangle is:", areaOfRectangle(a,b))
    base = 4
    height = 5
    print("Area of triangle:", areaOfTriangle(base, height))

if __name__ == "__main__":
    main()