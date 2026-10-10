# SpotiFLAC Mobile 5.1.0 简体中文补全版

这是基于上游正式标签 v5.1.0（0d13c9585c676c02451d0fdc8f564a1e632a24a0）的非官方中文源码修改。保留上游 MIT 许可证。本目录不是已生成的 APK；只有构建成功后的 .apk 才能安装。

## 修改内容

- 补全简体中文 UI 资源，启用 zh_CN 语言入口；跟随简体中文系统时也能选择中文。
- Android 应用名称为“SpotiFLAC 中文版”。
- 独立应用标识 com.zarz.spotiflac.zh，避免与原版 com.zarz.spotiflac 的签名冲突；可与原版并存。
- 新增本地化静态验证和手动触发的 GitHub Actions 构建流程。
- 汉化不修改音源扩展、下载处理和 USB 音频驱动。

选择 Lite 构建是为了绕开未公开分发的可选 Discord SDK。上游说明 Lite 保留下载和播放，省略 Discord 集成。扩展自身的名称、配置项和服务端错误由扩展提供，可能仍显示英文；歌曲名、艺人名、平台名和音乐格式保留原文。

## 重要状态

准备环境是 Android 上的 Alpine aarch64 PRoot：没有 Flutter 和 Android SDK；原项目的 NDK 构建脚本要求 x86-64 主机工具链。本地 Java 启动也报可执行内存页错误。因此此处不能验证 APK 编译或手机界面；静态检查通过不能当作完整构建通过。

## 推荐构建：GitHub Actions

1. 在自己的 GitHub 账户 Fork 上游仓库。
2. 将仓库切换到 v5.1.0 标签基础的分支，应用本包中的中文补丁；也可把本源码作为自己的新仓库。
3. 确认修改和 `.github/workflows/chinese-apk.yml`、`scripts/validate_chinese_translation.py` 已提交。
4. 在 Actions 中选择 “Build unofficial Simplified Chinese APK”，手动运行。
5. 成功后下载 `SpotiFLAC-5.1.0-zh-arm64` 构建产物里的 `SpotiFLAC-5.1.0-zh-arm64.apk`。
6. 在手机安装；它与原版并存，首次运行需要重新选择目录、添加扩展仓库和授权 USB。

GitHub Actions 工作流不需要原开发者签名或 Discord 解密密钥。它使用构建机生成的开发签名，产物仅包含 APK 和校验信息，不包含签名私钥。每次新构建机可能产生不同密钥，因此这份流程适合首次自用安装；要持续更新，应配置并保管自己的固定签名密钥，否则 Android 不能覆盖已有中文版本。

该工作流只是准备好的构建方案，尚未触发或验证运行。工具版本完全遵循 v5.1.0：Flutter 3.47.5、Java 25、Rust 1.98.1、NDK 29.0.14206865、Android 37、Build Tools 37.0.0、CMake 3.22.1。构建环境必须能下载这些上游要求的版本；如果公共工具尚不可用或依赖源失效，仍需解决构建错误。

## 电脑本地构建

使用 Linux x86-64，先安装锁定的 Flutter、Java、Android SDK/NDK、Rust/rustup、libclang；具体参考 CONTRIBUTING.md。命令：

```sh
python3 scripts/validate_chinese_translation.py
flutter pub get
flutter gen-l10n
export SPOTIFLAC_DISCORD_SDK=0
export SPOTIFLAC_RUST_ANDROID_ABIS=arm64-v8a
export ANDROID_NDK_HOME=/path/to/android-sdk/ndk/29.0.14206865
bash scripts/build_android.sh --lite --target lib/main.dart
```

构建后 APK 位于 `build/app/outputs/flutter-apk/app-arm64-v8a-release.apk`。源码包不要直接在官方已安装 APK 上覆写；中文包采用独立标识，不会自动继承原版设置和数据库。

## 验证

本地化验证检查：JSON 可解析、1663 个用户字符串键齐全、ICU 占位符和复数分支结构一致、网址未改动、中文语言入口已启用。必须另外在兼容主机执行 Flutter 生成/编译，再在手机检查设置、下载、播放、USB 独占和长中文文本布局。

## 扩展仓库

```
https://raw.githubusercontent.com/spotiflacapp/SpotiFLAC-Extension/main/registry.json
```

此处仅作为使用参考，未更改扩展默认配置，也未内置账号、令牌或音源服务。
