import fastdeploy as fd
import cv2
import os


def parse_arguments():
    import argparse
    import ast
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_dir",
        default=None,
        help="Path of PaddleDetection model directory")
    parser.add_argument(
        "--image", default=None, help="Path of test image file.")
    parser.add_argument(
        "--device",
        type=str,
        default='cpu',
        help="Type of inference device, support 'cpu' or 'gpu'.")
    parser.add_argument(
        "--use_trt",
        type=ast.literal_eval,
        default=False,
        help="Wether to use tensorrt.")
    return parser.parse_args()


def build_option(args):
    option = fd.RuntimeOption()

    if args.device.lower() == "gpu":
        # option.use_gpu()
        print(
            """GPU inference with Backend::Paddle in python has not been supported yet. \
          \nWill ignore this option.""")

    if args.use_trt:
        # TODO(qiuyanjun): may remove TRT option
        # Backend::TRT has not been supported yet.
        print(
            """Backend::TRT has not been supported yet, will ignore this option.\
              \nPaddleDetection/MaskRCNN has only support Backend::Paddle now."""
        )

    if args.device.lower() == "kunlunxin":
        option.use_kunlunxin()

    if args.device.lower() == "ascend":
        option.use_ascend()

    return option


args = parse_arguments()

if args.model_dir is None:
    model_dir = fd.download_model(name='mask_rcnn_r50_1x_coco')
else:
    model_dir = args.model_dir

model_file = os.path.join(model_dir, "model.pdmodel")
params_file = os.path.join(model_dir, "model.pdiparams")
config_file = os.path.join(model_dir, "infer_cfg.yml")

# 配置runtime，加载模型
runtime_option = build_option(args)
model = fd.vision.detection.MaskRCNN(
    model_file, params_file, config_file, runtime_option=runtime_option)

image_file_path = "../dataset/coco/val2017"
annotation_file_path = "../dataset/coco/annotations/instances_val2017.json"

res = fd.vision.evaluation.eval_detection(model, image_file_path,
                                          annotation_file_path)
print(res)
