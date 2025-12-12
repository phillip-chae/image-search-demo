from io import BytesIO
from typing import BinaryIO
from pathlib import Path
from PIL import Image
from pillow_heif import register_heif_opener
import imagehash # You'll need to install this: pip install imagehash Pillow

class Phasher:
    """
    A class for computing perceptual hashes (pHash) of images from in-memory
    file-like objects (like BytesIO or BinaryIO) and comparing them.

    It leverages the Pillow library for image decoding and the imagehash library
    for pHash computation.
    """

    def __init__(self, hash_size: int = 8):
        """
        Initializes the Phasher.

        Args:
            hash_size (int): The size of the hash to generate. A common value is 8,
                             resulting in a 64-bit hash. Larger values (e.g., 16)
                             can increase discrimination but also computation time
                             and sensitivity to minor changes. The hash length will be
                             hash_size * hash_size bits.
        """
        
        register_heif_opener()
        if not (4 <= hash_size <= 64): # Reasonable bounds for hash_size
            raise ValueError("hash_size must be an integer between 4 and 64 (inclusive).")
        self.hash_size = hash_size

    def compute_hash(self, image_data: str | Path | bytes | BinaryIO) -> imagehash.ImageHash:

        try:
            # Pillow's Image.open can directly read from a file-like object
            if isinstance(image_data, bytes):
                with BytesIO(image_data) as buf:
                    with Image.open(buf) as img:
                        img = img.convert('RGB')
                        if img.mode not in ('RGB', 'L'):
                            img = img.convert('RGB') # Convert to RGB if not already, or grayscale 'L'
                        image_hash = imagehash.phash(img, hash_size=self.hash_size)
            else:
                with Image.open(image_data) as img:
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    image_hash = imagehash.phash(img, hash_size=self.hash_size)

            return image_hash
        except IOError as e:
            raise IOError(f"Could not open or decode image from BytesIO: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during pHash computation: {e}")


    def compare_hashes(self, hash1: imagehash.ImageHash, hash2: imagehash.ImageHash, threshold: int) -> bool:

        if not isinstance(hash1, imagehash.ImageHash) or not isinstance(hash2, imagehash.ImageHash):
            raise TypeError("Both hash1 and hash2 must be imagehash.ImageHash objects.")
        
        # The imagehash library overloads the subtraction operator for Hamming distance
        distance = hash1 - hash2
        return distance <= threshold

    def __call__(self, image: str | Path | bytes | BinaryIO) -> str:

        hash_obj = self.compute_hash(image)

        return str(hash_obj) # Return the hash as a string for easier readability