# 仓库目录与职责说明

> 文档定位：本文档用于快速识别仓库中的关键目录、入口文件和常见工作位置，适合初次进入仓库时先阅读。

## 1. 根目录

### `platformio.ini`

平台构建入口，定义默认环境、公共编译选项、库依赖和各类通用配置。

### `README.md`

项目概览和外部入口说明。

### `CONTRIBUTING.md`

贡献指南，说明协作流程、CLA 和提交习惯。

### `CODE_OF_CONDUCT.md`

行为规范说明。

### `docs/`

本地说明文档目录。当前包括：

- `docs/logic-spec.md`
- `docs/architecture-diagram.md`
- `docs/development-conventions.md`
- `docs/repository-guide.md`

## 2. 核心源码

### `src/main.cpp`

系统主入口，负责启动流程和主循环。

### `src/PowerFSM.*`

电源状态机和睡眠策略。

### `src/modules/`

功能模块目录，是工程最重要的业务层之一。

### `src/graphics/`

显示、界面和绘制逻辑，包括屏幕驱动、字体、图形组件和一些特殊 UI。

### `src/gps/`

GPS 和坐标相关逻辑。

### `src/concurrency/`

线程、锁、信号量和并发封装。

### `src/motion/`

运动传感器相关逻辑。

### `src/watchdog/`

看门狗相关实现。

### `src/modules/Telemetry/`

遥测系统，包括设备、电源、环境、健康和传感器适配。

## 3. 板级与变体

### `variants/`

每个子目录对应一个板型或一类硬件适配。通常会包含：

- `platformio.ini`
- `variant.cpp`
- `variant.h`
- `pins_arduino.h`
- 板级补丁或特殊资源

### `boards/`

板级 JSON 定义，主要用于构建和板子描述。

## 4. 常见工作位置

- 想看启动流程，先看 `src/main.cpp`
- 想看模块装配，先看 `src/modules/Modules.cpp`
- 想看睡眠和供电，先看 `src/PowerFSM.cpp`
- 想看板级差异，先看 `variants/<platform>/<board>/`
- 想看仓库怎么贡献，先看 `CONTRIBUTING.md`

## 5. 推荐阅读顺序

1. `README.md`
2. `docs/index-zh.md`
3. `docs/repository-guide.md`
4. `docs/logic-spec.md`
5. `docs/architecture-diagram.md`
6. `docs/development-conventions.md`
7. `docs/terminology.md`

这样读下来，会先知道“这是个什么工程”，再知道“系统怎么跑”，最后知道“以后怎么改”。

## 6. 相关文档

- [`docs/README.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/README.md)
- [`docs/index-zh.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/index-zh.md)
- [`docs/terminology.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/terminology.md)
