from json import loads as json_loads
from argparse import ArgumentParser
from urllib.request import Request, urlopen


def get_list_of_friend(user_id: str, token: str, version: str) -> dict:
    if not user_id.isdigit():
        try:
            user_id = get_user_id_by_name(user_id, token, version)
        except KeyError:
            raise ValueError("Input user doesn't exist!")

    friends_list_request = (
        f'https://api.vk.com/method/friends.get?user_id={user_id}'
        f'&order=name&fields=nickname,domain'
        f'&access_token={token}'
        f'&v={version}'
    )

    try:
        return make_request_and_parse(friends_list_request)["response"]
    except KeyError:
        raise KeyError(f"{make_request_and_parse(friends_list_request)['error']['error_msg']}")


def get_message_list(user_id: str, token: str, version: str):
    if not user_id.isdigit():
        try:
            user_id = get_user_id_by_name(user_id, token, version)
        except KeyError:
            raise ValueError("Input user doesn't exist!")

    friends_list_request = (
        f'https://api.vk.com/method/friends.get?user_id={user_id}'
        f'&order=name&fields=nickname,domain'
        f'&access_token={token}'
        f'&v={version}'
    )

    try:
        return make_request_and_parse(friends_list_request)["response"]
    except KeyError:
        raise KeyError(f"{make_request_and_parse(friends_list_request)['error']['error_msg']}")


def get_user_id_by_name(name: str, token: str, version: str) -> str:
    request = (
        f"https://api.vk.com/method/users.get?user_id={name}"
        f"&access_token={token}"
        f"&v={version}"
    )
    return make_request_and_parse(request)["response"][0]["id"]


def make_request_and_parse(request_message) -> dict:
    return json_loads(make_request(request_message))


def make_request(request_message) -> bytes:
    return urlopen(Request(request_message)).read()


def config_argparse(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument('user_id', type=str, help='User id')
    arg_parser.add_argument('token', type=str, help='Your access token')


def main():
    arg_parser = ArgumentParser()
    config_argparse(arg_parser)
    args = arg_parser.parse_args()
    api_response = get_list_of_friend(args.user_id, args.token, "5.131")["items"]
    with open('response.txt', 'w', encoding='utf-8') as file:
        answer = '\n'.join([f"{person['first_name']} {person['last_name']}" for person in api_response])
        file.write(answer)
        print(answer)


if __name__ == "__main__":
    main()
