#!/bin/bash
# デフォルトアイコンを作成するスクリプト

echo "Creating default launcher icons..."

# アイコンディレクトリを作成
mkdir -p app/src/main/res/mipmap-hdpi
mkdir -p app/src/main/res/mipmap-mdpi
mkdir -p app/src/main/res/mipmap-xhdpi
mkdir -p app/src/main/res/mipmap-xxhdpi
mkdir -p app/src/main/res/mipmap-xxxhdpi

# 簡単な赤いアイコンを作成（ImageMagickがない場合の代替案）
# AndroidManifestを一時的に修正
cat > app/src/main/res/values/ic_launcher_background.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">#610610</color>
</resources>
EOF

# ダミーのPNGファイルを作成（最小限の赤い四角）
for size in 48 72 96 144 192; do
    # 赤い1x1ピクセルのPNGをbase64でデコード
    echo "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP4z8DwHwAFAAH/VscvAQAAAABJRU5ErkJggg==" | base64 -d > temp_icon.png
    
    case $size in
        48) cp temp_icon.png app/src/main/res/mipmap-mdpi/ic_launcher.png
            cp temp_icon.png app/src/main/res/mipmap-mdpi/ic_launcher_round.png ;;
        72) cp temp_icon.png app/src/main/res/mipmap-hdpi/ic_launcher.png
            cp temp_icon.png app/src/main/res/mipmap-hdpi/ic_launcher_round.png ;;
        96) cp temp_icon.png app/src/main/res/mipmap-xhdpi/ic_launcher.png
            cp temp_icon.png app/src/main/res/mipmap-xhdpi/ic_launcher_round.png ;;
        144) cp temp_icon.png app/src/main/res/mipmap-xxhdpi/ic_launcher.png
             cp temp_icon.png app/src/main/res/mipmap-xxhdpi/ic_launcher_round.png ;;
        192) cp temp_icon.png app/src/main/res/mipmap-xxxhdpi/ic_launcher.png
             cp temp_icon.png app/src/main/res/mipmap-xxxhdpi/ic_launcher_round.png ;;
    esac
done

rm -f temp_icon.png

echo "Default icons created!"