import os
import tarfile
abspath = os.path.abspath(__file__)

ROOT_PATH = os.path.dirname(abspath)


path = (ROOT_PATH+'/models')
a = os.listdir(path)
tar = tarfile.open(path+'/'+a[0])
tar.extractall(path)
tar.close()

