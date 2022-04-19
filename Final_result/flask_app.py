# 모듈 호출
import cv2
import numpy as np
import os
import sys
from datetime import datetime
import tensorflow as tf
from tensorflow.keras.layers import Layer, InputSpec
import PIL
import matplotlib.pyplot as plt
import torch
from torchvision import transforms, models
from flask import Flask, render_template

# # real esrGAN 환경 설정
# print('환경을 설정 중입니다')
# !pip install basicsr
# !pip install facexlib
# !pip install gfpgan
# !pip install -r requirements.txt
# !python setup.py develop
# print('환경 설정 완료')


app = Flask(__name__) # 플라스크 인스턴스 생성

@app.route('/')
@app.route('/home') # 기본 홈 경로 설정
def home(): # 경로에 대한 요청이 있을 때 실행될 함수 정의
    return render_template('index.html') # 저장된 html 템플릿 렌더링

@app.route("/test") # 실제 프로젝트의 내용이 구현될 부분에 대한 경로 및 함수 정의
def test():
    image_path = '/home/sjh7397/test_pythonanywhere/static/input_img/111.jpg'
    style = 'hayao' # 원하는 스타일명 지정(나중에 값 받아오도록 수정해야함)
    date_string = datetime.now().strftime("%d%m%Y%H%M%S") # 파일명 중복 방지를 위한 변수 지정


    # segmentation
    model = models.segmentation.deeplabv3_resnet101(pretrained=True).eval()
    # segmentation 함수 정의
    def segment(model, img):
        preprocess = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            ),
        ])

        input_tensor = preprocess(img)
        input_batch = input_tensor.unsqueeze(0)

        if torch.cuda.is_available():
            input_batch = input_batch.to('cuda')
            model.to('cuda')

        output = model(input_batch)['out'][0] # (21, height, width)

        output_predictions = output.argmax(0).byte().cpu().numpy() # (height, width)

        r = PIL.Image.fromarray(output_predictions).resize((img.shape[1], img.shape[0]))
        r.putpalette(colors)

        return r, output_predictions
    cmap = plt.cm.get_cmap('tab20c')
    colors = (cmap(np.arange(cmap.N)) * 255).astype(int)[:, :3].tolist()
    np.random.seed(2020)
    colors.insert(0, [0, 0, 0])
    colors = np.array(colors, dtype=np.uint8)
    img = np.array(PIL.Image.open(image_path))
    fg_h, fg_w, _ = img.shape

    while (fg_h >= 512) | (fg_w >= 512):
      img = cv2.resize(img, (fg_w//2,fg_h//2))
      fg_h, fg_w, _ = img.shape

    segment_map, pred = segment(model, img)
    background = np.ones((fg_h, fg_w, 3))*255.0
    mask = (pred == 12).astype(float) * 255 # 12: dog
    _, alpha = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
    alpha = cv2.GaussianBlur(alpha, (7, 7), 0).astype(float)
    alpha_scale = alpha / 255. # (height, width)
    alpha_1 = np.repeat(np.expand_dims(alpha_scale, axis=2), 3, axis=2) # (height, width, 3)
    foreground = cv2.multiply(alpha_1, img.astype(float))
    background = cv2.multiply(1. - alpha_1, background.astype(float))
    result = cv2.add(foreground, background).astype(np.uint8)

        # cartoonGAN 모델 구성 정의
    class InstanceNormalization(Layer):
        def __init__(self,
                     axis=3,
                     epsilon=1e-9,
                     center=True,
                     scale=True,
                     beta_initializer='zeros',
                     gamma_initializer='ones',
                     beta_regularizer=None,
                     gamma_regularizer=None,
                     beta_constraint=None,
                     gamma_constraint=None,
                     **kwargs):
            super(InstanceNormalization, self).__init__(**kwargs)
            self.supports_masking = True
            self.axis = axis
            self.epsilon = epsilon
            self.center = center
            self.scale = scale
            self.beta_initializer = tf.keras.initializers.get(beta_initializer)
            self.gamma_initializer = tf.keras.initializers.get(gamma_initializer)
            self.beta_regularizer = tf.keras.regularizers.get(beta_regularizer)
            self.gamma_regularizer = tf.keras.regularizers.get(gamma_regularizer)
            self.beta_constraint = tf.keras.constraints.get(beta_constraint)
            self.gamma_constraint = tf.keras.constraints.get(gamma_constraint)

        def build(self, input_shape):
            ndim = len(input_shape)
            if self.axis == 0:
                raise ValueError('Axis cannot be zero')

            if (self.axis is not None) and (ndim == 2):
                raise ValueError('Cannot specify axis for rank 1 tensor')

            self.input_spec = tf.keras.layers.InputSpec(ndim=ndim)

            if self.axis is None:
                shape = (1,)
            else:
                shape = (input_shape[self.axis],)

            if self.scale:
                self.gamma = self.add_weight(shape=shape,
                                             name='gamma',
                                             initializer=self.gamma_initializer,
                                             regularizer=self.gamma_regularizer,
                                             constraint=self.gamma_constraint)
            else:
                self.gamma = None
            if self.center:
                self.beta = self.add_weight(shape=shape,
                                            name='beta',
                                            initializer=self.beta_initializer,
                                            regularizer=self.beta_regularizer,
                                            constraint=self.beta_constraint)
            else:
                self.beta = None
            self.built = True

        def call(self, inputs, training=None):
            input_shape = tf.keras.backend.int_shape(inputs)
            reduction_axes = list(range(0, len(input_shape)))

            if self.axis is not None:
                del reduction_axes[self.axis]

            del reduction_axes[0]

            mean = tf.keras.backend.mean(inputs, reduction_axes, keepdims=True)
            stddev = tf.keras.backend.std(inputs, reduction_axes, keepdims=True) + self.epsilon
            normed = (inputs - mean) / stddev

            broadcast_shape = [1] * len(input_shape)
            if self.axis is not None:
                broadcast_shape[self.axis] = input_shape[self.axis]

            if self.scale:
                broadcast_gamma = tf.keras.backend.reshape(self.gamma, broadcast_shape)
                normed = normed * broadcast_gamma
            if self.center:
                broadcast_beta = tf.keras.backend.reshape(self.beta, broadcast_shape)
                normed = normed + broadcast_beta
            return normed

        def get_config(self):
            config = {
                'axis': self.axis,
                'epsilon': self.epsilon,
                'center': self.center,
                'scale': self.scale,
                'beta_initializer': tf.keras.initializers.serialize(self.beta_initializer),
                'gamma_initializer': tf.keras.initializers.serialize(self.gamma_initializer),
                'beta_regularizer': tf.keras.regularizers.serialize(self.beta_regularizer),
                'gamma_regularizer': tf.keras.regularizers.serialize(self.gamma_regularizer),
                'beta_constraint': tf.keras.constraints.serialize(self.beta_constraint),
                'gamma_constraint': tf.keras.constraints.serialize(self.gamma_constraint)
            }
            base_config = super(InstanceNormalization, self).get_config()
            return dict(list(base_config.items()) + list(config.items()))


    class ReflectionPadding2D(Layer):
        def __init__(self, padding=(1, 1), **kwargs):
            self.padding = tuple(padding)
            self.input_spec = [InputSpec(ndim=4)]
            super(ReflectionPadding2D, self).__init__(**kwargs)

        def compute_output_shape(self, s):
            """ If you are using "channels_last" configuration"""
            return s[0], s[1] + 2 * self.padding[0], s[2] + 2 * self.padding[1], s[3]

        def call(self, x):
            w_pad, h_pad = self.padding
            return tf.pad(x, [[0, 0], [h_pad, h_pad], [w_pad, w_pad], [0, 0]], 'REFLECT')


    def conv_layer(style, name, filters, kernel_size, strides=(1, 1), bias=True):
        init_weight = np.load(f"{PRETRAINED_WEIGHT_DIR}/{style}/{name}.weight.npy")
        init_weight = np.transpose(init_weight, [2, 3, 1, 0])
        init_bias = np.load(f"{PRETRAINED_WEIGHT_DIR}/{style}/{name}.bias.npy")

        if bias:
            bias_initializer = tf.keras.initializers.constant(init_bias)
        else:
            bias_initializer = "zeros"

        layer = tf.keras.layers.Conv2D(
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            kernel_initializer=tf.keras.initializers.constant(init_weight),
            bias_initializer=bias_initializer
        )
        return layer


    def instance_norm_layer(style, name, epsilon=1e-9):
        init_beta = np.load(f"{PRETRAINED_WEIGHT_DIR}/{style}/{name}.shift.npy")
        init_gamma = np.load(f"{PRETRAINED_WEIGHT_DIR}/{style}/{name}.scale.npy")

        layer = InstanceNormalization(
            axis=-1,
            epsilon=epsilon,
            beta_initializer=tf.keras.initializers.Constant(init_beta),
            gamma_initializer=tf.keras.initializers.Constant(init_gamma)
        )
        return layer


    def deconv_layers(style, name, filters, kernel_size, strides=(1, 1)):
        init_weight = np.load(f"{PRETRAINED_WEIGHT_DIR}/{style}/{name}.weight.npy")
        init_weight = np.transpose(init_weight, [2, 3, 1, 0])
        init_bias = np.load(f"{PRETRAINED_WEIGHT_DIR}/{style}/{name}.bias.npy")

        layers = list()
        layers.append(tf.keras.layers.Conv2DTranspose(
            filters=filters,
            kernel_size=kernel_size,
            strides=strides,
            kernel_initializer=tf.keras.initializers.constant(init_weight),
            bias_initializer=tf.keras.initializers.constant(init_bias)
        ))

        layers.append(tf.keras.layers.Cropping2D(cropping=((1, 0), (1, 0))))
        return layers


    def load_model(style):
        inputs = tf.keras.Input(shape=(None, None, 3))

        y = ReflectionPadding2D(padding=(3, 3))(inputs)
        y = conv_layer(style, "conv01_1", filters=64, kernel_size=7)(y)
        y = instance_norm_layer(style, "in01_1")(y)
        y = tf.keras.layers.Activation("relu")(y)

        y = ReflectionPadding2D(padding=(1, 1))(y)
        y = conv_layer(style, "conv02_1", filters=128, kernel_size=3, strides=(2, 2))(y)
        y = ReflectionPadding2D(padding=(1, 1))(y)
        y = conv_layer(style, "conv02_2", filters=128, kernel_size=3, strides=(1, 1))(y)
        y = instance_norm_layer(style, "in02_1")(y)
        y = tf.keras.layers.Activation("relu")(y)

        y = ReflectionPadding2D(padding=(1, 1))(y)
        y = conv_layer(style, "conv03_1", filters=256, kernel_size=3, strides=(2, 2))(y)
        y = ReflectionPadding2D(padding=(1, 1))(y)
        y = conv_layer(style, "conv03_2", filters=256, kernel_size=3, strides=(1, 1))(y)
        y = instance_norm_layer(style, "in03_1")(y)

        t_prev = tf.keras.layers.Activation("relu")(y)

        for i in range(4, 12):
            y = ReflectionPadding2D(padding=(1, 1))(t_prev)
            y = conv_layer(style, "conv%02d_1" % i, filters=256, kernel_size=3)(y)
            y = instance_norm_layer(style, "in%02d_1" % i)(y)
            y = tf.keras.layers.Activation("relu")(y)

            t = ReflectionPadding2D(padding=(1, 1))(y)
            t = conv_layer(style, "conv%02d_2" % i, filters=256, kernel_size=3)(t)
            t = instance_norm_layer(style, "in%02d_2" % i)(t)

            t_prev = tf.keras.layers.Add()([t, t_prev])

            if i == 11:
                y = t_prev

        layers = deconv_layers(style, "deconv01_1", filters=128, kernel_size=3, strides=(2, 2))
        for layer in layers:
            y = layer(y)
        y = ReflectionPadding2D(padding=(1, 1))(y)
        y = conv_layer(style, "deconv01_2", filters=128, kernel_size=3)(y)
        y = instance_norm_layer(style, "in12_1")(y)
        y = tf.keras.layers.Activation("relu")(y)

        layers = deconv_layers(style, "deconv02_1", filters=64, kernel_size=3, strides=(2, 2))
        for layer in layers:
            y = layer(y)
        y = ReflectionPadding2D(padding=(1, 1))(y)
        y = conv_layer(style, "deconv02_2", filters=64, kernel_size=3)(y)
        y = instance_norm_layer(style, "in13_1")(y)
        y = tf.keras.layers.Activation("relu")(y)

        y = ReflectionPadding2D(padding=(3, 3))(y)
        y = conv_layer(style, "deconv03_1", filters=3, kernel_size=7)(y)
        y = tf.keras.layers.Activation("tanh")(y)

        model = tf.keras.Model(inputs=inputs, outputs=y)

        return model


    # cartoonGAN
    if (style == "hayao") | (style == "paprika"):
        PRETRAINED_WEIGHT_DIR = '/home/sjh7397/test_pythonanywhere/model/cartoongan/pretrained_weights' # 저장된 pretrained 모델 가중치 파일 경로
        cartoonGAN_model = load_model(style)
        input_image = result
        input_image = np.expand_dims(input_image, axis=0)
        output_image = cartoonGAN_model.predict(input_image)
        output_image = output_image[0]
        output_image = output_image[:,:,[2,1,0]]
        output_image = output_image * 0.5 + 0.5
        alpha_output = cv2.cvtColor(output_image, cv2.COLOR_RGB2RGBA)
        resize_alpha = cv2.resize(alpha_scale, (output_image.shape[1],output_image.shape[0]))
        alpha_output[:,:,3] = resize_alpha
        alpha_output_2= alpha_output*255
        alpha_output_2 = alpha_output_2.astype(np.uint8)
        # alpha_output_2 = cv2.cvtColor(alpha_output_2, cv2.COLOR_RGBA2BGRA)
        cv2.imwrite(f'/home/sjh7397/test_pythonanywhere/static/output_img/{style}_{date_string}.png', alpha_output_2)

    else :
        model_dir = f'/home/sjh7397/test_pythonanywhere/model/saved_model/{style}' # 저장한 모델 디렉토리 경로
        model = tf.saved_model.load(model_dir)
        f = model.signatures["serving_default"]
        input_image = result
        input_image = np.expand_dims(input_image, 0).astype(np.float32) / 127.5 -1
        output_image = f(tf.constant(input_image))['output_1']
        output_image = ((output_image.numpy().squeeze() + 1) * 127.5).astype(np.uint8)
        alpha_output = cv2.cvtColor(output_image, cv2.COLOR_RGB2RGBA)
        resize_alpha = cv2.resize(alpha, (output_image.shape[1],output_image.shape[0]))
        alpha_output[:,:,3] = resize_alpha
        alpha_output_2= alpha_output
        alpha_output_2 = alpha_output_2.astype(np.uint8)
        # alpha_output_2 = cv2.cvtColor(alpha_output_2, cv2.COLOR_RGBA2BGRA)
        cv2.imwrite(f'/home/sjh7397/test_pythonanywhere/static/output_img/{style}_{date_string}.png', alpha_output_2)

    # 해상도 개선
    os.system(f'python inference_realesrgan.py -n RealESRGAN_x4plus_anime_6B -i /home/sjh7397/test_pythonanywhere/static/output_img/{style}_{date_string}.png  -o /home/sjh7397/test_pythonanywhere/static/output_img')


    return render_template('result.html', img_file=f'output_img/{style}_{date_string}_out.png' )

if __name__ == '__main__':
    app.run(debug=True) # 파이썬 파일을 직접 실행할 경우 app.run 수행