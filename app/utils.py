import secrets
import string


def random_code(length: int = 4) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


if __name__ == '__main__':
    print(random_code())
    print(random_code())
    print(random_code())
    print(random_code())
