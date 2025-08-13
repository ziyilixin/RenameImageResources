# Vexa 图片重命名工具

## 功能说明

这个工具可以自动重命名iOS项目中的图片资源，并更新所有相关的代码引用和JSON文件引用。

## 主要功能

- 🔄 重命名 `Assets.xcassets` 中的图片资源
- 📝 更新代码文件中的图片引用
- 📄 更新JSON文件中的图片引用
- 🔧 自动检查和修复JSON格式问题
- 📊 生成重命名映射报告

## 使用方法

### 基本用法

```bash
python3 rename_images.py "Vexa/Classes/Source/Assets.xcassets" --random-names --project-root "."
```

### 参数说明

- `assets_path`: Assets.xcassets 文件夹路径
- `--random-names`: 使用随机字符串作为图片名称
- `--project-root`: 项目根目录路径（用于更新代码和JSON引用）

### 其他选项

- `--dry-run`: 仅显示将要进行的操作，不实际执行
- `--json-only`: 仅更新JSON文件中的图片引用，不重命名图片

## 输出文件

运行后会生成以下文件：

- `image_mapping.json`: 图片重命名映射关系（JSON格式）
- `rename_report_project.txt`: 图片重命名映射报告（文本格式）

## 示例

```bash
# 重命名所有图片为随机名称，并更新所有引用
python3 rename_images.py "Vexa/Classes/Source/Assets.xcassets" --random-names --project-root "."

# 仅查看将要进行的操作（不实际执行）
python3 rename_images.py "Vexa/Classes/Source/Assets.xcassets" --random-names --project-root "." --dry-run
```

## 注意事项

1. 运行前请确保已备份重要文件
2. 脚本会自动检查和修复JSON格式问题
3. 重命名操作不可逆，请谨慎操作
4. 建议在版本控制系统中提交当前状态后再运行

## 技术特性

- ✅ 自动JSON格式检查和修复
- ✅ 支持Objective-C和Swift代码文件
- ✅ 递归更新JSON文件中的图片引用
- ✅ 生成详细的重命名报告
- ✅ 安全的文件操作（支持dry-run模式）
