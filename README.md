# ir-group-21
A collaboration project for DSAI ECS736p Assignment 3. 

This project is in development, so should not be used in a production environment!

## Pre-requisites 
NodeJS
<br>
Python 3.10
<br>
MongoDB Community Server 
<br>
Java
<br>
Local version of TREC clinical dataset 2021

## Instalation steps and instructions for processing data and starting "server" side of the system.   

1. Clone the GitHub Repository 
2. Open the search-engine-server folder in a text-editor / IDE or terminal of your choice and create a virtual environment for python packages. 
3. Install the requirements (pip install -r requirements.txt)
4. In order to run the code you must have the TREC clinical dataset  2021 downloaded. If not download it before continuing... ensure that the documents are unzipped. 
5. In the data_processing.py file found in the root of search-engine-server, edit line 113 to add the path to the dataset. 
6. Run the data_processing.py file to process the dataset... the creation of the term freqency term matrix leads to an exponential increase in time adding documents / terms so feel free to stop the process when you have a sufficiently large matrix. 
7. Run the main.py file (also found in the root of search-engine-server) to start the server running. This will enable the "server-side" element of the system. 

## Instalation steps and instructions for starting "client" side of the system.   

1. Open the search-engine-client folder in a text-editor / IDE or terminal of your choice. 
2. Install the requirements (npm i)
3. Enable the "client-side" element of the system. (npm run dev)
