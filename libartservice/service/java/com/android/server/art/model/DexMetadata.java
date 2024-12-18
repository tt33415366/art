/*
 * Copyright (C) 2024 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.server.art.model;

import android.annotation.IntDef;

import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

/** @hide */
public class DexMetadata {
    /** An explicit private class to avoid exposing constructor.*/
    private DexMetadata() {}

    public static final int TYPE_UNKNOWN = 0;
    public static final int TYPE_PROFILE = 1;
    public static final int TYPE_VDEX = 2;
    public static final int TYPE_PROFILE_AND_VDEX = 3;
    public static final int TYPE_NONE = 4;
    public static final int TYPE_ERROR = 5;

    /** @hide */
    // clang-format off
    @IntDef(prefix = "TYPE_", value = {
        TYPE_UNKNOWN,
        TYPE_PROFILE,
        TYPE_VDEX,
        TYPE_PROFILE_AND_VDEX,
        TYPE_NONE,
        TYPE_ERROR,
    })
    // clang-format on
    @Retention(RetentionPolicy.SOURCE)
    public @interface Type {}
}
