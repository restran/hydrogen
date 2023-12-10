# Rot47 Encode & Decode
from mountains.utils import PrintCollector


def encode_rot47(message: str) -> str:
    encoded_message = ""
    for char in message:
        char_code = ord(char)
        if 33 <= char_code <= 126:
            char_code -= 47
            if char_code < 33:
                char_code += 94
        encoded_message += chr(char_code)
    return encoded_message


def decode_rot47(message: str) -> str:
    decoded_message = ""
    for char in message:
        char_code = ord(char)
        if 33 <= char_code <= 126:
            char_code += 47
            if char_code > 126:
                char_code -= 94
        decoded_message += chr(char_code)
    return decoded_message


def decode(data, verbose=False):
    p = PrintCollector()
    d = decode_rot47(data)
    p.print(d)

    return p.smart_output(verbose=verbose)


if __name__ == '__main__':
    # input_data = "synt{mur_VF_syn9_svtug1at}"
    input_data = 'nffreg'
    x = decode_rot47(input_data)
    print(x)
