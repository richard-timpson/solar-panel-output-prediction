# Presentation

## Hook/headline
This should be centered around the fact that focusing on data driven solutions to renewable energy is the right way to approach the subject, both from a policy perspective and also application perspective. The perspective that I am approaching the problem from is an application perspective. I don't want to give out too much information but I could talk about how much of the work I'm doing is going to be used for a legimate company. 

## Thesis and Core Argument
This will probably be the most difficult part of the presentation for me to answer. I have done a lot of work centered around the topic but I need to focus on exactly what it is that I am doing. Here are some ideas.  

1. Using a combination of a time series analysis and standard linear regression models it is possible to build predictive models for both solar panel production and home energy consumption. Given enough data (a years worth) these models can be built with a certain amount of accuracy on a granular level. 

## Points 

1. Data is appropriate because it is coming from real homes and is therefore messy. The data is not simulated or produced from a lab which may be typical of public research in the same area. This makes the corresponding models suited for actual use in a home energy application for actual residential homes. 
2. The percentage error in the regression models is under a certain value. It's hard to define a hard boundary for what is good enough and what isn't, but if the error is less than 50% it is certinaly good enough to work with. The specific application would need to take this into account. Obviously, more accurate models are always better. 
3. Show figures from production regression and time series autoregression

## "To Be Sure"
There is a concern of how much the data can be trusted when modeling a real life future prediction. I have already talked and thought a lot about issues with weather data and that is worth mentioning. There could also be room for errors in the sensor data that is used to gather the data. If this is the case I have not come up with a way to validate that there are no errors or have looked into the probability that there would be an error. These concerns are definitely worth investigating but are a little outside the scope of the project. 

Given that the data does come from legitimate homes there is also a concern of missing data or outliers in the dataset. Many of the homes have quite a lot of missing data and I haven't been sure what the best way to deal with that has been. If not properly accounted for it could cause some issues. 

## Conclusion
Understanding and being able to predict home energy consumption and solar energy production at a granular level can be useful for smart energy applications. Given weather, location, and demographic data, along with an exploration of the temporal relationships in production and consumption data, it is possible to predict future values with a high level of accuracy. 