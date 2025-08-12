#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复JSON文件中的图片引用
根据映射关系文件更新JSON文件中的图片名称
"""

import json
import os
import sys
import argparse
import re

def load_mapping_from_json(mapping_file):
    """从JSON文件加载图片名称映射关系"""
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"读取文件内容长度: {len(content)} 字符")
            mapping = json.loads(content)
        print(f"从 {mapping_file} 加载了 {len(mapping)} 个映射关系")
        return mapping
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        print(f"错误位置: 第{e.lineno}行，第{e.colno}列")
        # 显示错误位置附近的内容
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                start_line = max(0, e.lineno - 3)
                end_line = min(len(lines), e.lineno + 2)
                print("错误位置附近的内容:")
                for i in range(start_line, end_line):
                    marker = ">>> " if i == e.lineno - 1 else "    "
                    print(f"{marker}{i+1:3d}: {lines[i].rstrip()}")
        except Exception as read_error:
            print(f"无法读取文件内容: {read_error}")
        return {}
    except Exception as e:
        print(f"❌ 加载映射文件失败: {e}")
        return {}

def load_mapping_from_report(report_file):
    """从报告文件加载映射关系"""
    mapping = {}
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            if '→' in line:
                parts = line.strip().split('→')
                if len(parts) == 2:
                    old_name = parts[0].strip()
                    new_name = parts[1].strip()
                    # 移除行号前缀
                    if ':' in old_name:
                        old_name = old_name.split(':', 1)[1].strip()
                    mapping[old_name] = new_name
        
        print(f"从 {report_file} 加载了 {len(mapping)} 个映射关系")
        return mapping
        
    except Exception as e:
        print(f"❌ 加载映射文件失败: {e}")
        return {}

def update_json_recursive(obj, mapping, updated_count):
    """递归更新JSON对象中的图片名称"""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str) and value in mapping:
                old_value = value
                new_value = mapping[value]
                obj[key] = new_value
                updated_count[0] += 1
                print(f"    {key}: {old_value} → {new_value}")
            elif isinstance(value, (dict, list)):
                update_json_recursive(value, mapping, updated_count)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, str) and item in mapping:
                old_value = item
                new_value = mapping[item]
                obj[i] = new_value
                updated_count[0] += 1
                print(f"    [索引{i}]: {old_value} → {new_value}")
            elif isinstance(item, (dict, list)):
                update_json_recursive(item, mapping, updated_count)

def fix_json_file(json_path, mapping):
    """修复JSON文件中的图片引用"""
    try:
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"正在修复 {json_path}...")
        print(f"  文件大小: {len(content)} 字符")
        
        # 尝试解析JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON解析错误: {e}")
            print(f"  错误位置: 第{e.lineno}行，第{e.colno}列")
            # 显示错误位置附近的内容
            lines = content.split('\n')
            start_line = max(0, e.lineno - 3)
            end_line = min(len(lines), e.lineno + 2)
            print("  错误位置附近的内容:")
            for i in range(start_line, end_line):
                marker = ">>> " if i == e.lineno - 1 else "    "
                print(f"  {marker}{i+1:3d}: {lines[i]}")
            return 0
        
        # 计数器
        updated_count = [0]
        
        # 递归更新所有图片引用
        update_json_recursive(data, mapping, updated_count)
        
        # 如果有更新，写回文件
        if updated_count[0] > 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"  ✅ 更新了 {updated_count[0]} 个引用")
        else:
            print(f"  - 没有找到需要更新的引用")
        
        return updated_count[0]
        
    except Exception as e:
        print(f"  ❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return 0

def find_json_files(project_root):
    """查找项目中的所有JSON文件"""
    json_files = []
    for root, dirs, files in os.walk(project_root):
        # 跳过 Pods 目录
        if 'Pods' in root:
            continue
        for file in files:
            if file.endswith('.json') and not file.startswith('.'):
                json_files.append(os.path.join(root, file))
    return json_files

def main():
    parser = argparse.ArgumentParser(description='修复JSON文件中的图片引用')
    parser.add_argument('--mapping-file', default='rename_report_project.txt', help='映射关系文件路径')
    parser.add_argument('--json-file', help='要修复的单个JSON文件路径')
    parser.add_argument('--project-root', help='项目根目录路径（处理所有JSON文件）')
    
    args = parser.parse_args()
    
    # 检查映射文件是否存在
    if not os.path.exists(args.mapping_file):
        print(f"错误: 映射文件不存在: {args.mapping_file}")
        print("请先运行 rename_images.py 生成映射文件")
        sys.exit(1)
    
    # 加载映射关系
    if args.mapping_file.endswith('.txt'):
        mapping = load_mapping_from_report(args.mapping_file)
    else:
        mapping = load_mapping_from_json(args.mapping_file)
    
    if not mapping:
        print("错误: 映射文件为空或加载失败")
        sys.exit(1)
    
    total_updated = 0
    
    if args.json_file:
        # 处理单个JSON文件
        if not os.path.exists(args.json_file):
            print(f"错误: JSON文件不存在: {args.json_file}")
            sys.exit(1)
        
        updated = fix_json_file(args.json_file, mapping)
        total_updated += updated
        
    elif args.project_root:
        # 处理项目中的所有JSON文件
        if not os.path.exists(args.project_root):
            print(f"错误: 项目根目录不存在: {args.project_root}")
            sys.exit(1)
        
        json_files = find_json_files(args.project_root)
        print(f"找到 {len(json_files)} 个JSON文件")
        
        for json_file in json_files:
            updated = fix_json_file(json_file, mapping)
            total_updated += updated
    
    else:
        print("错误: 请指定 --json-file 或 --project-root 参数")
        parser.print_help()
        sys.exit(1)
    
    print(f"\n✅ 处理完成！总共更新了 {total_updated} 个图片引用")

if __name__ == "__main__":
    main()