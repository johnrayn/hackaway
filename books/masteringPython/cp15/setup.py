import setuptools

if __name__ == '__main__':
    setuptools.setup(
        name='Our little project',
        entry_points={
            'console_scripts': [
                'spam = spam.main:main',
            ],
        },
    )

# pip install -e .
# spam 123 abc
