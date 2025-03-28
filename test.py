a = 2
b = 4
print(a+b)
print("Hello world")

def areaOfRectangle(length, breadth):
    return length * breadth

def main():
    print("Inside main function")
    print("Area of rectangle is:", areaOfRectangle(a,b))

if __name__ == "__main__":
    main()