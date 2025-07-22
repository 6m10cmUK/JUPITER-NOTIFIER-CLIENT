#!/bin/bash

# Android CLI プロジェクトセットアップスクリプト

echo "Creating Android project structure..."

# プロジェクトディレクトリ作成
mkdir -p android-project/{app/src/main/{java/com/jupiter/notifier,res/{layout,values,drawable}},gradle/wrapper}

# settings.gradle
cat > android-project/settings.gradle << 'EOF'
rootProject.name = "JupiterNotifier"
include ':app'
EOF

# build.gradle (root)
cat > android-project/build.gradle << 'EOF'
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
        classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:1.9.0'
    }
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
EOF

# build.gradle (app)
cat > android-project/app/build.gradle << 'EOF'
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.jupiter.notifier'
    compileSdk 33

    defaultConfig {
        applicationId "com.jupiter.notifier"
        minSdk 21
        targetSdk 33
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = '1.8'
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.10.1'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.9.0'
    implementation 'com.squareup.okhttp3:okhttp:4.11.0'
    implementation 'org.java-websocket:Java-WebSocket:1.5.3'
}
EOF

# gradle-wrapper.properties
cat > android-project/gradle/wrapper/gradle-wrapper.properties << 'EOF'
distributionUrl=https\://services.gradle.org/distributions/gradle-8.0-bin.zip
EOF

# gradlew作成用
cd android-project
curl -s https://raw.githubusercontent.com/gradle/gradle/master/gradle/wrapper/gradle-wrapper.jar -o gradle/wrapper/gradle-wrapper.jar

echo "Android project structure created!"
echo ""
echo "Next steps:"
echo "1. cd android-project"
echo "2. ./gradlew wrapper (初回のみ)"
echo "3. ./gradlew build"
echo "4. ./gradlew installDebug (デバイスに接続している場合)"