Gorw Smart is online market place and Ai assistance for farmers.It helps farmer to sell their produces directly to exporters.
It helps farmer to better manage supply chain of crops by taking Ai assistance.The frontend is implemented using html css and javascript.
The backend is implemented using python (django).SQLite is used as promary data base to store data.Farmer can list their products with name,price,desciption
catagory and can view their product on farmer dashboard.They can view their active product,order recieved,order completed and total revenue generated.
They can contact admin for any issue.Kafka is used as messaging service.When farmer list product, the notifiaction is send to all exporter with all product detail.
Farmer can add thier land information like land size,land location (agro-ecological zone)soil type,water resource(rain,tubewell,canal) etc.
Farmer cantake AI assistance for crop management like crop suggestion based on land inforamtion, what to do in specific stage.
crop managment flow:
1) farmer want to add product
2) Ai suggest top three crops and thir varaity based on land inforamtion and current weather condiotion(stage 1).
3) Farmer select one crop and varaity and proceed to next stage soil prepartion (stage 2).
4) Ai guide farmer how to prepare soil for selected crop and land information.
5) famer proceed to next stage and take Ai assistance related to that specific stage.
6) On last stage post-harvesting app prompt farmer to record harvest yield and any remark.
7) Harvest yield is stored in database for further analysis.
when farmer login the app will redirect farmer to farmer dashboard where app will give guidance about current crops.Data like crops condition,soil ph,crop image can be sent through IOTs,
and Ai will give guidnace to take actions.
Mian User:
1)farmer:
action:
 a) List product
 b) Fulfill order
 c) Take Ai assitance for crop managment.
2) exporter/buyer
actions:
   a)Browse  products
   b) Add product to cart
   c) purchase product
3) Analyst
action:
   a)View all currents crops by farmer.
   b) View all previous crops
   for analysis like which crops is currently growing most,how much specifict crop has been harvested etc.
AI Module:
Ai Module is implemented using Retrival Augmented Generation (RAG).
Relevent agricultural pdf is store in vectore database (pinecone) for context aware response.
Langchain and gemini is used for implementing RAG.
The RAG module will take data landsize,location,water resources,siol mosture current weather data,current crop stage and prevoice AI response and  generate response.
