package com.baidu.paddle.fastdeploy.vision.detection;

import android.graphics.Bitmap;

import com.baidu.paddle.fastdeploy.FastDeployInitializer;
import com.baidu.paddle.fastdeploy.RuntimeOption;
import com.baidu.paddle.fastdeploy.vision.DetectionResult;

public class PicoDet {
    protected long mCxxContext = 0; // Context from native.
    protected boolean mInitialized = false;

    public PicoDet() {
        mInitialized = false;
    }

    // Constructor with default runtime option
    public PicoDet(String modelFile,
                   String paramsFile,
                   String configFile) {
        init_(modelFile, paramsFile, configFile, "", new RuntimeOption());
    }

    public PicoDet(String modelFile,
                   String paramsFile,
                   String configFile,
                   String labelFile) {
        init_(modelFile, paramsFile, configFile, labelFile, new RuntimeOption());
    }

    // Constructor without label file
    public PicoDet(String modelFile,
                   String paramsFile,
                   String configFile,
                   RuntimeOption runtimeOption) {
        init_(modelFile, paramsFile, configFile, "", runtimeOption);
    }

    // Constructor with label file
    public PicoDet(String modelFile,
                   String paramsFile,
                   String configFile,
                   String labelFile,
                   RuntimeOption runtimeOption) {
        init_(modelFile, paramsFile, configFile, labelFile, runtimeOption);
    }

    // Call init manually without label file
    public boolean init(String modelFile,
                        String paramsFile,
                        String configFile,
                        RuntimeOption runtimeOption) {
        return init_(modelFile, paramsFile, configFile, "", runtimeOption);
    }

    // Call init manually with label file
    public boolean init(String modelFile,
                        String paramsFile,
                        String configFile,
                        String labelFile,
                        RuntimeOption runtimeOption) {
        return init_(modelFile, paramsFile, configFile, labelFile, runtimeOption);
    }

    public boolean release() {
        mInitialized = false;
        if (mCxxContext == 0) {
            return false;
        }
        return releaseNative(mCxxContext);
    }

    public boolean initialized() {
        return mInitialized;
    }

    // Predict without image saving and bitmap rendering.
    public DetectionResult predict(Bitmap ARGB8888Bitmap) {
        if (mCxxContext == 0) {
            return new DetectionResult();
        }
        // Only support ARGB8888 bitmap in native now.
        DetectionResult result = predictNative(mCxxContext, ARGB8888Bitmap,
                false, "", false, 0.f);
        if (result == null) {
            return new DetectionResult();
        }
        return result;
    }

    public DetectionResult predict(Bitmap ARGB8888Bitmap,
                                   boolean rendering,
                                   float scoreThreshold) {
        if (mCxxContext == 0) {
            return new DetectionResult();
        }
        // Only support ARGB8888 bitmap in native now.
        DetectionResult result = predictNative(mCxxContext, ARGB8888Bitmap,
                false, "", rendering, scoreThreshold);
        if (result == null) {
            return new DetectionResult();
        }
        return result;
    }

    // Predict with image saving and bitmap rendering (will cost more times)
    public DetectionResult predict(Bitmap ARGB8888Bitmap,
                                   String savedImagePath,
                                   float scoreThreshold) {
        // scoreThreshold is for visualizing only.
        if (mCxxContext == 0) {
            return new DetectionResult();
        }
        // Only support ARGB8888 bitmap in native now.
        DetectionResult result = predictNative(
                mCxxContext, ARGB8888Bitmap, true,
                savedImagePath, true, scoreThreshold);
        if (result == null) {
            return new DetectionResult();
        }
        return result;
    }

    private boolean init_(String modelFile,
                          String paramsFile,
                          String configFile,
                          String labelFile,
                          RuntimeOption runtimeOption) {
        if (!mInitialized) {
            mCxxContext = bindNative(
                    modelFile,
                    paramsFile,
                    configFile,
                    runtimeOption,
                    labelFile);
            if (mCxxContext != 0) {
                mInitialized = true;
            }
            return mInitialized;
        } else {
            // release current native context and bind a new one.
            if (release()) {
                mCxxContext = bindNative(
                        modelFile,
                        paramsFile,
                        configFile,
                        runtimeOption,
                        labelFile);
                if (mCxxContext != 0) {
                    mInitialized = true;
                }
                return mInitialized;
            }
            return false;
        }
    }

    // Bind predictor from native context.
    private native long bindNative(String modelFile,
                                   String paramsFile,
                                   String configFile,
                                   RuntimeOption runtimeOption,
                                   String labelFile);

    // Call prediction from native context with rendering.
    private native DetectionResult predictNative(long CxxContext,
                                                 Bitmap ARGB8888Bitmap,
                                                 boolean saveImage,
                                                 String savePath,
                                                 boolean rendering,
                                                 float scoreThreshold);

    // Release buffers allocated in native context.
    private native boolean releaseNative(long CxxContext);

    // Initializes at the beginning.
    static {
        FastDeployInitializer.init();
    }
}

