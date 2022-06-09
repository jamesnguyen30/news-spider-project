import tensorflow as tf
gpus = tf.config.list_physical_devices('GPU')
print("Num GPUs Available: ", len(gpus))


# tf.test.gpu_device_name()

if gpus:
    try:
        for gpu in gpus:
            print('Set GPU ', gpu, ' memory growth to True')
            tf.config.experimental.set_memory_growth(gpu, True)

        logical_gpus = tf.config.list_logical_devices('GPU')
        print('Physical GPUs ', len(gpus), ', Logical GPUs ', len(logical_gpus))
    except RuntimeError as e:
        print(e)
    
from transformers import BertTokenizer, TFBertForSequenceClassification
from sklearn.preprocessing import LabelEncoder
import numpy as np
import os
import pathlib

CWD = pathlib.Path(__file__).parent

class SentimentModel:

    def __init__(self):
        self.PRODUCTION_DIR = os.path.join(CWD, 'production')
        self.PRODUCTION_MODEL = os.path.join(self.PRODUCTION_DIR, 'trained_bert')
        self.BERT_BASED_UNCASED = os.path.join(self.PRODUCTION_DIR, 'bert-base-uncased')

        print(f"Loading BERT model from {self.PRODUCTION_MODEL}") 

        self.model = TFBertForSequenceClassification.from_pretrained(self.PRODUCTION_MODEL)

        self.tokenizer = BertTokenizer.from_pretrained(self.BERT_BASED_UNCASED, do_lower_case = True)
        self.label_encoder = LabelEncoder()

        classes = list()
        with open(os.path.join(self.PRODUCTION_DIR, 'label_encoder_classes.txt'), 'r') as file:
            for line in file.readlines():
                classes.append(line.strip())

        self.label_encoder.classes_ = np.asarray(classes)

        print("[SUCCESS] Loaded BERT model")
    
    def summary(self):
        print(self.model.summary())
    
    def predict(self, data: list) -> list:
        '''
        predict labels based on submitted data

        @params:
            list data: list of string
        
        @returns
            list labels: list of string 
        '''

        input = self.tokenizer(
            data,
            padding = True,
            max_length = 81,
            truncation=True,
            return_tensors = 'tf'
        )

        X_input = {
            "input_ids": np.asarray(input['input_ids']),
            "token_type_ids": np.asarray(input['token_type_ids']),
            "attention_mask": np.asarray(input['attention_mask']),
        }

        pred = self.model.predict(X_input)

        pred_prob = tf.nn.softmax(pred.logits).numpy()
        final_pred = tf.argmax(pred_prob, axis = 1).numpy()

        labels = list(self.label_encoder.inverse_transform(final_pred))

        return labels





