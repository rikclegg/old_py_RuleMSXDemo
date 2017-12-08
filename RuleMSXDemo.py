# RuleMSXDemo.py

import EasyMSX
import rulemsx

class RuleMSXDemo:
    
    def __init__(self):

        print("Initialising RuleMSX...")
        self.ruleMSX = rulemsx.RuleMSX()
        print("RuleMSX initialised...")
        print("Initialising EasyMSX...")
        self.easyMSX = EasyMSX.EasyMSX()
        print("EasyMSX initialised...")
        
        self.easyMSX.orders.addNotificationHandler(self.processNotification)
        self.easyMSX.routes.addNotificationHandler(self.processNotification)

        self.easyMSX.start()
             

if __name__ == '__main__':
    
    ruleMSXDemo = RuleMSXDemo();
    
    input("Press any to terminate")

