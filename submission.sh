#!/bin/bash
display_usage() { 
  echo -e "\nUsage:\n$0 path_to_repository\n" 
} 

# if less than two arguments supplied, display usage 
if [  $# -le 0 ] 
then 
  display_usage
  exit 1
fi 
 
echo --- Preparing submission file ---
mkdir submission
cd submission
git clone $1
cd CarND-Capstone-Solution
cat ros/src/tl_detector/light_classification/frozen_faster_rcnn.tar.bz2.parta* > ros/src/tl_detector/light_classification/frozen_faster_rcnn.tar.bz2
tar -vxjf ros/src/tl_detector/light_classification/frozen_faster_rcnn.tar.bz2 -C ros/src/tl_detector/light_classification/
rm -fR ros/src/tl_detector/light_classification/frozen_faster_rcnn.tar.bz2.parta*
rm -fR ros/src/tl_detector/light_classification/frozen_faster_rcnn.tar.bz2
rm -fR ./data/traffic_light_bag_images_part*.tgz
rm -fR .git
cd ..
zip -r CarND-Capstone-Solution.zip CarND-Capstone-Solution/
ls -lh CarND-Capstone-Solution.zip
echo --- Please submit submission/CarND-Capstone-Solution.zip --- 
