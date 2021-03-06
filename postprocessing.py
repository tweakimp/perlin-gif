import numpy as np
from abc import ABC, abstractmethod
from skimage.draw import circle


def circular_mask(shape):
    mask = np.zeros(shape, dtype=np.uint8)
    rr, cc = circle(shape[0]/2, shape[1]/2, radius=shape[0] / 2, shape=shape)
    mask[rr, cc] = 1
    
    return mask


class AbstractProcessing(ABC):
    """ Base class for post-processing """
    @abstractmethod
    def apply(self, *args, **kwargs):
        pass


class Quantize(AbstractProcessing):
    """ Apply quantization to each frame of a given 3D input. """
    def __init__(self, bins=2):
        self.bins = bins

    def apply(self, images):
        w = images.max() / self.bins

        for i in range(images.shape[0]):
            images[i, :, :] -= (images[i, :, :] - (images[i, :, :] // w) * w).astype('uint8')

        return images


class AdjustBrightness(AbstractProcessing):
    """ Gamma < 1 will decrease brightness, Gamma > 1 will increase it. """
    def __init__(self, gamma):
        self.gamma = gamma
    
    def apply(self, images):
        # Normalize, then apply brightness correction
        images = (images / images.max()) ** (1 / self.gamma)
        # Convert back to grayscale [0, 255]
        images = ((images - images.min()) * (1 / (images.max() - images.min()) * 255)).astype('uint8')

        return images


class Mask(AbstractProcessing):
    def __init__(self, mask):
        self.mask = mask
    
    def apply(self, images):
        for i in range(images.shape[0]):
            images[i, :, :] *= self.mask
        
        return images


class FromFunction(AbstractProcessing):
    """ Not tested, not fully compatible yet. """
    def __init__(self, fn=None, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    
    def apply(self, images):
        for i in range(images.shape[0]):
            images[i, :, :] = self.fn(images[i, :, :], *self.args, **self.kwargs)

        return images


class Pipeline():
    """ Define an AbstractProcessing pipeline object. """
    def __init__(self, *args):
        self._processing_list = args

    def run(self, images):
        if not self.is_empty():
            for f in self._processing_list:
                images = f.apply(images)

        return images
    
    def is_empty(self):
        return len(self._processing_list) == 0
