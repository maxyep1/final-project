Introduction

Living in PA and still struggling to find the right repair shop? Our project is designed specifically for car owners, offering an intelligent recommendation system for second-hand car repair shops. By deeply analyzing Yelp data, including business information and user reviews, we’ve identified which repair shops excel at solving specific problems and deliver the best results. No matter what issue your car is facing, we can help you find the most experienced repair shops!

Additionally, we’ve created an interactive GIS map that allows car owners to easily visualize the locations and specialties of nearby repair shops, enabling quick and informed decision-making. What’s more, we analyze seasonal trends in common car issues to provide customized maintenance recommendations, helping car owners prevent potential problems in advance and keep their vehicles in top condition all year round.

Whether you need urgent repairs or regular maintenance, our system is your reliable assistant, making car care simpler and worry-free! 🚗✨

![997EBFED-DCDC-4A7C-8FF8-D27B824E474B](https://github.com/user-attachments/assets/1c5479c4-d2c3-4971-b9be-3d9769ffd8c5)


Data Analysis and Experience Evaluation

In this section, we evaluate the frequency of specific faults repaired by each shop across different time periods to analyze their expertise in handling particular issues. By counting the number of times each shop repairs different fault types and combining this data with user ratings, we calculate a comprehensive score for each shop's proficiency in repairing specific issues. Additionally, we analyze the seasonal trends of various fault types to identify common seasonal issues, providing tailored maintenance recommendations to help car owners proactively prevent potential problems.

Step 1: Run the script code/backend/fault_maintenance_frequency.py to process the Yelp dataset and calculate the frequency of specific fault repairs for each shop. This script aggregates repair data by time periods and fault types to generate a detailed frequency table. This analysis provides insights into which shops are more experienced in certain repair projects and their active time periods.

Step 2: Run the script code/backend/calculate_score.py to score each repair shop's expertise. This script combines repair frequencies with user ratings to calculate a composite score for each shop’s performance in repairing specific faults. These scores help identify the top-performing shops for different repair projects, enabling car owners to make informed choices.

Step 3: Run the script code/backend/seasonal_trends.py to analyze the seasonal trends of fault types. Then, run the script code/backend/seasonal_tips_app.py to generate a visualized GIS map based on the analysis results. Together, these scripts identify the most common seasonal issues and provide corresponding tailored maintenance recommendations. For example, the analysis might reveal that battery failures are more frequent in winter, prompting maintenance tips for cold seasons to help car owners proactively address potential problems.
