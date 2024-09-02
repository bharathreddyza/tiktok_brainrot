# TikTok Video Generator

   This project automates the creation of TikTok brainrot videos .


   ## demo videos 
   [fgoogle drive](https://drive.google.com/drive/folders/1SqH56N9Sf3YdSg51gB4hn-jaoeOYvL3T?usp=drive_link)

   ## Setup Instructions
   
   1. Clone the repository:
      ```
      git clone https://github.com/your-username/tiktok-video-generator.git
      cd tiktok-video-generator
      ```
   
   2. [optional] create virtual environment
       ```
      myenv\Scripts\activate
       
      ```


   3. Set up environment variables in /server:
      ```
      cp .env.example .env
      ```
      Edit the `.env` file and fill in your OPEN_AI_API API keys.

   4. Install dependencies:
      ```
      cd frontend
      npm install

      cd ../server 
      pip install -r requirements.txt
      ```

   5. download the demo background videos
       ```
      python ytd.py

      ```
    

   6. Start the server and frontend:
      ```
     
      cd frontend
      npm start

     
      cd backend
      python app.py
      ```

   7. Open the browser and navigate to `http://localhost:3000`

 
 
   ## Troubleshooting
   there could be some package erros depending on your python version  with ImageMagick and ffmgpeg
   uninstall and install python to fix these issues and click on  "install legacy utilities".


   occalsionaly there could be errors creating audio files , just click on create again to start the process again
   AttributeError: 'str' object has no attribute 'items'


 ## Thank you!

 
