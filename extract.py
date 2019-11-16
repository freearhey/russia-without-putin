# USAGE
# python extract.py -d dataset-small

# import the necessary packages
import argparse
import imutils
import pickle
import cv2
import os
import cvlib as cv
from imutils import paths

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
	help="path to input directory of faces + images")
ap.add_argument("-e", "--embeddings", default="output/embeddings",
	help="path to output serialized db of facial embeddings")
ap.add_argument("-m", "--embedding-model", default="openface_nn4.small2.v1.t7",
	help="path to OpenCV's deep learning face embedding model")
args = vars(ap.parse_args())

# load our serialized face embedding model from disk
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(args["embedding_model"])

# grab the paths to the input images in our dataset
print("[INFO] quantifying faces...")
imagePaths = list(paths.list_images(args["dataset"]))

# initialize our lists of extracted facial embeddings and
# corresponding people names
embeddings = []
names = []

# initialize the total number of faces processed
total = 0

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
	# extract the person name from the image path
	print("[INFO] processing image {}/{}".format(i + 1,
		len(imagePaths)))
	name = imagePath.split(os.path.sep)[-2]

	# load the image, resize it to have a width of 600 pixels (while
	# maintaining the aspect ratio), and then grab the image
	# dimensions
	image = cv2.imread(imagePath)

	# construct a blob from the image
	imageBlob = cv2.dnn.blobFromImage(
		cv2.resize(image, (300, 300)), 1.0, (300, 300),
		(104.0, 177.0, 123.0), swapRB=False, crop=False)

	faces, confidences = cv.detect_face(image) 

	for faceBounds in faces:
		(startX, startY, endX, endY) = faceBounds

		# extract the face ROI and grab the ROI dimensions
		face = image[startY:endY, startX:endX]

		# construct a blob for the face ROI, then pass the blob
		# through our face embedding model to obtain the 128-d
		# quantification of the face
		faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255,
			(96, 96), (0, 0, 0), swapRB=True, crop=False)
		embedder.setInput(faceBlob)
		vec = embedder.forward()

		# add the name of the person + corresponding face
		# embedding to their respective lists
		embeddings.append(vec.flatten())
		names.append(name)
		total += 1

# dump the facial embeddings + names to disk
print("[INFO] serializing {} encodings...".format(total))
data = {"embeddings": embeddings, "names": names}
f = open(args["embeddings"], "wb")
f.write(pickle.dumps(data))
f.close()