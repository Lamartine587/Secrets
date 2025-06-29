from setuptools import setup

setup(
    name='Secrets',
    version='1.0.0',
    py_modules=['app'],
    url='https://github.com/lamartine587/Secrets',
    license='MIT',
    author='Don',
    author_email='kipkoechlamartine@gmail.com',  # Replace with your email
    description='A Tkinter-based encryption app with a neon hacker-style interface',
    install_requires=[
        'cryptography>=36.0.0',
    ],
    python_requires='>=3.8',  # Specify minimum Python version
    entry_points={
        'console_scripts': [
            'neoncrypt=app:main',
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)
