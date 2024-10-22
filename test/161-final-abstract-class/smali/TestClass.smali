# Copyright (C) 2017 The Android Open Source Project
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

.class LTestClass;
.super Ljava/lang/Object;

.method public static test()V
    .registers 1
    new-instance v0, LAbstractFinal;
    return-void
.end method

.method public static test2()V
    .registers 1
    const/4 v0, 0
    invoke-static {v0}, LTestClass;->test2Target(LAbstractFinal;)V
    return-void
.end method

.method public static test2Target(LAbstractFinal;)V
    .registers 1
    return-void
.end method
