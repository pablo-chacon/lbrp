from setuptools import setup, find_packages

setup(
    name='lbrp',
    version='1.0.2',
    packages=find_packages(),
    url='https://github.com/pablo-chacon/lbrp/tree/main',
    license='MIT',
    author='pablo-chacon',
    author_email='ekarlsson66@gmail.com',
    description='Location Based Route Planner',
    install_requires=[
        'pandas',
        'geopandas',
        'folium',
        'streamlit',
        'streamlit-folium',
        'geopy',
        'shapely',
        'scikit-learn',
        'matplotlib',
        'python-dotenv',
        'requests',
        'gpxpy'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.8',
)
