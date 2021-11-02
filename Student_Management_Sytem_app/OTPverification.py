import math,random
import time



def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(5):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

class TOTPVerification:

    def __init__(self):
        self.key =generateOTP()
        # counter with which last token was verified.
        # Next token must be generated at a higher counter value.
        self.last_verified_counter = -1
        # this value will return True, if a token has been successfully
        # verified.
        self.error = ""

        # validity period of a token. Default is 30 second.
        self.token_validity_period = 600
        self.time=time.time()
    def verify_key(self,key,ttime,token):
        print("ggggg")
        try:
           token = int(token)

        except ValueError:
            self.error = "Invalid OTP"
            return False
        else:
            timelapse=abs(float(time.time())-ttime)
            maxtime=float(self.token_validity_period)
            if timelapse <= maxtime:
                if(key==token):
                   return True
                else:
                    self.error='wrong OTP'
                    return False
            else:
                self.error="Time OUT"
                return False


