import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))) #상위 폴더 import
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))) # 상위 상위 폴더 import
import basicFunction as bf
import numpy as np
import keras as kr
import tensorflow as tf
import time
from numpy import array
from sklearn.metrics import precision_score, recall_score, confusion_matrix, classification_report, accuracy_score, f1_score
from sklearn.model_selection import KFold

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # imac setting.

def weight_variable(shape):
	initial = tf.truncated_normal(shape, stddev=0.1)
	return tf.Variable(initial)

def bias_variable(shape):
	initial = tf.constant(0.1, shape=shape)
	return tf.Variable(initial)

def conv2d(x, W):
	return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x1(x):
	return tf.nn.max_pool(x, ksize=[1, 2, 1, 1], strides=[1, 2, 1, 1], padding='SAME')

def max_pool_1x2(x):
	return tf.nn.max_pool(x, ksize=[1, 1, 2, 1], strides=[1, 1, 2, 1], padding='SAME')

def max_pool_2x2(x):
	return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

def aver_pool(x):
	return tf.nn.avg_pool(x, ksize=[1, 1, 3, 1], strides=[1, 1, 3, 1], padding='SAME')

if __name__ == "__main__":
	cTime = time.localtime()
	KFOLD = 5
	logDir = "../log/paperModel_CNN_%04d%02d%02d_" % (cTime.tm_year, cTime.tm_mon, cTime.tm_mday) + str(KFOLD) + "fold/"
	logFile = "%02d:%02d:%02d" % (cTime.tm_hour, cTime.tm_min, cTime.tm_sec) + ".log"
	if not os.path.isdir(logDir):
		os.mkdir(logDir)

	logPath = logDir + logFile
	BATCHSIZE = 50
	filePath = '../data/20191208/stft/win10000/abs+imag/'
	patternName = ['circle', 'close-open', 'high-low', 'left-right', 'low-high', 'nothing', 'open-close', 'right-left']

	numFreq = 20
	numAudioData = 245
	numTotalAud = numFreq * numAudioData
	numTotalAcc = numTotalAud
	windowSize = 10000
	numLabel = len(patternName)
	bf.allNumber = 0

	data = []
	#audioData = []
	for fileIndex in range(1,101):
		for patternIndex in range(len(patternName)):
			fileName = patternName[patternIndex]+"/"+patternName[patternIndex]+"_"+str(fileIndex)+".csv"
			if (patternName[patternIndex] == 'a'):
				label = '0'
			else:
				#label = patternName[patternIndex]
				label = patternIndex
			#tmp = bf.onlyFileRead(filePath, fileName, label)
			tmp = bf.audRead(filePath, fileName, label)
			data.append(tmp)
	np.random.shuffle(data)

	result_accuracy = np.zeros(shape=(KFOLD))
	result_precision = np.zeros(shape=(KFOLD))
	result_recall = np.zeros(shape=(KFOLD))
	result_f1Score = np.zeros(shape=(KFOLD))

	result_accuracy2 = np.zeros(shape=(KFOLD))
	result_precision2 = np.zeros(shape=(KFOLD))
	result_recall2 = np.zeros(shape=(KFOLD))
	result_f1Score2 = np.zeros(shape=(KFOLD))

	count = 0

	kf = KFold(n_splits = KFOLD)
	kf.get_n_splits(data)
	data = np.array(data)

	for train_index, test_index in kf.split(data):
		dataTrain, dataTest = data[train_index], data[test_index]

		#dTrain = bf.onlySampleSize(dataTrain, 1)
		dTrain = bf.sampleSize(dataTrain, 1)

		acc_xTrain = []
		acc_yTrain = []
		aud_xTrain = []
		aud_yTrain = []
		xTrain = []
		yTrain = []
		for d in dTrain:
			acc_xTrain.append(d[0 : numTotalAcc])
			aud_xTrain.append(d[numTotalAcc : numTotalAcc + numTotalAud])
			xTrain.append(d[0 : numTotalAcc + numTotalAud])
			acc_yTrain.append(bf.oneHotLabel(int(d[-1]), numLabel))
			aud_yTrain.append(bf.oneHotLabel(int(d[-1]), numLabel))
			yTrain.append(bf.oneHotLabel(int(d[-1]), numLabel))
		print('acc_xTrain : ', len(acc_xTrain))
		print('aud_xTrain : ', len(aud_xTrain))

	#       on Imac the GPU is not working. so
		with tf.device('/gpu:3'):
			acc_inputX = tf.placeholder(tf.float32, [None, numTotalAud])
			acc_outputY = tf.placeholder(tf.float32, [None, numLabel])
			keep_prob = tf.placeholder(tf.float32)

			W_conv11 = weight_variable([1, 3, 1, 4])
			#bias = 출력 갯수= kernel 수= filter 수
			b_conv11 = bias_variable([4])
			x_image = tf.reshape(acc_inputX, [-1, numFreq, numAudioData, 1])
			h_conv11 = tf.nn.relu(conv2d(x_image, W_conv11) + b_conv11)
			h_pool11 = max_pool_1x2(h_conv11)
		
			W_conv12 = weight_variable([1, 3, 4, 8])
			b_conv12 = bias_variable([8])
			h_conv12 = tf.nn.relu(conv2d(h_pool11, W_conv12) + b_conv12)
			h_pool12 = max_pool_1x2(h_conv12)

			W_conv13 = weight_variable([1, 3, 8, 16])
			b_conv13 = bias_variable([16])
			h_conv13 = tf.nn.relu(conv2d(h_pool12, W_conv13) + b_conv13)
			h_pool13 = max_pool_1x2(h_conv13)

			W_conv14 = weight_variable([1, 3, 16, 32])
			b_conv14 = bias_variable([32])
			h_conv14 = tf.nn.relu(conv2d(h_pool13, W_conv14) + b_conv14)
			h_pool14 = max_pool_1x2(h_conv14)

			W_conv15 = weight_variable([1, 3, 32, 64])
			b_conv15 = bias_variable([64])
			h_conv15 = tf.nn.relu(conv2d(h_pool14, W_conv15) + b_conv15)
			h_pool15 = max_pool_2x2(h_conv15)
			
			W_conv16 = weight_variable([1, 3, 64, 128])
			b_conv16 = bias_variable([128])
			h_conv16 = tf.nn.relu(conv2d(h_pool15, W_conv16) + b_conv16)
			h_pool16 = max_pool_2x2(h_conv16)
		
			W_conv17 = weight_variable([1, 3, 128, 256])
			b_conv17 = bias_variable([256])
			h_conv17 = tf.nn.relu(conv2d(h_pool16, W_conv17) + b_conv17)
			h_pool17 = max_pool_2x2(h_conv17)

			W_conv18 = weight_variable([1, 3, 256, 512])
			b_conv18 = bias_variable([512])
			h_conv18 = tf.nn.relu(conv2d(h_pool17, W_conv18) + b_conv18)
			h_pool18 = max_pool_2x2(h_conv18)

			W_conv19 = weight_variable([1, 3, 512, 1024])
			b_conv19 = bias_variable([1024])
			h_conv19 = tf.nn.relu(conv2d(h_pool18, W_conv19) + b_conv19)
			h_pool19 = max_pool_2x2(h_conv19)

			h_pool_aver = aver_pool(h_pool19)
			h_pool12_flat = tf.reshape(h_pool_aver, [-1, 1* 1 * 1024])

			W_fc13 = weight_variable([1024, numLabel])
			b_fc13 = bias_variable([numLabel])
			y_conv1 = tf.nn.softmax(tf.matmul(h_pool12_flat, W_fc13) + b_fc13)	

			cross_entropy1 = -tf.reduce_sum(acc_outputY * tf.log(tf.clip_by_value(y_conv1, 1e-10, 1.0)))
			train_step1 = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy1)
			correct_prediction1 = tf.equal(tf.argmax(y_conv1, 1), tf.argmax(acc_outputY, 1))
			accuracy1 = tf.reduce_mean(tf.cast(correct_prediction1, tf.float32))



		#Audio model
			aud_inputX = tf.placeholder(tf.float32, [None, numTotalAud])
			aud_outputY = tf.placeholder(tf.float32, [None, numLabel])

			W_conv21 = weight_variable([1, 3, 1, 4])
			#bias = 출력 갯수= kernel 수= filter 수
			b_conv21 = bias_variable([4])
			x_image = tf.reshape(aud_inputX, [-1, numFreq, numAudioData, 1])
			h_conv21 = tf.nn.relu(conv2d(x_image, W_conv21) + b_conv21)
			h_pool21 = max_pool_1x2(h_conv21)
		
			W_conv22 = weight_variable([1, 3, 4, 8])
			b_conv22 = bias_variable([8])
			h_conv22 = tf.nn.relu(conv2d(h_pool21, W_conv22) + b_conv22)
			h_pool22 = max_pool_1x2(h_conv22)

			W_conv23 = weight_variable([1, 3, 8, 16])
			b_conv23 = bias_variable([16])
			h_conv23 = tf.nn.relu(conv2d(h_pool22, W_conv23) + b_conv23)
			h_pool23 = max_pool_1x2(h_conv23)

			W_conv24 = weight_variable([1, 3, 16, 32])
			b_conv24 = bias_variable([32])
			h_conv24 = tf.nn.relu(conv2d(h_pool23, W_conv24) + b_conv24)
			h_pool24 = max_pool_1x2(h_conv24)

			W_conv25 = weight_variable([1, 3, 32, 64])
			b_conv25 = bias_variable([64])
			h_conv25 = tf.nn.relu(conv2d(h_pool24, W_conv25) + b_conv25)
			h_pool25 = max_pool_2x2(h_conv25)
			
			W_conv26 = weight_variable([1, 3, 64, 128])
			b_conv26 = bias_variable([128])
			h_conv26 = tf.nn.relu(conv2d(h_pool25, W_conv26) + b_conv26)
			h_pool26 = max_pool_2x2(h_conv26)
		
			W_conv27 = weight_variable([1, 3, 128, 256])
			b_conv27 = bias_variable([256])
			h_conv27 = tf.nn.relu(conv2d(h_pool26, W_conv27) + b_conv27)
			h_pool27 = max_pool_2x2(h_conv27)

			W_conv28 = weight_variable([1, 3, 256, 512])
			b_conv28 = bias_variable([512])
			h_conv28 = tf.nn.relu(conv2d(h_pool27, W_conv28) + b_conv28)
			h_pool28 = max_pool_2x2(h_conv28)

			W_conv29 = weight_variable([1, 3, 512, 1024])
			b_conv29 = bias_variable([1024])
			h_conv29 = tf.nn.relu(conv2d(h_pool28, W_conv29) + b_conv29)
			h_pool29 = max_pool_2x2(h_conv29)

			h_pool_aver = aver_pool(h_pool29)
			h_pool22_flat = tf.reshape(h_pool_aver, [-1, 1* 1 * 1024])

			W_fc23 = weight_variable([1024, numLabel])
			b_fc23 = bias_variable([numLabel])
			y_conv2 = tf.nn.softmax(tf.matmul(h_pool22_flat, W_fc23) + b_fc23)	

			#y_conv3 = kr.layers.Add()([y_conv1, y_conv2])
			y_conv3 = tf.maximum(y_conv1, y_conv2)

			cross_entropy2 = -tf.reduce_sum(aud_outputY * tf.log(tf.clip_by_value(y_conv2, 1e-10, 1.0)))
			train_step2 = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy2)
			correct_prediction2 = tf.equal(tf.argmax(y_conv2, 1), tf.argmax(aud_outputY, 1))
			accuracy2 = tf.reduce_mean(tf.cast(correct_prediction2, tf.float32))

			cross_entropy3 = -tf.reduce_sum(aud_outputY * tf.log(tf.clip_by_value(y_conv3, 1e-10, 1.0)))
			train_step3 = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy3)
			correct_prediction3 = tf.equal(tf.argmax(y_conv3, 1), tf.argmax(aud_outputY, 1))
			accuracy3 = tf.reduce_mean(tf.cast(correct_prediction3, tf.float32))

		#saver = tf.train.Saver()
		sess = tf.InteractiveSession()
		sess.run(tf.global_variables_initializer())
		acc_xTrain = array(acc_xTrain).reshape(len(acc_xTrain), numTotalAcc)
		acc_yTrain = array(acc_yTrain).reshape(len(acc_yTrain), numLabel)

		aud_xTrain = array(aud_xTrain).reshape(len(aud_xTrain), numTotalAud)
		aud_yTrain = array(aud_yTrain).reshape(len(aud_yTrain), numLabel)

		xTrain = array(xTrain).reshape(len(xTrain), numTotalAcc + numTotalAud)
		yTrain = array(yTrain).reshape(len(yTrain), numLabel)

		bf.mLog("training Start", logPath)


		for j in range(10001):
			batch_X, batch_Y = bf.getBatchData(BATCHSIZE, xTrain, yTrain)
			batch_XA = batch_X[:,0:numTotalAcc]
			batch_XB = batch_X[:,numTotalAcc : numTotalAcc + numTotalAud]
			train_step2.run(session=sess, feed_dict={aud_inputX:batch_XB, aud_outputY:batch_Y, keep_prob:0.5})

			if j % BATCHSIZE == 0:
				train_accuracy2 = accuracy2.eval(session=sess, feed_dict={aud_inputX: batch_XB, aud_outputY: batch_Y, keep_prob:1.0})	
				bf.mLog("AUD step %d, AUD accuracy %g" % (j, train_accuracy2), logPath)
				#bf.mLog("AUD step %d, tst accuracy %g" % (j, test_accuracy), logPath)
				#h1 = sess.run(y_conv1, feed_dict={acc_inputX: batch_XA, acc_outputY: batch_Y, aud_inputX: batch_XB, aud_outputY: batch_Y, keep_prob:1.0}) 
				#h2 = sess.run(y_conv2, feed_dict={acc_inputX: batch_XA, acc_outputY: batch_Y, aud_inputX: batch_XB, aud_outputY: batch_Y, keep_prob:1.0}) 
				#h3 = sess.run(y_conv3, feed_dict={acc_inputX: batch_XA, acc_outputY: batch_Y, aud_inputX: batch_XB, aud_outputY: batch_Y, keep_prob:1.0}) 
				#print('h1 : ',h1)
				#print('h2 : ',h2)
				#print('h3 : ',h3)
		for j in range(10001):
			batch_X, batch_Y = bf.getBatchData(BATCHSIZE, xTrain, yTrain)
			batch_XA = batch_X[:,0:numTotalAcc]
			batch_XB = batch_X[:,numTotalAcc : numTotalAcc + numTotalAud]
			train_step1.run(session=sess, feed_dict={acc_inputX: batch_XA, acc_outputY: batch_Y, keep_prob:0.5})

			if j % BATCHSIZE == 0:
				train_accuracy = accuracy1.eval(session=sess, feed_dict={acc_inputX: batch_XA, acc_outputY: batch_Y, keep_prob:1.0})
				bf.mLog("ACC step %d, ACC accuracy %g" % (j, train_accuracy), logPath)
				#bf.mLog("AUD step %d, tst accuracy %g" % (j, test_accuracy), logPath)

		bf.mLog("training Finish", logPath)

		dTest = bf.sampleSize(dataTest, 1)

		acc_xTest = []
		acc_yTest = []
		aud_xTest = []
		aud_yTest = []
		for d in dTest:
			acc_xTest.append(d[0 : numTotalAcc])
			aud_xTest.append(d[numTotalAcc : numTotalAcc + numTotalAud])
			acc_yTest.append(bf.oneHotLabel(int(d[-1]), numLabel))
			aud_yTest.append(bf.oneHotLabel(int(d[-1]), numLabel))

		acc_xTest = array(acc_xTest).reshape(len(acc_xTest), numTotalAcc)
		aud_xTest = array(aud_xTest).reshape(len(aud_xTest), numTotalAud)
		bf.mLog("test Start", logPath)
		
		yPreTmp = tf.argmax(y_conv1, 1)
#		val_acc, yPred = sess.run([accuracy3, yPreTmp], feed_dict={acc_inputX: acc_xTest, acc_outputY: acc_yTest, aud_inputX: aud_xTest, aud_outputY: aud_yTest, keep_prob: 1.0})
		val_acc, yPred = sess.run([accuracy1, yPreTmp], feed_dict={acc_inputX: acc_xTest, acc_outputY: acc_yTest, keep_prob: 1.0})
		yTrue = np.argmax(aud_yTest, 1)
		bf.mLog("test finish", logPath)

		result_accuracy[count] = accuracy_score(yTrue, yPred)
		result_precision[count] = precision_score(yTrue, yPred, average = 'macro')
		result_recall[count] = recall_score(yTrue, yPred, average = 'macro')
		result_f1Score[count] = f1_score(yTrue, yPred, average = 'macro')
		result_confusion = str(confusion_matrix(yTrue, yPred))
		bf.mLog("%d-fold %dth" % (KFOLD, count+1), logPath)
		bf.mLog("accuracy : " + str(result_accuracy[count]), logPath)
		bf.mLog("precision : " + str(result_precision[count]), logPath)
		bf.mLog("recall : " + str(result_recall[count]), logPath)
		bf.mLog("f1 Score : " +str(result_f1Score[count]), logPath)
		count = count + 1

		sess.close()

	modelAccuracy = 0
	modelPrecision = 0
	modelRecall = 0
	modelF1Score = 0

	for j in range(0, count):
		modelAccuracy = modelAccuracy + result_accuracy[j]
		modelPrecision = modelPrecision + result_precision[j]
		modelRecall = modelRecall + result_recall[j]
		modelF1Score = modelF1Score + result_f1Score[j]

	modelAccuracy = modelAccuracy / KFOLD
	modelPrecision = modelPrecision /KFOLD
	modelRecall = modelRecall / KFOLD
	modelF1Score = modelF1Score / KFOLD

	bf.mLog("total Accuracy : " + str(modelAccuracy), logPath)
	bf.mLog("total Precision : " + str(modelPrecision), logPath)
	bf.mLog("total Recall : " + str(modelRecall), logPath)
	bf.mLog("total f1 score : " + str(modelF1Score), logPath)