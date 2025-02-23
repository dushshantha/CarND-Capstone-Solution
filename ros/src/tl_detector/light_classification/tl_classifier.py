import rospy
from styx_msgs.msg import TrafficLight
from tl_detector import TLDetector
from tl_detector import _load_image_into_numpy_array
import tensorflow as tf

from PIL import Image
import numpy as np

class TLClassifier(object):
    def __init__(self, model_path1='light_classification/models/ssd_sim_and_real_30_03_2018', 
                       model_path2='light_classification/models/frozen_faster_rcnn_reallife_v2',
                       model_path3='light_classification/models/frozen_real_inception13', isSimulator=False):
        # Primary Model
	self.detector1 = TLDetector(model_path1)

        if isSimulator:
            self.detector2 = TLDetector('light_classification/models/frozen_faster_rcnn_sim_v2')
            self.detector3 = TLDetector('light_classification/models/frozen_sim_inception13')
        else:
            self.detector2 = TLDetector(model_path2)
            self.detector3 = TLDetector(model_path3)

    def get_state_string(self, state):
        if (state == 0):
            state_s = "RED"
        elif (state == 1):
            state_s = "YELLOW"
        elif (state == 2):
            state_s = "GREEN"
        else:
            state_s = "UNKNOWN"

        return state_s

    def get_classification(self, image):
        """Determines the color of the traffic light in the image

        Args:
            image (cv::Mat): image containing the traffic light

        Returns:
            int: ID of traffic light color (specified in styx_msgs/TrafficLight)

        """
        tl_class_index = {
                1 : TrafficLight.GREEN,
                2 : TrafficLight.RED,
                3 : TrafficLight.YELLOW,
                4 : TrafficLight.UNKNOWN
                }

        output_dict1 = self.detector1.run_inference_for_single_image(image)
        output_dict2 = self.detector2.run_inference_for_single_image(image)
        output_dict3 = self.detector3.run_inference_for_single_image(image)

        tl_class1 = TrafficLight.UNKNOWN
        if output_dict1['detection_scores'][0] >= 0.4:
            tl_class1 = tl_class_index.get(output_dict1['detection_classes'][0],
                    TrafficLight.UNKNOWN)

        tl_class2 = TrafficLight.UNKNOWN
        if output_dict2['detection_scores'][0] >= 0.4:
            tl_class2 = tl_class_index.get(output_dict2['detection_classes'][0],
                    TrafficLight.UNKNOWN)

        tl_class3 = TrafficLight.UNKNOWN
        if output_dict3['detection_scores'][0] >= 0.4:
            tl_class3 = tl_class_index.get(output_dict3['detection_classes'][0],
                    TrafficLight.UNKNOWN)

        rospy.loginfo('Yury says  : {} with {}'.format(self.get_state_string(tl_class1), output_dict1['detection_scores'][0]))
        rospy.loginfo('Marcus says: {} with {}'.format(self.get_state_string(tl_class2), output_dict2['detection_scores'][0]))
        rospy.loginfo('Duksan says: {} with {}'.format(self.get_state_string(tl_class3), output_dict3['detection_scores'][0]))
       
        classes = [tl_class1, tl_class2, tl_class3]
        scores  = [output_dict1['detection_scores'][0], output_dict2['detection_scores'][0], output_dict3['detection_scores'][0]] 
        if ((tl_class1 == tl_class2 and output_dict1['detection_scores'][0] >= 0.4 and output_dict2['detection_scores'][0] >= 0.4) or 
            (tl_class1 == tl_class3 and output_dict1['detection_scores'][0] >= 0.4 and output_dict3['detection_scores'][0] >= 0.4)):
            tl_class = tl_class1
        elif (tl_class2 == tl_class3 and output_dict2['detection_scores'][0] >= 0.4 and output_dict3['detection_scores'][0] >= 0.4):
            tl_class = tl_class2
        else:
            tl_class = classes[np.argmax(scores)]

        return tl_class


# Simple test
def _main(_):
    flags = tf.app.flags.FLAGS
    image_path = flags.input_image
    model_path1 = flags.model_path1
    model_path2 = flags.model_path2
    model_path3 = flags.model_path3
    simulator = flags.simulator

    image = Image.open(image_path)
    # the array based representation of the image will be used later in order to prepare the
    # result image with boxes and labels on it.
    image_np = _load_image_into_numpy_array(image)

    classifier = TLClassifier(model_path1, model_path2, model_path3, simulator)

    classification = classifier.get_classification(image_np)
    state_s = classifier.get_state_string(classification)
    print(state_s)

if __name__ == '__main__':
    flags = tf.app.flags
    flags.DEFINE_string('input_image', 'input/test.jpg', 'Path to input image')
    flags.DEFINE_string('model_path1', 'models/ssd_sim_and_real_30_03_2018', 'Path to the first model')
    flags.DEFINE_string('model_path2', 'models/frozen_faster_rcnn_reallife_v2', 'Path to the second model')
    flags.DEFINE_string('model_path3', 'models/frozen_real_inception13', 'Path to the third model')
    flags.DEFINE_bool('simulator', False, 'Whether image is coming from a simulator or not')

    tf.app.run(main=_main)
