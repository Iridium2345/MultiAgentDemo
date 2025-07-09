from .api_keys import ApiKeys

def main():
    keys = ApiKeys()
    print(keys.list_keys())
    print(keys.key_of("deepseek-r1"))

if __name__ == "__main__":
    main()
