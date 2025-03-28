a = 2
b = 4
print(a+b)
print("Hello world")

def area(length, breadth):
    return length * breadth

def main():
    print("Inside main function")
    print("Area of rectangle is:", area(a,b))

if __name__ == "__main__":
    main()