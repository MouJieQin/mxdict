from setuptools import setup, Extension
import pybind11

# 编译配置
ext_modules = [
    Extension(
        # 模块名：import word_engine
        name="word_engine",
        # 你的 C++ 源码文件名
        sources=["word_engine.cpp"],
        # 包含 pybind11 头文件
        include_dirs=[pybind11.get_include()],
        # C++17 标准
        language="c++",
        # 编译优化（生产环境必须开，速度拉满）
        extra_compile_args=["-O3", "-std=c++20", "-fvisibility=hidden"],
    ),
]

setup(
    name="word_engine",
    version="1.0",
    description="C++ 词典单词存储 + 高速搜索引擎",
    ext_modules=ext_modules,
    zip_safe=False,
)
