#!/usr/bin/env python3
#
# Copyright (C) 2021 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" This script generates the Android.run-test.bp build file"""

import glob
import json
import os
import textwrap
import sys

def main():
  os.chdir(os.path.dirname(__file__))
  with open("Android.run-test.bp", mode="wt") as f:
    f.write(textwrap.dedent(f"""
      // This file was generated by {os.path.basename(__file__)}
      // It is not necessary to regenerate it when tests are added/removed/modified.

      TEST_BUILD_COMMON_ARGS = "$(location run_test_build.py) --out $(out) " +
          "--bootclasspath $(location :art-run-test-bootclasspath) " +
          "--d8 $(location d8) " +
          "--jasmin $(location jasmin) " +
          "--rewrapper $(location rewrapper) " +
          "--smali $(location android-smali) " +
          "--soong_zip $(location soong_zip) " +
          "--zipalign $(location zipalign) "
    """).lstrip())
    for mode in ["host", "target", "jvm"]:
      names = []
      # Group the tests into shards based on the last two digits of the test number.
      # This keeps the number of generated genrules low so we don't overwhelm soong,
      # but it still allows iterating on single test without recompiling all tests.
      for shard in ["{:02}".format(i) for i in range(100)]:
        name = f"art-run-test-{mode}-data-shard{shard}"
        names.append(name)
        f.write(textwrap.dedent(f"""
          java_genrule {{
              name: "{name}-tmp",
              out: ["{name}.zip"],
              srcs: [
                  "?{shard}-*/**/*",
                  "??{shard}-*/**/*",
              ],
              cmd: TEST_BUILD_COMMON_ARGS + "--mode {mode} --test-dir-regex 'art/test/..?{shard}-' $(in)",
              defaults: ["art-run-test-{mode}-data-defaults"],
          }}

          // This filegroup is so that the host prebuilt etc can depend on a device genrule,
          // as prebuilt_etc doesn't have the equivalent of device_common_srcs.
          filegroup {{
              name: "{name}-fg",
              device_common_srcs: [":{name}-tmp"],
          }}

          // Install in the output directory to make it accessible for tests.
          prebuilt_etc_host {{
              name: "{name}",
              src: ":{name}-fg",
              sub_dir: "art",
              filename: "{name}.zip",
          }}
          """))

      # Build all hiddenapi tests in their own shard.
      # This removes the dependency on hiddenapi from all other shards,
      # which in turn removes dependency on ART C++ source code.
      name = "art-run-test-{mode}-data-shardHiddenApi".format(mode=mode)
      names.append(name)
      f.write(textwrap.dedent(f"""
        java_genrule {{
            name: "{name}-tmp",
            out: ["{name}.zip"],
            srcs: [
                "???-*hiddenapi*/**/*",
                "????-*hiddenapi*/**/*",
            ],
            defaults: ["art-run-test-{mode}-data-defaults"],
            tools: ["hiddenapi"],
            cmd: TEST_BUILD_COMMON_ARGS + "--hiddenapi $(location hiddenapi) --mode {mode} --test-dir-regex 'art/test/....?-[^/]*hiddenapi' $(in)",
        }}

        // This filegroup is so that the host prebuilt etc can depend on a device genrule,
        // as prebuilt_etc doesn't have the equivalent of device_common_srcs.
        filegroup {{
            name: "{name}-fg",
            device_common_srcs: [":{name}-tmp"],
        }}

        // Install in the output directory to make it accessible for tests.
        prebuilt_etc_host {{
            name: "{name}",
            src: ":{name}-fg",
            sub_dir: "art",
            filename: "{name}.zip",
        }}
        """))

      f.write(textwrap.dedent(f"""
        genrule_defaults {{
            name: "art-run-test-{mode}-data-defaults",
            srcs: [
                // Since genrules are sandboxed, all the sources they use must be listed in
                // the Android.bp file. Some tests have symlinks to files from other tests, and
                // those must also be listed to avoid a dangling symlink in the sandbox.
                "jvmti-common/*.java",
                "utils/python/**/*.py",
                ":art-run-test-bootclasspath",
                ":development_docs",
                ":asm-9.6-filegroup",
                ":ojluni-AbstractCollection",
                "988-method-trace/expected-stdout.txt",
                "988-method-trace/expected-stderr.txt",
                "988-method-trace/src/art/Test988Intrinsics.java",
                "988-method-trace/src/art/Test988.java",
                "988-method-trace/trace_fib.cc",
                "1953-pop-frame/src/art/Test1953.java",
                "1953-pop-frame/src/art/SuspendEvents.java",
                // Files needed to generate runner scripts.
                "testrunner/*.py",
                "knownfailures.json",
                "default_run.py",
                "globals.py",
                "run-test",
                "run_test_build.py",
            ],
            tools: [
                "android-smali",
                "d8",
                "jasmin",
                "rewrapper",
                "soong_zip",
                "zipalign",
            ],
        }}
        """))

      name = "art-run-test-{mode}-data-merged".format(mode=mode)
      srcs = ("\n"+" "*16).join('":{}-tmp",'.format(n) for n in names)
      deps = ("\n"+" "*16).join('"{}",'.format(n) for n in names)
      f.write(textwrap.dedent(f"""
        java_genrule {{
            name: "{name}-tmp",
            out: ["{name}.tgz"],
            srcs: [
                {srcs}
            ],
            tool_files: ["merge_zips_to_tgz.py"],
            cmd: "$(location merge_zips_to_tgz.py) $(out) $(in)",
        }}

        // This filegroup is so that the host prebuilt etc can depend on a device genrule,
        // as prebuilt_etc doesn't have the equivalent of device_common_srcs.
        filegroup {{
            name: "{name}-fg",
            device_common_srcs: [":{name}-tmp"],
        }}

        // Install in the output directory to make it accessible for tests.
        prebuilt_etc_host {{
            name: "{name}",
            src: ":{name}-fg",
            required: [
                {deps}
            ],
            sub_dir: "art",
            filename: "{name}.tgz",
        }}
        """))

      name = "art-run-test-{mode}-data".format(mode=mode)
      srcs = ("\n"+" "*16).join('":{}-tmp",'.format(n) for n in names)
      deps = ("\n"+" "*16).join('"{}",'.format(n) for n in names)
      f.write(textwrap.dedent(f"""
        // Phony target used to build all shards
        java_genrule {{
            name: "{name}-tmp",
            out: ["{name}.txt"],
            srcs: [
                {srcs}
            ],
            cmd: "echo $(in) > $(out)",
        }}

        // This filegroup is so that the host prebuilt etc can depend on a device genrule,
        // as prebuilt_etc doesn't have the equivalent of device_common_srcs.
        filegroup {{
            name: "{name}-fg",
            device_common_srcs: [":{name}-tmp"],
        }}

        // Phony target used to install all shards
        prebuilt_etc_host {{
            name: "{name}",
            src: ":{name}-fg",
            required: [
                {deps}
            ],
            sub_dir: "art",
            filename: "{name}.txt",
        }}
        """))

if __name__ == "__main__":
  main()
