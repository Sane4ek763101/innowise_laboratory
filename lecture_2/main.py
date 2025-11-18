def generate_profile(age):
    """Determine life stage based on age"""
    if 0 <= age <= 12:
        return "Child"
    elif 13 <= age <= 19:
        return "Teenager"
    elif age >= 20:
        return "Adult"
    else:
        return "Unknown"


def main():
    print("Welcome! Let's create your profile.\n")

    # Get basic information
    user_name = input("Enter your full name: ")
    birth_year_str = input("Enter your birth year: ")

    # Convert and calculate age
    birth_year = int(birth_year_str)
    current_year = 2025
    current_age = current_year - birth_year

    # Collect hobbies
    hobbies = []
    print("\nNow let's collect your hobbies!")
    print("Enter one hobby at a time. Type 'stop' to finish")

    while True:
        hobby = input("Enter a favorite hobby or type 'stop' to finish: ").strip()

        # Check if user wants to stop
        if hobby.lower() == "stop":
            break
        elif hobby:  # Check if input is not empty
            hobbies.append(hobby)
            print(f"Hobby '{hobby}' added!")

    # Determine life stage
    life_stage = generate_profile(current_age)

    # Create profile dictionary
    user_profile = {
        "name": user_name,
        "age": current_age,
        "birth_year": birth_year,
        "life_stage": life_stage,
        "hobbies": hobbies
    }

    # Display results
    print("\n" + "=" * 50)
    print("YOUR PROFILE")
    print("=" * 50)
    print(f"Name: {user_profile['name']}")
    print(f"Current age: {user_profile['age']} years")
    print(f"Birth year: {user_profile['birth_year']}")
    print(f"Life stage: {user_profile['life_stage']}")

    # Handle hobbies display
    print("\nHOBBIES:")
    if not user_profile['hobbies']:
        print("You didn't mention any hobbies.")
    else:
        hobby_count = len(user_profile['hobbies'])
        print(f"Favorite Hobbies ({hobby_count}):")
        for hobby in user_profile['hobbies']:
            print(f"  - {hobby}")

# Run the program
if __name__ == "__main__":
    main()