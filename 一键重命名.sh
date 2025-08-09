#!/bin/bash
# 图片重命名一键脚本
# 使用方法: ./一键重命名.sh

echo "🚀 开始图片重命名流程..."

# 检查必要文件
if [ ! -f "rename_images.py" ]; then
    echo "❌ 错误: 找不到 rename_images.py"
    exit 1
fi

if [ ! -f "fix_ai_json.py" ]; then
    echo "❌ 错误: 找不到 fix_ai_json.py"
    exit 1
fi

# 设置路径
ASSETS_PATH="Kicdel/Classes/Source/Assets.xcassets"
PROJECT_ROOT="."

# 检查Assets路径
if [ ! -d "$ASSETS_PATH" ]; then
    echo "❌ 错误: Assets路径不存在: $ASSETS_PATH"
    echo "请确认您在正确的项目根目录中运行此脚本"
    exit 1
fi

echo "📁 Assets路径: $ASSETS_PATH"
echo "📁 项目根目录: $PROJECT_ROOT"

# 询问是否继续
read -p "是否继续执行图片重命名? (y/N): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "操作已取消"
    exit 0
fi

# 第一步：重命名图片
echo ""
echo "第一步：重命名图片文件..."
python3 rename_images.py "$ASSETS_PATH" --random-names --project-root "$PROJECT_ROOT"

if [ $? -ne 0 ]; then
    echo "❌ 图片重命名失败"
    exit 1
fi

# 第二步：修复JSON引用
echo ""
echo "第二步：修复JSON文件引用..."
python3 fix_ai_json.py --project-root "$PROJECT_ROOT" --mapping-file "rename_report_project.txt"

if [ $? -ne 0 ]; then
    echo "❌ JSON引用修复失败"
    exit 1
fi

# 第三步：验证结果
echo ""
echo "第三步：验证结果..."

# 检查是否还有原始文件夹
ORIGINAL_FOLDERS=$(find "$ASSETS_PATH" -name "Kicdel_*" -type d 2>/dev/null | wc -l)
if [ $ORIGINAL_FOLDERS -gt 0 ]; then
    echo "⚠️  发现 $ORIGINAL_FOLDERS 个原始文件夹未处理"
    find "$ASSETS_PATH" -name "Kicdel_*" -type d
else
    echo "✅ 没有发现原始文件夹"
fi

# 检查映射文件
if [ -f "rename_report_project.txt" ]; then
    MAPPING_COUNT=$(grep "→" rename_report_project.txt | wc -l)
    echo "✅ 映射关系文件存在，包含 $MAPPING_COUNT 个映射"
else
    echo "⚠️  映射关系文件不存在"
fi

echo ""
echo "🎉 图片重命名流程完成！"
echo ""
echo "📋 重要文件："
echo "  - rename_images.py      (核心重命名脚本)"
echo "  - fix_ai_json.py        (JSON引用修复脚本)"
echo "  - rename_report_project.txt (映射关系报告)"
echo "  - image_mapping.json    (JSON格式映射文件)"
echo ""
echo "💡 建议："
echo "  1. 在Xcode中清理缓存并重新构建项目"
echo "  2. 测试应用确保图片正常显示"
echo "  3. 提交代码: git add -A && git commit -m '完成图片重命名'"
