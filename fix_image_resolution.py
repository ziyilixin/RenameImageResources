#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复图片文件分辨率后缀脚本
将图片文件重命名为正确的@2x和@3x格式
"""

import os
import json
import argparse
import shutil

def fix_image_resolution_files(assets_path, dry_run=False):
    """修复图片文件的分辨率后缀"""
    print(f"🔄 开始修复图片文件分辨率后缀...")
    
    fixed_count = 0
    
    # 遍历所有 .imageset 文件夹
    for root, dirs, files in os.walk(assets_path):
        for dir_name in dirs:
            if dir_name.endswith('.imageset'):
                imageset_path = os.path.join(root, dir_name)
                folder_name = dir_name.replace('.imageset', '')
                
                print(f"处理: {folder_name}")
                
                # 检查当前文件
                current_files = [f for f in os.listdir(imageset_path) if f.endswith('.png')]
                
                # 如果只有一个.png文件，需要创建@2x和@3x版本
                if len(current_files) == 1 and current_files[0] == f"{folder_name}.png":
                    single_file = current_files[0]
                    single_file_path = os.path.join(imageset_path, single_file)
                    
                    # 创建@2x和@3x版本
                    file_2x = f"{folder_name}@2x.png"
                    file_3x = f"{folder_name}@3x.png"
                    
                    if dry_run:
                        print(f"  预览: 复制 {single_file} → {file_2x}")
                        print(f"  预览: 复制 {single_file} → {file_3x}")
                        print(f"  预览: 删除 {single_file}")
                    else:
                        try:
                            shutil.copy2(single_file_path, os.path.join(imageset_path, file_2x))
                            shutil.copy2(single_file_path, os.path.join(imageset_path, file_3x))
                            os.remove(single_file_path)
                            print(f"  ✓ 创建: {file_2x}, {file_3x}")
                        except Exception as e:
                            print(f"  ✗ 处理失败: {e}")
                
                # 更新Contents.json
                contents_file = os.path.join(imageset_path, "Contents.json")
                if os.path.exists(contents_file):
                    try:
                        with open(contents_file, 'r', encoding='utf-8') as f:
                            contents = json.load(f)
                        
                        updated = False
                        for image in contents.get('images', []):
                            if 'filename' in image:
                                scale = image.get('scale', '1x')
                                if scale == '2x':
                                    new_filename = f"{folder_name}@2x.png"
                                elif scale == '3x':
                                    new_filename = f"{folder_name}@3x.png"
                                else:
                                    continue
                                
                                if image['filename'] != new_filename:
                                    if dry_run:
                                        print(f"  预览Contents.json: {image['filename']} → {new_filename}")
                                    else:
                                        image['filename'] = new_filename
                                        updated = True
                        
                        if updated and not dry_run:
                            with open(contents_file, 'w', encoding='utf-8') as f:
                                json.dump(contents, f, indent=2, ensure_ascii=False)
                            print(f"  ✓ 更新Contents.json")
                            
                    except Exception as e:
                        print(f"  ⚠️ 更新Contents.json失败: {e}")
                
                fixed_count += 1
    
    print(f"📊 {'预览' if dry_run else '完成'}修复: {fixed_count} 个imageset文件夹")

def main():
    parser = argparse.ArgumentParser(description='修复图片文件分辨率后缀')
    parser.add_argument('assets_path', help='Assets.xcassets 路径')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要进行的操作，不实际执行')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.assets_path):
        print(f"错误: Assets路径不存在: {args.assets_path}")
        return
    
    fix_image_resolution_files(args.assets_path, args.dry_run)
    print("✅ 图片文件分辨率后缀修复完成！")

if __name__ == "__main__":
    main()
