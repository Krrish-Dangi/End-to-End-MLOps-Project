from setuptools import setup, find_packages
from typing import List

def get_req()->List[str]:
    req = []

    try:
        with open("Requirements.txt", 'r') as file:
            lines = file.readlines()

            for line in lines:
                requirement = line.strip()

                if requirement and requirement != '-e .':
                    req.append(requirement)

    except Exception:
        pass

    return req


setup(
    name="Network Security",
    author="Krrish Dangi",
    version="0.0.1",
    author_email= "krrishdangi2005@gmail.com",
    packages=find_packages(),
    install_requires= get_req()
)