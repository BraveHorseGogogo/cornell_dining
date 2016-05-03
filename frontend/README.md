Cornell Dining App Build Instructions
=======
#   Cornell Dining Team, CS5150, Fall 2013
#
# - By following the instructions below, you will be able to build the app for iOS and Android

# - The complete file structure should look like the following:

#    frontend source code and build instructions/
#    |
#    |-android/                 - permissions and icons on Android
#    |-Build instructions.md    - this file
#    |-www/                     - contains the main code of the project
#    |-ios/                     - configurations, icons and splash images on iOS

# - Before using the instructions, you should have set up the phonegap environment already. You should be able to find enough instructions to do that online.
# - One starting point: http://phonegap.com/install/
# - This set of instructions are written for and tested with phonegap 3.0.0


# 1. create a new phonegap project using the following commands, you can change 'cornelldining' to whatever you want

phonegap create cornelldining
cd cornelldining

# 2. Manually replace the www/ folder in the current 'cornelldining' folder, then you can start building applications!


# for iOS
# run the following command in 'cornelldining'. 
phonegap build ios
#If the build is successful, you should be able to see some outputs followed by '[phonegap] successfully compiled ios app'. And you should see there is a new folder namely ios under cornelldining/platforms/. Then:
copy files under ios to cornelldining/platforms/ios 
  i. Clean project in XCode (shift + cmd + K)
  ii. Remove the app from the device or the simulator
  iii. Build again and reinstall


# for Android
# run the following command in 'cornelldining'. If the build is successful, you should be able to see some outputs followed by '[phonegap] successfully compiled Android app' And you should see there is a new folder namely Android under cornelldining/platforms/. Then:
phonegap build android
copy files under android to cornelldining/platforms/android
phonegap build android