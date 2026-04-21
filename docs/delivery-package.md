# Meshtastic Firmware 本地交付文档包

> 文档定位：本文档用于对当前仓库的逻辑、结构和开发约定做正式整理，适合作为本地交付材料、团队共享材料或长期维护参考。

## 1. 文档目标

本仓库是 Meshtastic 固件工程的本地源码镜像，涵盖多平台硬件适配、LoRa Mesh 通信、传感器遥测、屏幕交互、电源管理和后台任务调度。

本交付文档包的目标是：

- 明确工程职责边界
- 统一启动和模块装配理解
- 说明电源状态机和主循环的协作方式
- 规范后续开发和变体适配方式
- 为新人、协作者和审查者提供一致的阅读入口

## 2. 核心结论

### 2.1 这个工程是什么

这是一个以固件为核心的硬件通信平台，而不是单一功能应用。系统运行依赖于：

- 板级早期初始化
- 条件编译和变体适配
- 模块化功能装配
- 电源状态机控制
- 持续轮询和事件驱动调度

### 2.2 这个工程怎么组织

- `src/main.cpp` 负责启动编排。
- `src/modules/` 负责功能模块。
- `src/PowerFSM.*` 负责供电和睡眠状态。
- `variants/` 负责硬件差异。
- `boards/` 负责板级定义。

### 2.3 这个工程怎么扩展

新增能力时应优先考虑：

- 能否复用已有模块
- 是否需要板级差异隔离
- 是否会影响启动顺序
- 是否会影响电源状态切换
- 是否会影响其他平台编译

## 3. 运行模型

### 3.1 启动链路

1. 初始化电源 HAL
2. 检查供电安全
3. 执行变体早期初始化
4. 配置关键引脚和板级电源
5. 探测屏幕、GPS、I2C、无线和传感器
6. 创建全局状态对象
7. 装配模块
8. 启动电源状态机和相关线程
9. 进入主循环

### 3.2 模块链路

- 路由模块位于消息分发核心。
- 各业务模块负责各自的消息处理和状态更新。
- 遥测模块依赖传感器发现和配置开关。
- 输出侧模块负责屏幕、串口、通知和外围反馈。

### 3.3 电源链路

- 电源 HAL 提供底层供电判断。
- 状态机决定睡眠、唤醒和运行模式。
- 主循环负责持续检查命令和恢复逻辑。

## 4. 正式约定

### 4.1 代码边界

- 启动流程不应被业务逻辑污染。
- 模块职责应清晰单一。
- 变体只描述硬件差异，不承载通用业务。
- 全局状态对象应只保存状态，不保存复杂流程。

### 4.2 修改原则

- 先确认影响面，再修改实现。
- 先确认板型和平台，再加条件分支。
- 先确认状态机副作用，再改电源逻辑。
- 先确认模块创建顺序，再新增模块。

### 4.3 日志原则

- 启动阶段要能定位当前步骤。
- 失败信息要包含具体资源。
- 高频循环日志要节制。
- 状态切换日志要统一前缀。

## 5. 推荐使用方式

这份文档适合在以下场景使用：

- 作为本地交付包首页
- 作为团队共享材料
- 作为代码审查背景资料
- 作为后续扩展的基线说明

如果需要更细的内容，可继续顺着以下文档深入：

- [`docs/index-zh.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/index-zh.md)
- [`docs/repository-guide.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/repository-guide.md)
- [`docs/logic-spec.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/logic-spec.md)
- [`docs/architecture-diagram.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/architecture-diagram.md)
- [`docs/development-conventions.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/development-conventions.md)

## 6. 相关文档

- [`docs/README.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/README.md)
- [`docs/terminology.md`](/Users/bh4me_macair/Documents/Codex/mecho_f/docs/terminology.md)
