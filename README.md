# FPT VISION

<div>
  <p align="center">
    <img src="images/logo.svg" width="800"> 
  </p>
</div>

Welcome to FPT Vision, an application built using the QT library that combines the power of facial detection and recognition. With the utilization of the RetinaFace model for facial detection and the Iresnet100 and ArcFace models for facial recognition, FPT Vision provides accurate and efficient face labeling and recognition capabilities.

This application allows users to label names for faces captured through a camera or images, enabling the creation of labeled datasets for training and identification purposes. Additionally, FPT Vision leverages the camera to perform real-time face recognition, providing instant identification and verification.

With a user-friendly interface, FPT Vision offers seamless interaction and intuitive controls for capturing, labeling, and recognizing faces. The advanced deep learning techniques employed by FPT Vision ensure reliable and precise results, enabling users to effectively organize and analyze face-related data.

Make the most of FPT Vision to streamline your face labeling and recognition tasks, whether it's for security, identification, or personalized applications. Feel empowered with this powerful tool that harnesses the capabilities of QT, RetinaFace, Iresnet100, and ArcFace to enhance your facial analysis workflows.

<p align="center">
  <img src="https://img.shields.io/badge/OS-Windows-red?style=flat&logo=" />
  <img src="https://img.shields.io/badge/Python-v3.9.13-blue?style=flat&logo=python" />
  <img src="https://img.shields.io/badge/Neural%20Network-Iresnet100%2C%20ArcFace-yellow?style=flat&logo=pytorch" />
  <img src="https://img.shields.io/badge/QT-6.3.2-green?style=flat&logo=qt" />
  <a href="https://github.com/Zeres-Engel"><img src="https://img.shields.io/github/followers/Zeres-Engel.svg?style=social&label=Follow" /></a>
</p>

# Table of Content
- [Overview](#overview)
- [Construction](#construction)
- [Building the Model](#building-the-model)
- [Deploying the Product](#deploying-the-product)
    - [User Interface](#user-interface)
    - [Configuration](#configuration)

## Overview

The app is designed to automatically scrape stock data using the VNStock API and predict the stock price for the following day. The app displays the predicted stock price using a chart.
  <img src="images/overview.png" width="800">


## Construction


## Building the Model

## Deploying the Product

To use the Surfing Stock app, users simply need to download and install the required libraries and run the main.py file or         https://drive.google.com/file/d/1OmZuhPzRKWvL9k_hTiSArxFXpCDq9sx- . The app will automatically scrape stock data and use the saved LSTM model to make predictions for the following day's stock price.

The predicted stock price is displayed on the app's user interface, along with a chart that shows the historical stock prices and the predicted stock price for the next day.

The app also includes a settings menu where users can adjust the time range of the historical stock data displayed on the chart, as well as the time range of the predicted stock price.

Overall, the Surfing Stock app provides a user-friendly and efficient way for users to make informed decisions in their investment strategies by utilizing the power of deep learning to predict stock prices.

  ### User Interface

  The product has a user interface that displays the predicted stock price using a chart. The chart is designed to be easy to read and understand.

  Closing price chart:

  <img src="images/overview.png" width="800">

  Model quality rating chart:

  <img src="images/evaluate.png" width="800">

  ### Configuration

  The Surfing Stock app has a user-friendly interface that displays predicted stock prices using a chart. To run this code, programers need to install the required libraries, which are listed in the requirements.txt file.
