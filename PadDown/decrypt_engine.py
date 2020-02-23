from abc import abstractmethod
from .exceptions import PadDownException


class PadChecker:
    """
    Create a subclass of PadChecker to pass to DecryptEngine
    """

    @abstractmethod
    def has_valid_padding(self, ciphertext):
        """
        Override this method to check if the padding of the ciphertext is valid

        :param bytes ciphertext: The ciphertext to check
        :rtype: True for valid padding, False otherwise.
        """
        raise PadDownException("Not implemented")


class DecryptEngine:
    def __init__(self, pad_checker: PadChecker, blocksize: int = 16):
        if not isinstance(pad_checker, PadChecker):
            raise PadDownException(f"pad_checker not an instance of {PadChecker}")
        self.pad_checker = pad_checker
        self.blocksize = blocksize

    def decrypt_at_index(self, ciphertext: bytearray, index: int):
        if not isinstance(ciphertext, bytearray):
            raise PadDownException(f"ciphertext not an instance of {bytearray}")

        test_ct = ciphertext
        for guess in range(256):
            test_ct[index] = guess
            if self.pad_checker.has_valid_padding(test_ct):
                return guess

        raise RuntimeError(
            "[!] Found no valid padding, is PadChecker implemented correctly?"
        )

    def decrypt_block(self, block):
        if not isinstance(block, bytearray):
            raise PadDownException(f"block not an instance of {bytearray}")

        iv = bytearray(b"\x00" * self.blocksize)
        intermediate = bytearray(b"\x00" * self.blocksize)
        for i in range(self.blocksize):
            for j in range(i):
                iv[(self.blocksize - 1) - j] = (intermediate[(self.blocksize - 1) - j] ^ (i + 1))

            ep = self.decrypt_at_index(iv + block, (self.blocksize - 1) - i)
            intermediate[(self.blocksize - 1) - i] = ep ^ (i + 1)
            print("intermediate: {}".format([hex(x)[2:] for x in intermediate]))
        return intermediate

    def get_intermediate(self, ciphertext):
        key = b""
        blocks = len(ciphertext) // self.blocksize
        for i in range(blocks):
            block_start = len(ciphertext) - (i + 1) * self.blocksize
            block_end = len(ciphertext) - (i * self.blocksize)
            key = self.decrypt_block(ciphertext[block_start:block_end]) + key
        return key

    def decrypt(self, ciphertext):
        if not isinstance(ciphertext, bytes):
            raise Exception(f"Ciphertext {type(ciphertext)} not an instance of {bytes}")

        ciphertext = bytearray(ciphertext)
        key = self.get_intermediate(ciphertext)
        plaintext = bytearray() 
        for i in range(len(ciphertext) - self.blocksize):
            plaintext += bytearray(ciphertext[i] ^ key[i + self.blocksize])
        return plaintext
