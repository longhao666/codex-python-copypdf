## Why
- N-up 合并输出页始终为横向，默认体验与常见纵向阅读习惯不符。
- 需要在不影响单页合并的情况下，提供可选的横向输出能力。

## What Changes
- 默认将 N-up 生成的页面设为纵向（高度 >= 宽度）。
- 新增 `--orientation {portrait|landscape}` 选项以便显式挑选方向。
- 更新 README 说明并在代码中实现参数解析与布局逻辑。

## Impact
- CLI 接口新增一个可选参数（默认改为纵向行为）。
- 依赖横向输出的现有脚本需指定 `--orientation landscape`。