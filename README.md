### What kind of project is this?
A bot (written in python) in which you can view today's store in Fortnite, as well as subscribe to the newsletter from the bot when updating the store in the game. 

### What did I use?
- Python
- Fortnite API
- threading (library)

### How my telegram bot works?
In the **_get_shop_info_** file, I get data from the Fortnite API and process it, then I download the necessary images and create one single collage from them.

At 03:01 (UTC+3), the script described above is launched and a message is sent to all users who have subscribed to the newsletter. But the user also has the opportunity to get information about the store at the time of sending the request (/shop_today).

### Why did I even start creating this project?
This project was created to explore working with external APIs and a bit with multithreading.