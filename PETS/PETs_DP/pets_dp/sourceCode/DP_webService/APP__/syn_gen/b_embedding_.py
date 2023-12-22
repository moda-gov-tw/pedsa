
# coding: utf-8
import numpy
numpy.random.seed(123)
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import Normalizer

from keras.models import Sequential
from keras.models import Model as KerasModel
from keras.layers import Input, Dense, Activation, Reshape
from keras.layers import Concatenate
from keras.layers.embeddings import Embedding
from keras.callbacks import ModelCheckpoint
from keras.optimizers import Adam
import pickle

train_ratio = 1.0
save_embeddings = True
saved_embeddings_fname = "pkl/embeddings.pickle"  # set save_embeddings to True to create this file

def sample(X, y, n):
    '''random samples'''
    num_row = X.shape[0]
    indices = numpy.random.randint(num_row, size=n)
    return X[indices, :], y[indices]

class Model(object):
    def evaluate(self, X_val, y_val):
        assert(min(y_val) > 0)
        guessed_sales = self.guess(X_val)
        relative_err = numpy.absolute((y_val - guessed_sales) / y_val)
        result = numpy.sum(relative_err) / len(y_val)
        return result
    
class NN_with_EntityEmbedding(Model):
    def __init__(self, X_train, y_train, X_val, y_val,col_name,unique_att_num):
        super().__init__()
        self.epochs = 5
        self.checkpointer = ModelCheckpoint(filepath="best_model_weights.hdf5", verbose=1, save_best_only=True)
        self.max_log_y = max(numpy.max(numpy.log(y_train)), numpy.max(numpy.log(y_val)))
        self.unique_att_num = unique_att_num
        self.col_name = col_name
        self.__build_keras_model()
        self.fit(X_train, y_train, X_val, y_val)
#         self.col_name = col_name
#         self.unique_att_num = unique_att_num
    
    def split_features(self, X):
        X_list = []
        for i in range(len(self.col_name)): #parameter:len(categorical cols)
            class_name = X[..., [i]]
            X_list.append(class_name)
        return X_list
    
    
    def preprocessing(self, X):
        X_list = self.split_features(X)
        return X_list

    def __build_keras_model(self):
        
        structure = self.unique_att_num
        input_model = [] 
        output_embeddings = []
        
        for layer in range(len(structure)):
            
            input_class_name = Input(shape=(1,))
            if (structure[layer] > 100):
                output_class_name = Embedding(structure[layer], int(5), name= self.col_name[layer]+'_embedding')(input_class_name)
                output_class_name = Reshape(target_shape=(int(5),))(output_class_name)
#                 output_class_name = Embedding(structure[layer], int(structure[layer]/20), name= self.col_name[layer]+'_embedding')(input_class_name)
#                 output_class_name = Reshape(target_shape=(int(structure[layer]/20),))(output_class_name)
            elif (100>=structure[layer] > 30):
                output_class_name = Embedding(structure[layer], int(5), name= self.col_name[layer]+'_embedding')(input_class_name)
                output_class_name = Reshape(target_shape=(int(5),))(output_class_name)
                
            else:    
                output_class_name = Embedding(structure[layer], int(structure[layer]/2), name= self.col_name[layer]+'_embedding')(input_class_name)
                output_class_name = Reshape(target_shape=(int(structure[layer]/2),))(output_class_name)
            
            input_model.append(input_class_name)
            output_embeddings.append(output_class_name)
        
        nn = [ ]
        nn.append(int(sum(structure)*5/3))
        nn.append(int(sum(structure)*2))

        if len(structure)==1: #only pick up one categorical col
            output_model = output_class_name

        else: 
            output_model = Concatenate()(output_embeddings)
        
        output_model = Dense(nn[0], kernel_initializer="uniform")(output_model)
        output_model = Activation('relu')(output_model)
        output_model = Dense(nn[1], kernel_initializer="uniform")(output_model)
        output_model = Activation('relu')(output_model)
        output_model = Dense(1)(output_model)
        output_model = Activation('sigmoid')(output_model)
       
        self.model = KerasModel(inputs=input_model, outputs=output_model)
        
        #self.model.compile(loss='mean_absolute_error', optimizer=Adam(lr=0.001, beta_2=0.01))
        self.model.compile(loss='mean_absolute_error', optimizer='adam',metrics=['mse','mape'])
        
    def _val_for_fit(self, val):
        val = numpy.log(val) / self.max_log_y
        return val

    def _val_for_pred(self, val):
        return numpy.exp(val * self.max_log_y)

    def fit(self, X_train, y_train, X_val, y_val):
        self.model.fit(self.preprocessing(X_train), self._val_for_fit(y_train),
                       validation_data=(self.preprocessing(X_val), self._val_for_fit(y_val)),
                       epochs=self.epochs, batch_size=32, verbose=0
                       # callbacks=[self.checkpointer],
                       )
        # self.model.load_weights('best_model_weights.hdf5')
        #print("Result on validation data: ", self.evaluate(X_val, y_val))

    def guess(self, features):
        features = self.preprocessing(features)
        result = self.model.predict(features).flatten()
        return self._val_for_pred(result)

def embedding(directory,col_name,unique_att_num):
    print("######################1")
    f = open(directory+'pkl/feature_train_data.pickle', 'rb')
    (X, y) = pickle.load(f)
    
    num_records = len(X)
    train_size = int(train_ratio * num_records)
    y = numpy.array(y)
    
    X_train = X[:train_size]
    X_val = X[:int(0.9*train_size)]
    y_train = y[:train_size]
    y_val = y[:int(0.9*train_size)]
    #print(X_train[:5], y_train[:5])
    
    
    #X_train, y_train = sample(X_train, y_train, 200000)  # Simulate data sparsity
    #print("Number of samples used for training: " + str(y_train.shape[0]))

    models = []

    #print("Fitting NN_with_EntityEmbedding...")
    # for i in range(10):
    #     models.append(NN_with_EntityEmbedding(X_train, y_train, X_val, y_val))
    print("######################2")
    models.append(NN_with_EntityEmbedding(X_train, y_train, X_val, y_val,col_name,unique_att_num))

    if save_embeddings:
        model = models[0].model
        
        embedding_name = []
        for name in col_name:
            embedding_name.append(model.get_layer(name+'_embedding').get_weights()[0])
        with open(directory+saved_embeddings_fname, 'wb') as f:
            pickle.dump(embedding_name, f, -1)    

    ####command: python 1_a_preparing_csv2feature.py -d adult.csv -col workclass marital_status occupation relationship race sex native_country class -tar_col class -transfer False
