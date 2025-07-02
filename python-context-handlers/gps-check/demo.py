from gps_radius_check import checkRadius

def main():
    # Example usage from Athens center:
    result = checkRadius(37.9838, 23.7275, 37.9715, 23.7257, 2000)
    print("Result:", result)

if __name__ == "__main__":
    main()
