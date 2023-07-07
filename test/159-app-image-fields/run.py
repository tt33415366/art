#!/bin/bash
#
# Copyright (C) 2017 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


def run(ctx, args):
  # Use a profile to put specific classes in the app image.
  # Also run the compiler with -j1 to ensure specific class verification order.
  # And limit the managed heap to 16 MiB to speed up GCs.
  ctx.default_run(
      args,
      profile=True,
      Xcompiler_option=["--compiler-filter=speed-profile", "-j1"],
      runtime_option=["-Xmx16m"])
