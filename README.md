# travel_bot
Clone this repo  

#Make virtual env and activate it  
1.Make a virtul environment python -m venv bot_env  
2.cd bot_env/  
3.source bin/activate  

#Install all the Libraries
1.pip install -r requiements.txt  

#Build Model
1.Navigate to data folder  
2.Run Command: rasa train nlu  
3.A .tar file will be craeted in model directory.  

#Running the Script
1.Run the script file by : python script.py(only for once)  
2.Run command (To install the necessary java dependencies):  
	mvn dependency:copy-dependencies -DoutputDirectory=./jars -f $(python3 -c 'import importlib; import pathlib; print(pathlib.Path(importlib.util.find_spec("sutime").origin).parent / "pom.xml")')  
3. Run the app file : python app.py  
4.Acesss the bot using the link http://127.0.0.1:5000/  





