import glob
import os
import subprocess
import tempfile

def progress_bar(iterator, maxval=None):
    """ Returns an iterator for an iterator that renders a progress bar with a
    countdown timer """

    from progressbar import ProgressBar, SimpleProgress, Bar, ETA
    pbar = ProgressBar(
        maxval=maxval,
        widgets=[SimpleProgress(sep='/'), ' ', Bar(), ' ', ETA()],
    )
    return pbar(iterator)


# shape_root_dir should contain {shape1, shape2,...} where
# shape* contains .obj, .mtl files etc.
shape_root_dir = '/home/hlin/projects/caffe/data/mattrans/900/mvcnn_renderings/trainset/'
shapes_list = glob.glob(os.path.join(shape_root_dir, "*"))

shapes_list_orig = shapes_list
shapes_list = []
for entry in shapes_list_orig:
    if not os.path.isdir(entry):
        print 'Removing {} since it is not a shape directory'.format(entry)
    else:
        shapes_list.append(entry)


print '{} directories in {}'.format(len(shapes_list), shape_root_dir)

# Config files defining views
view_config_files_root = '/home/hlin/projects/sstk/ssc/config/'
view_config_files = ['render_model_normalized.json',
                     #'render_scan.json',
                     #'default.json',
                     ]

# render_file.js root
script_root = '/home/hlin/projects/sstk/ssc'
script = os.path.join(script_root, 'render-file.js')

batch_render_size = 10

count = 0
for shape in progress_bar(shapes_list):

    if count == 0:
        inputs = tempfile.NamedTemporaryFile(prefix='render-file-temp', suffix='.txt', dir=os.getcwd())
        inputs_filename = glob.glob(os.path.join(os.getcwd(), "render-file-temp*"))[0]

    name = shape.split('/')[-1]
    obj_file = os.path.join(shape, name+".obj")
    inputs.write(obj_file+'\n')

    count += 1
    #
    if count == batch_render_size:
        count = 0

        for config_file in view_config_files:
            full_config_file = os.path.join(view_config_files_root, config_file)

            print '  Rendering {}...'.format(obj_file)
            print '  Using config file {}...'.format(config_file)

            # It might be faster to batch inputs because render-file.js seems to make use of async operations.
            # In this case, we should gather all inputs into a single text file, and pass that as input into --input.
            options = ['--assetType model',
                        '--config_file {}'.format(full_config_file),
                        '--width 900',
                        '--height 900',
                        #'--input {}'.format(obj_file),
                        '--input {}'.format(inputs_filename),
                        '--output_dir render_outputs',
                        #'--output {}'.format(name + '_' + config_file.split('.json')[0]),
                        '--skip_existing',
                        ]
            call = ['node ' + script + ' ' + ' '.join(options)]
            print call
            subprocess.call(call, shell=True)

        inputs.close()

    #exit(1)

#./render-file.js --assetType model --config_file ./config/render_model_normalized.json --width 900 --height 900 --input ~/projects/caffe/data/mattrans/900/mvcnn_renderings/trainset/1011e1c9812b84d2a9ed7bb5b55809f8/1011e1c9812b84d2a9ed7bb5b55809f8.obj
# Started at ~7:02 pm. Check what the latest file is when done to get estimate for render time.


