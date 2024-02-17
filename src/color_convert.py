import sys, numpy as np
from scipy import stats
from PIL import Image, ImageColor, ImageOps

USE_GRAYSCALE = False # default option on whether to use grayscale

def find_new_color(color: int, first_array: np.ndarray, second_array: np.ndarray) -> int:
    '''
    Find a new color given current color and distribution information.
    Arguments:
        `color: int`: A color in a band.
        `first_array: np.ndarray`: The band array from the image to convert.
        `second_array: np.ndarray`: The band array from the image to compare.
    Returns:
        `int`: The converted color.
    '''
    perc = stats.percentileofscore(first_array.reshape(first_array.size), color)
    return np.percentile(second_array, perc)

def convert_percentiles(first_img: np.ndarray, second_img: np.ndarray, index: int) -> list[int]:
    '''
    Convert a band of colors within an image to the distribution of a second image.
    Arguments:
        `first_img: np.ndarray`: The image to convert the colors of.
        `second_img: np.ndarray`: The image used to perform the conversion.
        `index: int`: The index of the band to operate on.
    Returns:
        `list[int]`: An aligned list of integers for color conversions from 0-255.
    '''
    first_color, second_color = first_img[:, :, index], second_img[:, :, index]
    return [int(find_new_color(i, first_color, second_color)) for i in range(256)]

def make_lookup_table(first_img: np.ndarray, second_img: np.ndarray) -> list[int]:
    '''
    Make a lookup table for image conversion.
    Arguments:
        `first_img: np.ndarray`: The image to construct the lookup table for.
        `second_img: np.ndarray`: The reference image used to construct the lookup table.
    Returns:
        `list[int]`: The completed lookup table for color conversions.
    '''
    lookup_table = []
    for i in range(3):
        lookup_table += convert_percentiles(first_img, second_img, i)
    return lookup_table

def open_image(filename: str) -> tuple[Image.Image, np.ndarray]:
    '''
    Open an image file.
    Arguments:
        `filename: str`: The name of the file.
    Returns:
        `Image.Image`: The image object itself.
        `np.ndarray`: A numpy array of color information.
    '''
    img = Image.open(filename)
    img.load()
    return img, np.array(img)

def apply_lut(rgb: tuple[np.ndarray, np.ndarray, np.ndarray], img: Image.Image, 
              lookup_table: list[int]) -> Image.Image:
    '''
    Apply a lookup table to an image.
    Arguments:
        `rgb: tuple[np.ndarray, np.ndarray, np.ndarray]`: The respective RGB values of the image 
            pixels.
        `img: Image.Image`: The image itself.
        `lookup_table: list[int]`: The constructed lookup table to apply.
    Returns:
        `Image.Image`: The finalized image after lookup table application.
    '''
    return Image.merge(img.mode, rgb).point(lookup_table)

def change_color(img: Image.Image, img_array: np.ndarray, other_array: np.ndarray) -> Image.Image:
    '''
    Change the color of an image without a grayscale step.
    Arguments:
        `img: Image.Image`: The image object to change the colors of.
        `img_array: np.ndarray`: The pixel color information of the image to change.
        `other_array: np.ndarray`: The pixel color information of the reference image.
    Returns:
        `Image.Image`: The image object after color changes applied.
    '''
    lookup_table = make_lookup_table(img_array, other_array)
    return apply_lut(img.split(), img, lookup_table)

def change_grayscale(img: Image.Image, img_array: np.ndarray,
        other_array: np.ndarray) -> Image.Image:
    '''
    Change the color of an image with an additional grayscale step.
    Arguments:
        `img: Image.Image`: The image object to change the colors of.
        `img_array: np.ndarray`: The pixel color information of the image to change.
        `other_array: np.ndarray`: The pixel color information of the reference image.
    Returns:
        `Image.Image`: The image object after color changes applied.
    '''
    lookup_table = make_lookup_table(img_array, other_array)
    gray = ImageOps.grayscale(img)
    return apply_lut((gray, gray, gray), img, lookup_table)

def main():
    use_grayscale = USE_GRAYSCALE
    to_convert, to_compare, output = sys.argv[1:4]
    if len(sys.argv) > 4: # check for grayscale usage
        option = sys.argv[4]
        use_grayscale = option == '-gray'
    
    conv, conv_arr = open_image(to_convert)
    _, comp_arr = open_image(to_compare)
    
    if use_grayscale:
        result = change_grayscale(conv, conv_arr, comp_arr)
    else:
        result = change_color(conv, conv_arr, comp_arr)
    result.save(output)

if __name__ == '__main__':
    main()