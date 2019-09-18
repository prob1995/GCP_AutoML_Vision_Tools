# gs = google storage

import subprocess
import csv
import os

from PIL import Image

def convert_image(source_folder,destination_folder, output_file_type):
    """ Convert image from different type to JPEG or PNG """
    print ("Converting files to",output_file_type,"from",source_folder,"to", destination_folder,"...")
    for (dirpath, dirnames, filenames) in os.walk(source_folder):
        for dirname in dirnames:
            for file in os.listdir(os.path.join(dirpath, dirname)):
                file_dir = os.path.join(dirpath, dirname)
                file_full_path = os.path.join(dirpath, dirname, file)
                if os.path.isfile(file_full_path):
                    im = Image.open(file_full_path)
                    out = im.convert("RGB")
                    relative_path = os.path.relpath(os.path.join(dirpath,dirname),source_folder)
                    file_no_ext = os.path.splitext(file)[0]
                    new_dir = os.path.join(destination_folder,relative_path)
                    
                    try:
                        os.makedirs(new_dir)        
                    except:
                        pass
                    
                    output_file_type = output_file_type.upper()
                    if output_file_type in ["JPG","JPEG"]:
                        output_file_type="JPEG"
                        out.save(os.path.join(new_dir,file_no_ext+'.'+output_file_type), output_file_type, quality=95)
                    elif output_file_type in ["PNG"]:
                        out.save(os.path.join(new_dir,file_no_ext+'.'+output_file_type), output_file_type, compress_level=0)
                    else:
                        out.save(os.path.join(new_dir,file_no_ext+'.'+output_file_type), output_file_type)
    return destination_folder

def upload_file(data_local, data_gs):
    """Upload file to GCP."""
    #subprocess.run(['gsutil','-m','cp','-r',data_local,data_gs])
    subprocess.run(['gsutil','-m','rsync','-r',data_local,data_gs])
    return "Upload OK."

def generate_csv(gs_folder, output_csv):
    """Generate .csv file to local and GCP"""
    train_folder = os.path.join(gs_folder, 'train')
    files_path = subprocess.run(['gsutil','ls','-r',train_folder], stdout=subprocess.PIPE).stdout.decode('utf-8')
    files_path = files_path.split('\n')
    with open(output_csv, 'w+', newline='') as outcsv:
            for file_path in files_path:
                try : 
                    full_path = os.path.split(file_path)
                    folder_name = os.path.basename(full_path[0])
                    file_name = full_path[1]
                    match_suff = [".jpg",".png",".jpeg"]
                    match_suff_lower = [x.lower() for x in match_suff]
                    match_suff_upper = [x.upper() for x in match_suff]
                    match_suff = tuple(match_suff_lower + match_suff_upper)
                    if file_name.endswith(match_suff):
                        writer = csv.writer(outcsv)
                        writer.writerow([file_path, folder_name])
                except:
                    raise
    subprocess.run(['gsutil','-m','cp','-r',output_csv,gs_folder])
    print ("GCP_csv_path: ", os.path.join(data_gs,output_csv))
    return "CSV has been generated and uploaded to GCP"

if __name__ == '__main__':
    data_local = '{YOUR_LOCAL_DATA_FOLDER_PATH}'  # Give "c:/data/flowers" if you have image data in c:/data/flowers/OK and c:/data/flowers/NG
    data_local_converted = data_local+"_"+ "PNG"
    data_gs = '{GS_PATH}'  # Where you want to upload to. ex. gs://automl_test/flowers/ 
    output_csv = 'data.csv'
    data_local_converted = convert_image(data_local,data_local_converted,"PNG")
    print (upload_file(data_local_converted, data_gs))
    print (generate_csv(data_gs, output_csv))