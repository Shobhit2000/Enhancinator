import numpy as np
import tensorflow as tf
import os
import cv2
from tensorflow.keras.layers import Add, Conv2D, Input, Lambda
from tensorflow.keras.models import Model
from model import resolve_single

DIV2K_RGB_MEAN = np.array([0.4488, 0.4371, 0.4040]) * 255

def edsr(scale, num_filters=64, num_res_blocks=8, res_block_scaling=None):
    x_in = Input(shape=(None, None, 3))
    x = Lambda(normalize)(x_in)
    x = b = Conv2D(num_filters, 3, padding='same')(x)
    for i in range(num_res_blocks):
        b = res_block(b, num_filters, res_block_scaling)
    b = Conv2D(num_filters, 3, padding='same')(b)
    x = Add()([x, b])
    x = upsample(x, scale, num_filters)
    x = Conv2D(3, 3, padding='same')(x)
    x = Lambda(denormalize)(x)
    return Model(x_in, x, name="edsr")


def res_block(x_in, filters, scaling):
    x = Conv2D(filters, 3, padding='same', activation='relu')(x_in)
    x = Conv2D(filters, 3, padding='same')(x)
    if scaling:
        x = Lambda(lambda t: t * scaling)(x)
    x = Add()([x_in, x])
    return x

def upsample(x, scale, num_filters):
    def upsample_1(x, factor, **kwargs):
        x = Conv2D(num_filters * (factor ** 2), 3, padding='same', **kwargs)(x)
        return Lambda(pixel_shuffle(scale=factor))(x)

    if scale == 2:
        x = upsample_1(x, 2, name='conv2d_1_scale_2')
    elif scale == 3:
        x = upsample_1(x, 3, name='conv2d_1_scale_3')
    elif scale == 4:
        x = upsample_1(x, 2, name='conv2d_1_scale_2')
        x = upsample_1(x, 2, name='conv2d_2_scale_2')
    return x


def pixel_shuffle(scale):
    return lambda x: tf.nn.depth_to_space(x, scale)

def normalize(x):
    return (x - DIV2K_RGB_MEAN) / 127.5

def denormalize(x):
    return x * 127.5 + DIV2K_RGB_MEAN

def resolve_and_plot(model_pre_trained, model_fine_tuned, lr_image_path):

    lr = lr_image_path
    sr_pt = resolve_single(model_pre_trained, lr)
    return sr_pt
        
weights_dir = 'weights/'

# Load weights
edsr_pre_trained = edsr(scale=4, num_res_blocks=16)
edsr_pre_trained.load_weights(os.path.join(weights_dir, 'weights-edsr-16-x4.h5'))

edsr_fine_tuned = edsr(scale=4, num_res_blocks=16)
edsr_fine_tuned.load_weights(os.path.join(weights_dir, 'weights-edsr-16-x4-fine-tuned.h5'))

# Prediction
def sr(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    lr = cv2.resize(img, (640, 360))
    sr = resolve_and_plot(edsr_pre_trained, edsr_fine_tuned, img)
    sr = np.array(sr)
    sr = cv2.cvtColor(sr, cv2.COLOR_RGB2BGR)
    sr = cv2.resize(sr, (640, 360))
    return lr, sr
