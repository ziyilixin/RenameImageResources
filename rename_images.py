#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片重命名工具 - 核心脚本
将Assets.xcassets中的图片重命名为随机字符串，并更新所有引用
"""

import os
import re
import json
import shutil
import random
import string
import argparse
from pathlib import Path

class ImageRenamer:
    def __init__(self, project_name, assets_path, use_random_names=False):
        self.project_name = project_name.lower()
        self.assets_path = Path(assets_path)
        self.rename_mapping = {}
        self.old_to_new = {}
        self.use_random_names = use_random_names
        self.used_names = set()  # 避免重复的随机名称

    def generate_random_name(self, length=8):
        """生成随机字符串名称，不以数字开头"""
        while True:
            # 第一个字符必须是字母
            first_char = random.choice(string.ascii_lowercase)
            # 其余字符可以是字母或数字
            rest_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length-1))
            random_name = first_char + rest_chars
            
            # 确保名称唯一
            if random_name not in self.used_names:
                self.used_names.add(random_name)
                return random_name

    def generate_new_name(self, old_name, folder_name):
        """生成新的图片名称"""
        # 移除 .imageset 后缀
        base_name = old_name.replace('.imageset', '')
        
        # 如果使用随机名称
        if self.use_random_names:
            # 生成随机名称
            random_name = self.generate_random_name()
            new_name = f"{random_name}.imageset"
            return new_name
        
        # 使用项目前缀（原逻辑）
        if base_name.startswith(f"{self.project_name}_"):
            return old_name
        
        new_name = f"{self.project_name}_{base_name}.imageset"
        return new_name

    def rename_images(self, dry_run=False):
        """重命名图片文件夹"""
        print(f"🔄 开始重命名图片...")
        
        # 遍历所有 .imageset 文件夹
        for root, dirs, files in os.walk(self.assets_path):
            for dir_name in dirs:
                if dir_name.endswith('.imageset'):
                    old_path = os.path.join(root, dir_name)
                    
                    # 生成新名称
                    new_dir_name = self.generate_new_name(dir_name, dir_name)
                    new_path = os.path.join(root, new_dir_name)
                    
                    if old_path != new_path:
                        # 记录映射关系
                        old_base_name = dir_name.replace('.imageset', '')
                        new_base_name = new_dir_name.replace('.imageset', '')
                        self.old_to_new[old_base_name] = new_base_name
                        
                        if dry_run:
                            print(f"  预览: {old_base_name} → {new_base_name}")
                        else:
                            try:
                                # 重命名文件夹
                                shutil.move(old_path, new_path)
                                
                                # 重命名文件夹内的图片文件
                                self.rename_files_in_imageset(new_path, old_base_name, new_base_name)
                                
                                print(f"  ✓ {old_base_name} → {new_base_name}")
                            except Exception as e:
                                print(f"  ✗ 重命名失败 {old_base_name}: {e}")
        
        print(f"📊 {'预览' if dry_run else '完成'}重命名: {len(self.old_to_new)} 个图片")

    def rename_files_in_imageset(self, imageset_path, old_name, new_name):
        """重命名imageset文件夹内的文件并更新Contents.json"""
        # 重命名图片文件
        for file in os.listdir(imageset_path):
            if file.startswith(old_name) and file.endswith(('.png', '.jpg', '.jpeg')):
                old_file_path = os.path.join(imageset_path, file)
                new_file_name = file.replace(old_name, new_name)
                new_file_path = os.path.join(imageset_path, new_file_name)
                os.rename(old_file_path, new_file_path)
        
        # 更新Contents.json
        contents_file = os.path.join(imageset_path, "Contents.json")
        if os.path.exists(contents_file):
            try:
                with open(contents_file, 'r', encoding='utf-8') as f:
                    contents = json.load(f)
                
                # 更新filename字段
                for image in contents.get('images', []):
                    if 'filename' in image and old_name in image['filename']:
                        image['filename'] = image['filename'].replace(old_name, new_name)
                
                with open(contents_file, 'w', encoding='utf-8') as f:
                    json.dump(contents, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"    ⚠️ 更新Contents.json失败: {e}")

    def update_code_references(self, project_root):
        """更新代码文件中的图片引用"""
        print(f"🔄 更新代码文件中的图片引用...")
        
        code_files = []
        for root, dirs, files in os.walk(project_root):
            if 'Pods' in root:
                continue
            for file in files:
                if file.endswith(('.m', '.swift')):
                    code_files.append(os.path.join(root, file))
        
        total_updated = 0
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                file_updated = False
                
                # 更新所有映射关系
                for old_name, new_name in self.old_to_new.items():
                    patterns_replacements = []
                    
                    # Objective-C 模式
                    patterns_replacements.extend([
                        (f'ImageNamed\\(@"{re.escape(old_name)}"\\)', f'ImageNamed(@"{new_name}")'),
                        (f'\\[UIImage imageNamed:@"{re.escape(old_name)}"\\]', f'[UIImage imageNamed:@"{new_name}"]'),
                        (f'setImage:\\[UIImage imageNamed:@"{re.escape(old_name)}"\\]', f'setImage:[UIImage imageNamed:@"{new_name}"]'),
                        (f'setBackgroundImage:\\[UIImage imageNamed:@"{re.escape(old_name)}"\\]', f'setBackgroundImage:[UIImage imageNamed:@"{new_name}"]'),
                        (f'@"{re.escape(old_name)}"', f'@"{new_name}"'),
                    ])
                    
                    # Swift 模式
                    patterns_replacements.extend([
                        (f'UIImage\\(named: "{re.escape(old_name)}"\\)', f'UIImage(named: "{new_name}")'),
                        (f'UIImage\\.init\\(named: "{re.escape(old_name)}"\\)', f'UIImage.init(named: "{new_name}")'),
                        (f'"{re.escape(old_name)}"', f'"{new_name}"'),
                    ])
                    
                    for pattern, replacement in patterns_replacements:
                        if re.search(pattern, content):
                            content = re.sub(pattern, replacement, content)
                            file_updated = True
                
                # 如果文件有更新，写回文件
                if file_updated:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"  ✓ 更新: {os.path.relpath(file_path, project_root)}")
                    total_updated += 1
                
            except Exception as e:
                print(f"  ✗ 更新失败 {file_path}: {e}")
        
        print(f"📊 更新了 {total_updated} 个代码文件")

    def update_json_files(self, project_root):
        """更新JSON文件中的图片引用"""
        print(f"🔄 更新JSON文件中的图片引用...")
        
        json_files = []
        for root, dirs, files in os.walk(project_root):
            if 'Pods' in root:
                continue
            for file in files:
                if file.endswith('.json') and not file.startswith('.'):
                    json_files.append(os.path.join(root, file))
        
        total_updated = 0
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue
                
                updated_count = [0]
                self._update_json_recursive(data, self.old_to_new, updated_count)
                
                if updated_count[0] > 0:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f"  ✓ 更新: {os.path.relpath(file_path, project_root)} ({updated_count[0]} 个引用)")
                    total_updated += 1
                    
            except Exception as e:
                print(f"  ✗ 更新失败 {file_path}: {e}")
        
        print(f"📊 更新了 {total_updated} 个JSON文件")

    def _update_json_recursive(self, obj, mapping, updated_count):
        """递归更新JSON对象中的图片名称"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and value in mapping:
                    obj[key] = mapping[value]
                    updated_count[0] += 1
                elif isinstance(value, (dict, list)):
                    self._update_json_recursive(value, mapping, updated_count)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, str) and item in mapping:
                    obj[i] = mapping[item]
                    updated_count[0] += 1
                elif isinstance(item, (dict, list)):
                    self._update_json_recursive(item, mapping, updated_count)

    def save_mapping_to_json(self, filename="image_mapping.json"):
        """保存映射关系到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.old_to_new, f, indent=4, ensure_ascii=False)
        print(f"映射关系已保存到: {filename}")

    def save_mapping_to_report(self, filename="rename_report_project.txt"):
        """保存映射关系到报告文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("图片重命名映射关系报告\n")
            f.write("=" * 40 + "\n\n")
            for i, (old_name, new_name) in enumerate(self.old_to_new.items(), 1):
                f.write(f"{i:2d}:  {old_name} → {new_name}\n")
            f.write(f"\n总计: {len(self.old_to_new)} 个图片\n")
        print(f"映射关系报告已保存到: {filename}")

    def load_mapping_from_json(self, filename="image_mapping.json"):
        """从JSON文件加载映射关系"""
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                self.old_to_new = json.load(f)
            print(f"从 {filename} 加载了 {len(self.old_to_new)} 个映射关系")
            return True
        return False

def main():
    parser = argparse.ArgumentParser(description='图片重命名工具')
    parser.add_argument('assets_path', help='Assets.xcassets 路径')
    parser.add_argument('--project-name', default='project', help='项目名称（用作图片前缀，使用随机名称时可选）')
    parser.add_argument('--project-root', help='项目根目录路径（用于更新代码引用）')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要进行的操作，不实际执行')
    parser.add_argument('--json-only', action='store_true', help='仅更新JSON文件中的图片引用，不重命名图片')
    parser.add_argument('--random-names', action='store_true', help='使用随机字符串作为图片名称（不以数字开头）')
    parser.add_argument('--mapping-file', default='image_mapping.json', help='映射关系文件名')
    
    args = parser.parse_args()
    
    # 检查路径
    if not os.path.exists(args.assets_path):
        print(f"错误: Assets路径不存在: {args.assets_path}")
        return
    
    # 创建重命名器
    renamer = ImageRenamer(args.project_name, args.assets_path, args.random_names)
    
    if args.json_only:
        # 仅更新引用模式
        if renamer.load_mapping_from_json(args.mapping_file):
            if args.project_root:
                renamer.update_code_references(args.project_root)
                renamer.update_json_files(args.project_root)
        else:
            print("错误: 找不到映射文件，无法更新引用")
    else:
        # 完整重命名模式
        print("🚀 开始图片重命名流程...")
        
        # 重命名图片
        renamer.rename_images(args.dry_run)
        
        if not args.dry_run and renamer.old_to_new:
            # 保存映射关系
            renamer.save_mapping_to_json(args.mapping_file)
            renamer.save_mapping_to_report()
            
            # 更新引用
            if args.project_root:
                renamer.update_code_references(args.project_root)
                renamer.update_json_files(args.project_root)
        
        print("✅ 图片重命名完成！")

if __name__ == "__main__":
    main()
