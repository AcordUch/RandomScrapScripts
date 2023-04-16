def main() -> None:
    request = (
        f"https://oauth.vk.com/authorize"
        f"?client_id=8197339"
        f"&redirect_id=https://oauth.vk.com/blank.html&scope=friends&response_type=token&v=5.131"
    )
    print(request)


if __name__ == '__main__':
    main()
