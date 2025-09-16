# main.py

from utils import greet_user, add_numbers

def main():
    # Call function from utils.py
    print(greet_user("Vijay"))

    result = add_numbers(10, 20)
    print(f"The sum is: {result}")

if __name__ == "__main__":
    main()
