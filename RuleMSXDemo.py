# RuleMSXDemo.py

from EasyMSX import EasyMSX
from rulemsx import RuleMSX
from rulecondition import RuleCondition
from ruleevaluator import RuleEvaluator
from action import Action

class RuleMSXDemo:
    
    def __init__(self):

        print("Initialising RuleMSX...")
        self.ruleMSX = RuleMSX()
        print("RuleMSX initialised...")
        
        print("Create RuleSet...")
        self.buildRules()
        print("RuleSet ready...")
        
        print("Initialising EasyMSX...")
        self.easyMSX = EasyMSX()
        print("EasyMSX initialised...")
        
        self.easyMSX.orders.addNotificationHandler(self.processNotification)
        self.easyMSX.routes.addNotificationHandler(self.processNotification)

        self.easyMSX.start()
             
    class StringEqualityEvaluator(RuleEvaluator):
        
        def __init__(self, dataPointName, targetValue):
            self.dataPointName = dataPointName
            self.targetValue = targetValue
            super().addDependentDataPointName(dataPointName)
        
        def evaluate(self,dataSet):
            dpValue = dataSet.dataPoints[self.dataPointName].getValue()
            return dpValue==self.targetValue
        
    class SendMessageWithDataPointValue(Action):
        
        def __init__(self,msgStr, dataPointName):
            self.msgStr = msgStr
            self.dataPointName = dataPointName
            
        def execute(self,dataSet):
            dpValue = dataSet.dataPoints[self.dataPointName].getValue()
            print (self.msgStr + dpValue)
            
        
    class ShowFillEvent(Action):
        
        def __init__(self):
            pass
        
        def execute(self,dataSet):
            dpOrderNo = dataSet.dataPoints["OrderNumber"].getValue()
            ord = self.easyMSX.orders[dpOrderNo]
            print("Fill event for: " + dpOrderNo)
            
    def buildRules(self):
        
        condStatusNew = RuleCondition("OrderStatusIsNew", self.StringEqualityEvaluator("OrderStatus","NEW"))
        condStatusWorking = RuleCondition("OrderStatusIsWorking", self.StringEqualityEvaluator("OrderStatus","WORKING"))
        condStatusPartFilled = RuleCondition("OrderStatusIsPartFilled", self.StringEqualityEvaluator("OrderStatus","PARTFILLED"))
        condStatusFilled = RuleCondition("OrderStatusIsFilled", self.StringEqualityEvaluator("OrderStatus","FILLED"))

        #condUSExchange = RuleCondition("IsUSExchange", self.StringEqualityEvaluator("Exchange","US"))
        #condLNExchange = RuleCondition("IsLNExchange", self.StringEqualityEvaluator("Exchange","LN"))

        #condPercentFilled = RuleCondition("Route50%Filled", self.PercentageFilledEvaluator(50))
        
        #actionSetDestBrokerBB = self.ruleMSX.createAction("SetDestBroker", self.SetDestinationBroker("BB"))
        #actionSetDestBrokerBMTB = self.ruleMSX.createAction("SetDestBroker", self.SetDestinationBroker("BMTB"))
        #actionRouteOrder = self.ruleMSX.createAction("RouteOrder", self.RouteOrder())
        
        actionSendNewMessage = self.ruleMSX.createAction("SendNewMessage", self.SendMessageWithDataPointValue("New Order Created: ", "OrderNumber"))
        actionSendAckMessage = self.ruleMSX.createAction("SendAckMessage", self.SendMessageWithDataPointValue("Broker Acknowledged Route: ", "OrderNoAndRouteID"))
        actionSendFillMessage = self.ruleMSX.createAction("SendFillMessage", self.ShowFillEvent())
        
        #actionShowOrderDetails = self.ruleMSX.createAction("ShowOrderDetails", self.ShowOrderDetails())
        #actionShowRouteDetails = self.ruleMSX.createAction("ShowRouteDetails", self.ShowRouteDetails())
        #actionCancelRoute = self.ruleMSX.createAction("CancelRoute", self.CancelRoute())
        
        demoRuleSet = self.ruleMSX.createRuleSet("demoRuleSet")

        ruleNewOrder = demoRuleSet.addRule("NewOrder")
        ruleNewOrder.addRuleCondition(condStatusNew)
        ruleNewOrder.addAction(actionSendNewMessage)
        
        ruleWorkingOrder = demoRuleSet.addRule("WorkingOrder")
        ruleWorkingOrder.addRuleCondition(condStatusWorking)
        ruleWorkingOrder.addAction(actionSendAckMessage)
        
        rulePartFilledOrder = demoRuleSet.addRule("PartFilledOrder")
        rulePartFilledOrder.addRuleCondition(condStatusPartFilled)
        rulePartFilledOrder.addAction(actionSendFillMessage)
        
        ruleFilledOrder = demoRuleSet.addRule("FilledOrder")
        ruleFilledOrder.addRuleCondition(condStatusFilled)
        ruleFilledOrder.addAction(actionSendFillMessage)

        #ruleSetUSDestBroker = demoRuleSet.addRule("SetUSDestBroker")
        #ruleSetUSDestBroker.addRuleCondition(condUSExchange)
        #ruleSetUSDestBroker.addRuleCondition(condStatusNew)
        
        #ruleRouteOrder = demoRuleSet.addRule("RouteOrder")
        

    def processNotification(self,notification):

        if notification.category == EasyMSX.NotificationCategory.ORDER:
            if notification.type == EasyMSX.NotificationType.NEW or notification.type == EasyMSX.NotificationType.INITIALPAINT: 
                print("EasyMSX Event (NEW/INITALPAINT): " + notification.source.field("EMSX_SEQUENCE").value())
                self.parseOrder(notification.source)


    def parseOrder(self,o):
        
        

if __name__ == '__main__':
    
    ruleMSXDemo = RuleMSXDemo();
    
    input("Press any to terminate")

    print("Terminating...")

    quit()
    