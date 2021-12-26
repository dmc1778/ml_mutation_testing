#!/bin/bash

cd /media/nimashiri/SSD/tensorflow/

bazelisk-linux-amd64 --output_user_root=/media/nimashiri/SSD/bazel_temp_dir build --config=opt -c fastbuild //tensorflow/tools/pip_package:build_pip_package --jobs 6




