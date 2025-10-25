#!/usr/bin/env python3
"""
MinerU 模型预下载脚本
在 Docker 构建时运行此脚本，预下载所有必需的模型文件到缓存目录
这样可以利用 Docker 层缓存机制，避免每次构建都重新下载模型
"""
import os
import sys

def download_mineru_models():
    """下载 MinerU 所需的模型文件"""
    print("=" * 60)
    print("开始预下载 MinerU 模型文件...")
    print("=" * 60)
    
    try:
        # 设置模型源
        model_source = os.getenv('MINERU_MODEL_SOURCE', 'modelscope')
        print(f"使用模型源: {model_source}")
        
        # 导入 magic_pdf 相关模块来触发模型下载
        print("\n[1/4] 导入 magic_pdf 模块...")
        from magic_pdf.model.doc_analyze_by_custom_model import ModelSingleton
        
        print("[2/4] 初始化文档分析模型...")
        # 初始化模型单例，这会触发模型下载
        model = ModelSingleton()
        
        print("[3/4] 预加载模型...")
        # 调用模型方法确保所有依赖都已下载
        # 这里使用一个空的测试来触发模型初始化
        try:
            # 尝试初始化各个模型组件
            _ = model.get_model()
            print("    ✓ 文档分析模型加载成功")
        except Exception as e:
            print(f"    ⚠ 模型初始化警告: {e}")
            # 某些模型可能需要实际数据才能完全初始化，这里忽略错误
        
        print("[4/4] 检查其他依赖...")
        # 导入其他可能需要下载模型的组件
        try:
            import torch
            print(f"    ✓ PyTorch 版本: {torch.__version__}")
            print(f"    ✓ CUDA 可用: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"    ✓ CUDA 版本: {torch.version.cuda}")
                print(f"    ✓ GPU 设备: {torch.cuda.get_device_name(0)}")
        except ImportError:
            print("    ⚠ PyTorch 未安装")
        
        print("\n" + "=" * 60)
        print("✅ 模型下载完成!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 模型下载失败: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(download_mineru_models())
