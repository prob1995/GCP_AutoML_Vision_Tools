import sys
import os
import json
import time

from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2
from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np

def get_prediction(content):
    """Use model from GCP AutoML Vision to do inference and get results"""
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content }}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request  # waits till request is returned

def get_prediction_folder(folder_path, project_id, model_id):
    """Use model from GCP AutoML Vision to do inference and get results"""
    time_a = time.time()
    prediction_client = automl_v1beta1.PredictionServiceClient()
    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    params = {}
    output = {}
    f = []
    time_b = time.time()
    print ("init_time: ", time_b-time_a, "(s)")
    with open("confusion_matrix.txt", 'w+') as cf:
        cf.write ("Results: ")
        cf.write ("\n")

    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        f.extend(filenames)
        for dirname in dirnames:
            label = dirname
            for file in os.listdir(os.path.join(dirpath, dirname)):
                time_c=time.time()
                file_path = os.path.join(dirpath, dirname, file)
                with open(file_path, 'rb') as ff:
                    content = ff.read()
                payload = {'image': {'image_bytes': content}}
                response = prediction_client.predict(name, payload, params)
                for result in response.payload:
                    score = result.classification.score
                    predict_result = result.display_name
                    output['file_path'] = file_path
                    output['predict_result']=predict_result
                    output['score']=score
                    output['true_label']=label
                    time_d = time.time()
                    output['inference_time']=time_d-time_c
                    output_json = json.dumps(output)
                    outputs.append(output_json)
                    print (output_json)
                    with open("confusion_matrix.txt", 'a+') as cf:
                        cf.write (output_json)
                        cf.write ("\n")
        #break
    return outputs

def get_confusion_matrix(datain):
    """Get Confusion Matrix and inference time."""
    predict = []
    actual = []
    time = []
    
    for data in datain:
        data = json.loads(data)
        predict.append(data["predict_result"])
        actual.append(data["true_label"])
        time.append(data["inference_time"])

    s = pd.Series(time)
    inference_time = s.describe()
    predict_pd = pd.Series(predict, name='Predicted')
    actual_pd = pd.Series(actual, name='Actual')
    confusion_matrix_pandas = pd.crosstab(actual_pd, predict_pd, dropna=False)
    confusion_matrix_scikit = confusion_matrix(actual, predict, labels=["OK", "NG"])
    print ()
    print ("Inference Time Analysis(s):")
    print (inference_time)
    print ()
    print ("Confusion Matrix (pandas): ")
    print (confusion_matrix_pandas)
    print ()
    print ("Confusion Matrix (scikit): ")
    print (confusion_matrix_scikit)
    print ()

    with open("confusion_matrix.txt", 'a+') as cf:
        cf.write("Inference Time Analysis(s):\n")
        cf.write (inference_time.to_string())
        cf.write ("\n")
        cf.write ("Confusion Matrix (pandas):\n")
        cf.write (confusion_matrix_pandas.to_string())
        cf.write ("\n")
        cf.write ("Confusion Matrix (scikit):\n")
        cf.write (np.array2string(confusion_matrix_scikit))

if __name__ == '__main__':
    testfolder_path = '{YOUR_LOCAL_DATA_FOLDER_TO_EVALUATE}'  # Give "c:/data/flowers" if you have image data in c:/data/flowers/OK and c:/data/flowers/NG
    project_id = "{GCP_AUTOML_PROJECT_ID}}"
    model_id = '{YOUR_TRAINED_MODEL_ID}' # ex ICN1234567800000000001
    outputs = []
    try:
        outputs = get_prediction_folder(testfolder_path, project_id, model_id)
        get_confusion_matrix(outputs)
    except KeyboardInterrupt:
        get_confusion_matrix(outputs)
        sys.exit()
