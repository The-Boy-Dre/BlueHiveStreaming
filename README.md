
============================================================================================================================
=== To setup ===
============================================================================================================================
1. npx @react-native-community/cli init FirestickStreamingApp

2. npm install @react-navigation/native @react-navigation/stack react-native-screens react-native-safe-area-context react-native-gesture-handler react-native-reanimated react-native-get-random-values react-native-tvos react-native-video axios lru-cache

3. Run the following command in your back end project folder (movie-backend):
npm install nodemon --save-dev
npm install ts-node --save-dev


============================================================================================================================
=== To RUN ===
============================================================================================================================
see these  steps:
1.  enter command in in the backend's directory: "node server.js"

2.  Connecting Your Fire TV for Testing enabling Developer Options on Fire TV:
    Go to Settings > My Fire TV > Developer Options and enable ADB Debugging and Apps from Unknown Sources.

    Find Your Fire TV’s IP Address:
    (Under Settings > Network.)
    Connect via ADB in PowerShell:

3.  enter command: "adb connect <FIRE_TV_IP>:5555"

4.  verify devices:
    "adb devices"

    If the app fails to launch or connect, check your server logs (the terminal where node server.js is running).
    "adb logcat"

5.  Navigate to the Front-End Directory:
    "npx react-native run-android"


============================================================================================================================
Project Overview
============================================================================================================================
Fetch movie data from external sources (via web scraping or APIs).
Stream movies using video URLs.
Cache API responses using lru-cache to improve performance.
Use Axios for making HTTP requests.
Use a database to store user data, movie metadata, and session information.

Tech Stack
Front End: React Native (with react-native-tvos for Firestick support).
Back End: Node.js with Express.
Database: MongoDB (or any database of your choice).
Web Scraping: Cheerio or Puppeteer.
Caching: lru-cache.
HTTP Requests: Axios.

Video Streaming: react-native-video.

============================================================================================================================
=== To Uninstall ClI ===
============================================================================================================================
1. npm uninstall -g react-native-cli
2. npm cache clean --force





web scrappers can roate their ip addresses via residential proxy networks making it look like  the traffic is from actual users

I will leave glob at version 7.2.3 as thats the version used by the react-native0tvos dependencies,
Any more code needed for glob's development on my part will make use of the latest version





Add this to your gradle.properties file in your project:

# Set Gradle cache location to shorter path
gradle.user.home=C:\\gradle_cache

# Enable long path support
org.gradle.internal.longliving.process=1