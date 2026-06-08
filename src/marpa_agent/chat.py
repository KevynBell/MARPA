from memory_manager import load_project_memory


def main():
    memory = load_project_memory()

    print("MARPA Agent initialized.")
    print("\nLoaded Memory:\n")
    print(memory)


if __name__ == "__main__":
    main()