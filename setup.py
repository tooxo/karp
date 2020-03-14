from setuptools import find_packages, setup

with open("README.MD", "r") as f:
    t = f.read()

setup(
    name="karp",
    version="0.0.2",
    packages=find_packages(),
    url="https://github.com/tooxo/karp",
    license="None",
    author="tooxo",
    author_email="till@s.chulte.de",
    description="KARP Communication Protocol",
    long_description=t,
    long_description_content_type="text/markdown"
)
