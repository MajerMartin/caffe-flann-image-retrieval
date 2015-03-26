from flask import Flask, request, render_template, send_from_directory
from img_search import kdtree
import os.path
import cv2
import urllib
import numpy as np

# initialize flask server
app = Flask(__name__)

# image dimensions for features calculation
height = 227.
width = 227.

# switch between deployment (True) and local testing mode (False)
caffe_toggle = False

if caffe_toggle:
    import caffe

    # paths for caffe
    caffe_root = '/storage/plzen1/home/campr/metacentrum/caffe/caffe_cemi_7_dev'
    caffe_mean_fn = os.path.join(caffe_root, 'python/caffe/imagenet/ilsvrc_2012_mean.npy')
    caffe_deploy_fn = os.path.join(caffe_root, 'models/bvlc_reference_caffenet/deploy.prototxt')
    caffe_model_fn = os.path.join(caffe_root, 'models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel')

    # initialize caffe neural network
    net = caffe.Classifier(caffe_deploy_fn,
                       caffe_model_fn,
                       mean=np.load(caffe_mean_fn),
                       # imagenet uses BGR, same as opencv, swap is not needed:
                       #channel_swap=(2,1,0),
                       # bvlc_reference_caffenet uses pixel values [0, 255], but we don't normalize loaded image to [0.0-1.0], so it is scaled to [0.0, 255.0] already after conversion to float32
                       #raw_scale=255,
                       )
    # run net on cpu
    net.set_mode_cpu()

    # path to data folder
    app.config['UPLOAD_FOLDER'] = '/storage/plzen1/home/mmajer/pr4/data/image_search/'
else:
    import h5py
    from random import randint

    # path to h5df file with features
    h5_fts_fn = '/Users/martin.majer/PycharmProjects/PR4/data/sun_sample.hdf5.features.hdf5'

    # path to data folder
    app.config['UPLOAD_FOLDER'] = '/Users/martin.majer/PycharmProjects/PR4/data/kdt_server/'

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def keep_ratio(shape, height, width):
    '''
    Calculates dimensions for resizing without affecting ratio.
    :param shape: shape of array of image saved in numpy
    :param height: height the image will be resized to
    :param width: width the image will be resized to
    :return: dimensions the image will be resized to
    '''
    #height <= width
    if shape[0] <= shape[1]:
        ratio = height / shape[0]
        width = shape[1] * ratio
    else:
        ratio = width / shape[1]
        height = shape[0] * ratio

    #opencv dimension format
    dim = int(width), int(height)

    return dim

def crop(img, height, width):
    '''
    Crop center of the image.
    :param img: image to be cropped
    :param height: height the image will be cropped to
    :param width: width the image will be cropped to
    :return: cropped image
    '''
    if (img.shape[0] == height) and (img.shape[1] == width):
        return img
    elif img.shape[0] == height:
        middle = img.shape[1] / 2
        return img[:, (middle - width / 2):(middle + width / 2)]
    else:
        middle = img.shape[0] / 2
        return img[(middle - height / 2):(middle + height / 2), :]


def check_allowed(filename):
    '''
    Check whether uploaded file is image or not.
    :param filename: name of the uploaded image
    :return: boolean value
    '''
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
@app.route('/search')
def search():
    '''
    Main page with form.
    :return: rendered template from html file
    '''
    return render_template('search.html')

@app.route('/results', methods=['POST'])
def results():
    '''
    Add image to database, calculates features and finds nearest neighbors.
    :return: rendered template from html file
    '''

    # get data from form
    search_file = request.files['search_file']
    search_url = request.form['search_url']

    # path to temporary image file
    filename = 'img.jpg'
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # list of images to be passed to render_template
    filenames = []

    if search_url or search_file:
        if search_url:
            if check_allowed(search_url):
                msg = 'Searching using URL (%s)' % search_url
                # temporarily save image in full resolution
                urllib.urlretrieve(search_url, path)
            else:
                msg = 'Please provide URL containing image.'
                return render_template('results.html', msg=msg, filenames=filenames)

        else:
            if check_allowed(search_file.filename):
                msg = 'Searching using file (filename: %s)' % search_file.filename
                # temporarily save image in full resolution
                search_file.save(path)
            else:
                msg = 'Please provide valid image file.'
                return render_template('results.html', msg=msg, filenames=filenames)


        # open image using opencv, resize it and crop it (BGR, float32)
        img = cv2.imread(path)
        dim = keep_ratio(img.shape, height, width)
        img_resized = cv2.resize(img, dim, interpolation = cv2.INTER_CUBIC)
        img_cropped = crop(img_resized, height, width)
        img_cropped = img_cropped.astype(np.float32)

        # calculate features (or choose random for local testing)
        if caffe_toggle:
            score = net.predict([img_cropped]).flatten()
        else:
            with h5py.File(h5_fts_fn, 'r') as fr_features:
                score = fr_features['score'][randint(0, 9999)]

        # convert image to RGB uint8





        # zavolat add_images()
        print 'len(kdt.features) before\t|\t', len(kdt.features)
        kdt.add_images([img_cropped], [score])
        print 'len(kdt.features) after\t|\t', len(kdt.features)

        # zavolat save()
        kdt.save()

        # smazat obrazek
        os.remove(path)

        # zavolat find()
        indexes, distances = kdt.find_k_nearest_by_index(len(kdt.features) - 1, 6)

        filenames = []
        for index in indexes:
            filenames.append(str(index) + '.jpg')

        print filenames
    else:
        msg = 'Please provide URL or file.'

    return render_template('results.html', msg=msg, filenames=filenames)


@app.route('/thumbs/<filename>')
def send_file(filename):
    '''
    Send image from directory to server.
    :param filename: name of the image
    :return: image
    '''
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbs'), filename)

if __name__ == '__main__':
    kdt = kdtree.ImageSearchKDTree(app.config['UPLOAD_FOLDER'], 1000000000, (150,150,3))
    app.run(port=8080, debug=True)