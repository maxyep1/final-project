Automotive Repair Provider Recommendation System in Pennsylvania

December 13, 2024
Python, Big Data, and Databases (ECO395m)

Fan Ye, Huiwen Lian, Chengyang Xu, Ningtao Xu, Songyang Wu

## Introduction

Living in PA and still struggling to find the right repair shop? Our project is designed specifically for car owners, offering an intelligent recommendation system for second-hand car repair shops. By deeply analyzing Yelp data, including business information and user reviews, we’ve identified which repair shops excel at solving specific problems and deliver the best results. No matter what issue your car is facing, we can help you find the most experienced repair shops!

Additionally, we’ve created an interactive GIS map that allows car owners to easily visualize the locations and specialties of nearby repair shops, enabling quick and informed decision-making. What’s more, we analyze seasonal trends in common car issues to provide customized maintenance recommendations, helping car owners prevent potential problems in advance and keep their vehicles in top condition all year round.

Whether you need urgent repairs or regular maintenance, our system is your reliable assistant, making car care simpler and worry-free! 🚗✨

![997EBFED-DCDC-4A7C-8FF8-D27B824E474B](https://github.com/user-attachments/assets/1c5479c4-d2c3-4971-b9be-3d9769ffd8c5)


## Data Analysis and Experience Evaluation

In this section, we evaluate the frequency of specific faults repaired by each shop across different time periods to analyze their expertise in handling particular issues. By counting the number of times each shop repairs different fault types and combining this data with user ratings, we calculate a comprehensive score for each shop's proficiency in repairing specific issues. Additionally, we analyze the seasonal trends of various fault types to identify common seasonal issues, providing tailored maintenance recommendations to help car owners proactively prevent potential problems.

Step 1: Run the script code/backend/fault_maintenance_frequency.py to process the Yelp dataset and calculate the frequency of specific fault repairs for each shop. This script aggregates repair data by time periods and fault types to generate a detailed frequency table. This analysis provides insights into which shops are more experienced in certain repair projects and their active time periods.

Step 2: Run the script code/backend/calculate_score.py to score each repair shop's expertise. This script combines repair frequencies with user ratings to calculate a composite score for each shop’s performance in repairing specific faults. These scores help identify the top-performing shops for different repair projects, enabling car owners to make informed choices.

Step 3: Run the script code/backend/seasonal_trends.py to analyze the seasonal trends of fault types. Then, run the script code/backend/seasonal_tips_app.py to generate a visualized GIS map based on the analysis results. Together, these scripts identify the most common seasonal issues and provide corresponding tailored maintenance recommendations. For example, the analysis might reveal that battery failures are more frequent in winter, prompting maintenance tips for cold seasons to help car owners proactively address potential problems.




## Limitation and Further Extension

Despite the functionality our project provides, there are still some limitations that can be improved in the future:

Manual Location Input: Currently, users need to manually input latitude and longitude coordinates to perform a search. This process is not very user-friendly. In the future, we plan to integrate JavaScript to request location permissions directly from users, enabling the system to automatically retrieve and use their geographic coordinates for instant feedback and seamless interaction.

Basic NLP Approach: Our current NLP implementation relies on a predefined fault dictionary for keyword matching. While effective for specific scenarios, it lacks flexibility and adaptability to diverse queries. In the future, we aim to incorporate more advanced algorithms, such as transformer-based models, to provide more accurate and contextual query interpretations.

Lack of Personalization in Recommendations: The current recommendation results are primarily based on repair frequency and user ratings, without taking individual user preferences into account, such as budget, distance preferences, or repair time requirements. In the future, we plan to introduce user profiling, allowing users to customize their queries with more options and receive recommendations tailored to their specific needs.

Static Recommendation Logic: The current recommendation logic is static and focuses solely on repair frequency and user ratings. It does not account for dynamic factors such as shop availability, current workload, or estimated repair times. In the future, integrating live data streams and shop scheduling systems could make the recommendations more dynamic and practical.

## Deploy
### Project structure
The project frontend uses **Streamlit**, and the backend uses the **Flask** framework. The two communicate via the HTTP protocol. The project structure is as follows:

```bash
code/
│
├── backend/           # Flask application codes
│   ├── app.py         # Flask main file
│   ├── ...
│   ├── requirements.txt  # Backend dependencies
│
├── frontend/          # Streamlit application codes
│   ├── main.py        # Streamlit main file
│   ├── ... 
│   ├── requirements.txt  # Frontend dependencies
│
├── Dockerfile         # used to pack the whole project
└── start.sh      # project start script
```
### Deployment Method
1. Integrate Flask and Streamlit into a **single container**.
2. Build a Docker image and push it to **Google Container Registry (GCR)**.
3. Deploy the containerized application to **Google Cloud Run** using Google Cloud SDK.

#### Google Cloud Run
Google Cloud Run is a fully managed container cloud platform that allows applications to be easily deployed in Docker containers and automatically scales container instances based on usage.

#### GCR (Google Container Registry) 
GCR is a private container image storage service provided by Google Cloud Platform (GCP). It allows developers to store, manage, and deploy Docker container images. It integrates seamlessly with Cloud Run and other GCP services for easy container deployment.

### Project URL
Our website can be accessed by following link:

[Best Auto Repair](https://my-web-app-280617041204.us-central1.run.app/)
