#!/bin/bash
# JUPITER NOTIFIER ANDROID プロジェクト作成スクリプト

PROJECT_NAME="JUPITER-NOTIFIER-ANDROID"
PACKAGE_NAME="com.jupiter.notifier"
PACKAGE_PATH="com/jupiter/notifier"

echo "Creating Android project: $PROJECT_NAME"
echo "Package: $PACKAGE_NAME"
echo ""

# ディレクトリ構造の作成
mkdir -p $PROJECT_NAME/{app/src/main/{java/$PACKAGE_PATH,res/{layout,values,drawable,mipmap-hdpi}},gradle/wrapper,.idea}

cd $PROJECT_NAME

# settings.gradle.kts
cat > settings.gradle.kts << 'EOF'
rootProject.name = "JUPITER-NOTIFIER-ANDROID"
include(":app")
EOF

# build.gradle.kts (root)
cat > build.gradle.kts << 'EOF'
// Top-level build file
plugins {
    id("com.android.application") version "8.1.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.0" apply false
}
EOF

# build.gradle.kts (app)
cat > app/build.gradle.kts << 'EOF'
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.jupiter.notifier"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.jupiter.notifier"
        minSdk = 21
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
    buildFeatures {
        viewBinding = true
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.12.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.10.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    
    // WebSocket
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    
    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    
    // Preferences
    implementation("androidx.preference:preference-ktx:1.2.1")
}
EOF

# gradle.properties
cat > gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
EOF

# local.properties (SDK pathは環境に応じて変更)
cat > local.properties << EOF
sdk.dir=$ANDROID_HOME
EOF

# gradle-wrapper.properties
cat > gradle/wrapper/gradle-wrapper.properties << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

echo "Project structure created successfully!"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Install Android SDK components if not already installed"
echo "3. Open in VSCode: code ."