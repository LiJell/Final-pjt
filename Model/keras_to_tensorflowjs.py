# -*- coding: utf-8 -*-
"""keras_to_tensorflowjs

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gY-puOIH1RnluEGekY4sSrhW9FRteyqJ
"""



from google.colab import drive
drive.mount('/content/drive')

!pip install tensorflowjs

import tensorflow as tf
import tensorflowjs as tfjs

new_model = tf.keras.models.load_model("model path")

tfjs.converters.save_keras_model(new_model, "converted_model_saving_path")

