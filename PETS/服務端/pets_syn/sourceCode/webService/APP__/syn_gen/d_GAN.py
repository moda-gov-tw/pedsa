###tensorflow-gpu-1.0.0
###keras2.0.6
import sys
import os
os.environ["KERAS_BACKEND"] = "tensorflow"
import numpy as np
import tensorflow as tf
from tqdm import tqdm
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from keras.layers import Input, Activation
from keras.models import Model, Sequential
from keras.layers.core import Reshape, Dense, Dropout, Flatten
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import Convolution2D, UpSampling2D
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l1, l2

from keras.optimizers import Adam,SGD
from keras import backend as K
from keras import initializers
from keras.initializers import RandomNormal
import pandas as pd
#from bdistance import bhattacharyya
import time
import argparse
from sklearn import preprocessing
from keras.utils import multi_gpu_model
#from noisy_optimizers import NoisySGD, NoisyAdam
#from privacy_accountant.accountant import *

   
def pre_proccesing(directory,sum_col):
    #print("loading original data with class")
    dataset=pd.read_csv(os.path.join(directory,'pkl','test_category_conti.csv'),header=0)
    #print(dataset.head())
    dataset=np.array(dataset)
    row,col =  dataset.shape
    #print (dataset.shape)
    #print(sum_col)
    if sum_col != col:
        min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
        X = min_max_scaler.fit_transform(dataset[:,sum_col:col])#-1])
        X = pd.DataFrame(X)
        df_slice = pd.DataFrame(dataset[:,0:sum_col])
        X = pd.concat([df_slice, X],axis=1)
        #print(X.head())
        #print(X.shape)
        dataset = np.array(X)
        row,col =  dataset.shape
    return dataset, col

def pre_proccesing_conti(file_path,sum_col):
    print("loading original data with class")
    dataset=pd.read_csv(file_path,header=0)
    #print(dataset.head())
    dataset=np.array(dataset)
    row,col =  dataset.shape
    print (dataset.shape)
    print(sum_col)
    min_max_scaler = preprocessing.MinMaxScaler(feature_range=(-1, 1))
    X = min_max_scaler.fit_transform(dataset[:,0:col])#-1])
    #print(X[:2])
    return X, col

def generation(directory,file_path,sum_col,GAN_flag):
    
    #create come folder to save images/loss or models
#     dir_=(directory+'fake_generatebyGAN_OHE/')
#     if not os.path.exists(dir_):
#         os.mkdir(dir_)
    dir_syn=os.path.join(directory,'synthetic')
    if not os.path.exists(dir_syn):
        os.mkdir(dir_syn)
    dir_loss=os.path.join(directory,'loss')
    if not os.path.exists(dir_loss):
        os.mkdir(dir_loss)
    dir_model=os.path.join(directory,'models')
    if not os.path.exists(dir_model):
        os.mkdir(dir_model)
    
    
    # The results are a little better when the dimensionality of the random vector is only 10.
    # The dimensionality has been left at 100 for consistency with other GAN implementations.
    # randomDim
    if GAN_flag == 'False': #all cols are continuous
        X_train, randomDim = pre_proccesing_conti(file_path,sum_col)
    elif GAN_flag == 'True':
        X_train, randomDim = pre_proccesing(directory,sum_col)
    
    # Function for initializing network weights
    def initNormal(shape, dtype=None):
        return RandomNormal(mean=0.0, stddev=0.02, seed=None)

    # Optimizer
    adam = Adam(lr=1e-4, beta_1=0.5)
    sgd=SGD(lr=0.005)
    ###############build_generator#######################
    generator = Sequential()
    generator.add(Dense(128, input_dim=randomDim,kernel_initializer=initializers.random_normal(stddev=0.8)))# init=initNormal))
    #generator.add(LeakyReLU())
    generator.add(Activation('relu'))
    generator.add(Dense(int(128*2)))
    generator.add(Activation('relu'))
    generator.add(Dense(int(randomDim)))
    #generator.add(LeakyReLU())
    #generator.add(Dense(randomDim))#, activation='tanh'))

    ##SGD
    #generator.compile(loss='binary_crossentropy', optimizer=sgd)
    ##adam
    generator.compile(loss='binary_crossentropy', optimizer=adam)

    ###############build_discriminator#######################
    discriminator = Sequential()
    discriminator.add(Dense(int(128*2), input_dim=randomDim,kernel_initializer=initializers.random_normal(stddev=0.8)))# init=initNormal))
    discriminator.add(Activation('relu'))
    #discriminator.add(LeakyReLU())
    discriminator.add(Dropout(0.1))
    discriminator.add(Dense(128))
    #discriminator.add(LeakyReLU())
    discriminator.add(Dense(1, activation='sigmoid'))

    ##adam
    discriminator.compile(loss='binary_crossentropy', optimizer=Adam(lr=1e-4, beta_1=0.5))
    ###############combined network#######################
    # Combined network
    discriminator.trainable = False
    ganInput = Input(shape=(randomDim,))
    x = generator(ganInput)
    ganOutput = discriminator(x)
    gan = Model(input=ganInput, output=ganOutput)

    ##SGD
    #gan.compile(loss='binary_crossentropy', optimizer=sgd)

    #adam
#     gan.compile(loss='binary_crossentropy', optimizer=adam)
    
    
#     with tf.device('/cpu:0'):
#            model = gan
#     gan = multi_gpu_model(gan,4)
    gan.compile(loss='binary_crossentropy', optimizer=adam)
    #########################################################
    dLosses = []
    gLosses = []

    # Plot the loss from each batch
    def plotLoss(directory,epoch):
        plt.figure(figsize=(10, 8))
        plt.plot(dLosses, label='Discriminitive loss')
        plt.plot(gLosses, label='Generative loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(dir_loss+'/gan_loss_epoch_%d.png' % epoch)
    # Save the generator and discriminator networks (and weights) for later use
    def saveModels(directory,epoch):
        generator.save(dir_model+'/gan_generator_epoch_%d.h5' % epoch)
#         discriminator.save(dir_model+'/gan_discriminator_epoch_%d.h5' % epoch)

    def train(epochs=120, batchSize=10):
        #print((args))
        batchCount = X_train.shape[0] / batchSize
        #print('Epochs:', epochs)
        #print('Batch size:', batchSize)
        #print('Batches per epoch:', batchCount)
    
        #print(X_train.shape[0])
        config = tf.ConfigProto()
        config.gpu_options.allow_growth=True
    
        with tf.Session(config=config) as sess:
            #eps = tf.placeholder(tf.float32)
            #delta = tf.placeholder(tf.float32)
            sess.run(tf.initialize_all_variables())
            initial_time= time.time()
#             initial_time=time.clock()
            for e in range(1, epochs+1):
                #print('-'*15 + 'Epoch %d' % e + '-'*15)
#                 train_start_time = time.clock()
                # for _ in tqdm(range(int(batchCount))):
                for _ in range(int(batchCount)):
                    # Get a random set of input noise and images
                    noise = np.random.normal(0, 1, (batchSize, randomDim))
                    imageBatch = X_train[np.random.randint(0, X_train.shape[0], size=batchSize)]

                    # Generate fake MNIST images
                    #print noise.shape
                    generatedImages = generator.predict(noise)
                    # print np.shape(imageBatch), np.shape(generatedImages)
                    X = np.concatenate([imageBatch, generatedImages])
    
                    # Labels for generated and real data
                    yDis = np.zeros(2*batchSize)
                    # One-sided label smoothing
                    yDis[:batchSize] = 0.9

                    # Train discriminator
                    discriminator.trainable = True
                    dloss = discriminator.train_on_batch(X, yDis)

                    # Train generator
                    noise = np.random.normal(0, 1, size=[batchSize, randomDim])
                    yGen = np.ones(batchSize)
                    discriminator.trainable = False
                    gloss = gan.train_on_batch(noise, yGen)

                # Store loss of most recent batch from this epoch
                dLosses.append(dloss)
                gLosses.append(gloss)

#                 print('\n Train time: ', time.clock() - train_start_time)
                #print('accum privacy, batches: ' + str(batchCount))
#                 priv_start_time = time.clock()


                if  e % 10 == 0:
                    plotLoss(directory,e)

    #             if  e % 5 == 0:
    #                 plotGeneratedImages(e)
    #                     #plotLoss(e)

                if e == 1 or e % 3 == 0:
                    saveModels(directory,e)

                # Plot losses from every epoch

            total_time = time.time() - initial_time
            #print ("This took %.2f seconds" % (total_time))
            return total_time
#     total_time = train(200, 32)   
    total_time = train(50,256) #(30, 32)  
    #print('GAN Train time: ', total_time )
    ##https://github.com/keras-team/keras/issues/9204
