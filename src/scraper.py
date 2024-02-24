import requests

def main():
    request = requests.get("https://menus.princeton.edu/dining/_Foodpro/online-menu/")
    print(request)

if __name__ == "__main__":
    main()
