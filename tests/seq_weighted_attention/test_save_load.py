import unittest
import os
import tempfile
import random
import keras
from keras_self_attention import SeqWeightedAttention as Attention


class TestSaveLoad(unittest.TestCase):

    def _test_save_load(self, attention):
        inputs = keras.layers.Input(shape=(None,), name='Input')
        embd = keras.layers.Embedding(input_dim=3,
                                      output_dim=5,
                                      mask_zero=True,
                                      name='Embedding')(inputs)
        lstm = keras.layers.Bidirectional(keras.layers.LSTM(units=7,
                                                            return_sequences=True),
                                          name='Bi-LSTM')(embd)
        weighted, attention = attention(lstm)
        dense = keras.layers.Dense(units=2, activation='softmax', name='Softmax')(weighted)
        model = keras.models.Model(inputs=inputs, outputs=[dense, attention])
        model.compile(
            optimizer='adam',
            loss={'Softmax': 'sparse_categorical_crossentropy'},
            metrics={'Softmax': 'sparse_categorical_accuracy'},
        )
        model_path = os.path.join(tempfile.gettempdir(), 'keras_weighted_att_test_sl_%f.h5' % random.random())
        model.save(model_path)
        model = keras.models.load_model(model_path, custom_objects=Attention.get_custom_objects())
        model.summary(line_length=100)

    def test_default(self):
        self._test_save_load(Attention(name='Attention'))

    def test_return_attention(self):
        self._test_save_load(Attention(return_attention=True, use_bias=False, name='Attention'))
