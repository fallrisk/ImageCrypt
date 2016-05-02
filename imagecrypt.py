"""
Goal of this project is to take an image and encrypt a message into it. Should be JPG or PNG.
This is also known as Steganography https://en.wikipedia.org/wiki/Steganography
"""

import argparse
import sys

import png  # https://pythonhosted.org/pypng/png.html

_exit_code = 0


def _get_pixel(x, y, pixels):
    """

    :param x: x is from left to right
    :param y: y is from top to bottom
    :param pixels:
    :return:
    """
    return pixels[y][x * 3], pixels[y][x * 3 + 1], pixels[y][x * 3 + 2]


def _set_pixel(x, y, pixels, r, g, b):
    pixels[y][x * 3] = r
    pixels[y][x * 3 + 1] = g
    pixels[y][x * 3 + 2] = b


def get_bit(message, bit_index):
    # char_index = bit_index / 8
    # bit_in_char_index = bit_index % 8
    # v = ord(message[char_index])
    # return v & bit_in_char_index
    return ord(message[int(bit_index / 8)]) >> (bit_index % 8) & 1


def encrypt(img, message, key, output_filename):
    """

    :param img:
    :param message:
    :param key: [x_start, y_start, end_seq0, end_seq1, end_seq2] The end sequence tells the decrypter when to stop
    it should not be found in your message.
    :return:
    """
    ir = png.Reader(filename=img)
    width, height, pixels, metadata = ir.read()
    # pixels are returned in boxed row flat pixel format
    # list([R,G,B R,G,B R,G,B], [...])
    print('metadata {}\r\n'.format(metadata))
    # Each of the bytes of the message is to be encoded into the last nibble of the picture.
    # Even is 1, Odd is 0 we shift the pixel by one to set the bit.
    pixels = list(pixels)
    # print('{}'.format(len(pixels[0])/3))

    x = key[0]
    y = key[1]

    num_bits_to_encode = len(message) * 8

    for i in range(num_bits_to_encode):
        r, g, b = _get_pixel(x, y, pixels)
        bit = get_bit(message, i)
        # ODD is a 0
        # Even is a 1
        if bit == 0:
            # Is the red value even? If it is then we need to make it odd
            # so that it represents a 0. If it's odd then we do nothing.
            if r % 2 == 0:
                r += 1
        else:
            # In this case the bit is a 1 so we must make the value even.
            if r % 2 == 1:
                if r == 255:
                    r -= 1
                else:
                    r += 1
        _set_pixel(x, y, pixels, r, g, b)
        x += 1
        y += 1

    num_bits_to_encode = 3 * 8
    end_sequence = chr(key[2]) + chr(key[3]) + chr(key[4])
    c = 0
    count = 0

    # Now we right the end sequence.
    for i in range(num_bits_to_encode):
        r, g, b = _get_pixel(x, y, pixels)
        bit = get_bit(end_sequence, i)
        # ODD is a 0
        # Even is a 1
        if bit == 0:
            # Is the red value even? If it is then we need to make it odd
            # so that it represents a 0. If it's odd then we do nothing.
            if r % 2 == 0:
                r += 1
        else:
            # In this case the bit is a 1 so we must make the value even.
            if r % 2 == 1:
                if r == 255:
                    r -= 1
                else:
                    r += 1
        _set_pixel(x, y, pixels, r, g, b)
        x += 1
        y += 1

    # Now we save the file.
    iw = png.Writer(width=width, height=height, planes=3)
    f = open(output_filename, 'wb')
    iw.write(f, pixels)


def decrypt(img, key):
    """

    :param img:
    :param key:
    :return: The decrypted message.
    """
    ir = png.Reader(filename=img)
    width, height, pixels, metadata = ir.read()
    print('metadata {}\r\n'.format(metadata))
    pixels = list(pixels)
    x = key[0]
    y = key[1]
    num_bits_to_encode = 40 * 8
    message = ''
    count = 0
    c = 0
    end_sequence = chr(key[2]) + chr(key[3]) + chr(key[4])

    for i in range(num_bits_to_encode):
        r, g, b = _get_pixel(x, y, pixels)
        bit = None
        # ODD is a 0
        # Even is a 1
        if r % 2 == 1:
            c = (c << 1)
        else:
            c = (c << 1) + 1

        count += 1

        if count % 8 == 0:
            message += chr(reverse_bits(c))
            c = 0

            if message[-3:] == end_sequence:
                return message

        x += 1
        y += 1

    return message


def reverse_bits(c):
    r = 0
    for i in range(0, 8, 1):
        r = (r << 1) + ((c >> i) & 1)
    return r


def main():
    # x = 0
    # for i in range(8):
    #     x = (x << 1) + get_bit('H', i)
    #     print(get_bit('H', i), end='')
    # print(chr(x))
    # print(x)
    # print(reverse_bits(x))
    # return
    global _exit_code
    _exit_code = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('--encrypt', action='store_true', help='Encrypt')
    parser.add_argument('--decrypt', action='store_true', help='Decrypt')
    parser.add_argument('--image', help='Image')
    parser.add_argument('--message', help='Message to be encrypted')
    parser.add_argument('--key', help='Encryption/Decryption Key')
    parser.add_argument('--out', help='Output Image')
    args = parser.parse_args()

    if args.encrypt and not args.decrypt:
        if not args.message or not args.image or not args.out:
            parser.print_help()
            sys.exit(_exit_code)
        print('Message is \"{}\"'.format(args.message))
        encrypt(args.image, args.message, [502, 402, 12, 12, 13], args.out)
    elif args.decrypt and not args.encrypt:
        if not args.image:
            parser.print_help()
            sys.exit(_exit_code)
        print('{}'.format(decrypt(args.image, [502, 402, 12, 12, 13])))
    else:
        parser.print_help()

    sys.exit(_exit_code)


if __name__ == '__main__':
    main()
